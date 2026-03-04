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


# def user_can_access_collection(
#     user: DBUser,
#     collection: Collection,
# ) -> bool:
   
#      # 1) Tenant isolation (hard gate)
#     if collection.tenant_id != user.tenant_id:
#         return False

#     # 2) Normalize ACL fields once
#     roles = _to_list(collection.allowed_roles)
#     user_ids = _to_list(collection.allowed_user_ids)
#     explicit_acl_allow = str(user.id) in user_ids or user.role in roles


#     # 3) User-scoped collections: private to specific users, regardless of role bucket
#     if collection.visibility == CollectionVisibility.user:
#         return str(user.id) in user_ids

#     # 4) Highest, umbrella company-wide roles
#     if user.role in SUPER_ROLES:
#         # Super roles can see all collections in their tenant
#         # (can be tightened later if required)
#         return True

#     # 5) Group roles (org-scoped, role-based, e.g. group_hr, group_admin)
#     if user.role in GROUP_ROLES:
#         # Org-scoped: same org + role allowed No ACL check for this user
#         if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
#             return (
#                 user.organization_id is not None
#                 and user.organization_id == collection.organization_id
#             )

#         # Group roles do NOT automatically get tenant-wide access
#         if collection.visibility == CollectionVisibility.tenant:
#             return False

#         # Any other visibility value
#         return False
    
#     # 6) Subsidiary / normal users (sub-roles, e.g. sub_hr)
#     if user.role in SUB_ROLES:
#         # Tenant-wide: only if their role is explicitly allowed
#         if collection.visibility == CollectionVisibility.tenant:
#             # Only via ACL, not automatic
#             return explicit_acl_allow
        

#         # Org-scoped or role-scoped collections:
#         if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
#             # First: explicit ACL
#             if explicit_acl_allow:
#                 return True
            
#             # Then: org-wide default for sub_* in their own org
#             if (
#                 user.organization_id is not None
#                 and user.organization_id == collection.organization_id
#                 and user.role.startswith("sub_")
#             ):
#                 return True
            
#             return False
        
#         return False

#     # 7) Any other / unknown role -> deny by default
#     return False

def user_can_access_collection(
    user: DBUser,
    collection: Collection,
) -> bool:

    print(f"ACL | user={user.email} role={user.role} org={user.organization_id} tenant={user.tenant_id}", flush=True)
    print(f"ACL | collection={collection.name} vis={collection.visibility} org={collection.organization_id} tenant={collection.tenant_id}", flush=True)

    # ── 1) Tenant isolation ───────────────────────────────────────────────
    if collection.tenant_id != user.tenant_id:
        print("ACL | DENIED — tenant mismatch", flush=True)
        return False

    roles    = _to_list(collection.allowed_roles)
    user_ids = _to_list(collection.allowed_user_ids)
    explicit_acl_allow = str(user.id) in user_ids or user.role in roles

    print(f"ACL | allowed_roles={roles} allowed_user_ids={user_ids} explicit={explicit_acl_allow}", flush=True)

    if collection.visibility == CollectionVisibility.user:
        print(f"ACL | user-vis path → {str(user.id) in user_ids}", flush=True)
        return str(user.id) in user_ids

    if user.role in SUPER_ROLES:
        print("ACL | ALLOWED — super role", flush=True)
        return True

    if user.role in GROUP_ROLES:
        print(f"ACL | group role path | vis={collection.visibility}", flush=True)
        if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
            result = (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
            )
            print(f"ACL | org check → user_org={user.organization_id} col_org={collection.organization_id} result={result}", flush=True)
            return result
        print("ACL | DENIED — group role, wrong visibility", flush=True)
        return False

    if user.role in SUB_ROLES:
        print("ACL | sub role path", flush=True)
        if collection.visibility == CollectionVisibility.tenant:
            return explicit_acl_allow
        if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
            if explicit_acl_allow:
                return True
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role.startswith("sub_")
            )
        return False

    if user.role == "employee":
        return explicit_acl_allow

    print(f"ACL | DENIED — unknown role {user.role}", flush=True)
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

        
   

       
    
  
  
    