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
    """Classify the user's message and optionally rewrite vague follow-ups.

    On any LLM connection/parsing error, fall back to treating it as NEW_QUESTION.
    """
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
        # Use the small model for intent; cheaper and fast
        resp = suggestion_llm_client.invoke(messages)
    except Exception:
        # Any error here: don't crash, just treat as a new question
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
      - Call main LLM for answer.
      - Call small LLM for follow-up suggestions (best-effort).
      - Return answer, follow_up, and sources.
    """

    # 1) Infer intent on the raw user message
    intent, rewritten = infer_intent_and_rewrite(
        user_message=question,
        history_turns=history,
    )

    # 2) Handle pure chitchat cheaply (no vector search)
    if intent == "CHITCHAT":
        return {
            "answer": (
                "Hello! I’m your Organization Knowledge Assistant. "
                "You can ask me questions about your organization’s policies, procedures  and guidelines, "
                "or any other internal information you might want to know, and I’ll answer based on the information I currently have access to."
            ),
            "follow_up": [],
            "sources": [],
        }

    # 3) Decide the effective question used for retrieval + prompting
    effective_question = rewritten if rewritten else question

    # 4) RETRIEVE
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
            "follow_up": [],
            "sources": [],
        }

    # 5) Build context chunks and sources
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
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    if history:
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": user_prompt})

    # 8) Call main LLM for the answer (guarded)
    try:
        response = llm_client.invoke(messages)
        answer = getattr(response, "content", None) or str(response)
    except Exception:
        # If the main model is unreachable, fail gracefully
        return {
            "answer": "There was a temporary problem contacting the language model. Please try again.",
            "follow_up": [],
            "sources": unique_sources,
        }

    answer = answer.strip()

    # 9) Generate follow-up suggestions (best-effort, non-fatal)
    follow_ups: List[Any] = []
    suggestion_message = create_suggestion_prompt(question, answer)

    try:
        raw = suggestion_llm_client.invoke(suggestion_message)
        raw_content = getattr(raw, "content", None) or str(raw)
        follow_ups = json.loads(raw_content)
    except Exception:
        follow_ups = []

    return {
        "answer": answer,
        "follow_up": follow_ups,
        "sources": unique_sources,
    }
