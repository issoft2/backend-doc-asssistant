#!/usr/bin/env python3

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from typing import Optional


from Vector_setup.API.ingest_routes import get_store
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from LLM_Config.llm_pipeline import llm_pipeline
from Vector_setup.user.auth_jwt import get_current_user, TokenUser  # <-- add this

router = APIRouter()

class QueryRequest(BaseModel):
    collection_name: Optional[str] = None
    question: str
    top_k: int = 5

@router.post("/query")
def query_policies_api(
    req: QueryRequest,
    current_user: TokenUser = Depends(get_current_user),
    store: MultiTenantChromaStoreManager = Depends(get_store),
):
    
    print("Collections:", [c.name for c in store._client.list_collections()])

    print("Helium collections:", store.list_collections("Helium"))
    
    result = llm_pipeline(
        store=store,
        tenant_id=current_user.tenant_id,
        collection_name=req.collection_name,
        user_question=req.question,
        top_k=req.top_k,
    )
    return result
