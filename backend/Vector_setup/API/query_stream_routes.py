from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select 
from typing import Optional, AsyncGenerator, List,  Dict, Any
import json

from LLM_Config.system_user_prompt import create_suggestion_prompt
from LLM_Config.llm_setup import suggestion_llm_client


from Vector_setup.user.db import get_db, Tenant, DBUser, Collection
from Vector_setup.API.ingest_routes import get_store
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from Vector_setup.user.auth_jwt import (
    get_current_db_user_from_header_or_query,
    TokenUser,
)
from Vector_setup.chat_history.chat_store import get_last_n_turns, save_chat_turn, get_last_doc_id
from LLM_Config.llm_pipeline import llm_pipeline_stream
from Vector_setup.user.auth_jwt import ensure_tenant_active
from Vector_setup.access.collections_acl import get_allowed_collections_for_user
from Vector_setup.user.audit import write_audit_log

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

import json
@router.get("/query/stream")
async def query_knowledge_stream(
    request: Request,
    question: str,
    conversation_id: str,
    top_k: int = 100,
    collection_name: Optional[str] = None,
    current_user: TokenUser = Depends(get_current_db_user_from_header_or_query),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    if not conversation_id:
        raise HTTPException(status_code=403, detail="Session has expired!")

    # Optional FE filter
    requested_names = [collection_name] if collection_name else None

    # --- ACL: which collections can this user query? ---
    allowed_collections = get_allowed_collections_for_user(
        db=db,
        user=current_user,         # make sure this is the same shape your ACL expects
        requested_name=requested_names,
    )

    logger.info(
        "ACL_DEBUG user_id=%s role=%s org=%s allowed=%s",
        current_user.id,
        current_user.role,
        current_user.organization_id,
        [(c.id, c.name, c.organization_id) for c in allowed_collections],
    )

    # Hard stop: no allowed collections => no LLM, no stream
    if not allowed_collections:
        raise HTTPException(
            status_code=403,
            detail="You are not given permission to query this system.",
        )

    collection_names = [c.name for c in allowed_collections]
    collection_ids = [str(c.id) for c in allowed_collections]

    logger.info("Collection names for query: %s", collection_names)

    # --- conversation history + last doc ---
    history_turns = get_last_n_turns(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        n_turns=3,
        conversation_id=conversation_id,
    )

    last_doc_id = get_last_doc_id(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        conversation_id=conversation_id,
    )

    def send_status(msg: str) -> str:
        return f"event: status\ndata: {msg}\n\n"

    async def event_generator() -> AsyncGenerator[str, None]:
        full_answer: List[str] = []
        result_holder: Dict[str, Any] = {}

        # 1) Understand question
        yield send_status("Analyzing your question…")

        # 2) Retrieval + ranking (done inside llm_pipeline_stream)
        yield send_status("Retrieving relevant information…")
        yield send_status("Ranking and summarizing retrieved information…")

        # 3) Generate answer (streaming tokens)
        yield send_status("Generating final answer…")

        try:
            async for chunk in llm_pipeline_stream(
                store=store,
                tenant_id=current_user.tenant_id,
                question=question,
                history=history_turns,
                top_k=top_k,
                result_holder=result_holder,
                last_doc_id=last_doc_id,
                collection_names=collection_names,
            ):
                if await request.is_disconnected():
                    break
                if not chunk:
                    continue

                full_answer.append(chunk)
                safe_chunk = chunk.replace("\n", "<|n|>")
                yield f"event: token\ndata: {safe_chunk}\n\n"
        except Exception:
            logger.exception("Pipeline error in /api/query/stream")
            yield send_status("An error occurred while generating the answer.")
            yield "event: done\ndata: END\n\n"
            return

        answer_str = "".join(full_answer)

        # 4) Save conversation turn only if there is an answer
        if answer_str:
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

            # 5) Follow-up suggestions
            yield send_status("Generating related follow-up questions…")

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
                        s for s in suggestions_list
                        if isinstance(s, str) and s.strip()
                    ]
            except Exception:
                suggestions_list = []

            if suggestions_list:
                payload = json.dumps(suggestions_list)
                yield f"event: suggestions\ndata: {payload}\n\n"

            # 6) Chart event (optional)
            chart_spec = result_holder.get("chart_specs")
            if chart_spec:
                try:
                    chart_payload = json.dumps({"charts": chart_spec})
                    logger.info("CHART_DEBUG emitting chart SSE: %s", chart_payload)
                    yield f"event: chart\ndata: {chart_payload}\n\n"
                except Exception:
                    logger.warning("Failed to serialize chart_spec for SSE")

        # 7) Audit log (once per request)
        try:
            write_audit_log(
                db=db,
                user=current_user,
                action="query",
                resource_type="collection_query",
                resource_id=",".join(collection_ids),
                metadata={
                    "question": question,
                    "top_k": top_k,
                    "tenant_id": current_user.tenant_id,
                    "organization_id": current_user.organization_id,
                    "user_id": current_user.id,
                    "user_role": current_user.role,
                    "conversation_id": conversation_id,
                    "collection_ids": collection_ids,
                    "collection_names": collection_names,
                    "client_ip": request.client.host,
                },
            )
        except Exception:
            logger.warning("Failed to write audit log for query", exc_info=True)

        yield send_status("Finalizing…")
        yield "event: done\ndata: END\n\n"

    # Only users with allowed_collections ever get here; SSE/LLM never start otherwise
    return StreamingResponse(event_generator(), media_type="text/event-stream")
