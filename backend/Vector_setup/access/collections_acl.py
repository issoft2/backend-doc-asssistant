from Vector_setup.user.db import DBUser, Collection, CollectionVisibility
from Vector_setup.user.roles import GROUP_ROLES, SUB_ROLES, SUPER_ROLES

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
    # 1) Tenant isolation (hard gate)
    if collection.tenant_id != user.tenant_id:
        return False

    # 2) Normalize ACL fields once
    roles = _to_list(collection.allowed_roles)
    user_ids = _to_list(collection.allowed_user_ids)
    
    # 3 User-coped collections: private to specific users, regardles of role bucket
    if collection.visibility == CollectionVisibility.user:
        return str(user.id) in user_ids
    
    # 4 Highest, Unbrella Company-wide roles
    if user.role in SUPER_ROLES:
        # Supper ROLES can see all collections in their tenant
        # It can be tightened late if required
        return True
    
    # 5 Group-role (org-scoped, role-based), have oversight of what is happening in the
    # sub company wide.
    if user.role in GROUP_ROLES:
        # org-scoped: same org + role allowed
        if collection.visibility == CollectionVisibility.org:
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role in roles
            )
            
        # Role-scoped: same org + role allowed
        if collection.visibility == CollectionVisibility.role:
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role in roles
            )
            
        
        # Group roles do Not automatically get tenant-wide access
        if collection.visibility == CollectionVisibility.tenant:
            return False
        
        # Any other visibility value
        return False
    
    # 6 subsidiary / normal users (sub-roles)
    if user.role in SUB_ROLES:
        # Tenant-wide: only if their role is explicitly allowed, I don't think I need this
        if collection.visibility == CollectionVisibility.tenant:
            return user.role in roles
        
        # Org-scoped: same org + allowed
        if collection.visibility == CollectionVisibility.org:
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role in roles
            )
            
        # Role-scoped: same as org + role allowed
        if collection.visibility == CollectionVisibility.role:
            return (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
                and user.role in roles
            ) 
         
        return False # defensive fallback
    
    # 7 Any other / unknown role -> deny by default
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

        
   

       
    
  
  
    