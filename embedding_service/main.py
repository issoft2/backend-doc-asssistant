#!/usr/bin/env python3
"""
Embedding Service API
FastAPI service for batch text embeddings (GPU-accelerated)
Consumes: List[str] texts → List[List[float]] embeddings
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
from sentence_transformers import SentenceTransformer
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Embedding Service", version="1.0.0")

# Global model cache (shared across workers)
_model_cache = {}

class EmbeddingRequest(BaseModel):
    texts: List[str]
    model: str = "all-MiniLM-L6-v2"

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    input_count: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load default model
    logger.info("Loading default embedding model...")
    _model_cache["all-MiniLM-L6-v2"] = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Embedding service ready")
    yield
    # Shutdown
    logger.info("Embedding service shutdown")

app.router.lifespan_context = lifespan

@app.post("/embed", response_model=EmbeddingResponse)
async def embed_texts(req: EmbeddingRequest):
    """
    Batch embed texts → embeddings
    - GPU-accelerated via SentenceTransformer
    - Supports model switching (cached)
    """
    if not req.texts:
        raise HTTPException(status_code=400, detail="Empty texts list")
    
    if len(req.texts) > 1000:
        raise HTTPException(status_code=400, detail="Max 1000 texts per request")
    
    # Get or load model
    if req.model not in _model_cache:
        logger.info(f"Loading model: {req.model}")
        _model_cache[req.model] = SentenceTransformer(req.model)
    
    model = _model_cache[req.model]
    
    # Batch encode (GPU-accelerated)
    embeddings = model.encode(req.texts, batch_size=32, show_progress_bar=False).tolist()
    
    return EmbeddingResponse(
        embeddings=embeddings,
        model=req.model,
        input_count=len(req.texts)
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "models_loaded": len(_model_cache)}

@app.get("/models")
async def list_models():
    return {"available": list(_model_cache.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
