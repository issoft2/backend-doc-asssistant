from Vector_setup.user.db import DBUser, Collection, CollectionVisibility
from Vector_setup.user.roles import GROUP_ROLES, SUB_ROLES

from sqlmodel import Session, select, List



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

def user_can_access_collection(
    user: DBUser,
    collection: Collection,
) -> bool:
    # Tenant isolation (hard gate)
    if collection.tenant_id != user.tenant_id:
        return False
    
    #2  Group-wide roles (umbrella)
    if user.role in GROUP_ROLES:
        if collection.visibility == CollectionVisibility.role:
            roles = collection.allowed_roles or []
            return user.role in roles
        
        if collection.visibility == CollectionVisibility.user:
            user_ids = collection.allowed_user_ids or []
            return str(user.id) in user_ids
        
        # Tenant / org visibilities are fine for group roles
        return True
    
    # 3 Subsidiary / normal users
    if user.role in SUB_ROLES:
        # Tenant-wide collection
        if collection.visibility == CollectionVisibility.tenant:
            return True
        
        # Org-scoped collection
        if collection.visibility == CollectionVisibility.org:
            return (
                user.Organization_id is not None
                and user.Organization_id == collection.organization_id
            )
        
         # Role-scoped collection
        if collection.visibility == CollectionVisibility.role:
            roles = collection.allowed_roles or []
            if user.Organization_id != collection.organization_id:
                return False
            return user.role in roles   
        
        # User-scoped collection
        if collection.visibility == CollectionVisibility.user:
            user_ids = collection.allowed_user_ids or []
            return str(user.id) in user_ids 
       
        
    # 4 Any other / unknown role -> deny by default
    return False



def get_allowed_collections_for_user(
    db: Session,
    user: DBUser,
    requested_names: Optional[List[str]] = None,
) -> List[Collection]:
    stmt = select(Collection).where(Collection.tenant_id == user.tenant_id)
    if requested_names:
        stmt = stmt.where(Collection.name.in_(requested_names))

    collections = db.exec(stmt).all()
    return [
        c for c in collections
        if user_can_access_collection(user, c)
    ]
    

        
    
    
    