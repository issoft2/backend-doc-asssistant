#!/usr/bin/env python3
from typing import List, Dict, Any, Tuple, Literal, Optional
import json

from LLM_Config.llm_setup import llm_client, suggestion_llm_client
from LLM_Config.system_user_prompt import create_context, create_suggestion_prompt
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager


IntentType = Literal["FOLLOWUP_ELABORATE", "NEW_QUESTION", "CHITCHAT", "UNSURE"]


INTENT_PROMPT_TEMPLATE = """
You are classifying a user's latest message in a policy/HR/finance assistant chat.

Conversation (most recent last):
{history_block}

Latest user message:
"{user_message}"

Decide:
- If the user is clearly asking a new, specific question, label it NEW_QUESTION.
- If the user is giving a short confirmation or vague follow-up like "Yes", "I want more information", "Tell me more", "I still need details", label it FOLLOWUP_ELABORATE and rewrite it into a more explicit question about the assistant's last answer.
- If the message is just small talk or courtesy (for example "Thanks", "Thank you, it is working now"), label it CHITCHAT and do not rewrite.
- If you really cannot tell, label it UNSURE.

Respond as pure JSON:
{{
  "intent": "<one of: FOLLOWUP_ELABORATE | NEW_QUESTION | CHITCHAT | UNSURE>",
  "rewritten_question": "<a clear, explicit question, or empty string if not needed>"
}}
""".strip()


def _format_history_for_intent(
    history_turns: Optional[List[Tuple[str, str]]],
    max_turns: int = 3,
) -> str:
    if not history_turns:
        return "(no previous turns)"
    recent = history_turns[-max_turns:]
    lines: List[str] = []
    for u, a in recent:
        lines.append(f"User: {u}")
        lines.append(f"Assistant: {a}")
    return "\n".join(lines)


def infer_intent_and_rewrite(
    user_message: str,
    history_turns: Optional[List[Tuple[str, str]]],
) -> Tuple[IntentType, str]:
    history_block = _format_history_for_intent(history_turns)
    prompt = INTENT_PROMPT_TEMPLATE.format(
        history_block=history_block,
        user_message=user_message,
    )

    messages = [
        {"role": "system", "content": "You are a strict intent classification helper."},
        {"role": "user", "content": prompt},
    ]
    
    try:
        resp =  llm_client.invoke(messages)
        
    except APIConnectionError:
        # If intent model is unreachable, just treat this as a new question
        return "NEW_QUESTION", user_message
    raw = getattr(resp, "content", None) or str(resp)

    try:
        data = json.loads(raw)
        intent = data.get("intent", "UNSURE")
        rewritten = data.get("rewritten_question") or ""
    except Exception:
        intent = "UNSURE"
        rewritten = ""

    if intent not in ("FOLLOWUP_ELABORATE", "NEW_QUESTION", "CHITCHAT", "UNSURE"):
        intent = "UNSURE"

    return intent, rewritten


async def llm_pipeline(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,  # [(user, assistant), ...]
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    End-to-end RAG pipeline:
      - Infer intent and possibly rewrite vague follow-ups.
      - Retrieve relevant chunks from Chroma for a given tenant.
      - Build system + user prompts with context (+ optional history).
      - Call LLM.
      - Return answer and sources.
    """

    # 1) Infer intent on the raw user message
    intent, rewritten =  infer_intent_and_rewrite(
        user_message=question,
        history_turns=history,
    )

    # 2) Handle pure chitchat cheaply (optional)
    if intent == "CHITCHAT":
        return {
            "answer": (
                "You’re welcome. If you have more questions about your payslips or company policies, "
                "feel free to ask."
            ),
            "sources": [],
        }

    # 3) Decide the effective question used for retrieval + prompting
    effective_question = rewritten if rewritten else question

    # 4) RETRIEVE (use effective_question, not the raw one)
    retrieval = await store.query_policies(
        tenant_id=tenant_id,
        collection_name=None,
        query=effective_question,
        top_k=top_k,
    )
    hits = retrieval.get("results", [])

    if not hits:
        return {
            "answer": (
                "The provided documents do not contain information to answer this question."
            ),
            "sources": [],
        }

    # 5) Build context chunks as strings including titles/filenames
    context_chunks: List[str] = []
    sources: List[str] = []

    for hit in hits:
        doc_text = hit["document"]
        meta = hit.get("metadata", {}) or {}

        title = meta.get("title") or meta.get("filename") or "Unknown document"
        section = meta.get("section")
        doc_id = meta.get("doc_id")

        header_parts = [f"Title: {title}"]
        if section:
            header_parts.append(f"Section: {section}")
        if doc_id:
            header_parts.append(f"Doc ID: {doc_id}")

        header = " | ".join(header_parts)
        chunk_str = f"{header}\n\n{doc_text}"
        context_chunks.append(chunk_str)

        sources.append(title)

    unique_sources = sorted(set(sources))

    # 6) Build system + user prompt from context + effective question
    system_prompt, user_prompt = create_context(context_chunks, effective_question)

    # 7) Build messages with optional history
    messages: List[Dict[str, str]] = []
    messages.append({"role": "system", "content": system_prompt})

    if history:
        # history already limited by caller
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": user_prompt})

    # 8) CALL LLM (await, since llm_client is async)
    response = llm_client.invoke(messages)
    answer = getattr(response, "content", None) or str(response)
    
    # generate followup for the user
    suggestion_message = create_suggestion_prompt(question, answer)
    raw  = suggestion_llm_client.invoke(suggestion_message)
    follow_ups = json.loads(raw.content)

    return {
        "answer": answer.strip(),
        "follow_up": follow_ups,
        "sources": unique_sources,
        
    }
