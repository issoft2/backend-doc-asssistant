from typing import List, Dict
from sqlmodel import SQLModel, Field, Session, select, delete
from datetime import datetime

from Vector_setup.user.db import ChatMessage  # adjust import


class ConversationSummary(SQLModel):
    conversation_id: str = Field(primary_key=True)
    first_question: str
    last_activity_at: datetime


class ConversationDetail(SQLModel):
    conversation_id: str
    messages: list[tuple[str, str]]  # (role, content)
    
def get_conversation_details_for_user(
    db: Session,
    conversation_id: str,
    tenant_id: str,
    user_id: str
):
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.tenant_id == tenant_id)
        .where(ChatMessage.conversation_id == conversation_id)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at, ChatMessage.id)
    )
    rows = db.exec(stmt).all()
    
    if not rows:
        return []
    msgs: list[tuple[str, str]] = []
    for msg in rows:
        msgs.append((msg.role, msg.content))
        
    return ConversationDetail(
        conversation_id=conversation_id,
        messages=msgs
    )    
            

def list_conversations_for_user(
    db: Session,
    tenant_id: str,
    user_id: str,
    limit: int = 20,
) -> List[ConversationSummary]:
    # 1) first user message per conversation, excluding NULL ids
    first_stmt = (
        select(
            ChatMessage.conversation_id,
            ChatMessage.content,
            ChatMessage.created_at,
        )
        .where(ChatMessage.tenant_id == tenant_id)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.role == "user")
        .where(ChatMessage.conversation_id.is_not(None))  # <‑‑ important
        .order_by(ChatMessage.conversation_id, ChatMessage.created_at)
    )
    first_rows = db.exec(first_stmt).all()

    if not first_rows:
        return []

    summaries_by_conv: Dict[str, ConversationSummary] = {}

    for conv_id, content, created_at in first_rows:
        if conv_id is None:          # extra safety
            continue
        conv_id_str = str(conv_id)
        if conv_id_str not in summaries_by_conv:
            summaries_by_conv[conv_id_str] = ConversationSummary(
                conversation_id=conv_id_str,
                first_question=content,
                last_activity_at=created_at,
            )

    if not summaries_by_conv:
        return []

    # 2) last activity per conversation (only for known ids)
    last_stmt = (
        select(
            ChatMessage.conversation_id,
            ChatMessage.created_at,
        )
        .where(ChatMessage.tenant_id == tenant_id)
        .where(ChatMessage.user_id == user_id)
        .where(ChatMessage.conversation_id.in_(list(summaries_by_conv.keys())))
        .order_by(ChatMessage.conversation_id, ChatMessage.created_at)
    )
    last_rows = db.exec(last_stmt).all()

    for conv_id, created_at in last_rows:
        if conv_id is None:
            continue
        conv_id_str = str(conv_id)
        if conv_id_str in summaries_by_conv:
            summaries_by_conv[conv_id_str].last_activity_at = created_at

    summaries = sorted(
        summaries_by_conv.values(),
        key=lambda c: c.last_activity_at,
        reverse=True,
    )
    return summaries[:limit]

# Delete a single conversation
def delete_conversation(
    db: Session,
    conversation_id: str,
    user_id: str,
    tenant_id: str
):
    stmt = select(ChatMessage).where(
        ChatMessage.conversation_id == conversation_id,
        ChatMessage.tenant_id == tenant_id,
        ChatMessage.user_id == user_id 
    )
    conv = db.exec(stmt).first()
    if not conv:
        return False
    
    # Delete messages first, then conversation (or use ON DELETE CASCADE in schema)
    db.exec(
        delete(ChatMessage).where(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.tenant_id == tenant_id,
            ChatMessage.user_id == user_id,
        )
    )
    db.delete(conv)
    db.commit()
    return True