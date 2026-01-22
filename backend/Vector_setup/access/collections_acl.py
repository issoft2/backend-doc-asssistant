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
    logger.info(
        "DEBUG user properties use can process collection"
        "user_id=%s role=%s org=%s collection_id=%s name=%s visibility=%s coll_org=%s "
        "allowed_roles=%s allowed_user_ids=%s",
        str(user.id),
        user.role,
        user.organization_id,
        str(collection.id),
        collection.name,
        str(collection.visibility),
        collection.organization_id,
        _to_list(collection.allowed_roles),
        _to_list(collection.allowed_user_ids),
    )
    # 1) Tenant isolation (hard gate)
    if collection.tenant_id != user.tenant_id:
        return False

    # 2) Normalize ACL fields once
    roles = _to_list(collection.allowed_roles)
    user_ids = _to_list(collection.allowed_user_ids)

    # 3) User-scoped collections: private to specific users, regardless of role bucket
    if collection.visibility == CollectionVisibility.user:
        return str(user.id) in user_ids

    # 4) Highest, umbrella company-wide roles
    if user.role in SUPER_ROLES:
        # Super roles can see all collections in their tenant
        # (can be tightened later if required)
        return True

    # 5) Group roles (org-scoped, role-based, e.g. group_hr, group_admin)
    if user.role in GROUP_ROLES:
        # Org-scoped: same org + role allowed
        if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role in roles
            )

        # Group roles do NOT automatically get tenant-wide access
        if collection.visibility == CollectionVisibility.tenant:
            return False

        # Any other visibility value
        return False

    # 6) Subsidiary / normal users (sub-roles, e.g. sub_hr)
    if user.role in SUB_ROLES:
        # Tenant-wide: only if their role is explicitly allowed
        if collection.visibility == CollectionVisibility.tenant:
            return user.role in roles

        # Org-scoped or role-scoped collections:
        if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
            # Auto-allow sub_* roles in their own org,
            # even if not explicitly listed in allowed_roles
            if (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role.startswith("sub_")
            ):
                return True

            # Fallback to explicit ACL (if you still want it)
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role in roles
            )
            
        # DEBUG: log decision
        logger.info(
                "DBG user_can_access_collection "
                f"user_id=%s role=%s org=%s collection_id=%s name=%s visibility=%s coll_org=%s "
                f"allowed_roles=%s allowed_user_ids=%s result=%s",
                str(user.id),
                user.role,
                user.organization_id,
                str(collection.id),
                collection.name,
                str(collection.visibility),
                collection.organization_id,
                _to_list(collection.allowed_roles),
                _to_list(collection.allowed_user_ids),
            )

        # Defensive fallback
        return False

    # 7) Any other / unknown role -> deny by default
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

        
   

       
    
  
  
    