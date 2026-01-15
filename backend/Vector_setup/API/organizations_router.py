from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from Vector_setup.user.db import DBUser, Tenant, Organization, get_db
from Vector_setup.schema.schema_signature import OrganizationCreateIn, OrganizationOut
from Vector_setup.user.auth_jwt import ensure_tenant_active
from Vector_setup.user.auth_store import get_current_db_user
from Vector_setup.user.roles import ORG_ADMIN_ROLES

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _ensure_org_admin(user: DBUser) -> None:
    if user.role not in ORG_ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to manage organizations.",
        )


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    body: OrganizationCreateIn,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
    tenant: Tenant = Depends(ensure_tenant_active),
):
    """
    Create an organization (umbrella or subsidiary) for a tenant.
    Only group_admin / group_exec can create.
    """
    print("BODY:", body)
    _ensure_org_admin(current_user)

    # Tenant isolation
    if body.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create organizations for this tenant.",
        )

    tenant_row = db.get(Tenant, body.tenant_id)
    if not tenant_row:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    if body.parent_id:
        parent = db.get(Organization, body.parent_id)
        if not parent or parent.tenant_id != body.tenant_id:
            raise HTTPException(status_code=400, detail="Invalid parent_id for tenant.")

    org_id = str(uuid.uuid4())
    org = Organization(
        id=org_id,
        tenant_id=body.tenant_id,
        name=body.name,
        type=body.type,
        parent_id=body.parent_id,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    return OrganizationOut(
        id=org.id,
        tenant_id=org.tenant_id,
        name=org.name,
        type=org.type,
        parent_id=org.parent_id,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


@router.get("", response_model=List[OrganizationOut])
def list_organizations_for_current_tenant(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
):
    """
    List all organizations for the current user's tenant.
    """
    stmt = select(Organization).where(Organization.tenant_id == current_user.tenant_id)
    rows = db.exec(stmt).all()

    return [
        OrganizationOut(
            id=o.id,
            tenant_id=o.tenant_id,
            name=o.name,
            type=o.type,
            parent_id=o.parent_id,
            created_at=o.created_at,
            updated_at=o.updated_at,
        )
        for o in rows
    ]
