from typing import List, Dict, Any, Tuple, Literal, Optional, AsyncGenerator
import json

from LLM_Config.llm_setup import llm_client, suggestion_llm_client, llm_client_streaming
from LLM_Config.system_user_prompt import create_context, create_suggestion_prompt, create_critique_prompt
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager


import textwrap

RERANK_SYSTEM_PROMPT = """
You are a ranking assistant.

Goal:
- Given a user question and a list of text snippets, rank the snippets from most relevant to least relevant.

Instructions:
- Consider semantic relevance to the user question.
- Respond with ONLY a JSON array of indices (0-based) in descending order of relevance.
  For example: [2, 0, 1]
""".strip()


def build_rerank_messages(question: str, snippets: list[str]) -> list[dict]:
    numbered = "\n\n".join(
        [f"[{i}] {textwrap.shorten(s, width=800, placeholder='...')}" for i, s in enumerate(snippets)]
    )
    user_content = f"""
User question:
{question}

Snippets to rank (0-based indices in brackets):
{numbered}

Return a JSON array of indices from most relevant to least relevant.
""".strip()

    return [
        {"role": "system", "content": RERANK_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]



IntentType = Literal["FOLLOWUP_ELABORATE", "NEW_QUESTION", "CHITCHAT", "UNSURE"]



INTENT_PROMPT_TEMPLATE = """
You are classifying a user's latest message in a policy/HR/finance assistant chat.

Conversation (most recent last):
{history_block}

Latest user message:
"{user_message}"

Decide the intent of the latest message:

- If the user is clearly asking a new, specific question that does not simply ask to expand on the last answer,
  label it NEW_QUESTION.

- If the user is giving a short confirmation or follow-up that is mainly asking to elaborate on the assistant's
  previous answer (for example: "Yes", "I want more information", "Tell me more", "How did you arrive at your answer?",
  "Can you break this down?", "I still need details", "following the information you have"),
  label it FOLLOWUP_ELABORATE and rewrite it into a more explicit question ABOUT THE ASSISTANT'S LAST ANSWER
  or the SAME DOCUMENT. The rewritten question should:
  - Mention the main topic of the last answer (for example, retention rates, a specific policy, or a calculation),
  - If the last answer included a formula or numeric result, ask to explain the calculation step by step,
  - Otherwise, ask to provide more detail, examples, implications, or a clearer breakdown of that answer.

- If the message is just small talk or courtesy (for example: "Thanks", "Thank you, it is working now",
  "Great, that helps"), label it CHITCHAT and do not rewrite.

- If you really cannot tell, label it UNSURE.

Respond as pure JSON:
{{
  "intent": "<one of: FOLLOWUP_ELABORATE | NEW_QUESTION | CHITCHAT | UNSURE>",
  "rewritten_question": "<a clear, explicit question about the last answer, or empty string if not needed>"
}}
""".strip()



FINANCE_KEYWORDS = [
    "budget", "expense", "cost", "financial", "invoice", "payment",
    "revenue", "profit", "loss", "fiscal", "audit",
    "forecast", "projection", "balance sheet", "cash flow",
    "tax", "cashflow", "expenses", "earnings", "cash balance",
    "financial statement", "net income", "operating income",
]

HR_KEYWORDS = [
    "leave", "vacation", "benefits", "payroll", "hiring",
    "onboarding", "offboarding", "performance review", "promotion",
    "disciplinary action", "work from home", "remote work",
    "employee relations", "training", "development", "compensation",
    "overtime", "time off", "sick leave", "maternity leave",
]

TECH_KEYWORDS = [
    "deployment", "server", "database", "api", "bug",
    "feature", "release", "version control", "ci/cd",
    "infrastructure", "scalability", "performance", "latency",
    "uptime", "monitoring", "logging", "cloud", "on-premise",
    "virtualization", "containerization", "microservices",
    "docker", "kubernetes", "load balancing", "networking",
    "ssh", "password", "network", "backup",
]

POLICY_KEYWORDS = [
    "policy", "procedure", "guideline", "compliance",
    "regulation", "standard", "protocol", "rule",
    "governance", "audit", "risk management", "code of conduct",
    "ethics", "confidentiality", "data protection", "security",
]

def _format_history_for_intent(
    history_turns: Optional[List[Tuple[str, str]]]
) -> str:
    if not history_turns:
        return "(no prior conversation)"

    lines: List[str] = []
    for user_msg, assistant_msg in history_turns[-5:]:
        lines.append(f"User: {user_msg}")
        lines.append(f"Assistant: {assistant_msg}")
    return "\n".join(lines)


def infer_intent_and_rewrite(
    user_message: str,
    history_turns: Optional[List[Tuple[str, str]]] = None,
) -> Tuple[str, Optional[str], str]:
    """
    Returns:
      - intent: e.g. "CHITCHAT", "LOOKUP", "NUMERIC_ANALYSIS", "NEW_QUESTION",
                "IMPLICATIONS", "STRATEGY", "FOLLOWUP_ELABORATE", ...
      - rewritten: optional rewritten question (or None)
      - domain: "FINANCE" | "HR" | "TECH" | "POLICY" | "GENERAL"
    """
    text = user_message.lower()

    # 1) Cheap chitchat short-circuit (pure appreciation only)
    if any(x in text for x in [
        "thank you", "thanks", "got it", "great", "good job",
        "well done", "appreciate it",
    ]):
        return "CHITCHAT", None, "GENERAL"

    # 2) Domain guess
    domain = "GENERAL"
    if any(k in text for k in FINANCE_KEYWORDS):
        domain = "FINANCE"
    elif any(k in text for k in HR_KEYWORDS):
        domain = "HR"
    elif any(k in text for k in TECH_KEYWORDS):
        domain = "TECH"
    elif any(k in text for k in POLICY_KEYWORDS):
        domain = "POLICY"

    # 3) Cheap intent guess (rule-based hybrid layer)
    # 3a) Explicit follow-up patterns like "How did you arrive at your answer?"
    if any(x in text for x in [
        "how did you arrive at your answer",
        "how did you arrive at that answer",
        "how did you get this answer",
        "explain how you arrived at your answer",
        "explain how you arrived at that",
        "how did you come up with this answer",
    ]):
        cheap_intent = "FOLLOWUP_ELABORATE"
    elif any(x in text for x in [
        "implication", "implications", "what does this mean",
        "so what", "how does this affect", "what does this imply",
        "for our employee engagement", "for our retention strategy",
    ]):
        cheap_intent = "IMPLICATIONS"
    elif any(x in text for x in [
        "how can we improve", "how can we increase", "suggest ways",
        "what can we do", "which other areas", "what else can we do",
        "how do we increase", "how do we reduce churn",
    ]):
        cheap_intent = "STRATEGY"
    elif any(x in text for x in [
        "sum", "total", "calculate", "projection", "compare",
        "increase", "decrease", "analyze", "average",
        "how much", "what is the amount", "amount of",
    ]):
        cheap_intent = "NUMERIC_ANALYSIS"
    elif any(x in text for x in ["how do i", "steps", "procedure", "process"]):
        cheap_intent = "PROCEDURE"
    elif any(x in text for x in ["list", "what are the", "do we have"]):
        cheap_intent = "LOOKUP"
    else:
        cheap_intent = "GENERAL"

    # 4) History block for LLM helper
    history_block = _format_history_for_intent(history_turns)

    prompt = INTENT_PROMPT_TEMPLATE.format(
        history_block=history_block,
        user_message=user_message,
    )

    messages = [
        {"role": "system", "content": "You are a strict intent classification helper."},
        {"role": "user", "content": prompt},
    ]

    # 5) LLM-based intent + rewrite
    try:
        resp = suggestion_llm_client.invoke(messages)
        raw = getattr(resp, "content", None) or str(resp)
        data = json.loads(raw)

        llm_intent = (data.get("intent") or "UNSURE").strip().upper()
        rewritten = data.get("rewritten_question") or None
    except Exception:
        llm_intent = "UNSURE"
        rewritten = None

    # 6) Sanitize LLM intent
    allowed_intents = {
        "FOLLOWUP_ELABORATE",
        "NEW_QUESTION",
        "CHITCHAT",
        "UNSURE",
    }
    if llm_intent not in allowed_intents:
        llm_intent = "UNSURE"

    # 7) Combine rule-based and LLM intents
    # If the LLM confidently says FOLLOWUP_ELABORATE / NEW_QUESTION / CHITCHAT, trust it.
    if llm_intent in {"FOLLOWUP_ELABORATE", "NEW_QUESTION", "CHITCHAT"}:
        intent = llm_intent
    else:
        # llm_intent == "UNSURE": fall back to cheap_intent
        intent = cheap_intent

    # FOLLOWUP_ELABORATE fallback if no rewrite was produced:
    # We keep FOLLOWUP_ELABORATE if there is history; otherwise, demote to cheap_intent.
    if intent == "FOLLOWUP_ELABORATE" and not rewritten:
        if not history_turns:
            intent = cheap_intent or "GENERAL"

    # CHITCHAT should always be GENERAL
    if intent == "CHITCHAT":
        domain = "GENERAL"

    return intent, rewritten, domain


async def llm_pipeline_stream(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
    top_k: int = 5,
    result_holder: Optional[dict] = None,
    last_doc_id: Optional[str] = None,   # anchor doc for follow-ups
) -> AsyncGenerator[str, None]:
    intent, rewritten, domain = infer_intent_and_rewrite(
        user_message=question,
        history_turns=history,
    )

    # CHITCHAT: short acknowledgement
    if intent == "CHITCHAT":
        msg = "You’re welcome."
        if result_holder is not None:
            result_holder["answer"] = msg
            result_holder["sources"] = []
        yield msg
        return

    effective_question = rewritten or question

    # Optional filter for follow-ups / implications / strategy
    query_filter = None
    if intent in {"FOLLOWUP_ELABORATE", "IMPLICATIONS", "STRATEGY"} and last_doc_id:
        query_filter = {"doc_id": last_doc_id}

    retrieval = await store.query_policies(
        tenant_id=tenant_id,
        collection_name=None,
        query=effective_question,
        top_k=top_k,
        where=query_filter,
    )
    hits = retrieval.get("results", [])

    if not hits:
        msg = (
            "The information I have access to right now is not sufficient to answer this question. "
            "Please consider checking with the appropriate internal team or rephrasing with more detail."
        )
        if result_holder is not None:
            result_holder["answer"] = msg
            result_holder["sources"] = []
        yield msg
        return

    context_chunks: List[str] = []
    sources: List[str] = []

    for hit in hits:
        doc_text = hit["document"]
        meta = hit.get("metadata", {}) or {}
        title = meta.get("title") or meta.get("filename") or "Unknown document"
        section = meta.get("section")

        header_parts = [f"Title: {title}"]
        if section:
            header_parts.append(f"Section: {section}")
        header = " | ".join(header_parts)

        chunk_str = f"{header}\n\n{doc_text}"
        context_chunks.append(chunk_str)
        sources.append(title)

    # Rerank and trim to top 3–5 chunks
    try:
        rerank_messages = build_rerank_messages(effective_question, context_chunks)
        rerank_resp = suggestion_llm_client.invoke(rerank_messages)
        rerank_raw = getattr(rerank_resp, "content", None) or str(rerank_resp)
        indices = json.loads(rerank_raw)
        indices = [i for i in indices if isinstance(i, int) and 0 <= i < len(context_chunks)]
        if indices:
            max_chunks = 5
            indices = indices[:max_chunks]
            context_chunks = [context_chunks[i] for i in indices]
            sources       = [sources[i]       for i in indices]
    except Exception:
        max_chunks = 5
        context_chunks = context_chunks[:max_chunks]
        sources       = sources[:max_chunks]

    unique_sources = sorted(set(sources))

    # Get last answer from history (if any) for follow-ups
    last_answer_text: Optional[str] = None
    if history:
        # history is list of (user, assistant) tuples
        _, last_answer_text = history[-1]

    system_prompt, user_prompt = create_context(
        context_chunks=context_chunks,
        user_question=effective_question,
        intent=intent,
        domain=domain,
        last_answer=last_answer_text,   # NEW: pass summary anchor into prompt builder
    )

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    if history:
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": user_prompt})

    try:
        full_answer_parts: List[str] = []

        async for chunk in llm_client_streaming.astream(messages):
            text = getattr(chunk, "content", None) or ""
            if not text:
                try:
                    text = chunk.generations[0].text  # type: ignore
                except Exception:
                    text = ""
            if text:
                full_answer_parts.append(text)
                yield text

        full_answer = "".join(full_answer_parts)

        # ---- CRITIQUE BLOCK ----
        context_text = "\n\n".join(context_chunks)

        critique_messages = create_critique_prompt(
            user_question=question,
            assistant_answer=full_answer,          # use full_answer here
            context_text=context_text[:2000],
        )

        try:
            critique_resp = suggestion_llm_client.invoke(critique_messages)
            critique = getattr(critique_resp, "content", None) or str(critique_resp)
            critique = critique.strip().upper()
        except Exception:
            critique = "OK"

        if critique == "BAD":
            full_answer = (
                "The previous attempt was not fully consistent with the available documents. "
                "Here is a more precise answer based strictly on the context:\n\n"
                + full_answer
            )
        # ---- END CRITIQUE BLOCK ----

        if result_holder is not None:
            result_holder["answer"] = full_answer
            result_holder["sources"] = unique_sources

    except Exception:
        error_msg = (
            "There was a temporary problem contacting the model, please try again."
        )
        if result_holder is not None:
            result_holder["answer"] = error_msg
            result_holder["sources"] = unique_sources
        yield error_msg
        return



async def llm_pipeline(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    pass
   # no longer in use for now but could still be called some where in the code.