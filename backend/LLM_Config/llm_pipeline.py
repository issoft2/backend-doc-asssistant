#!/usr/bin/env python3

from typing import List, Dict, Any
from LLM_Config.llm_setup import llm_client
from LLM_Config.system_user_prompt import create_context
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager


def llm_pipeline(
    store: MultiTenantChromaStoreManager,
    tenant_id: str,
    collection_name: str | None,
    user_question: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    End-to-end RAG pipeline:
      - Retrieve relevant chunks from Chroma for a given tenant.
        * If collection_name is provided -> only that collection.
        * If collection_name is None/empty -> all collections for the tenant.
      - Build system + user prompts with context.
      - Call LLM.
      - Return answer and sources for display in the UI.
    """
    print("RAG query:", tenant_id, collection_name, top_k, user_question)

    # 1) RETRIEVE (delegates filtering logic to the manager)
    retrieval = store.query_policies(
        tenant_id=tenant_id,
        collection_name=collection_name,  # can be None for all collections
        query=user_question,
        top_k=top_k,
    )
    hits = retrieval.get("results", [])  # list of {id, document, metadata, distance}

    if not hits:
        return {
            "answer": (
                "The provided policy documents do not contain information to answer this question. "
                "please check with the company HR or policy owner for clarification."
            ),
            "sources": [],
        }

    # Build context chunks as strings that already include titles/filenames
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

    # 2) Build PROMPTS
    system_prompt, user_prompt = create_context(context_chunks, user_question)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # 3) CALL LLM
    response = llm_client.invoke(messages)
    answer = getattr(response, "content", None) or response

    # 4) RETURN ANSWER + SOURCES
    return {
        "answer": answer.strip(),
    }
