from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Optional, AsyncGenerator, List,  Dict, Any
from fastapi.responses import JSONResponse

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
async def query_knowledge(
    request: Request,
    question: str,
    conversation_id: str,
    top_k: int = 100,
    collection_name: Optional[str] = None,  # kept for compatibility
    current_user: TokenUser = Depends(get_current_user_from_header_or_query),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Non-streaming RAG query endpoint.

    - Runs the same RAG + LLM pipeline as /query/stream
    - Collects the *final formatted* answer
    - Persists the turn
    - Returns JSON: { answer, suggestions, sources }
    """
    if not conversation_id:
        raise HTTPException(status_code=403, detail="Session has expired!")

    # 1) Conversation history for RAG + intent
    history_turns = get_last_n_turns(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        n_turns=3,
        conversation_id=conversation_id,
    )

    # 2) Optional: last primary document id (for FOLLOWUP_ELABORATE)
    last_doc_id = get_last_doc_id(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        conversation_id=conversation_id,
    )

    result_holder: Dict[str, Any] = {}
    chunks: List[str] = []

    # 3) Run the pipeline once and collect the final formatted answer
    try:
        async for chunk in llm_pipeline_stream(
            store=store,
            tenant_id=current_user.tenant_id,
            question=question,
            history=history_turns,
            top_k=top_k,
            result_holder=result_holder,  # will contain sources, primary_doc_id, etc.
            last_doc_id=last_doc_id,
        ):
            if chunk:
                chunks.append(chunk)
    except Exception:
        logger.exception("Pipeline error in /api/query")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the answer.",
        )

    answer_str = "".join(chunks).strip()

    if not answer_str:
        # No answer returned from pipeline
        raise HTTPException(
            status_code=500,
            detail="No answer was generated for this query.",
        )

    # 4) Persist chat turn
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

    # 5) Generate follow-up suggestions (same logic as in /query/stream)
    suggestions_list: List[str] = []
    try:
        suggestion_messages = create_suggestion_prompt(question, answer_str)
        raw = suggestion_llm_client.invoke(suggestion_messages)
        raw_content = getattr(raw, "content", None) or str(raw)
        suggestions_list = json.loads(raw_content)

        if not isinstance(suggestions_list, list):
            suggestions_list = []
        else:
            suggestions_list = [
                s for s in suggestions_list if isinstance(s, str) and s.strip()
            ]
    except Exception:
        suggestions_list = []

    # 6) Optional: expose sources if you want them in the UI
    sources = result_holder.get("sources", [])

    payload = {
        "answer": answer_str,
        "suggestions": suggestions_list,
        "sources": sources,
    }

    return JSONResponse(content=payload)
