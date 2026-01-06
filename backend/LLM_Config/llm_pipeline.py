from typing import List, Dict, Any, Tuple, Literal, Optional, AsyncGenerator
import json
import textwrap

from LLM_Config.llm_setup import llm_client, suggestion_llm_client, llm_client_streaming, formatter_llm_client
from LLM_Config.system_user_prompt import create_context, create_markdown_context,SYSTEM_PROMPT, create_suggestion_prompt, create_critique_prompt, FORMATTER_SYSTEM_PROMPT
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def build_capabilities_message_from_store(store_summary: dict) -> str:
    collections = store_summary.get("collections", [])
    if not collections:
        return (
            "I can answer questions based on any documents you upload or connect, "
            "including policies, technical documentation, reports, contracts, and more. "
            "Once documents are ingested, you can ask questions directly about their content."
        )

    lines = ["I can help you with questions about documents in this workspace, including:"]
    example_qs: list[str] = []

    for c in collections:
        label = c.get("display_name") or c.get("name")
        topics = c.get("topics") or []
        if topics:
            lines.append(f"- {label} ({', '.join(topics)})")
        else:
            lines.append(f"- {label}")
        if c.get("example_questions"):
            example_qs.extend(c["example_questions"])

    msg = "\n".join(lines)

    if example_qs:
        preview = "\n".join(f'- "{q}"' for q in example_qs[:3])
        msg += "\n\nYou can ask things like:\n" + preview

    return msg


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


IntentType = Literal[
    "FOLLOWUP_ELABORATE",
    "NEW_QUESTION",
    "CHITCHAT",
    "CAPABILITIES",
    "UNSURE",
]


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
  "Great, that helps", "Hello", "Hi", "Good morning", "Good afternoon", "Good evening"),
  label it CHITCHAT and do not rewrite.

- If the user is asking what you can do, what topics you know, or what information you currently have
  (for example: "What information can you help me with now?",
   "What can you do for me?",
   "What topics should I ask you about?",
   "What do you know?"),
  label it CAPABILITIES and do not rewrite.

- If you really cannot tell, label it UNSURE.

Respond as pure JSON:
{{
  "intent": "<one of: FOLLOWUP_ELABORATE | NEW_QUESTION | CHITCHAT | CAPABILITIES | UNSURE>",
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
      - intent: e.g. "CHITCHAT", "CAPABILITIES", "LOOKUP", "NUMERIC_ANALYSIS",
                "NEW_QUESTION", "IMPLICATIONS", "STRATEGY", "FOLLOWUP_ELABORATE", ...
      - rewritten: optional rewritten question (or None)
      - domain: "FINANCE" | "HR" | "TECH" | "POLICY" | "GENERAL"
    """
    text = (user_message or "").lower().strip()

    # 1) Cheap chitchat short-circuit (greetings & pure appreciation)
    if any(x in text for x in [
        "thank you", "thanks", "thx", "got it", "great", "good job",
        "well done", "appreciate it",
        "hello", "hi ", "hi,", "hey", "good morning", "good afternoon", "good evening",
    ]):
        return "CHITCHAT", None, "GENERAL"

    # 2) Cheap CAPABILITIES detection
    if any(x in text for x in [
        "what can you do",
        "what information can you help me with",
        "what information can you currently have",
        "what information do you have",
        "what topics should i ask you",
        "what do you know",
        "what is your knowledge base",
        "what can you assist me with",
        "what information can you provide for me now",
    ]):
        return "CAPABILITIES", None, "GENERAL"

    # 3) Domain guess
    domain = "GENERAL"
    if any(k in text for k in FINANCE_KEYWORDS):
        domain = "FINANCE"
    elif any(k in text for k in HR_KEYWORDS):
        domain = "HR"
    elif any(k in text for k in TECH_KEYWORDS):
        domain = "TECH"
    elif any(k in text for k in POLICY_KEYWORDS):
        domain = "POLICY"

    # 4) Cheap intent guess (rule-based hybrid layer)
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

    # 5) History block for LLM helper
    history_block = _format_history_for_intent(history_turns)

    prompt = INTENT_PROMPT_TEMPLATE.format(
        history_block=history_block,
        user_message=user_message,
    )

    messages = [
        {"role": "system", "content": "You are a strict intent classification helper."},
        {"role": "user", "content": prompt},
    ]

    # 6) LLM-based intent + rewrite (robust JSON parsing)
    llm_intent = "UNSURE"
    rewritten: Optional[str] = None

    try:
        resp = suggestion_llm_client.invoke(messages)
        raw = getattr(resp, "content", None) or str(resp)
        raw = raw.strip()
        logger.info("Intent raw output: $r", raw)

        data = None

        # Fast path: pure JSON
        try:
            data = json.loads(raw)
        except Exception:
            # Try to extract JSON object from within surrounding text
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = raw[start : end + 1]
                try:
                    data = json.loads(candidate)
                except Exception:
                    data = None

        if isinstance(data, dict):
            llm_intent = (data.get("intent") or "UNSURE").strip().upper()
            rewritten_raw = (data.get("rewritten_question") or "").strip()
            rewritten = rewritten_raw or None
        else:
            raise ValueError("Intent classifier did not return a JSON object")

    except Exception as e:
        logger.warning("Intent parsing failed: %r", e)
        llm_intent = "UNSURE"
        rewritten = None

    # 7) Sanitize LLM intent
    allowed_intents = {
        "FOLLOWUP_ELABORATE",
        "NEW_QUESTION",
        "CHITCHAT",
        "CAPABILITIES",
        "UNSURE",
    }
    if llm_intent not in allowed_intents:
        llm_intent = "UNSURE"

    # 8) Combine rule-based and LLM intents
    if llm_intent in {"FOLLOWUP_ELABORATE", "NEW_QUESTION", "CHITCHAT", "CAPABILITIES"}:
        intent = llm_intent
    else:
        intent = cheap_intent

    # FOLLOWUP_ELABORATE fallback if no rewrite was produced
    if intent == "FOLLOWUP_ELABORATE" and not rewritten:
        if not history_turns:
            intent = cheap_intent or "GENERAL"

    # CHITCHAT and CAPABILITIES should always be GENERAL
    if intent in {"CHITCHAT", "CAPABILITIES"}:
        domain = "GENERAL"

    return intent, rewritten, domain


def create_formatter_prompt(raw_answer: str) -> List[Dict[str, str]]:
    """
    Wraps the raw LLM answer with the formatter system prompt
    to produce a clean, human-readable Markdown output.
    """
    return [
        {
            "role": "system",
            "content": FORMATTER_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": raw_answer
        }
    ]

async def llm_pipeline_stream_bk(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
    top_k: int = 5,
    result_holder: Optional[dict] = None,
    last_doc_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    intent, rewritten, domain = infer_intent_and_rewrite(
        user_message=question,
        history_turns=history,
    )

    text_lower = (question or "").lower()

    # 1) CHITCHAT
    if intent == "CHITCHAT":
        if any(p in text_lower for p in ["thank you", "thanks", "thx", "appreciate it"]):
            msg = "You’re welcome. If you have more questions, feel free to ask."
        elif any(p in text_lower for p in ["hello", "hi ", "hi,", "hey", "good morning", "good afternoon", "good evening"]):
            msg = (
                "Hello! I can help you with questions about the documents and data in this workspace. "
                "What would you like to explore?"
            )
        else:
            msg = (
                "I’m here to help with your questions about the documents and information in this workspace. "
                "What would you like to know?"
            )

        if result_holder is not None:
            result_holder["answer"] = msg
            result_holder["sources"] = []
        yield msg
        return

    # 2) CAPABILITIES – dynamic from store
    if intent == "CAPABILITIES":
        summary = await store.summarize_capabilities(tenant_id)
        msg = build_capabilities_message_from_store(summary)

        if result_holder is not None:
            result_holder["answer"] = msg
            result_holder["sources"] = []
        yield msg
        return

    # 3) Normal RAG path
    effective_question = rewritten or question

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

    # 4) No hits: intent-aware fallback
    if not hits:
        if intent == "NEW_QUESTION":
            msg = (
                "I could not find relevant information in the current knowledge base for this question. "
                "I'm best at questions about the documents and data that have been ingested here. "
                "Could you rephrase or specify the document, topic, or area you’re interested in?"
            )
        else:
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

    # Rerank
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
            sources = [sources[i] for i in indices]
    except Exception:
        max_chunks = 5
        context_chunks = context_chunks[:max_chunks]
        sources = sources[:max_chunks]

    unique_sources = sorted(set(sources))

    last_answer_text: Optional[str] = None
    if history:
        _, last_answer_text = history[-1]

    system_prompt, user_prompt = create_context(
        context_chunks=context_chunks,
        user_question=effective_question,
        intent=intent,
        domain=domain,
        last_answer=last_answer_text,
    )

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    if history:
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": user_prompt})

    try:
        # =========================
        # PASS 1: STREAMED ANSWER
        # =========================
        full_answer_parts: List[str] = []

        async for chunk in llm_client_streaming.astream(messages):
            text = getattr(chunk, "content", "") or ""
            if not text:
                try:
                    text = chunk.generations[0].text  # type: ignore[attr-defined]
                except Exception:
                    text = ""
            if text:
                full_answer_parts.append(text)
                # stream raw tokens to user
                yield text

        # Combine streamed chunks
        raw_answer = "".join(full_answer_parts).strip()

        # =========================
        # PASS 2: CRITIQUE
        # =========================
        context_text = "\n\n".join(context_chunks)
        critique_messages = create_critique_prompt(
            user_question=question,
            assistant_answer=raw_answer,
            context_text=context_text[:2000],
        )

        try:
            critique_resp = suggestion_llm_client.invoke(critique_messages)
            critique = (getattr(critique_resp, "content", "") or "").strip().upper()
        except Exception:
            critique = "OK"

        if critique == "BAD":
            raw_answer = (
                "⚠️ **Warning:** The previous attempt may not be fully consistent with the available documents. "
                "Here is a corrected response strictly based on the context:\n\n"
                + raw_answer
            )


        # 2. Build formatter messages
        formatter_messages = create_formatter_prompt(raw_answer)

        try:
            formatted_resp = formatter_llm_client.invoke(formatter_messages)
            formatted_answer = getattr(formatted_resp, "content", raw_answer)
        except Exception:
            formatted_answer = raw_answer  # fallback to unformatted

        yield "\n\n---\n\n"
        yield formatted_answer
        # =========================
        # STORE FINAL ANSWER ONLY
        # =========================
        if result_holder is not None:
            result_holder["answer"] = formatted_answer
            result_holder["sources"] = unique_sources


    except Exception as e:
        error_msg = f"There was a temporary problem generating the answer: {str(e)}"
        if result_holder is not None:
            result_holder["answer"] = error_msg
            result_holder["sources"] = unique_sources
        yield error_msg
        return

async def llm_pipeline_stream(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
    top_k: int = 5,
    last_doc_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    # 1) Determine intent and domain
    intent, rewritten, domain = infer_intent_and_rewrite(question, history)
    effective_question = rewritten or question

    # 2) Retrieve relevant context chunks
    query_filter = {"doc_id": last_doc_id} if intent in {"FOLLOWUP_ELABORATE", "IMPLICATIONS", "STRATEGY"} and last_doc_id else None
    retrieval = await store.query_policies(
        tenant_id=tenant_id,
        collection_name=None,
        query=effective_question,
        top_k=top_k,
        where=query_filter,
    )
    hits = retrieval.get("results", [])

    context_chunks = []
    for hit in hits:
        doc_text = hit.get("document", "")
        meta = hit.get("metadata", {})
        title = meta.get("title") or meta.get("filename") or "Unknown document"
        section = meta.get("section")
        header = f"**{title}**"
        if section:
            header += f" | Section: {section}"
        context_chunks.append(f"{header}\n{doc_text}")

    # 3) Include last answer if follow-up
    last_answer_text = history[-1][1] if history else None

    # 4) Build full prompt
    user_prompt = create_markdown_context(
        context_chunks=context_chunks,
        user_question=effective_question,
        intent=intent,
        domain=domain,
        last_answer=last_answer_text
    )

    # 5) LLM streaming
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
    async for chunk in llm_client_streaming.astream(messages):
        text = getattr(chunk, "content", "") or ""
        if not text:
            try:
                text = chunk.generations[0].text  # fallback
            except Exception:
                text = ""
        if text:
            yield text


async def llm_pipeline(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    pass
   # no longer in use for now but could still be called some where in the code.