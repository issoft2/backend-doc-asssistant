from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from Vector_setup.user.db import get_db, Tenant, Collection
from Vector_setup.user.auth_jwt import ensure_tenant_active, get_current_user
from Vector_setup.access.collections_acl import user_can_access_collection
from Vector_setup.user.db import DBUser, Collection
from Vector_setup.API.collections_router import _ensure_collection_admin
from Vector_setup.schema.schema_signature import CollectionOut, CompanyOut, OrganizationOut


import logging

logger = logging.getLogger(__name__)

from Vector_setup.base.db_setup_management import (
    MultiTenantChromaStoreManager,
    CollectionCreateRequest,
    CompanyProvisionRequest,
    CompanyCreateRequest,
)
from Vector_setup.user.auth_store import  get_current_db_user
from Vector_setup.base.auth_models import UserOut
from Vector_setup.services.extraction_documents_service import extract_text_from_upload
from Vector_setup.user.roles import COLLECTION_MANAGE_ROLES, UPLOAD_ROLES, VENDOR_ROLES

router = APIRouter()

# Single shared store instance
vector_store = MultiTenantChromaStoreManager("./chromadb_multi_tenant")


def get_store() -> MultiTenantChromaStoreManager:
    return vector_store


# ---------- Role helpers ----------
def require_vendor(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    if current_user.role not in VENDOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendor can perform this action.",
        )
    return current_user



def require_collection_creator(
    current_user: UserOut = Depends(get_current_user),
) -> UserOut:
    """
    Users allowed to create collections: .
    Vendor is explicitly blocked here (even though vendor is 'super' elsewhere).
    """
    if current_user.role in COLLECTION_MANAGE_ROLES:
        return current_user

    if current_user.role in  VENDOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor cannot create collections for companies.",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to create collections.",
    )


def require_uploader(
    current_user: UserOut = Depends(get_current_user),
) -> UserOut:
    """
    Users allowed to upload documents.
    Extend if you want management etc.
    """
    if current_user.role in UPLOAD_ROLES:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to upload Document.",
    )


# ---------- Admin configuration APIs ----------

@router.post("/companies/configure", response_model=CompanyOut)
def configure_company_and_collection(
    req: CompanyCreateRequest,
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(require_vendor),
):
    """
    Configure a company and its first collection in a single call.
    Only vendor can create/provision companies.
    """
    
    # 1) Ensure Tenant exisits in SQL
    tenant = db.get(Tenant, req.tenant_id)
    if not tenant:
        now = datetime.utcnow()
        tenant = Tenant(
            id = req.tenant_id,
            name = req.name or req.tenant_id,  # ← ensure non-null
            plan = req.plan,
            subscription_status=req.subscription_status,
            trial_ends_at=now + timedelta(days=60),
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # 2) Configure in Chroma 
    result =store.provision_company_space(
        CompanyProvisionRequest(tenant_id=req.tenant_id)
    )

    return CompanyOut(
        tenant_id=tenant.id,
        display_name=tenant.name,
        created_at=tenant.created_at,
        plan=tenant.plan,
        subscription_status=tenant.subscription_status,
        trial_ends_at=tenant.trial_ends_at,
    )


# ---- Extra schema for creation ----

class CollectionCreateIn(BaseModel):
    name: str  # just the collection/policy name


def enforce_tenant_limits(
    tenant: Tenant,
    db: Session,
):
    # Example: max 1 collection on trial
    if tenant.plan == "free_trial":
        stmt = select(func.count(Collection.id)).where(
            Collection.tenant_id == tenant.id
        )
        count = db.exec(stmt).one()  # already an int

        if count >= 1:
            raise HTTPException(
                status_code=492,
                detail="Trial Limit reached: maximum 1 collection. Please upgrade.",
            )

@router.post("/collections", response_model=CollectionOut)
def create_collection_for_current_tenant(
    req: CollectionCreateIn,
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(require_collection_creator),
    tenant: Tenant = Depends(ensure_tenant_active),

):
    """
     creates a collection for their own tenant.
    Tenant is taken from the authenticated user, not from the client.
    Vendor cannot create collections.
    """
    tenant_id = current_user.tenant_id
    
    # enforce trial limit to one
    enforce_tenant_limits(tenant, db)

    # 2) Create in Chroma
    result = store.create_collection(
        CollectionCreateRequest(
            tenant_id=tenant_id,
            collection_name=req.name,
        )
    )
    
    # 3) Mirror in SQL
    collection = Collection(
        tenant_id=tenant_id,
        name=result['collection_name'],
        doc_count=result['document_count'],
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    
    return CollectionOut(
        tenant_id=tenant_id,
        collection_name=collection.name,
        doc_count=collection.doc_count,
    )



@router.get("/companies", response_model=List[CompanyOut])
def list_companies(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """
    List companies/tenants.

    - Vendor: sees all tenants.
    - Other users: only their own tenant.
    """
    if current_user.role in VENDOR_ROLES:
        stmt = select(Tenant)
    else:
        stmt = select(Tenant).where(Tenant.id == current_user.tenant_id)

    rows = db.exec(stmt).all()

    return [
        CompanyOut(
            tenant_id=t.id,
            display_name=t.name,
            created_at=t.created_at,
            plan=t.plan,
            subscription_status=t.subscription_status,
            trial_ends_at=t.trial_ends_at,
        )
        for t in rows
    ]

@router.get("/companies/{tenant_id}/organization", response_model=List[OrganizationOut])
def list_company_collections(
    tenant_id: str,
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
    tenant: Tenant = Depends(ensure_tenant_active),
):
    """
    List collections for a tenant, filtered by ACL.

    - Vendor / group roles can list any tenant.
    - Other users can only list their own tenant.
    """
    # Tenant-level access check
    if tenant_id != current_user.tenant_id and current_user.role not in  COLLECTION_MANAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this tenant",
        )

    # Ensure tenant exists
    tenant_row = db.get(Tenant, tenant_id)
    if not tenant_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # Fetch collections from SQL
    stmt = select(Collection).where(Collection.tenant_id == tenant_id)
    collections = db.exec(stmt).all()

    # ACL filter
    visible = [
        c for c in collections
        if user_can_access_collection(current_user, c)
    ]

    # Optionally get doc_count from Chroma
    collections_out: List[CollectionOut] = []
    for c in visible:
        doc_count = 0
        try:
            chroma_col = store.get_collection(
                tenant_id=tenant_id,
                collection_name=c.name,
            )
            doc_count = chroma_col.count()
        except Exception:
            doc_count = 0

        collections_out.append(
            CollectionOut(
                id=c.id,
                tenant_id=c.tenant_id,
                organization_id=c.organization_id,
                name=c.name,
                doc_count=doc_count,
                visibility=c.visibility,
                allowed_roles=c.allowed_roles,
                allowed_user_ids=c.allowed_user_ids,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return collections_out   
    
    
from Vector_setup.access.collections_acl import _to_list
def get_collection_for_user_or_403(
    db: Session,
    current_user: DBUser,
    tenant_id: str,
    collection_name: str,
) -> Collection:
    collection = (
        db.query(Collection)
        .filter(
            Collection.tenant_id == tenant_id,
            Collection.name == collection_name,
        )
        .first()
    )
    logger.info(
        "DEBUG user properties ",
        extra={
            "user_id": str(current_user.id),
            "user_role": current_user.role,
            "user_org": current_user.organization_id,
            "collection_id": str(collection.id),
            "collection_name": collection.name,
            "visibility": str(collection.visibility),
            "collection_org": collection.organization_id,
            "allowed_roles": _to_list(collection.allowed_roles),
            "allowed_user_ids": _to_list(collection.allowed_user_ids)
        }
        )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not user_can_access_collection(current_user, collection):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed for this collection.",
        )

    return collection

# ---------- Document upload (production) ----------
from Vector_setup.user.audit import write_audit_log

@router.post("/documents/upload")
async def upload_document(
    tenant_id: str = Form(...),
    collection_name: str = Form(...),
    title: Optional[str] = Form(None),
    doc_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(require_uploader),
    # tenant: Tenant = Depends(ensure_tenant_active),
):
    """
    Upload a document file and index it into the tenant's collection.

    Rules:
    - can upload (require_uploader).
    - Must upload only into their own tenant.
    """
    # Enforce tenant isolation
    if tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to upload into this tenant.",
        )

    # Basic validation
    if not tenant_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid tenant_id")

    if not collection_name.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid collection name")

    #resolve collection and enforce ACL
    collection = get_collection_for_user_or_403(
        db=db,
        current_user=current_user,
        tenant_id=tenant_id,
        collection_name=collection_name,
    )

    # Read raw bytes
    raw_bytes = await file.read()

    text = extract_text_from_upload(file.filename, raw_bytes)
    
    # Defensive checks in case any extractor changes
    if not isinstance(text, str):
        raise HTTPException(
            status_code=500,
            detail="Internal text extraction error.",
        )
        
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the document",
        )

    # Generate doc_id if not supplied
    final_doc_id = doc_id or str(uuid.uuid4())
    # Look up collection info
    collection_info = store.get_collection_info(tenant_id, collection_name) # to be implemented
    collection_display_name = collection_info.get("display_name", collection_name)
    high_level_topic = collection_info.get("topic") # e.g. "HR & Policies", "Engineering", etc.
    
    # Build document-level metadata (for later source display)
    metadata = {
        "filename": file.filename,
        "title": title or file.filename,
        "content_type": file.content_type,
        "size_bytes": len(raw_bytes),
        "tenant_id": tenant_id,
        "collection": collection_name,
         "collection_display_name": collection_display_name,
        "high_level_topic": high_level_topic,
        "collection_id": collection.id,
        "organization_id": collection.organization_id,
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
        raise HTTPException(
            status_code=500,
            detail=result.get("message", "Indexing failed"),
        )
    
    # add to audit log
    write_audit_log(
        db=db,
        user=current_user,
        action="document_ingest",
        resource_type="collection",
        resource_id=collection.id,
        metadata={
            "tenant_id": tenant_id,
            "collection_name": collection.name,
            "doc_id": final_doc_id,
            "filename": file.filename,
            "source": "upload",
        },
    )
    

    return result


@router.get("/collections/old", response_model=List[CollectionOut])
def list_collections_for_current_user(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
):
    """
    List collections in the current user's tenant, filtered by ACL.
    """
    stmt = select(Collection).where(Collection.tenant_id == current_user.tenant_id)
    collections = db.exec(stmt).all()

    visible = [
        c for c in collections
        if user_can_access_collection(current_user, c)
    ]

    # If you have doc_count from SQL or Chroma, compute it here; else 0.
    result: List[CollectionOut] = []
    for c in visible:
        result.append(
            CollectionOut(
                id=c.id,
                tenant_id=c.tenant_id,            # fixed: was c.tenant
                organization_id=c.organization_id,
                name=c.name,
                doc_count=0,                      # or real count if available
                visibility=c.visibility,
                allowed_roles=c.allowed_roles,
                allowed_user_ids=c.allowed_user_ids,
                created_at=c.created_at,
            )
        )

    return result
    



