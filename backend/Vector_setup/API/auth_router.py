from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlmodel import Session

from Vector_setup.base.auth_models import UserCreate, UserOut, LoginRequestTenant
from Vector_setup.user.auth_store import create_user, get_user_by_email, login_tenant_request
from Vector_setup.user.auth_jwt import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from Vector_setup.user.db import get_db
from Vector_setup.user.auth_jwt import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserOut)
def read_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.post("/signup", response_model=UserOut)
def signup(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
) -> UserOut:
     # 1) Block employees completely
    if current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees are not allowed to create users",
        )

    # 2) Vendor can create for any tenant; other roles only for their own tenant
    if current_user.role != "vendor" and user_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create user for this tenant",
        )

    # 3) Check email uniqueness
    existing = get_user_by_email(user_in.email, user_in.tenant_id, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = create_user(user_in, db)
    return UserOut(id=user.id, email=user.email, tenant_id=user.tenant_id, role=user.role)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # form_data.username holds the email
    auth_result = authenticate_user(form_data.username, form_data.password, db)
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
    user, tenant_rows = auth_result    
    # 👇 block deactivated users
    if not user.is_active:  # or user.disabled, or user.status == "inactive"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your Account has been disabled!",
        )
        
    # Distinct tenant ids from rows
    tenant_ids = {row.tenant_id for row in tenant_rows}
    
    # Phase 2 not needed only one tenant
    if len(tenant_ids) == 1:
        tenant_id = next(iter(tenant_ids))

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "tenant_id": tenant_id},
            expires_delta=access_token_expires,
        )
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "requires_tenant_selection": False
        }
        
    # Phase needed: multiple tenants
    # Map to something frontend friendly (you likely have a company/Tenant table to join)
    return {
        "requires_tenant_selection": True,
        "tenants": [
            {"tenant_id": row.tenant_id, "role": row.role} for row in tenant_rows
        ],
    }
    
# Tenant login when the user select a tenant
@router.post("/login/tenant")
def login_tenant(
    body: LoginRequestTenant,
    db: Session = Depends(get_db),
):
    user = login_tenant_request(body, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this tenant",
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "tenant_id": user.tenant_id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}    