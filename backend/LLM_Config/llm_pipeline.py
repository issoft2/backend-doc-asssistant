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

FINANCE_KEYWORDS = [ 
                    "budget", "expense", "cost", "financial", "invoice", "payment",
                    "revenue", "profit", "loss", "fiscal", "audit"
                    "forecast", "projection", "balance sheet", "cash flow", 
                    "tax", "cashflow", "expenses", "earnings", "cash balance",
                    "financial statement", "net income", "operating income"
                    ]

HR_KEYWORDS = [
                    "leave", "vacation", "benefits", "payroll", "hiring",
                    "onboarding", "offboarding", "performance review", "promotion",
                    "disciplinary action", "work from home", "remote work",
                    "employee relations", "training", "development", "compensation",
                    "overtime", "time off", "sick leave", "maternity leave"
        ]

TECH_KEYWORDS = [
                    "deployment", "server", "database", "API",  "bug",
                    "feature", "release", "version control", "CI/CD",
                    "infrastructure", "scalability", "performance", "latency",
                    "uptime", "monitoring", "logging", "cloud", "on-premise",
                    "virtualization", "containerization", "microservices",
                    "docker", "kubernetes", "load balancing", "networking",
                    "ssh", "password", "network", "database", "backup",
        ]

POLICY_KEYWORDS = [
                    "policy", "procedure", "guideline", "compliance",
                    "regulation", "standard", "protocol", "rule",
                    "governance", "audit", "risk management", "code of conduct",
                    "ethics", "confidentiality", "data protection", "security",
        ]


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
    history_turns: Optional[List[Tuple[str, str]]] = None,
) -> Tuple[str, Optional[str], str]:
    """
    Returns:
      - intent: e.g. "CHITCHAT", "LOOKUP", "NUMERIC_ANALYSIS", "NEW_QUESTION", ...
      - rewritten: optional rewritten question (or None)
      - domain: "FINANCE" | "HR" | "TECH" | "POLICY" | "GENERAL"
    """
    text = user_message.lower()

    # ---- 1) Very simple chitchat detection (short-circuit) ----
    if any(x in text for x in [
        "thank you", "thanks", "got it", "great", "good job",
        "well done", "appreciate it", "hello", "hi"
    ]):
        return "CHITCHAT", None, "GENERAL"

    # ---- 2) Infer domain by keyword buckets (first match wins; tune order) ----
    domain = "GENERAL"
    if any(k in text for k in FINANCE_KEYWORDS):
        domain = "FINANCE"
    elif any(k in text for k in HR_KEYWORDS):
        domain = "HR"
    elif any(k in text for k in TECH_KEYWORDS):
        domain = "TECH"
    elif any(k in text for k in POLICY_KEYWORDS):
        domain = "POLICY"

    # ---- 3) Cheap local intent guess (numeric / procedure / lookup / general) ----
    cheap_intent: str
    if any(x in text for x in [
        "sum", "total", "calculate", "projection", "compare",
        "increase", "decrease", "analyze", "average",
        "how much", "what is the amount", "amount of"
    ]):
        cheap_intent = "NUMERIC_ANALYSIS"
    elif any(x in text for x in ["how do i", "steps", "procedure", "process"]):
        cheap_intent = "PROCEDURE"
    elif any(x in text for x in ["list", "what are the", "which", "do we have"]):
        cheap_intent = "LOOKUP"
    else:
        cheap_intent = "GENERAL"

    # ---- 4) Prepare history block for the LLM-based intent helper ----
    history_block = ""
    if history_turns:
        # last N turns already selected by caller; just stringify compactly
        lines = []
        for u, a in history_turns:
            lines.append(f"USER: {u}")
            lines.append(f"ASSISTANT: {a}")
        history_block = "\n".join(lines)

    prompt = INTENT_PROMPT_TEMPLATE.format(
        history_block=history_block,
        user_message=user_message,
    )

    messages = [
        {"role": "system", "content": "You are a strict intent classification helper."},
        {"role": "user", "content": prompt},
    ]

    # ---- 5) Call small LLM for fine-grained intent + rewrite (best-effort) ----
    try:
        resp = suggestion_llm_client.invoke(messages)
        raw = getattr(resp, "content", None) or str(resp)
        data = json.loads(raw)

        llm_intent = data.get("intent", "UNSURE")
        rewritten = data.get("rewritten_question") or None
    except Exception:
        llm_intent = "UNSURE"
        rewritten = None

    # ---- 6) Sanitize LLM intent label; fall back to cheap intent when needed ----
    allowed_intents = {
        "FOLLOWUP_ELABORATE",
        "NEW_QUESTION",
        "CHITCHAT",
        "UNSURE",
    }

    if llm_intent not in allowed_intents:
        llm_intent = "UNSURE"

    # Map UNSURE → cheap_intent; keep NEW_QUESTION/FOLLOWUP_ELABORATE/CHITCHAT as-is
    if llm_intent == "UNSURE":
        intent = cheap_intent
    else:
        intent = llm_intent

    # If LLM says CHITCHAT, domain is effectively GENERAL
    if intent == "CHITCHAT":
        domain = "GENERAL"

    return intent, rewritten, domain


async def llm_pipeline(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,  # [(user, assistant), ...]
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    End-to-end RAG pipeline:
      - Infer intent (and optionally domain) and rewrite vague follow-ups.
      - Retrieve relevant chunks from Chroma for a given tenant.
      - Build system + user prompts with context (+ optional history).
      - Call main LLM for answer.
      - Call small LLM for follow-up suggestions (best-effort).
      - Return answer, follow_up, and sources.
    """

    # 1) Infer intent on the raw user message
    # Extend this to optionally return a coarse domain label as well.
    # Example return: intent="NUMERIC_ANALYSIS", domain="FINANCE", rewritten="..."
    intent, rewritten, domain = infer_intent_and_rewrite(
        user_message=question,
        history_turns=history,
    )

    # 2) Handle pure chitchat cheaply (no vector search)
    if intent == "CHITCHAT":
        return {
            "answer": (
                "Hello! I’m your Organization Knowledge Assistant. "
                "You can ask me questions about your organization’s policies, procedures, guidelines, "
                "financial information, contracts, projects, or other internal information, "
                "and I’ll answer based on the information I currently have access to."
            ),
            "follow_up": [],
            "sources": [],
        }

    # 3) Decide the effective question used for retrieval + prompting
    effective_question = rewritten if rewritten else question

    # 4) RETRIEVE (make this the main place you later add domain-aware logic)
    # You can extend query_policies to accept domain/doc_type hints if needed.
    retrieval = await store.query_policies(
        tenant_id=tenant_id,
        collection_name=None,
        query=effective_question,
        top_k=top_k,
        # Optional future extension: doc_type/domain hint
        # domain=domain,
        # intent=intent,
    )
    hits = retrieval.get("results", [])

    # 4b) If nothing comes back at all, fail gracefully but generically
    if not hits:
        return {
            "answer": (
                "The available documents do not contain enough information to answer this question "
                "based on the data I currently have."
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
        # Keep doc_id only in metadata; do not encourage the model to repeat it
        doc_id = meta.get("doc_id")

        header_parts = [f"Title: {title}"]
        if section:
            header_parts.append(f"Section: {section}")
        # NOTE: intentionally NOT including Doc ID in the visible header string,
        # to avoid leaking internal identifiers into the model's text context.

        header = " | ".join(header_parts)
        chunk_str = f"{header}\n\n{doc_text}"
        context_chunks.append(chunk_str)

        sources.append(title)

    unique_sources = sorted(set(sources))

    # 6) Build system + user prompt from context + effective question
    # Make sure your create_context uses the refined, generic SYSTEM_PROMPT
    # and contains the numeric/financial + follow-up rules we discussed.
    system_prompt, user_prompt = create_context(
        context_chunks=context_chunks,
        user_question=effective_question,
        intent=intent,
        domain=domain,
    )

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
