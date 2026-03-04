
from Vector_setup.base.db_setup_management import (
    MultiTenantChromaStoreManager,
    CompanyProvisionRequest,
    CompanyCreateRequest,
)
from Vector_setup.schema.schema_signature import CompanyOut

from Vector_setup.user.db import get_db, DBUser, Tenant, Collection, Organization
from Vector_setup.user.auth_jwt import ensure_tenant_active, get_current_user
from Vector_setup.base.auth_models import UserOut
from datetime import datetime, timedelta
from Vector_setup.user.db import get_db, Tenant
from fastapi import APIRouter, Depends,  HTTPException, status
from Vector_setup.base.vector_store import get_store
from Vector_setup.user.roles import COLLECTION_MANAGE_ROLES, VENDOR_ROLES, VENDOR_ROLES
from sqlmodel import Session, select
from typing import List
from Vector_setup.schema.schema_signature import CollectionOut, OrganizationOut
from Vector_setup.access.collections_acl import user_can_access_collection
from Vector_setup.user.auth_store import  get_current_db_user

import logging

logger = logging.getLogger(__name__)


router = APIRouter()

# ---------- Role helpers ----------
def require_vendor(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    if current_user.role not in VENDOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendor can perform this action.",
        )
    return current_user


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
    tenant_id = req.tenant_id.replace(" ", "-").lower()  # sanitize tenant_id for Chroma collection naming
    # 1) Ensure Tenant exisits in SQL
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        now = datetime.utcnow()
        tenant = Tenant(
            id = tenant_id,
            name = req.name or tenant_id,  # ← ensure non-null
            plan = req.plan,
            subscription_status=req.subscription_status,
            trial_ends_at=now + timedelta(days=60),
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # 2) Configure in Chroma 
    result =store.provision_company_space(
        CompanyProvisionRequest(tenant_id=tenant_id)
    )

    return CompanyOut(
        tenant_id=tenant.id,
        display_name=tenant.name,
        created_at=tenant.created_at,
        plan=tenant.plan,
        subscription_status=tenant.subscription_status,
        trial_ends_at=tenant.trial_ends_at,
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