"""

"""


from typing import List, Dict, Any, Tuple, Literal, Optional, AsyncGenerator
import json
import textwrap
import logging
import re

from LLM_Config.llm_setup import call_llm, stream_llm
from LLM_Config.system_user_prompt import (
    create_context,
    FORMATTER_SYSTEM_PROMPT,
    RERANK_SYSTEM_PROMPT,
    create_chart_spec_prompt,
)
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- typing ---
IntentType = Literal[
    "FOLLOWUP_ELABORATE",
    "NEW_QUESTION",
    "CHITCHAT",
    "CAPABILITIES",
    "UNSURE",
    "EXPORT_TABLE",
    "ANALYSIS",
    "IMPLICATIONS",
    "STRATEGY",
    "NUMERIC_ANALYSIS",
    "PROCEDURE",
    "LOOKUP",
    "GENERAL",
    "CHART",
]

YEAR_REGEX = re.compile(r"\b(20[0-4][0-9])\b")  # 2000–2049

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

# ---------- helpers ----------

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


def extract_year_filter(user_message: str, domain: str) -> Optional[dict]:
    if domain != "FINANCE":
        return None
    text = (user_message or "").lower()
    match = YEAR_REGEX.search(text)
    if not match:
        return None
    year = match.group(1)
    return {"year": year}


def is_year_level_question(question: str) -> bool:
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
            q = q[len(p):].lstrip(" ,.")
            break
    return q


def build_retrieval_query(
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
) -> str:
    q = normalize_query(question)
    if not history:
        return q

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


def parse_raw_chart(raw: str, logger: logging.Logger) -> Any:
    try:
        return json.loads(raw)
    except Exception as e:
        logger.warning("CHART_DEBUG JSON parse failed: %s", e)
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start: end + 1]
            try:
                return json.loads(candidate)
            except Exception as e2:
                logger.warning("CHART_DEBUG salvage parse failed: %s", e2)
        return None


def infer_intent_rule_based(user_message: str) -> Tuple[IntentType, str, bool]:
    """
    Pure rule-based intent + domain + chart_only, no LLM call.
    Call 1 (main answer) can still *use* this intent (e.g., CHANGE style, mention charts),
    and can also *re-interpret/override* it in-text if needed.
    """
    text = (user_message or "").lower().strip()

    chart_only = any(
        p in text
        for p in [
            "charts only",
            "chart only",
            "only charts",
            "just the chart",
            "just charts",
            "no explanation",
            "no text",
            "skip the explanation",
        ]
    )

    # 1) CHITCHAT
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
        return "CHITCHAT", "GENERAL", chart_only

    # 2) CAPABILITIES
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
        return "CAPABILITIES", "GENERAL", chart_only

    # 3) Domain guess
    domain: str = "GENERAL"
    if any(k in text for k in FINANCE_KEYWORDS):
        domain = "FINANCE"
    elif any(k in text for k in HR_KEYWORDS):
        domain = "HR"
    elif any(k in text for k in TECH_KEYWORDS):
        domain = "TECH"
    elif any(k in text for k in POLICY_KEYWORDS):
        domain = "POLICY"

    # 4) Intent guess
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
        intent: IntentType = "FOLLOWUP_ELABORATE"
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
        intent = "IMPLICATIONS"
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
        intent = "STRATEGY"
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
        intent = "NUMERIC_ANALYSIS"
    elif any(x in text for x in ["how do i", "steps", "procedure", "process"]):
        intent = "PROCEDURE"
    elif any(x in text for x in ["list", "what are the", "do we have"]):
        intent = "LOOKUP"
    elif any(
        x in text
        for x in ["export as table", "as a table", "table of", "csv", "spreadsheet"]
    ):
        intent = "EXPORT_TABLE"
    elif any(
        x in text
        for x in ["analyze this", "detailed analysis", "deep analysis", "root cause"]
    ):
        intent = "ANALYSIS"
    elif any(
        x in text
        for x in ["chart", "graph", "plot", "visualize", "line chart", "bar chart"]
    ):
        intent = "CHART"
    else:
        intent = "NEW_QUESTION"

    return intent, domain, chart_only


# ---------- main pipeline ----------

async def llm_pipeline_stream(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    question: str,
    history: Optional[List[Tuple[str, str]]] = None,
    top_k: int = 10,
    result_holder: Optional[dict] = None,
    last_doc_id: Optional[str] = None,
    collection_names: Optional[List[str]] = None,
) -> AsyncGenerator[str, None]:
    # Intent & domain are rule-based (no LLM call)
    intent, domain, chart_only = infer_intent_rule_based(question)

    text_lower = (question or "").lower()
    unique_sources: list[str] = []

    def _store(answer: str, sources: list[str]) -> None:
        if result_holder is not None:
            result_holder["answer"] = answer
            result_holder["sources"] = sources

    # 1) CHITCHAT short‑circuit (handled without vector + LLM context)
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

    # 2) CAPABILITIES (no vector retrieval)
    if intent == "CAPABILITIES":
        summary = await store.summarize_capabilities(tenant_id)
        msg = build_capabilities_message_from_store(summary)
        _store(msg, [])
        yield msg
        return

    # 3) RETRIEVAL
    raw_question = question
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

    year_filter = extract_year_filter(question, domain)
    if year_filter and intent not in {"EXPORT_TABLE"}:
        query_filter = {**(query_filter or {}), **year_filter}

    year_level = is_year_level_question(question)
    is_numeric_finance = (domain == "FINANCE") and (
        intent in {"NUMERIC_ANALYSIS", "LOOKUP", "EXPORT_TABLE"}
    )
    if year_level or is_numeric_finance:
        effective_top_k = max(top_k, 20)
    else:
        effective_top_k = top_k

    retrieval = await store.query_policies(
        tenant_id=tenant_id,
        collection_name=None,
        collection_names=collection_names or None,
        query=effective_question,
        top_k=effective_top_k,
        where=query_filter,
    )
    hits = retrieval.get("results", [])

    if not hits and year_filter is not None:
        retrieval = await store.query_policies(
            tenant_id=tenant_id,
            collection_name=None,
            collection_names=collection_names or None,
            query=effective_question,
            top_k=effective_top_k,
            where=None,
        )
        hits = retrieval.get("results", [])

    if not hits:
        if intent == "EXPORT_TABLE":
            msg = (
                "I could not find any data you have access to that can be exported as a table "
                "for this question. This may mean the relevant data is either missing or not "
                "visible to your account."
            )
        else:
            msg = (
                "There is not enough information in the documents you can access to answer this question. "
                "Try rephrasing, or specify a particular document or topic, or ask your administrator "
                "to grant you access to the relevant policies."
            )
        _store(msg, [])
        yield msg
        return

    # 4) BUILD CONTEXT
    context_chunks: list[str] = []
    sources: list[str] = []

    for hit in hits:
        doc_text = (hit.get("document") or "").strip()
        meta = hit.get("metadata", {}) or {}
        title = meta.get("display_name") or meta.get("title") or meta.get("filename") or "Unknown document"
        context_chunks.append(doc_text)
        sources.append(title)

    # 5) RERANK (Call 2)
    try:
        rerank_messages = build_rerank_messages(effective_question, context_chunks)
        rerank_resp = await call_llm(
            messages=rerank_messages,
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=300,
        )
        raw = (rerank_resp.choices[0].message.content or "[]").strip()
        try:
            indices = json.loads(raw)
        except Exception:
            start = raw.find("[")
            end = raw.rfind("]")
            if start != -1 and end != -1 and end > start:
                indices = json.loads(raw[start: end + 1])
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

    # Let create_context know both the rule-based intent & domain;
    # the main call will also be instructed to do its own "intent understanding" and formatting.
    system_prompt, user_prompt = create_context(
        context_chunks=context_chunks,
        user_question=raw_question,
        intent=intent,
        domain=domain,
        last_answer=last_answer_text,
        chart_only=chart_only,
    )

    # Merge your formatting instructions into system prompt
    system_prompt = FORMATTER_SYSTEM_PROMPT + "\n\n" + system_prompt

    # You can also add an explicit instruction here:
    # "Additionally, infer the user intent (e.g., CHITCHAT, LOOKUP, ANALYSIS, CHART)
    # and make sure the answer style fits that intent."
    system_prompt += (
        "\n\nYou should internally infer the user's intent type based on the question "
        "and respond in a style that matches it (e.g., short direct answers for LOOKUP, "
        "stepwise explanations for PROCEDURE, numeric focus for NUMERIC_ANALYSIS). "
        "You do not need to output the intent label, only adapt your behavior."
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    if history:
        for u, a in history[-2:]:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})

    messages.append({"role": "user", "content": user_prompt})

    # 7) MAIN ANSWER (Call 1 – streaming, formatting, self-check inside prompt)
    try:
        full_answer_parts: list[str] = []

        stream = await stream_llm(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta or {}
            text = getattr(delta, "content", "") or ""
            if text:
                full_answer_parts.append(text)

        formatted_answer = "".join(full_answer_parts).strip()

        _store(formatted_answer, unique_sources)
        yield formatted_answer

        # 8) Optional chart spec (Call 3, only when needed)
        try:
            lower_q = (question or "").lower()
            chart_intent_trigger = any(
                kw in lower_q
                for kw in ["chart", "graph", "plot", "visual", "visualise", "visualize"]
            )

            logger.info(
                f"CHART_DEBUG domain={domain} intent={intent} "
                f"chart_intent_trigger={chart_intent_trigger}"
            )

            if ((domain == "FINANCE" and chart_intent_trigger) or intent in {
                "NUMERIC_ANALYSIS",
                "LOOKUP",
                "CHART",
            }):
                logger.info("CHART_DEBUG entering chart_spec generation block")

                chart_messages = create_chart_spec_prompt(question, formatted_answer)
                chart_resp = await call_llm(
                    messages=chart_messages,
                    model="gpt-4o-mini",
                    temperature=0.0,
                    max_tokens=1500,
                )

                raw_chart = (chart_resp.choices[0].message.content or "").strip()
                logger.info(f"RAW_CHART_SPEC {raw_chart}")

                chart_obj = parse_raw_chart(raw_chart, logger)

                required_keys = {
                    "chart_type",
                    "title",
                    "x_field",
                    "x_label",
                    "y_fields",
                    "y_label",
                    "data",
                }

                def normalize_one(spec: dict) -> dict | None:
                    if "x-label" in spec and "x_field" in spec:
                        spec["x_label"] = spec.pop("x-label")

                    if not required_keys.issubset(spec.keys()):
                        logger.warning(
                            "CHART_DEBUG chart_spec missing required keys: %s",
                            spec.keys(),
                        )
                        return None

                    return spec

                chart_specs: list[dict] = []

                if isinstance(chart_obj, dict):
                    normalized = normalize_one(chart_obj)
                    if normalized:
                        chart_specs.append(normalized)
                elif isinstance(chart_obj, list):
                    for idx, item in enumerate(chart_obj):
                        if not isinstance(item, dict):
                            logger.warning(
                                "CHART_DEBUG chart_specs[%s] is not a dict, skipping",
                                idx,
                            )
                            continue
                        normalized = normalize_one(item)
                        if normalized:
                            chart_specs.append(normalized)
                elif chart_obj is not None:
                    logger.warning(
                        "CHART_DEBUG chart_spec is neither dict nor list. skipping: %r",
                        type(chart_obj),
                    )

                if chart_specs and result_holder is not None:
                    result_holder["chart_specs"] = chart_specs
                    logger.info(
                        "CHART_DEBUG set chart_specs on result_holder: %s",
                        chart_specs,
                    )

        except Exception as e:
            logger.warning(f"Chart spec generation failed: {e}")

    except Exception as e:
        error_msg = f"There was a temporary problem generating the answer: {str(e)}"
        _store(error_msg, unique_sources)
        yield error_msg
    return

