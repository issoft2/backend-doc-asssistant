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
    - list_documents()
    - add_document()
    - query_policies()
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import tiktoken
from chromadb import PersistentClient
from Vector_setup.embeddings.embedding_service import EmbeddingService



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------------------------------
# Pydantic models for validated input
# ------------------------------------------------
class TenantCollectionConfigRequest(BaseModel):
    tenant_id: str
    collection_name: Optional[str] = None

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
    Production ChromaDB manager with in-process embedding service integration.

    - Uses a single PersistentClient on disk.
    - Namespaces collections as "<tenant_id>__<collection_name>".
    - Async API for add_document / query_policies to fit FastAPI nicely.
    """

    def __init__(
        self,
        persist_dir: str = "./chromadb_multi_tenant",
        embedding_model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        # Embedding service (owns the SentenceTransformer model)
        self._embedding_service = EmbeddingService(model_name=embedding_model_name)

        # Ensure persistence directory exists
        self.persist_dir = Path(persist_dir).resolve()
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # One global Chroma client
        self._client: PersistentClient = PersistentClient(path=str(self.persist_dir))

        # Tokenizer for token-based chunking
        self._encoding = tiktoken.get_encoding("o200k_base")

        logger.info(
            "MultiTenantChromaStoreManager initialized at %s (model: %s)",
            self.persist_dir,
            embedding_model_name,
        )
  
    async def _get_embeddings_batch(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Compute embeddings locally using SentenceTransformer.
        
        Kept async for interface compatibility; uses sync encode under the hood.
        """
        
         # You can ignore `model` or add logic to switch models later
        return self._embedding_service.embed_batch(texts)

                 
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
    # Public API-facing methods
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
        """Logical provisioning when a company first configure."""
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
    ) -> dict:
        """
        Ingest document with async batch embedding via external service.
        """
        chunks = self._chunk_text_tokens(text, max_tokens=512, overlap_tokens=64)
        if not chunks:
            return {
                "status": "error", 
                "message": "Document has no text content after processing."
            }

        # Batch embed all chunks at once for performance
        
        embeddings = await self._get_embeddings_batch(chunks)
        if not embeddings:
            return {
                "status": "error",
                "message": "Failed to compute embeddings for document.",
            }

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

    
    async def query_policies(
        self,
        tenant_id: str,
        collection_name: Optional[str],
        query: str,
        top_k: int = 5,
        where: Optional[dict] = None,   # <-- NEW: optional metadata filter

    ) -> dict:
        """
        Vector search within tenant collections.
        
        - Single collection if collection_name provided
        - All tenant collections if None
        Uses local embedding model  to embed the query.
         Optionally filters by metadata via `where` (e.g. {"doc_id": "..."}).
        """
        
        hits: list[dict] = []

        # 1) Compute query embedding via local model 
        query_embeddings = await self._get_embeddings_batch([query])
        if not query_embeddings:
            return {"query": query, "results": []}
      

        # 2) Select collections for this tenant
        if collection_name:
            full_name = self._tenant_collection_name(tenant_id, collection_name)
            collections = [self._client.get_or_create_collection(full_name)]
        else:
            prefix = f"{tenant_id}__"
            all_cols = self._client.list_collections()
            collections = [c for c in all_cols if c.name.startswith(prefix)]

        # 3) Query each collection with the SAME query embedding
        for col in collections:
            logger.debug(
                "Querying collection %s with embeddings len=%d inner_len=%d",
                col.name,
                len(query_embeddings),
                len(query_embeddings[0]) if query_embeddings and query_embeddings[0] else 0,
            )
            results = col.query(
                query_embeddings=query_embeddings,   #  [[...]]
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
                 where=where or {}, 
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

        # 4) Sort across all collections and trim to top_k
        hits.sort(key=lambda h: h["distance"])
        hits = hits[:top_k]

        return {"query": query, "results": hits}
    
    

    async def close(self):
        """Clean shutdown. hook (Kept for symmetry, nothing to close now)."""
        # Nothing to close. Kept for compatibility if you later add resources
        return None
