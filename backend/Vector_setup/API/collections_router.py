from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
import json

from Vector_setup.user.db import DBUser, Tenant, Collection, Organization, get_db
from Vector_setup.user.auth_jwt import ensure_tenant_active
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager, CollectionCreateRequest
from Vector_setup.schema.schema_signature import (
    CollectionCreateIn,
    CollectionOut,
    CollectionUpdateIn,
    CollectionAccessOut,
    CollectionAccessUpdate,
)
from Vector_setup.user.audit import write_audit_log
from Vector_setup.user.roles import COLLECTION_MANAGE_ROLES
from Vector_setup.access.collections_acl import user_can_access_collection
from Vector_setup.user.auth_store import get_current_db_user

vector_store = MultiTenantChromaStoreManager("./chromadb_multi_tenant")

def get_store() -> MultiTenantChromaStoreManager:
    return vector_store

router = APIRouter(prefix="/collections", tags=["collections"])


# turn this into a dependency helper
def _ensure_collection_admin(
    user: DBUser = Depends(get_current_db_user),
) -> DBUser:
    if user.role not in COLLECTION_MANAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to manage collections.",
        )
    return user


@router.post("/create", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
def create_collection(
    body: CollectionCreateIn,
    db: Session = Depends(get_db),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    current_user: DBUser = Depends(_ensure_collection_admin),
    tenant: Tenant = Depends(ensure_tenant_active),
):
    """
    Create a new collection for a tenant with ACL fields.
    Only collection admins (group_admin/group_exec/sub_admin/sub_md) can create.
    """
    # current_user already validated as collection admin

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

    tenant_row = db.get(Tenant, body.tenant_id)
    if not tenant_row:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    if body.organization_id:
        org = db.get(Organization, body.organization_id)
        if not org or org.tenant_id != body.tenant_id:
            raise HTTPException(status_code=400, detail="Invalid organization_id for tenant.")

    stmt = (
        select(Collection)
        .where(Collection.tenant_id == body.tenant_id)
        .where(Collection.organization_id == body.organization_id)
        .where(Collection.name == body.name)
    )
    existing = db.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="Collection name already exists for this tenant.")

    collection_id = str(uuid.uuid4())
    db_collection = Collection(
        id=collection_id,
        tenant_id=body.tenant_id,
        organization_id=body.organization_id,
        name=body.name,
        visibility=body.visibility,
        allowed_roles=body.allowed_roles,
        allowed_user_ids=body.allowed_user_ids,
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)

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
    if current_user.role != "vendor":
        effective_tenant_id = current_user.tenant_id
    else:
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
        roles = json.loads(c.allowed_roles) if c.allowed_roles else []
        user_ids = json.loads(c.allowed_user_ids) if c.allowed_user_ids else []
        result.append(
            CollectionOut(
                id=c.id,
                tenant_id=c.tenant_id,
                organization_id=c.organization_id,
                name=c.name,
                doc_count=0,
                visibility=c.visibility,
                allowed_roles=roles,
                allowed_user_ids=user_ids,
                created_at=c.created_at,
            )
        )
    return result


@router.get("/{collection_id}/access", response_model=CollectionAccessOut)
def get_collection_access(
    collection_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(_ensure_collection_admin),
):
    col = db.get(Collection, collection_id)
    if not col or col.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Collection not found")

    user_ids = json.loads(col.allowed_user_ids) if col.allowed_user_ids else []
    user_roles = json.loads(col.allowed_roles) if col.allowed_roles else []

    # if you keep the model_validator that forbids both empty,
    # ensure at least one side is non-empty or relax that validator
    return CollectionAccessOut(allowed_user_ids=user_ids, allowed_roles=user_roles)


@router.put("/{collection_id}/access", status_code=204)
def update_collection_access(
    collection_id: str,
    body: CollectionAccessUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(_ensure_collection_admin),
):
    col = db.get(Collection, collection_id)
    if not col or col.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Collection not found")

    col.allowed_user_ids = json.dumps([str(uid) for uid in body.allowed_user_ids])
    col.allowed_roles = json.dumps([str(role) for role in body.allowed_roles])
    db.add(col)
    db.commit()
    write_audit_log(
        db=db,
        user=current_user,
        action="collection_access_update",
        resource_type="collection",
        resource_id=db.id,
        metadata={
            "tenant_id": db.tenant_id,
            "name": db.name,
            "visibility": str(db.visibility),
            "organization_id": db.organization_id,
        },
    )
    return


@router.get("/by-org", response_model=list[CollectionOut])
def list_collections_for_org(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
):
    stmt = (
        select(Collection)
        .where(Collection.tenant_id == current_user.tenant_id)
        .where(Collection.organization_id == current_user.organization_id)
    )
    rows = db.exec(stmt).all()
    return [
        CollectionOut(
            id=c.id,
            tenant_id=c.tenant_id,
            organization_id=c.organization_id,
            name=c.name,
            doc_count=c.doc_count,
            visibility=c.visibility,
            allowed_roles=json.loads(c.allowed_roles) if c.allowed_roles else [],
            allowed_user_ids=json.loads(c.allowed_user_ids) if c.allowed_user_ids else [],
            created_at=c.created_at,
        )
        for c in rows
    ]


