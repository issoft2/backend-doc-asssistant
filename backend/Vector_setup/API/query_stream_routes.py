from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Optional

from Vector_setup.user.db import get_db
from Vector_setup.API.ingest_routes import get_store
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from Vector_setup.user.auth_jwt import get_current_user, TokenUser, get_current_user_from_header_or_query
from Vector_setup.chat_history.chat_store import get_last_n_turns, save_chat_turn
from LLM_Config.llm_pipeline import llm_pipeline_stream

router = APIRouter()

@router.get("/query/stream")
async def query_knowledge_stream(
    request: Request,
    question: str,
    conversation_id: str,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    current_user: TokenUser = Depends(get_current_user_from_header_or_query),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
):
    if not conversation_id:
        raise HTTPException(status_code=403, detail="Session have expired!")

    history_turns = get_last_n_turns(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        n_turns=3,
        conversation_id=conversation_id,
    )

    async def event_generator():
        full_answer: list[str] = []

        yield "event: status\ndata: Analyzing your request.....\n\n"
        yield "event: status\ndata: Retrieving relevant information.....\n\n"

        async for chunk in llm_pipeline_stream(
            store=store,
            tenant_id=current_user.tenant_id,
            question=question,
            history=history_turns,
            top_k=top_k,
        ):
            if await request.is_disconnected():
                break
            if chunk:
                full_answer.append(chunk)
                yield f"event: token\ndata: {chunk}\n\n"

        answer_str = "".join(full_answer).strip()

        if answer_str:
            save_chat_turn(
                db=db,
                tenant_id=current_user.tenant_id,
                user_id=current_user.email,
                user_message=question,
                assistant_message=answer_str,
                conversation_id=conversation_id,
            )

        yield "event: status\ndata: Finalizing.....\n\n"
        yield "event: done\ndata: END\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
