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

import logging
logger = logging.getLogger(__name__)

def user_can_access_collection(
    user: DBUser,
    collection: Collection,
) -> bool:
   
    logger.info("DBG access check start",
               user_id=str(user.id), user_role=user.role,
               user_tenant_id=user.tenant_id,
               user_org_id=user.organization_id,
               coll_tenant_id=collection.tenant_id,
               coll_vis=collection.visibility,
               coll_roles=_to_list(collection.allowed_roles),
               coll_user_ids=_to_list(collection.allowed_user_ids))
   
     # 1) Tenant isolation (hard gate)
    if collection.tenant_id != user.tenant_id:
        logger.info("DBG denied: tenant mismatch")
        return False

    # 2) Normalize ACL fields once
    roles = _to_list(collection.allowed_roles)
    user_ids = _to_list(collection.allowed_user_ids)

    explicit_acl_allow = str(user.id) in user_ids or user.roles in roles
    logger.info("DBG explicity ACL", allow=explicit_acl_allow, user_id=str(user.id),
                roles=roles)
    

    # 3) User-scoped collections: private to specific users, regardless of role bucket
    if collection.visibility == CollectionVisibility.user:
        result = str(user.id) in user_ids
        logger.info("DBG user vis", result=result)
        return result

    # 4) Highest, umbrella company-wide roles
    if user.role in SUPER_ROLES:
        # Super roles can see all collections in their tenant
        # (can be tightened later if required)
        logger.info("DBG super role allow")
        return True

    # 5) Group roles (org-scoped, role-based, e.g. group_hr, group_admin)
    if user.role in GROUP_ROLES:
        # Org-scoped: same org + role allowed No ACL check for this user
        if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
            result = (user.organization_id is not None and 
                      user.organization_id == collection.organization_id and
                      user.role in roles)
            logger.info("DBG group role", result=result)
            return result
        logger.info("DBG group denied: vis")
        return False

     
    
    # 6) sub roles: Prioritize ACL First
    if user.role in SUB_ROLES:
        if explicit_acl_allow:
            logger.info("DBG sub ACL allow")
            return True # Explicit wins over org check
        
        # Tenant-wide: only if their role is explicitly allowed
        if collection.visibility == CollectionVisibility.tenant:
            logger.info("DBG sub Tenant no ACL")
            # Only via ACL, not automatic
            return False
        

        # Org-scoped or role-scoped collections:
        if collection.visibility in (CollectionVisibility.org, CollectionVisibility.role):
            result = (user.organization_id is not None and 
                      user.organization_id == collection.organization_id)
            logger.info("DBG sub org check", result=result)
            return result
           
            
        logger.info("DBG sub denied: vis")
        return False

    # 7) Any other / unknown role -> deny by default
    logger.info("DBG unknown role deny")
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

        
   

       
    
  
  
    