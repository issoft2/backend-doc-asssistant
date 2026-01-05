import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import tiktoken
from chromadb import PersistentClient
from Vector_setup.embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        if v is None:
            return v
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Collection name must be alphanumeric and may include '-' or '_'.")
        return v


class CompanyProvisionRequest(BaseModel):
    tenant_id: str = Field(..., min_length=1, max_length=64)

    @validator("tenant_id")
    def safe_tenant_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("tenant_id must be alphanumeric and may include '-' or '_'.")
        return v


class CollectionCreateRequest(BaseModel):
    tenant_id: str
    collection_name: str = Field(..., min_length=1, max_length=64)

    @validator("collection_name")
    def safe_collection_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Collection name must be alphanumeric and may include '-' or '_'.")
        return v


class MultiTenantChromaStoreManager:
    """
    Production ChromaDB manager with in-process embedding service.

    - Uses a single PersistentClient on disk.
    - Namespaces collections as "<tenant_id>__<collection_name>".
    """

    def __init__(
        self,
        persist_dir: str = "./chromadb_multi_tenant",
        embedding_model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        self._embedding_service = EmbeddingService(model_name=embedding_model_name)

        self.persist_dir = Path(persist_dir).resolve()
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._client: PersistentClient = PersistentClient(path=str(self.persist_dir))

        self._encoding = tiktoken.get_encoding("o200k_base")

        # cache for collection-level metadata (name -> info)
        self._collection_meta_cache: Dict[tuple[str, str], dict] = {}

        logger.info(
            "MultiTenantChromaStoreManager initialized at %s (model: %s)",
            self.persist_dir,
            embedding_model_name,
        )

    async def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Compute embeddings locally using SentenceTransformer.
        Kept async for interface compatibility; uses sync encode under the hood.
        """
        return self._embedding_service.embed_batch(texts)

    def _tenant_collection_name(self, tenant_id: str, collection_name: str) -> str:
        return f"{tenant_id}__{collection_name}"

    def _chunk_text_tokens(
        self,
        text: str,
        max_tokens: int = 512,
        overlap_tokens: int = 64,
    ) -> List[str]:
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

    # -----------------------
    # Tenant / collection API
    # -----------------------

    def configure_tenant_and_collection(self, req: TenantCollectionConfigRequest) -> dict:
        provision_result = self.provision_company_space(
            CompanyProvisionRequest(tenant_id=req.tenant_id)
        )
        collection_result = None
        if req.collection_name:
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
        return {
            "status": "ok",
            "tenant_id": req.tenant_id,
        }

    def list_companies(self) -> List[dict]:
        all_cols = self._client.list_collections()
        tenants: Dict[str, dict] = {}

        for col in all_cols:
            name = getattr(col, "name", "") or ""
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
        """
        List collection *names* (UI names) for a specific tenant.
        """
        prefix = f"{tenant_id}__"
        all_cols = self._client.list_collections()
        internal_names = [
            getattr(c, "name", "")
            for c in all_cols
            if getattr(c, "name", "").startswith(prefix)
        ]
        return [name[len(prefix):] for name in internal_names]

    def list_collections_for_tenant(self, tenant_id: str) -> List[dict]:
        """
        Rich listing for a tenant: used by capabilities & get_collection_info.
        Later, you can enrich each row with data from SQL or another store.
        """
        names = self.list_collections(tenant_id)
        rows: List[dict] = []
        for name in names:
            rows.append(
                {
                    "name": name,
                    "display_name": name,
                    "topic": None,
                    "example_questions": [],
                }
            )
        return rows

    def get_collection_info(self, tenant_id: str, collection_name: str) -> dict:
        """
        Return metadata for a specific collection (display_name, topic, example_questions).
        Dynamic over existing collections; no hard-coded topics.
        """
        key = (tenant_id, collection_name)
        if key in self._collection_meta_cache:
            return self._collection_meta_cache[key]

        rows = self.list_collections_for_tenant(tenant_id)
        info = next(
            (r for r in rows if r["name"] == collection_name),
            {
                "name": collection_name,
                "display_name": collection_name,
                "topic": None,
                "example_questions": [],
            },
        )

        self._collection_meta_cache[key] = info
        return info
    
    # Santize the metadata before ingestion
    def _clean_metadata(meta: dict) -> dict:
        cleaned = {}
        for k, v in meta.items():
            if v is None:
                continue  # or set to "" if you need the key
            # Optionally, coerce non-primitive types to strings:
            if isinstance(v, (str, int, float, bool)):
                cleaned[k] = v
            else:
                cleaned[k] = str(v)
        return cleaned

    # -----------------------
    # Ingest / query
    # -----------------------

    async def add_document(
        self,
        tenant_id: str,
        collection_name: str,
        doc_id: str,
        text: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        chunks = self._chunk_text_tokens(text, max_tokens=512, overlap_tokens=64)
        if not chunks:
            return {
                "status": "error",
                "message": "Document has no text content after processing.",
            }

        embeddings = await self._get_embeddings_batch(chunks)
        if not embeddings:
            return {
                "status": "error",
                "message": "Failed to compute embeddings for document.",
            }

        full_name = self._tenant_collection_name(tenant_id, collection_name)
        collection = self._client.get_or_create_collection(full_name)

        chunk_ids = [f"{doc_id}__chunk_{i}" for i in range(len(chunks))]
        
        chunk_metadatas = []
        for idx, _chunk_text in enumerate(chunks):
            base_meta = metadata or {}
            meta = {
                **base_meta,          # doc-level metadata from router
                "tenant_id": tenant_id,
                "collection": collection_name,
                "doc_id": doc_id,
                "chunk_index": idx,
                "chunk_count": len(chunks),
            }
            chunk_metadatas.append(_clean_metadata(meta))

        
        collection.add(
            ids=chunk_ids,
            documents=chunks,
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
        where: Optional[dict] = None,
    ) -> dict:
        """
        Vector search within tenant collections.

        - Single collection if collection_name provided
        - All tenant collections if None
        """
        hits: list[dict] = []

        query_embeddings = await self._get_embeddings_batch([query])
        if not query_embeddings:
            return {"query": query, "results": []}

        if collection_name:
            full_name = self._tenant_collection_name(tenant_id, collection_name)
            collections = [self._client.get_or_create_collection(full_name)]
        else:
            prefix = f"{tenant_id}__"
            all_cols = self._client.list_collections()
            collections = [
                c for c in all_cols if getattr(c, "name", "").startswith(prefix)
            ]
            
        if not collections:
            logger.info("No collections found for tenant %s", tenant_id)
            return {"query": query, "results": []}    

        for col in collections:
            logger.debug(
                "Querying collection %s",
                getattr(col, "name", ""),
            )
            results = col.query(
                query_embeddings=query_embeddings,
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
                        "collection": getattr(col, "name", ""),
                    }
                )

        hits.sort(key=lambda h: h["distance"])
        hits = hits[:top_k]

        return {"query": query, "results": hits}

    async def summarize_capabilities(self, tenant_id: str) -> dict:
        """
        Summarize tenant workspace for CAPABILITIES answers.
        """
        rows = self.list_collections_for_tenant(tenant_id)
        collections: list[dict] = []

        for r in rows:
            collections.append(
                {
                    "name": r["name"],
                    "display_name": r.get("display_name") or r["name"],
                    "topics": [r["topic"]] if r.get("topic") else [],
                    "example_questions": r.get("example_questions") or [],
                }
            )

        return {"collections": collections}

    async def close(self):
        return None
