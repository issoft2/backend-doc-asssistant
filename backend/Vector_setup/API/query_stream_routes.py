from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Optional, AsyncGenerator, List,  Dict, Any
import json

from LLM_Config.system_user_prompt import create_suggestion_prompt
from LLM_Config.llm_setup import suggestion_llm_client


from Vector_setup.user.db import get_db
from Vector_setup.API.ingest_routes import get_store
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from Vector_setup.user.auth_jwt import (
    get_current_user_from_header_or_query,
    TokenUser,
)
from Vector_setup.chat_history.chat_store import get_last_n_turns, save_chat_turn, get_last_doc_id
from LLM_Config.llm_pipeline import llm_pipeline_stream
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

@router.get("/query/stream")
async def query_knowledge_stream(
    request: Request,
    question: str,
    conversation_id: str,
    top_k: int = 100,
    collection_name: Optional[str] = None,  # currently unused, kept for compatibility
    current_user: TokenUser = Depends(get_current_user_from_header_or_query),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Streaming RAG query endpoint using Server-Sent Events (SSE).

    Events:
      - event: status       data: <human-readable pipeline stage>
      - event: token        data: <partial answer tokens, with '\\n' encoded as '<|n|>'>
      - event: suggestions  data: JSON list of follow-up question strings
      - event: done         data: END
    """
    if not conversation_id:
        raise HTTPException(status_code=403, detail="Session has expired!")

    # Recent conversation history for RAG + intent
    history_turns = get_last_n_turns(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        n_turns=3,
        conversation_id=conversation_id,
    )

    # Optional: last primary document id (for FOLLOWUP_ELABORATE)
    last_doc_id = get_last_doc_id(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        conversation_id=conversation_id,
    )

    def send_status(msg: str) -> str:
        """Format a status event for SSE."""
        return f"event: status\ndata: {msg}\n\n"

    async def event_generator() -> AsyncGenerator[str, None]:
        full_answer: List[str] = []
        result_holder: Dict[str, Any] = {}

        # --- high-level pipeline steps ---
        # 1) Understand question
        yield send_status("Analyzing your question…")

        # 2) Retrieve & rank docs for RAG
        yield send_status("Retrieving relevant information…")
        yield send_status("Ranking and summarizing retrieved information…")

        # 3) Generate answer (streaming tokens)
        yield send_status("Generating final answer…")

        # --- main answer streaming ---
        try:
            async for chunk in llm_pipeline_stream(
                store=store,
                tenant_id=current_user.tenant_id,
                question=question,
                history=history_turns,
                top_k=top_k,
                result_holder=result_holder,   # will contain sources, primary_doc_id, etc.
                last_doc_id=last_doc_id,       # helps keep follow-ups on same doc
            ):
                # Stop if client disconnects
                if await request.is_disconnected():
                    break
                if not chunk:
                    continue

                full_answer.append(chunk)

                # Encode newlines for SSE clients that treat lines as records
                safe_chunk = chunk.replace("\n", "<|n|>")
                yield f"event: token\ndata: {safe_chunk}\n\n"
        except Exception as e:
            # Optional: send an error event (or just log and fall through)
           logger.exception("Pipeline error in /api/query/stream")
           # keep message generic to client
           yield (
                "event: status\n"
                "data: An error occurred while generating the answer.\n\n"
            )
           yield "event: done\ndata: END\n\n"


        # Reconstruct final answer exactly as produced
        answer_str = "".join(full_answer)

        # --- persistence + suggestions ---
        if answer_str:
            # 4) Save conversation turn
            yield send_status("Saving this conversation…")

            primary_doc_id = result_holder.get("primary_doc_id")

            save_chat_turn(
                db=db,
                tenant_id=current_user.tenant_id,
                user_id=current_user.email,
                user_message=question,
                assistant_message=answer_str,
                conversation_id=conversation_id,
                primary_doc_id=primary_doc_id,
            )

            # 5) Generate follow-up suggestions
            yield send_status("Generating related follow-up questions…")

            suggestions_list: List[str] = []
            try:
                suggestion_messages = create_suggestion_prompt(question, answer_str)
                raw = suggestion_llm_client.invoke(suggestion_messages)
                raw_content = getattr(raw, "content", None) or str(raw)
                suggestions_list = json.loads(raw_content)
                # Be defensive: ensure it is a list of strings
                if not isinstance(suggestions_list, list):
                    suggestions_list = []
                else:
                    suggestions_list = [
                        s for s in suggestions_list if isinstance(s, str) and s.strip()
                    ]
            except Exception:
                suggestions_list = []

            if suggestions_list:
                payload = json.dumps(suggestions_list)
                yield f"event: suggestions\ndata: {payload}\n\n"
                
            # ... Chart spec event ---
            chart_spec = result_holder.get("chart_spec")
            if chart_spec:
                try:
                    chart_payload = json.dumps({"charts": result_holder["chart_specs"]})
                    yield f"event: chart\ndata: {chart_payload}\n\n"
                except Exception:
                    logger.warning("Failed to serialize chart_spec for SSE")    

        # 6) Finalize
        yield send_status("Finalizing…")
        yield "event: done\ndata: END\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

