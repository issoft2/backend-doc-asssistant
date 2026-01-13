#!/usr/bin/env python3

from datetime import datetime


from pydantic import BaseModel
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from .auth_store import get_user_by_email, get_db_user_by_email
from Vector_setup.base.auth_models import UserOut
from .db import DBUser, Tenant, get_db
import os
from sqlmodel import Session


SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "CHANGE_ME_SUPER_SECRET") # "CHANGE_ME_IN_PROD"
ALGORITHM = "HS256"

# This must match your login endpoint path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")



class TokenUser(BaseModel):
    email: str
    tenant_id: str

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        tenant_id: str | None = payload.get("tenant_id")
        if email is None or tenant_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # now pass db into get_user_by_email
    user = get_user_by_email(email, tenant_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserOut(
        id=user.id,
        email=user.email,
        tenant_id=tenant_id,
        first_name=user.first_name,
        last_name=user.last_name,
        date_of_birth=user.date_of_birth,
        phone=user.phone,
        role=user.role,
        )


async def get_current_user_from_header_or_query(
    request: Request,
) -> TokenUser:
    # 1) Try Authorization header (existing behavior)
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]
        return get_current_user(token)

    # 2) Fallback: token from query param
    token = request.query_params.get("token")
    if token:
        return decode_and_get_user(token)

    raise HTTPException(status_code=401, detail="Not authenticated")

def decode_and_get_user(token: str) -> TokenUser:
    """
    Decode a JWT string and return a TokenUser.
    Used when token is passed via query param instead of Authorization header.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        tenant_id: str | None = payload.get("tenant_id")
        if email is None or tenant_id is None:
            raise  HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                
            )
            
        return TokenUser(email=email, tenant_id=tenant_id)
    
    except ExpiredSignatureError:
        # token is structurally OK but expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except JWTError as e:
        # signature mismatch, malformed, wrong algorithm, etc.
        print("JWT decode error:", repr(e))  # TEMP: see logs
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )
   
   
def get_current_tenant(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Tenant:
    tenant = db.get(Tenant, current_user.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=400,
            detail="Tenant not found"
        )
    return tenant

def ensure_tenant_active(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),

) -> Tenant:
    # Vendor bypass sunscription/trial checks
    if current_user.role == "vendor":
        return tenant
    
    now = datetime.utcnow()
    if (
        tenant.subscription_status == "trialing"
        and tenant.trial_ends_at 
        and tenant.trial_ends_at < now
    ):
        tenant.subscription_status = "expired"
        db.add(tenant)
        db.commit()
        raise HTTPException(
            status_code=402,
            detail="Trial expired. Please contact support.",
        )
        
    if tenant.subscription_status in ("expired", 'canceled'):
        raise HTTPException(
            status_code=402,
            detail="Subscription inactive."
        )
        
    return tenant               


async def get_current_db_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        tenant_id: str | None = payload.get("tenant_id")
        if email is None or tenant_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_db_user_by_email(email, tenant_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user  # this is DBUser

def ensure_tenant_active_by_id(
    tenant_id: str,
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=400,
            detail="Tenant not found",
        )

    now = datetime.utcnow()
    if (
        tenant.subscription_status == "trialing"
        and tenant.trial_ends_at
        and tenant.trial_ends_at < now
    ):
        tenant.subscription_status = "expired"
        db.add(tenant)
        db.commit()
        raise HTTPException(
            status_code=402,
            detail="Trial expired. Please contact support.",
        )

    if tenant.subscription_status in ("expired", "canceled"):
        raise HTTPException(
            status_code=402,
            detail="Subscription inactive.",
        )

    return tenant
