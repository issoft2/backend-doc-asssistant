
from fastapi import Depends, HTTPException, status
from Vector_setup.user.auth_jwt import get_current_user
from Vector_setup.base.auth_models import UserOut
from typing import Annotated


# Permission/Access authentication dependencies would be defined elsewhere
ALLOWED_ADMIN_ROLES = {"hr", "executive", "management", "vendor"}

def require_tenant_admin(user: UserOut = Depends(get_current_user)) -> UserOut:
    if user.role not in ALLOWED_ADMIN_ROLES:
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


AdminRoles = {"hr", "executive", "management", "vendor", "admin"}

def require_tenant_admin(
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> UserOut:
    role = (current_user.role or "").lower()
    if role not in AdminRoles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user
 