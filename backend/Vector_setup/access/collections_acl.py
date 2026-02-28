from Vector_setup.user.db import DBUser, Collection, CollectionVisibility
from Vector_setup.user.roles import GROUP_ROLES, SUB_ROLES, SUPER_ROLES
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from sqlmodel import Session, select
from typing import List, Optional  


GROUP_ROLES = {
    "group_gmd",
    "group_exe",
    "group_hr",
    "group_admin",
    "group_finance",
    "group_operation",
    "group_production",
    "group_marketing",
    "group_legal",
}

SUB_ROLES = {
    "sub_md",
    "sub_exec",
    "sub_admin",
    "sub_operations",
    "sub_hr",
    "sub_finance",
    "sub_production",
    "sub_legal",
    "sub_marketing",
    "employee",
}

import json



def _to_list(value):
    """Normalize DB field (None / JSON string / list) into a Python list."""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return value


def user_can_access_collection(
    user: DBUser,
    collection: Collection,
) -> bool:
    """
    Determines whether a user has access to a given collection.

    Access hierarchy (evaluated in order):
        1. Tenant isolation       — hard wall, cross-tenant always denied
        2. User-scoped visibility — private, explicit user ID required
        3. SUPER_ROLES            — full tenant access
        4. GROUP_ROLES            — full tenant access
        5. SUB_ROLES              — tenant + org-scoped access
        6. employee               — explicit ACL only (no visibility grants)
        7. Default                — deny
    """

    # ── 1) Tenant Isolation (Hard Wall) ───────────────────────────────────
    # Cross-tenant access is never permitted regardless of role.
    if collection.tenant_id != user.tenant_id:
        return False

    # ── 2) Normalize ACL fields ───────────────────────────────────────────
    # Handles stored formats: comma string, JSON array, or Python list.
    roles    = _to_list(collection.allowed_roles)
    user_ids = _to_list(collection.allowed_user_ids)
    explicit_acl_allow = str(user.id) in user_ids or user.role in roles

    # ── 3) User-Scoped Collections (Private) ──────────────────────────────
    # Strictly private — only explicitly listed user IDs may access.
    # No role override, including SUPER/GROUP roles.
    if collection.visibility == CollectionVisibility.user:
        return str(user.id) in user_ids

    # ── 4) Super Roles (Full Tenant Access) ───────────────────────────────
    # Admins/superadmins see everything within their tenant.
    if user.role in SUPER_ROLES:
        return True

    # ── 5) Group Roles (Tenant Leadership) ────────────────────────────────
    # Group managers/leads see all non-private collections within the tenant.
    if user.role in GROUP_ROLES:
        return True

    # ── 6) Sub Roles (Org-Scoped Access) ──────────────────────────────────
    # Explicit ACL always wins first.
    # Beyond that: tenant-wide and same-org collections are accessible.
    if user.role in SUB_ROLES:
        if explicit_acl_allow:
            return True

        if collection.visibility == CollectionVisibility.tenant:
            return True

        if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
            )

        return False

    # ── 7) Employee (Explicit ACL Only) ───────────────────────────────────
    # Employees have zero visibility-based access.
    # The ONLY way in is being listed in allowed_user_ids or allowed_roles.
    if user.role == "employee":
        return explicit_acl_allow

    # ── 8) Unknown Role → Deny ────────────────────────────────────────────
    # Any role not explicitly handled above is denied by default.
    return False





def get_allowed_collections_for_user(
    db: Session,
    user: DBUser,
    requested_name: Optional[List[str]] = None,
) -> List[Collection]:
    # 1) Tenant boundary in SQL
    stmt = select(Collection).where(Collection.tenant_id == user.tenant_id)

    # 2) Optional name filter
    if requested_name:
        stmt = stmt.where(Collection.name.in_(requested_name))

    rows: List[Collection] = db.exec(stmt).all()

    # 3) Per-collection ACL in Python
    return [c for c in rows if user_can_access_collection(user, c)]

        
   

       
    
  
  
    