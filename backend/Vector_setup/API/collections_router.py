from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
import json

from Vector_setup.user.db import DBUser, Tenant, Collection, Organization,  get_db
from Vector_setup.user.auth_jwt import ensure_tenant_active
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager, CollectionCreateRequest
from Vector_setup.schema.schema_signature import (
    CollectionCreateIn,
    CollectionOut,
    CollectionUpdateIn,
)
from Vector_setup.user.audit import write_audit_log
from Vector_setup.user.roles import COLLECTION_MANAGE_ROLES
from Vector_setup.access.collections_acl import user_can_access_collection
from Vector_setup.user.auth_store import get_current_db_user




vector_store = MultiTenantChromaStoreManager("./chromadb_multi_tenant")
   
def get_store() -> MultiTenantChromaStoreManager:
    return vector_store


router = APIRouter(prefix="/collections", tags=["collections"])

def _ensure_collection_admin(user: DBUser) -> None:
    if user.role not in COLLECTION_MANAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to manage collections.",
        )


@router.post("/create", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
def create_collection(
    body: CollectionCreateIn,
    db: Session = Depends(get_db),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    current_user: DBUser = Depends(get_current_db_user),
    tenant: Tenant = Depends(ensure_tenant_active),
):
    """
    Create a new collection for a tenant with ACL fields.

    Only collection admins (group_admin/group_exec/sub_admin/sub_md) can create.
    """
    _ensure_collection_admin(current_user)

    # Tenant isolation: can only create in own tenant unless group/vendor
    if body.tenant_id != current_user.tenant_id and current_user.role not in {
        "vendor",
        "group_admin",
        "group_exec",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create collections for this tenant.",
        )

    # Ensure tenant exists
    tenant_row = db.get(Tenant, body.tenant_id)
    if not tenant_row:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    # Optional: validate organization belongs to tenant
    if body.organization_id:
        org = db.get(Organization, body.organization_id)
        if not org or org.tenant_id != body.tenant_id:
            raise HTTPException(status_code=400, detail="Invalid organization_id for tenant.")

    # Enforce unique (tenant_id, name)
    stmt = (
        select(Collection)
        .where(Collection.tenant_id == body.tenant_id and Collection.organization_id == body.organization_id)
        .where(Collection.name == body.name)
    )
    existing = db.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="Collection name already exists for this tenant.")

    # Create SQL row
    collection_id = str(uuid.uuid4())
    db_collection = Collection(
        id=collection_id,
        tenant_id=body.tenant_id,
        organization_id=body.organization_id,
        name=body.name,
        visibility=body.visibility,
        allowed_roles=json.dumps(body.allowed_roles or []),
        allowed_user_ids=json.dumps(body.allowed_user_ids or []),
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    
    # Log audit log
    write_audit_log(
        db=db,
        user=current_user,
        action="collection_create",
        resource_type="collection",
        resource_id=db_collection.id,
        metadata={
            "tenant_id": db_collection.tenant_id,
            "name": db_collection.name,
            "visibility": str(db_collection.visibility),
            "organization_id": db_collection.organization_id,
        },
    )    
    # Ensure underlying Chroma collection exists
    store.create_collection(
        CollectionCreateRequest(
            tenant_id=body.tenant_id,
            collection_name=body.name,
        )
    )

    return CollectionOut(
        id=db_collection.id,
        tenant_id=db_collection.tenant_id,
        organization_id=db_collection.organization_id,
        name=db_collection.name,
        doc_count=0,
        visibility=db_collection.visibility,
        allowed_roles=db_collection.allowed_roles,
        allowed_user_ids=db_collection.allowed_user_ids,
        created_at=db_collection.created_at,
        updated_at=db_collection.updated_at,
    )


@router.patch("/{collection_id}", response_model=CollectionOut)
def update_collection(
    collection_id: str,
    body: CollectionUpdateIn,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
    tenant: Tenant = Depends(ensure_tenant_active),
):
    """
    Update ACL and org fields of a collection.

    Only collection admins (group_admin/group_exec/sub_admin/sub_md) can update.
    """
    _ensure_collection_admin(current_user)

    db_collection = db.get(Collection, collection_id)
    if not db_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found.")

    # Tenant isolation: user must be allowed to manage this tenant
    if db_collection.tenant_id != current_user.tenant_id and db.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update collections for this tenant.",
        )

    # Optional: validate organization belongs to tenant if changed
    if body.organization_id is not None:
        org = db.get(Organization, body.organization_id)
        if not org or org.tenant_id != db_collection.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization_id for this tenant.",
            )

    update_data = body.model_dump(exclude_unset=True)

    # Apply changes field-by-field
    for field, value in update_data.items():
        setattr(db_collection, field, value)

    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    
    # add to audit log;
    write_audit_log(
        db=db,
        user=current_user,
        action="collection_update",
        resource_type="collection",
        resource_id=db_collection.id,
        metadata={
            "tenant_id": db_collection.tenant_id,
            "name": db_collection.name,
            "visibility": str(db_collection.visibility),
            "organization_id": db_collection.organization_id,
        },
    )
    # doc_count remains whatever your listing logic computes (0 here)
    return CollectionOut(
        id=db_collection.id,
        tenant_id=db_collection.tenant_id,
        organization_id=db_collection.organization_id,
        name=db_collection.name,
        doc_count=0,
        visibility=db_collection.visibility,
        allowed_roles=db_collection.allowed_roles,
        allowed_user_ids=db_collection.allowed_user_ids,
        created_at=db_collection.created_at,
        updated_at=db_collection.updated_at,
    )

@router.get("", response_model=List[CollectionOut])
def list_collections(
    tenant_id: Optional[str] = Query(default=None),
    visibility: Optional[str] = Query(
        default=None,
        description="Optional visibility filter: tenant|org|role|user",
    ),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
):
    # non-vendor: always own tenant
    if current_user.role != "vendor":
        effective_tenant_id = current_user.tenant_id
    else:
        # vendor: must specify tenant_id
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tenant_id is required for vendor.",
            )
        effective_tenant_id = tenant_id

    stmt = select(Collection).where(Collection.tenant_id == effective_tenant_id)

    if visibility is not None:
        stmt = stmt.where(Collection.visibility == visibility)

    collections = db.exec(stmt).all()
    visible = [c for c in collections if user_can_access_collection(current_user, c)]

    result: List[CollectionOut] = []
    for c in visible:
        result.append(
            CollectionOut(
                id=c.id,
                tenant_id=c.tenant_id,
                organization_id=c.organization_id,
                name=c.name,
                doc_count=0,
                visibility=c.visibility,
                allowed_roles=c.allowed_roles,
                allowed_user_ids=c.allowed_user_ids,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return result
