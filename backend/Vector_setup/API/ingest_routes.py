from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from Vector_setup.base.db_setup_management import (
    MultiTenantChromaStoreManager,
    TenantCollectionConfigRequest,
)
from Vector_setup.test.add_document_manual_testing import AddDocumentRequest  # test only
from Vector_setup.user.auth_jwt import get_current_user   # ⬅ adjust path if different
from Vector_setup.base.auth_models import UserOut        # ⬅ or whatever your User schema is

import uuid



router = APIRouter()

# Single shared store instance
vector_store = MultiTenantChromaStoreManager("./chromadb_multi_tenant")




def get_store() -> MultiTenantChromaStoreManager:
  return vector_store


# ---------- Schemas for responses ----------

class TenantCollectionConfigOut(BaseModel):
  status: str
  tenant_id: str
  collection_name: str


class CompanyOut(BaseModel):
  tenant_id: str
  display_name: str | None = None


class CollectionOut(BaseModel):
  name: str


# ---------- Admin configuration APIs ----------

@router.post("/companies/configure", response_model=TenantCollectionConfigOut)
def configure_company_and_collection(
  req: TenantCollectionConfigRequest,
  store: MultiTenantChromaStoreManager = Depends(get_store),
  current_user: UserOut = Depends(get_current_user),

):
  """
  Configure a company and its first collection in a single call.
  Configure a company and its first collection.
  Only vendor can create/provision companies.
  """
   
  if current_user.role != "vendor":
      raise HTTPException(status_code=403, detail="Only vendor can create companies")
    
  result = store.configure_tenant_and_collection(req)
  return {
    "status": result["status"],
    "tenant_id": result["tenant_id"],
    "collection_name": result["collection_name"],
  }


@router.get("/companies", response_model=List[CompanyOut])
def list_companies(
  store: MultiTenantChromaStoreManager = Depends(get_store),
  current_user: UserOut = Depends(get_current_user),
):
  """
  List all companies/tenants that currently have collections.
  """
  all_tenants = store.list_companies() # list[{ "tenant_id", "display_name"}]
  my_tenant_id = current_user.tenant_id
  
  if current_user.role == "vendor":
      # Vendor: see every company
      return [CompanyOut(**t) for t in all_tenants]
  
  # normal tenants only see their own company
  return [
    CompanyOut(**t)
    for t in all_tenants 
    if t["tenant_id"] == my_tenant_id
  ]


@router.get("/companies/{tenant_id}/collections", response_model=List[CollectionOut])
def list_company_collections(
  tenant_id: str,
  store: MultiTenantChromaStoreManager = Depends(get_store),
  current_user: UserOut = Depends(get_current_user),
):
  """
  List all collections for a given tenant (names without tenant prefix).
  Only allowed for the current user's tenant.
  """
  if current_user.role != "vendor" and tenant_id != current_user.tenant_id:
      raise HTTPException(status_code=403, detail="Not allowed to access this tenant")

  names = store.list_collections(tenant_id)
  return [{"name": n} for n in names]


# ---------- Document upload (production) ----------

@router.post("/documents/upload")
async def upload_document(
  tenant_id: str = Form(...),
  collection_name: str = Form(...),
  title: Optional[str] = Form(None),
  doc_id: Optional[str] = Form(None),
  file: UploadFile = File(...),
  store: MultiTenantChromaStoreManager = Depends(get_store),
  current_user: UserOut = Depends(get_current_user),
):
  """
  Upload a document file and index it into the tenant's collection.

  Responsibilities:
  - Validate basic inputs.
  - Read and decode file content into text.
  - Build document-level metadata (filename, title, content_type, size).
  - Generate a stable doc-id if not provided.
  - Delegate chunking + embeddings + storage to store.add_document().
  """
  
  # Enforce tenant isolation
  if tenant_id != current_user.tenant_id:
    raise HTTPException(status_code=403, detail="Not Allowed to upload this this this tenant")
  
  # Restrict By Role
  if current_user.role not in { "hr", "executive", "management" }:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
  
  # Basic validation
  if not tenant_id.replace("-", "").replace("_", "").isalnum():
    raise HTTPException(status_code=400, detail="Invalid tenant_id")

  if not collection_name.replace("-", "").replace("_", "").isalnum():
    raise HTTPException(status_code=400, detail="Invalid collection name")
 

  # Read raw bytes
  raw_bytes = await file.read()

  # Simple text extraction (for now: treat as UTF-8 text)
  try:
    text = raw_bytes.decode("utf-8", errors="ignore")
  except Exception:
    raise HTTPException(status_code=400, detail="Could not decode file as text")

  if not text.strip():
    raise HTTPException(status_code=400, detail="No text content found in file")

  # Generate doc_id if not supplied
  final_doc_id = doc_id or str(uuid.uuid4())

  # Build document-level metadata (for later source display)
  metadata = {
    "filename": file.filename,
    "title": title or file.filename,
    "content_type": file.content_type,
    "size_bytes": len(raw_bytes),
    "tenant_id": tenant_id,
    "collection": collection_name,
  }

  # Delegate to vector store (chunking + embeddings)
  result = await store.add_document(
    tenant_id=tenant_id,
    collection_name=collection_name,
    doc_id=final_doc_id,
    text=text,
    metadata=metadata,
  )

  if result.get("status") != "ok":
    raise HTTPException(status_code=500, detail=result.get("message", "Indexing failed"))

  return result

