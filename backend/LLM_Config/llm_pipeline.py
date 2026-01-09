from typing import List, Dict, Any, Tuple, Literal, Optional, AsyncGenerator
import json
import textwrap
import logging
import re

from LLM_Config.llm_setup import (
    llm_client,
    suggestion_llm_client,
    llm_client_main,
    formatter_llm_streaming,
)
from LLM_Config.system_user_prompt import (
    create_context,
    create_critique_prompt,
    FORMATTER_SYSTEM_PROMPT,
    INTENT_PROMPT_TEMPLATE,
)
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def build_capabilities_message_from_store(store_summary: dict) -> str:
    collections = store_summary.get("collections", [])
    if not collections:
        return (
            "I can answer questions based on any documents you upload or connect, "
            "including policies, technical documentation, reports, contracts, and more. "
            "Once documents are ingested, you can ask questions directly about their content."
        )

    lines = [
        "I can help you with questions about documents in this workspace, including:"
    ]
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


YEAR_REGEX = re.compile(r"\b(20[0-4][0-9])\b")  # 2000–2049


def extract_year_filter(user_message: str, domain: str) -> Optional[dict]:
    """
    Extract a simple year metadata filter for finance questions.

    Expects your Chroma metadata to have something like: {"year": "2025"}
    for each row/chunk built from the Date column.
    """
    if domain != "FINANCE":
        return None

    text = (user_message or "").lower()
    match = YEAR_REGEX.search(text)
    if not match:
        return None

    year = match.group(1)
    return {"year": year}


def is_year_level_question(question: str) -> bool:
    """
    Heuristic: user is asking about a whole year or long range.
    """
    q = (question or "").lower()
    if YEAR_REGEX.search(q) and any(
        kw in q
        for kw in [
            "whole year",
            "year ",
            "for the year",
            "jan to dec",
            "january to december",
            "entire year",
            "full year",
        ]
    ):
        return True
    return False


def build_rerank_messages(question: str, snippets: list[str]) -> list[dict]:
    numbered = "\n\n".join(
        [
            f"[{i}] {textwrap.shorten(s, width=800, placeholder='...')}"
            for i, s in enumerate(snippets)
        ]
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

# --- typing ---
IntentType = Literal[
    "FOLLOWUP_ELABORATE",
    "NEW_QUESTION",
    "CHITCHAT",
    "CAPABILITIES",
    "UNSURE",
    "EXPORT_TABLE",
    "ANALYSIS",
    # rule-based extras (still typed if you like)
    "IMPLICATIONS",
    "STRATEGY",
    "NUMERIC_ANALYSIS",
    "PROCEDURE",
    "LOOKUP",
    "GENERAL",
]





FINANCE_KEYWORDS = [
    "budget",
    "expense",
    "cost",
    "financial",
    "invoice",
    "payment",
    "revenue",
    "profit",
    "loss",
    "fiscal",
    "audit",
    "forecast",
    "projection",
    "balance sheet",
    "cash flow",
    "tax",
    "cashflow",
    "expenses",
    "earnings",
    "cash balance",
    "financial statement",
    "net income",
    "operating income",
]

HR_KEYWORDS = [
    "leave",
    "vacation",
    "benefits",
    "payroll",
    "hiring",
    "onboarding",
    "offboarding",
    "performance review",
    "promotion",
    "disciplinary action",
    "work from home",
    "remote work",
    "employee relations",
    "training",
    "development",
    "compensation",
    "overtime",
    "time off",
    "sick leave",
    "maternity leave",
]

TECH_KEYWORDS = [
    "deployment",
    "server",
    "database",
    "api",
    "bug",
    "feature",
    "release",
    "version control",
    "ci/cd",
    "infrastructure",
    "scalability",
    "performance",
    "latency",
    "uptime",
    "monitoring",
    "logging",
    "cloud",
    "on-premise",
    "virtualization",
    "containerization",
    "microservices",
    "docker",
    "kubernetes",
    "load balancing",
    "networking",
    "ssh",
    "password",
    "network",
    "backup",
]

POLICY_KEYWORDS = [
    "policy",
    "procedure",
    "guideline",
    "compliance",
    "regulation",
    "standard",
    "protocol",
    "rule",
    "governance",
    "audit",
    "risk management",
    "code of conduct",
    "ethics",
    "confidentiality",
    "data protection",
    "security",
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
      - intent: one of "CHITCHAT", "CAPABILITIES", "FOLLOWUP_ELABORATE", "NEW_QUESTION", "UNSURE" or a rule-based type
      - rewritten: optional rewritten question (or None)
      - domain: "FINANCE" | "HR" | "TECH" | "POLICY" | "GENERAL"
    """
    text = (user_message or "").lower().strip()

    # 1) Cheap chitchat short-circuit (greetings & pure appreciation)
    if any(
        x in text
        for x in [
            "thank you",
            "thanks",
            "thx",
            "got it",
            "great",
            "good job",
            "well done",
            "appreciate it",
            "hello",
            "hi ",
            "hi,",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        ]
    ):
        return "CHITCHAT", None, "GENERAL"

    # 2) Cheap CAPABILITIES detection
    if any(
        x in text
        for x in [
            "what can you do",
            "what information can you help me with",
            "what information can you currently have",
            "what information do you have",
            "what topics should i ask you",
            "what do you know",
            "what is your knowledge base",
            "what can you assist me with",
            "what information can you provide for me now",
        ]
    ):
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
    if any(
        x in text
        for x in [
            "how did you arrive at your answer",
            "how did you arrive at that answer",
            "how did you get this answer",
            "explain how you arrived at your answer",
            "explain how you arrived at that",
            "how did you come up with this answer",
        ]
    ):
        cheap_intent = "FOLLOWUP_ELABORATE"
    elif any(
        x in text
        for x in [
            "implication",
            "implications",
            "what does this mean",
            "so what",
            "how does this affect",
            "what does this imply",
        ]
    ):
        cheap_intent = "IMPLICATIONS"
    elif any(
        x in text
        for x in [
            "how can we improve",
            "how can we increase",
            "suggest ways",
            "what can we do",
            "which other areas",
            "what else can we do",
            "how do we increase",
            "how do we reduce",
        ]
    ):
        cheap_intent = "STRATEGY"
    elif any(
        x in text
        for x in [
            "sum",
            "total",
            "calculate",
            "projection",
            "compare",
            "increase",
            "decrease",
            "analyze",
            "average",
            "how much",
            "what is the amount",
            "amount of",
        ]
    ):
        cheap_intent = "NUMERIC_ANALYSIS"
    elif any(x in text for x in ["how do i", "steps", "procedure", "process"]):
        cheap_intent = "PROCEDURE"
    elif any(x in text for x in ["list", "what are the", "do we have"]):
        cheap_intent = "LOOKUP"
        
    elif any(
        x in text
        for x in ["export as table", "as a table", "table of", "csv", "spreadsheet"]
    ):
        cheap_intent = "EXPORT_TABLE"
    elif any(
        x in text
        for x in ["analyze this", "detailed analysis", "deep analysis", "root cause"]
    ):
        cheap_intent = "ANALYSIS"    
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
        logger.info(f"Intent raw output: {raw}")

        data = None

        try:
            data = json.loads(raw)
        except Exception:
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

            # Only accept rewrites that look like real questions or instructions,
            # not critiques of the assistant.
            if rewritten_raw:
                lowered = rewritten_raw.lower()
                if lowered.startswith(("why was your answer", "your previous answer", "the assistant")):
                    # Discard critique-style rewrites
                    rewritten = None
                else:
                    rewritten = rewritten_raw
            else:
                rewritten = None
        else:
            raise ValueError("Intent classifier did not return a JSON object")


    except Exception as e:
        logger.warning(f"Intent parsing failed: {e}")
        llm_intent = "UNSURE"
        rewritten = None

    allowed_intents = {
        "FOLLOWUP_ELABORATE",
        "NEW_QUESTION",
        "CHITCHAT",
        "CAPABILITIES",
        "UNSURE",
        "EXPORT_TABLE",  
        "ANALYSIS",  
    }
    
    if llm_intent not in allowed_intents:
        llm_intent = "UNSURE"

    if llm_intent in {"FOLLOWUP_ELABORATE", "NEW_QUESTION", "CHITCHAT", "CAPABILITIES"}:
        intent = llm_intent
    else:
        intent = cheap_intent

    if intent == "FOLLOWUP_ELABORATE" and not rewritten:
        if not history_turns:
            intent = cheap_intent or "GENERAL"

    if intent in {"CHITCHAT", "CAPABILITIES"}:
        domain = "GENERAL"

    return intent, rewritten, domain


def create_formatter_prompt(raw_answer: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": FORMATTER_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": raw_answer,
        },
    ]


def normalize_query(q: str) -> str:
    q = (q or "").strip()
    lower = q.lower()
    prefixes = [
        "can you please",
        "could you please",
        "please",
        "i was wondering",
        "i would like to know",
    ]
    for p in prefixes:
        if lower.startswith(p):
            q = q[len(p) :].lstrip(" ,.")
            break
    return q


def build_retrieval_query(
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
) -> str:
    q = normalize_query(question)
    if not history:
        return q

    # Take last assistant answer for topic hint
    last_user, last_assistant = history[-1]
    hint = (last_assistant or "")[:300].strip()
    if not hint:
        return q

    return (
        "Follow-up based on the previous answer:\n"
        f"{hint}\n\n"
        "New question:\n"
        f"{q}"
    )


def create_refinement_prompt(
    user_question: str,
    assistant_answer: str,
    context_text: str,
) -> list[dict]:
    user_content = f"""
    User question:
    {user_question}

    Document context (truncated if long):
    {context_text}

    Previous assistant answer (judged problematic):
    {assistant_answer}

    Task:
    Rewrite the answer so that:
    - Every factual and numeric statement is directly supported by the context.
    - You clearly indicate when data is missing or not visible instead of inventing it.
    - You directly answer the user's question as far as the context allows.

    Return only the improved answer, with no explanation of your changes.
    """.strip()

    return [
        {
            "role": "system",
            "content": (
                "You are a careful assistant that fixes and improves previous answers "
                "based only on the given context."
            ),
        },
        {"role": "user", "content": user_content},
    ]


async def llm_pipeline_stream(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
    top_k: int = 100,
    result_holder: Optional[dict] = None,
    last_doc_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    intent, rewritten, domain = infer_intent_and_rewrite(
        user_message=question,
        history_turns=history,
    )

    text_lower = (question or "").lower()

    def _store(answer: str, sources: list[str]) -> None:
        if result_holder is not None:
            result_holder["answer"] = answer
            result_holder["sources"] = sources

    # 1) CHITCHAT
    if intent == "CHITCHAT":
        if any(
            p in text_lower
            for p in ["thank you", "thanks", "thx", "appreciate it"]
        ):
            msg = "You’re welcome. If you have more questions, feel free to ask."
        elif any(
            p in text_lower
            for p in ["hello", "hi ", "hi,", "hey", "good morning", "good afternoon", "good evening"]
        ):
            msg = (
                "Hello! I can help you with questions about the documents and data in this workspace. "
                "What would you like to explore?"
            )
        else:
            msg = (
                "I’m here to help with your questions about the documents and information in this workspace. "
                "What would you like to know?"
            )

        _store(msg, [])
        yield msg
        return

    # 2) CAPABILITIES
    if intent == "CAPABILITIES":
        summary = await store.summarize_capabilities(tenant_id)
        msg = build_capabilities_message_from_store(summary)
        _store(msg, [])
        yield msg
        return

    # 3) RETRIEVAL
    raw_question = rewritten or question
    # NEW: strip export phrasing for retrieval
    if intent == "EXPORT_TABLE":
        retrieval_question = normalize_query(
            raw_question
                .replace("export", "")
                .replace("as a table", "")
                .replace("as table", "")
                .replace("table", "")
                .replace("downloadable", "")
                .strip()
        )
    else:
        retrieval_question = raw_question
        
    effective_question = build_retrieval_query(retrieval_question, history)

    query_filter: Optional[dict] = None
    if intent in {"FOLLOWUP_ELABORATE", "IMPLICATIONS", "STRATEGY"} and last_doc_id:
        query_filter = {"doc_id": last_doc_id}
        
    # year-aware filter for finance questions
    year_filter = extract_year_filter(question, domain)
    if year_filter and intent not in {"EXPORT_TABLE"}:
        query_filter = year_filter
        
    # 3b) Dynamic top_k for year/numeric finance queries
    year_level = is_year_level_question(question)
    is_numeric_finance = (domain == "FINANCE") and (
        intent in {"NUMERIC_ANALYSIS", "LOOKUP", "EXPORT_TABLE"}
    )
    if year_level or is_numeric_finance:
        effective_top_k = max(top_k, 200)
    else:
        effective_top_k = top_k
                    

    retrieval = await store.query_policies(
        tenant_id=tenant_id,
        collection_name=None,
        query=effective_question,
        top_k=effective_top_k,
        where=query_filter,
    )
    hits = retrieval.get("results", [])
    
    if not hits and year_filter is not None:
        # fallback: try again without year filter
        retrieval = await store.query_policies(
        tenant_id=tenant_id,
        collection_name=None,
        query=effective_question,
        top_k=effective_top_k,
        where=None,
    )
    hits = retrieval.get("results", [])

    logger.debug(
        {
            "event": "retrieval_result",
            "tenant_id": tenant_id,
            "question": effective_question,
            "intent": intent,
            "domain": domain,
            "num_hits": len(hits),
            "sample_hits": [
                {
                    "metadata": h.get("metadata", {}),
                    "preview": (h.get("document") or "")[:200],
                }
                for h in hits[:3]
            ],
        }
    )

    if not hits:
        if intent == "NEW_QUESTION":
            msg = (
                "I could not find relevant information in the current knowledge base for this question. "
                "I am best at questions about the documents and data that have been ingested here. "
                "Could you rephrase or specify the document, topic, or area you’re interested in?"
            )
            
        elif intent == "EXPORT_TABLE":
            msg = (
                "I could not find any visible data rows to export as a table for this question. "
                "This may mean that data for the requested year or period is not present in the current workspace."
            )
        else:
            msg = (
                "The information visible in the current context is not sufficient to answer this question. "
                "You may want to rephrase with more detail or specify a particular document or topic."
            )

        _store(msg, [])
        yield msg
        return

    # 4) BUILD CONTEXT (no titles injected into content)
    context_chunks: list[str] = []
    sources: list[str] = []

    for hit in hits:
        doc_text = (hit.get("document") or "").strip()
        meta = hit.get("metadata", {}) or {}
        title = meta.get("display_name") or meta.get("title") or meta.get("filename") or "Unknown document"
        context_chunks.append(doc_text)
        sources.append(title)

    # 5) RERANK (best-effort, robust)
    try:
        rerank_messages = build_rerank_messages(effective_question, context_chunks)
        rerank_resp = suggestion_llm_client.invoke(rerank_messages)
        raw = getattr(rerank_resp, "content", "") or "[]"
        raw = raw.strip()
        try:
            indices = json.loads(raw)
        except Exception:
            start = raw.find("[")
            end = raw.rfind("]")
            if start != -1 and end != -1 and end > start:
                indices = json.loads(raw[start : end + 1])
            else:
                raise 
            
        if not isinstance(indices, list):
            raise ValueError
        indices = [
            i for i in indices if isinstance(i, int) and 0 <= i < len(context_chunks)
        ]
    except Exception as e:
        logger.warning(f"Rerank failed, falling back to original order: {e}")
        indices = list(range(len(context_chunks)))

    # 5b) Allow more chunk for year-level finance
    if year_level and domain == "FINANCE":
        max_chunks = 10
    elif intent == "EXPORT_TABLE":
        max_chunks = 10    
    else:
        max_chunks = 5
        
    if indices:
        indices = indices[:max_chunks]
        context_chunks = [context_chunks[i] for i in indices]
        sources = [sources[i] for i in indices]
    else:
        context_chunks = context_chunks[:max_chunks]
        sources = sources[:max_chunks]

    unique_sources = sorted(set(sources))

    # 6) PROMPT BUILDING
    last_answer_text = history[-1][1] if history else None

    system_prompt, user_prompt = create_context(
        context_chunks=context_chunks,
        user_question=raw_question,
        intent=intent,
        domain=domain,
        last_answer=last_answer_text,
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    if history:
        for u, a in history[-2:]:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})

    messages.append({"role": "user", "content": user_prompt})

    try:
         # 7) GENERATE (non-streaming main model)
        resp = llm_client_main.invoke(messages)
        raw_answer = (getattr(resp, "content", "") or "").strip()
        logger.info(f"RAW_ANSWER:\n {raw_answer}")

        # 8) CRITIQUE AS CORRECTOR, NOT JUST LABEL
        critique_messages = create_critique_prompt(
            user_question=question,
            assistant_answer=raw_answer,
            context_text="\n\n".join(context_chunks)[:10000],
        )
        critique_resp = suggestion_llm_client.invoke(critique_messages)
        critique = (getattr(critique_resp, "content", "") or "").strip().upper()
        
        if critique == "BAD":
            # One refinement pass
            refinement_messages = create_refinement_prompt(
                user_question=question,
                assistant_answer=raw_answer,
                context_text="\n\n".join(context_chunks)[:10000],
            )
            refine_resp = llm_client.invoke(refinement_messages)
            refined = (getattr(refine_resp, "content", "") or "").strip()

            # Use refined answer if non-empty, otherwise fall back to original
            if refined:
                raw_answer = refined

        # 9) FORMAT AND STREAM
        try:
            formatter_messages = create_formatter_prompt(raw_answer)
            formatted_parts: list[str] = []

            async for chunk in formatter_llm_streaming.astream(formatter_messages):
                text = getattr(chunk, "content", "") or ""
                if not text:
                    try:
                        text = chunk.generations[0].text or ""
                    except Exception:
                        text = ""
                if text:
                    formatted_parts.append(text)
                    # stream formatted Markdown to the client
                    yield text

            formatted_answer = "".join(formatted_parts)
            logger.info(f"FORMATTED_ANSWER:\n {formatted_answer}")

        except Exception as e:
            logger.warning(f"Formatter failed, returning raw answer: {e}")
            formatted_answer = raw_answer
            # fallback: send full raw answer once
            yield formatted_answer

        _store(formatted_answer, unique_sources)


    except Exception as e:
        error_msg = f"There was a temporary problem generating the answer: {str(e)}"
        _store(error_msg, unique_sources)
        yield error_msg

