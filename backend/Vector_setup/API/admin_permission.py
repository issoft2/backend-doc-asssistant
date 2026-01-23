
from fastapi import Depends, HTTPException, status
from Vector_setup.user.auth_jwt import get_current_user
from Vector_setup.base.auth_models import UserOut
from typing import Annotated
from Vector_setup.user.roles import USER_CREATOR_ROLES, COLLECTION_MANAGE_ROLES

# Permission/Access authentication dependencies would be defined elsewhere
def require_user_admin(user: UserOut = Depends(get_current_user)) -> UserOut:
    if user.role not in USER_CREATOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    if not user.is_active:  # or current_user.disabled / status check
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your Account has been disabled!",
        )    
    return user



def require_tenant_admin(
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> UserOut:
    role = (current_user.role or "").lower()
    if role not in COLLECTION_MANAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user
 