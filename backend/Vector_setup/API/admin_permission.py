
from fastapi import Depends, HTTPException, status
from Vector_setup.user.auth_jwt import get_current_user
from Vector_setup.base.auth_models import UserOut

# Permission/Access authentication dependencies would be defined elsewhere
ALLOWED_ADMIN_ROLES = {"hr", "executive", "management", "vendor"}

def require_user_admin(user: UserOut = Depends(get_current_user)) -> UserOut:
    if user.role not in ALLOWED_ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user 