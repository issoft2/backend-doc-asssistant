#!/usr/bin/env python3

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlmodel import Session


from Vector_setup.user.db import get_db, Tenant
from Vector_setup.API.ingest_routes import get_store
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from Vector_setup.user.auth_jwt import get_current_user, TokenUser  # <-- add this
from Vector_setup.base.auth_models import UserOut
from Vector_setup.chat_history.chat_store import get_last_n_turns, save_chat_turn
from Vector_setup.chat_history.conversation_store import list_conversations_for_user, ConversationSummary, get_conversation_details_for_user, delete_conversation
from Vector_setup.user.auth_jwt import ensure_tenant_active


router = APIRouter()

class QueryRequest(BaseModel):
    collection_name: Optional[str] = None
    top_k: int = 5
    question: str
    conversation_id: str | None = None
    
class ConversationDetail(BaseModel):
    conversation_id: str
    messages: list[tuple[str, str]]  # (role, content)    

@router.post("/query")
async def query_policies_api(
    req: QueryRequest,
    current_user: TokenUser = Depends(get_current_user),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(ensure_tenant_active)
):
    
    # 2) Get last 3 turns of chat this user + tenant
    history_turns = get_last_n_turns(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        n_turns=3,
        conversation_id=req.conversation_id,
    )
    # history_turns: list((user_msg, assistant_msg))
    
        
    # 3) Call LLM pipeline with history    
    response_text = ""
    
    # 4) Save this new turn
    if not req.conversation_id:
        raise HTTPException(status_code=403, detail="Session have expired!")
        
    save_chat_turn(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_message=req.question,
        assistant_message=response_text["answer"],
        conversation_id=req.conversation_id
    )
    
    
    
    
    return {"answer": response_text["answer"], "follow_up": response_text["follow_up"]}


@router.get("/conversations", response_model=list[ConversationSummary])
def list_user_conversations(
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(ensure_tenant_active),
):
    return list_conversations_for_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.email,
        limit=20,
    )
    


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation_detail(
    conversation_id: str,
    current_user: TokenUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(ensure_tenant_active),
):
   return get_conversation_details_for_user(
       db=db,
       conversation_id=conversation_id,
       tenant_id=current_user.tenant_id,
       user_id=current_user.email
   )  


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    delete_conv = delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.email,
        tenant_id=current_user.tenant_id
     )
    if delete_conv is False:
        raise HTTPException(status_code=404, detail="Could find conversation to delete")
    
    return 