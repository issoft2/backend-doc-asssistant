#!/usr/bin/env python3

from datetime import datetime, timedelta
from typing import Optional


from pydantic import BaseModel
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from .auth_store import get_user_by_email
from Vector_setup.base.auth_models import UserOut
import os
from .password import verify_password
from sqlmodel import Session

from .db import get_db


SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "CHANGE_ME_SUPER_SECRET") # "CHANGE_ME_IN_PROD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# This must match your login endpoint path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Put at least: {\"sub\": user.email, \"tenant_id\": user.tenant_id}
    """
    print("DEBUG SECRET_KEY:", SECRET_KEY, type(SECRET_KEY))

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # [web:298]



def authenticate_user(email: str, password: str, db: Session):
    user = get_user_by_email(email, db)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


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
    user = get_user_by_email(email, db)
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
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )
   