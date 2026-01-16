from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from Vector_setup.user.db import DBUser, Tenant, Organization, get_db
from Vector_setup.schema.schema_signature import OrganizationCreateIn, OrganizationOut, OrganizationUpdate
from Vector_setup.user.auth_jwt import ensure_tenant_active
from Vector_setup.user.auth_store import get_current_db_user
from Vector_setup.user.roles import ORG_MANAGER_ROLES
from Vector_setup.user.permissions import is_sub_role, is_group_role

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _ensure_org_admin(user: DBUser) -> None:
    if user.role not in ORG_MANAGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to manage organizations.",
        )


def require_org_manager(current_user: DBUser = Depends(get_current_db_user)) -> DBUser:
    # Only allow non-sub_* elevated roles to manage organizations
    if current_user.role.startswith("sub_") or current_user.role not in ORG_MANAGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to manage organizations.",
        )
    return current_user


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    body: OrganizationCreateIn,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(require_org_manager),
    # tenant: Tenant = Depends(ensure_tenant_active),
):
 
    # Tenant isolation
    target_tenant_id = body.tenant_id or current_user.tenant_id

    if current_user.role != "vendor" and target_tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create organizations for this tenant.",
        )

    tenant_row = db.get(Tenant, body.tenant_id)
    if not tenant_row:
        raise HTTPException(status_code=404, detail="Tenant not found.")


    org_id = str(uuid.uuid4())
    org = Organization(
        id=org_id,
        tenant_id=body.tenant_id,
        name=body.name,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    return OrganizationOut(
        id=org.id,
        tenant_id=org.tenant_id,
        name=org.name,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )



@router.get("", response_model=List[OrganizationOut])
def list_organizations(
    tenant_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
):
    """
    List organizations.

    - Non-vendor: always scoped to their own tenant; ignores tenant_id param.
    - Vendor: can pass tenant_id to view orgs for that tenant.
    - sub_* within the effective tenant, only see their own org.
    """
    # non‑vendor: always own tenant
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

    # Base filter: tenant
    stmt = select(Organization).where(Organization.tenant_id == effective_tenant_id)
    
    # 3 Org filter for sub_* roles
    if is_sub_role(current_user.role):
        if current_user.organization_id is None:
            # no org -> orgs visible
            stmt = stmt.where(False)
            
        else:
            stmt = stmt.where(Organization.id == current_user.organization_id)
                
    rows = db.exec(stmt).all()

    return [
        OrganizationOut(
            id=o.id,
            tenant_id=o.tenant_id,
            name=o.name,
            created_at=o.created_at,
            updated_at=o.updated_at,
        )
        for o in rows
    ]


@router.put("/{org_id}", response_model=OrganizationOut)
def update_organization(
    org_id: str,
    body: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(require_org_manager),
):
    org = db.get(Organization, org_id)
    if not org or org.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.name = body.name or org.name
    db.add(org)
    db.commit()
    db.refresh(org)
    return OrganizationOut.from_orm(org)


@router.delete("/{org_id}", status_code=204)
def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(require_org_manager),
):
    org = db.get(Organization, org_id)
    if not org or org.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Organization not found")

    db.delete(org)
    db.commit()
