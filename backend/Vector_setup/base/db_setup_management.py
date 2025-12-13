#!/usr/bin/env python3
"""
Multi-tenant vectorstore

Production-ready ChromaDB manager for use behind a FastAPI (or any HTTP) API.

Design:
- One embedded Chroma instance (single DB on disk).
- Multi-tenancy implemented at the application level by prefixing
  collection names with the tenant_id.
- Embeddings delegated to external service (no SentenceTransformer dependency).
- Simple API surface:
    - configure_tenant_and_collection()
    - list_companies()
    - list_collections()
    - add_document()
    - query_policies()
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import aiohttp
import asyncio
from pydantic import BaseModel, Field, validator
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

class EmbeddingRequest(BaseModel):
    """Request payload for external embedding service."""
    texts: List[str]
    model: str = "all-MiniLM-L6-v2"

# ------------------------------------------------
# Multi-tenant ChromaDB manager (collection-prefix approach)
# ------------------------------------------------
class MultiTenantChromaStoreManager:
    """
    Production ChromaDB manager with external embedding service integration.
    
    Key changes from previous version:
    - No SentenceTransformer dependency (moved to embedding_service)
    - Batch embedding calls for performance
    - Async HTTP client for non-blocking embedding requests
    - Configurable embedding service endpoint
    """

    def __init__(
        self, 
        persist_dir: str = "./chromadb_multi_tenant",
        embedding_service_url: str = "http://embedding_service:8001/embed"
    ):
        # Ensure persistence directory exists
        self.persist_dir = Path(persist_dir).resolve()
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # ONE global client, no tenant/database args
        from chromadb import PersistentClient
        self._client: PersistentClient = PersistentClient(path=str(self.persist_dir))

        # External embedding service configuration
        self.embedding_service_url = embedding_service_url
        self._http_session: Optional[aiohttp.ClientSession] = None

        # Tokenizer for token-based chunking
        self._encoding = tiktoken.get_encoding("o200k_base")

        logger.info("MultiTenantChromaStoreManager initialized at %s (embeddings: %s)", 
                   self.persist_dir, embedding_service_url)

    async def _init_http_session(self):
        """Lazy initialization of HTTP session for embedding service."""
        if self._http_session is None:
            self._http_session = aiohttp.ClientSession()
    
    async def _get_embeddings_batch(self, texts: List[str], model: str = "all-MiniLM-L6-v2") -> List[List[float]]:
        """
        Fetch embeddings from external service in batch for performance.
        """
        await self._init_http_session()
        
        req = EmbeddingRequest(texts=texts, model=model)
        async with self._http_session.post(
            self.embedding_service_url, 
            json=req.dict()
        ) as resp:
            if resp.status != 200:
                raise ValueError(f"Embedding service failed: {await resp.text()}")
            result = await resp.json()
            return result["embeddings"]

    def _tenant_collection_name(self, tenant_id: str, collection_name: str) -> str:
        """Build the internal collection name, namespaced by tenant."""
        return f"{tenant_id}__{collection_name}"

    def _chunk_text_tokens(
        self,
        text: str,
        max_tokens: int = 512,
        overlap_tokens: int = 64,
    ) -> List[str]:
        """
        Token-based chunking with overlap for consistent retrieval quality.
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
            start = max(0, end - overlap_tokens)

        return chunks

    # -----------------------------------------------------
    # Public API-facing methods (unchanged interface)
    # -----------------------------------------------------
    def configure_tenant_and_collection(self, req: TenantCollectionConfigRequest) -> dict:
        """Provision company + create collection in one call."""
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
        """Logical provisioning when a company first configures RAG."""
        return {
            "status": "ok",
            "tenant_id": req.tenant_id,
        }

    def list_companies(self) -> List[dict]:
        """Derive companies/tenants from existing collections."""
        all_cols = self._client.list_collections()
        tenants: Dict[str, dict] = {}
        
        for col in all_cols:
            name = col.name or ""
            if "__" not in name:
                continue
            tenant_id, _ = name.split("__", 1)
            if tenant_id and tenant_id not in tenants:
                tenants[tenant_id] = {
                    "tenant_id": tenant_id,
                    "display_name": tenant_id,
                }
        return list(tenants.values())

    def create_collection(self, req: CollectionCreateRequest) -> dict:
        """Create a new collection for a tenant."""
        full_name = self._tenant_collection_name(req.tenant_id, req.collection_name)
        collection = self._client.get_or_create_collection(full_name)
        
        return {
            "status": "ok",
            "tenant_id": req.tenant_id,
            "collection_name": req.collection_name,
            "internal_name": collection.name,
            "document_count": collection.count(),
        }

    def list_collections(self, tenant_id: str) -> List[str]:
        """List collections for a specific tenant (UI names)."""
        prefix = f"{tenant_id}__"
        all_cols = self._client.list_collections()
        internal_names = [c.name for c in all_cols if c.name.startswith(prefix)]
        return [name[len(prefix):] for name in internal_names]

    async def add_document(
        self,
        tenant_id: str,
        collection_name: str,
        doc_id: str,
        text: str,
        metadata: Optional[dict] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> dict:
        """
        Ingest document with async batch embedding via external service.
        """
        chunks = self._chunk_text_tokens(text, max_tokens=512, overlap_tokens=64)
        if not chunks:
            return {"status": "error", "message": "Document has no text content after processing."}

        # Batch embed all chunks at once for performance
        embeddings = await self._get_embeddings_batch(chunks, embedding_model)

        full_name = self._tenant_collection_name(tenant_id, collection_name)
        collection = self._client.get_or_create_collection(full_name)

        # Prepare payloads
        chunk_ids = [f"{doc_id}__chunk_{i}" for i in range(len(chunks))]
        chunk_texts = chunks
        chunk_metadatas = [
            {
                **(metadata or {}),
                "tenant_id": tenant_id,
                "collection": collection_name,
                "doc_id": doc_id,
                "chunk_index": i,
                "chunk_count": len(chunks),
            }
            for i in range(len(chunks))
        ]

        collection.add(
            ids=chunk_ids,
            documents=chunk_texts,
            embeddings=embeddings,
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
        Vector search within tenant collections.
        - Single collection if collection_name provided
        - All tenant collections if None
        """
        # Note: Query embedding must come from same service - handled at API level
        # This method assumes pre-computed query embedding passed separately
        
        hits = []

        if collection_name:
            full_name = self._tenant_collection_name(tenant_id, collection_name)
            collections = [self._client.get_or_create_collection(full_name)]
        else:
            prefix = f"{tenant_id}__"
            all_cols = self._client.list_collections()
            collections = [c for c in all_cols if c.name.startswith(prefix)]

        for col in collections:
            results = col.query(
                query_embeddings=[[]],  # Placeholder - embed at API level
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            
            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]

            for i in range(len(ids)):
                hits.append({
                    "id": ids[i],
                    "document": docs[i],
                    "metadata": metas[i],
                    "distance": dists[i],
                    "collection": col.name,
                })

        hits.sort(key=lambda h: h["distance"])
        hits = hits[:top_k]

        return {"query": query, "results": hits}

    async def close(self):
        """Clean shutdown."""
        if self._http_session:
            await self._http_session.close()
