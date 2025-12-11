#!/usr/bin/env python3
"""
Multi-tenant vectorstore

Production-ready ChromaDB manager for use behind a FastAPI (or any HTTP) API.

Design:
- One embedded Chroma instance (single DB on disk).
- Multi-tenancy implemented at the application level by prefixing
  collection names with the tenant_id.
- Simple API surface:
    - configure_tenant_and_collection()
    - list_companies()
    - list_collections()
    - add_document()
    - query_policies()
"""

import logging
from pathlib import Path
from typing import Optional, List, Tuple, Dict

from chromadb import PersistentClient
from pydantic import BaseModel, Field, validator
from sentence_transformers import SentenceTransformer
import tiktoken

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ------------------------------------------------
# Pydantic models for validated input
# ------------------------------------------------
class TenantCollectionConfigRequest(BaseModel):
    tenant_id: str
    collection_name: str

    @validator("tenant_id")
    def safe_tenant_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("tenant_id must be alphanumeric and may include '-' or '_'.")
        return v

    @validator("collection_name")
    def safe_collection_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Collection name must be alphanumeric and may include '-' or '_'.")
        return v


class CompanyProvisionRequest(BaseModel):
    """Logical provisioning of a company space (tenant_id only)."""

    tenant_id: str = Field(..., min_length=1, max_length=64)

    @validator("tenant_id")
    def safe_tenant_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("tenant_id must be alphanumeric and may include '-' or '_'.")
        return v


class CollectionCreateRequest(BaseModel):
    """Create a collection within a tenant space."""

    tenant_id: str
    collection_name: str = Field(..., min_length=1, max_length=64)

    @validator("collection_name")
    def safe_collection_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Collection name must be alphanumeric and may include '-' or '_'.")
        return v


# ------------------------------------------------
# Multi-tenant ChromaDB manager (collection-prefix approach)
# ------------------------------------------------
class MultiTenantChromaStoreManager:
    """
    Wrap ChromaDB in a way that's easy to expose via an API.

    Implementation notes:
    - Single shared persistence location (embedded Chroma).
    - Multi-tenancy via collection name prefix "tenant_id__collection_name".
    """

    def __init__(self, persist_dir: str = "./chromadb_multi_tenant"):
        # Ensure persistence directory exists
        self.persist_dir = Path(persist_dir).resolve()
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # ONE global client, no tenant/database args
        self._client: PersistentClient = PersistentClient(path=str(self.persist_dir))

        # Cache a single embedding model instance process-wide
        self._embedding_cache: Optional[Tuple[str, SentenceTransformer]] = None

        # Tokenizer for token-based chunking (choose encoding compatible with your model)
        self._encoding = tiktoken.get_encoding("o200k_base")

        logger.info("MultiTenantChromaStoreManager initialized at %s", self.persist_dir)

    # -----------------------------------------------
    # Internal helpers
    # -----------------------------------------------
    def _get_embedding_model(self, model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
        """
        Lazily load and cache the embedding model.
        Shared by all tenants; change if you ever need per-tenant models.
        """
        if self._embedding_cache is None or self._embedding_cache[0] != model_name:
            logger.info("Loading embedding model '%s'", model_name)
            model = SentenceTransformer(model_name)
            self._embedding_cache = (model_name, model)
        return self._embedding_cache[1]

    def _tenant_collection_name(self, tenant_id: str, collection_name: str) -> str:
        """
        Build the internal collection name, namespaced by tenant.
        Example: "isof_corp__policies".
        """
        return f"{tenant_id}__{collection_name}"

    def _chunk_text_tokens(
        self,
        text: str,
        max_tokens: int = 512,
        overlap_tokens: int = 64,
    ) -> List[str]:
        """
        Token-based chunking with overlap.

        - max_tokens: target length per chunk.
        - overlap_tokens: how many tokens to overlap between consecutive chunks.

        Returns chunks as strings reconstructed from tokens.
        """
        text = text.strip()
        if not text:
            return []

        token_ids = self._encoding.encode(text)
        n_tokens = len(token_ids)
        if n_tokens == 0:
            return []

        chunks: List[str] = []
        start = 0

        while start < n_tokens:
            end = min(start + max_tokens, n_tokens)
            chunk_token_ids = token_ids[start:end]
            chunk_text = self._encoding.decode(chunk_token_ids)
            chunks.append(chunk_text)

            if end == n_tokens:
                break

            # Move start forward with overlap
            start = end - overlap_tokens
            if start < 0:
                start = 0

        return chunks

    # -----------------------------------------------------
    # Public API-facing methods
    # -----------------------------------------------------
    def configure_tenant_and_collection(self, req: TenantCollectionConfigRequest) -> dict:
        """
        Provision company + create collection in one call.
        """
        provision_result = self.provision_company_space(
            CompanyProvisionRequest(tenant_id=req.tenant_id)
        )
        collection_result = self.create_collection(
            CollectionCreateRequest(
                tenant_id=req.tenant_id,
                collection_name=req.collection_name,
            )
        )
        return {
            "status": "ok",
            "tenant_id": req.tenant_id,
            "collection_name": req.collection_name,
            "provision": provision_result,
            "collection": collection_result,
        }

    def provision_company_space(self, req: CompanyProvisionRequest) -> dict:
        """
        Logical provisioning when a company first configures RAG.
        Currently just validation; extend later to touch your app DB.
        """
        return {
            "status": "ok",
            "tenant_id": req.tenant_id,
        }

    def list_companies(self) -> List[dict]:
        """
        Derive the list of companies/tenants from the existing collections.
        Any collection whose name looks like "<tenant_id>__<collection_name>"
        contributes a tenant_id entry.
        """
        all_cols = self._client.list_collections()

        tenants: Dict[str, dict] = {}
        for col in all_cols:
            name = col.name or ""
            if "__" not in name:
                continue
            tenant_id, _ = name.split("__", 1)
            if not tenant_id:
                continue
            if tenant_id not in tenants:
                tenants[tenant_id] = {
                    "tenant_id": tenant_id,
                    "display_name": tenant_id,  # override from app DB if needed
                }
        return list(tenants.values())

    def create_collection(self, req: CollectionCreateRequest) -> dict:
        """
        Called when a company defines a new collection from the UI.
        Collection names can be reused across different tenants because
        they are internally prefixed with tenant_id.
        """
        full_name = self._tenant_collection_name(req.tenant_id, req.collection_name)
        collection = self._client.get_or_create_collection(full_name)

        return {
            "status": "ok",
            "tenant_id": req.tenant_id,
            "collection_name": req.collection_name,  # UI name
            "internal_name": collection.name,        # namespaced name in Chroma
            "document_count": collection.count(),
        }

    def list_collections(self, tenant_id: str) -> List[str]:
        """
        List all collections for a specific tenant.
        Returns the collection names without the tenant prefix for UI display.
        """
        prefix = f"{tenant_id}__"
        all_cols = self._client.list_collections()
        internal_names = [c.name for c in all_cols if c.name.startswith(prefix)]
        return [name[len(prefix):] for name in internal_names]

    def add_document(
        self,
        tenant_id: str,
        collection_name: str,
        doc_id: str,
        text: str,
        metadata: Optional[dict] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> dict:
        """
        Ingest a single logical document:
        - Split into token-based chunks.
        - Embed each chunk.
        - Store chunks in the tenant's collection with rich metadata.

        metadata is expected to at least contain:
        - "filename" or "title"
        - any other fields useful for later reference (e.g. source, content_type).
        """
        chunks = self._chunk_text_tokens(
            text,
            max_tokens=512,
            overlap_tokens=64,
        )
        if not chunks:
            return {
                "status": "error",
                "message": "Document has no text content after processing.",
            }

        embedder = self._get_embedding_model(embedding_model)

        full_name = self._tenant_collection_name(tenant_id, collection_name)
        collection = self._client.get_or_create_collection(full_name)

        # Prepare per-chunk payloads
        chunk_ids: List[str] = []
        chunk_texts: List[str] = []
        chunk_embeddings: List[list] = []
        chunk_metadatas: List[dict] = []

        base_meta = metadata or {}
        for idx, chunk in enumerate(chunks):
            chunk_ids.append(f"{doc_id}__chunk_{idx}")
            chunk_texts.append(chunk)
            # Optional micro-optimization: batch encode instead of per chunk
            chunk_embeddings.append(embedder.encode(chunk).tolist())
            chunk_metadatas.append(
                {
                    **base_meta,
                    "tenant_id": tenant_id,
                    "collection": collection_name,
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "chunk_count": len(chunks),
                }
            )

        collection.add(
            ids=chunk_ids,
            documents=chunk_texts,
            embeddings=chunk_embeddings,
            metadatas=chunk_metadatas,
        )

        return {
            "status": "ok",
            "tenant_id": tenant_id,
            "collection_name": collection_name,
            "doc_id": doc_id,
            "chunks_indexed": len(chunks),
            "new_collection_count": collection.count(),
        }


    def query_policies(
        self,
        tenant_id: str,
        collection_name: Optional[str],
        query: str,
        top_k: int = 5,
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> dict:
        """
        Vector search within a tenant.
        - If collection_name is provided: search only that collection.
        - If collection_name is None: search across all collections for this tenant.
        """
        embedder = self._get_embedding_model(embedding_model)
        query_embedding = embedder.encode(query).tolist()

        hits = []

        if collection_name:
            # Single collection
            full_name = self._tenant_collection_name(tenant_id, collection_name)
            collections = [self._client.get_or_create_collection(full_name)]
        else:
            # All collections for this tenant
            prefix = f"{tenant_id}__"
            all_cols = self._client.list_collections()
            collections = [c for c in all_cols if c.name.startswith(prefix)]

        for col in collections:
            results = col.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]

            for i in range(len(ids)):
                hits.append(
                    {
                        "id": ids[i],
                        "document": docs[i],
                        "metadata": metas[i],
                        "distance": dists[i],
                        "collection": col.name,
                    }
                )

        # Sort best matches first and trim globally
        hits.sort(key=lambda h: h["distance"])
        hits = hits[:top_k]

        return {"query": query, "results": hits}

