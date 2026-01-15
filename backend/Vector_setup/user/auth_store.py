# auth_store.py
from sqlmodel import Session, select
from  Vector_setup.base.auth_models  import UserCreate, UserInDB, LoginRequestTenant
from .db import DBUser, FirstLoginToken, Organization,  get_db
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import secrets, hashlib
from Vector_setup.user.password import get_password_hash
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
import os  # ← add this




# This must match your login endpoint path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "CHANGE_ME_SUPER_SECRET") # "CHANGE_ME_IN_PROD"
ALGORITHM = "HS256"


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

def create_user(data: UserCreate, db: Session) -> UserInDB:
    user_id = str(uuid.uuid4())
    
    # Optionally validate that organization belongs to the same tenant
    org = db.get(Organization, data.organization_id)
    if not org or org.tenant_id != data.tenant_id:
        raise HTTPException(status_code=400, detail="Invalid organization for tenant")
    
    
    db_user = DBUser(
        id=user_id,
        email=data.email,
        tenant_id=data.tenant_id,
        organization_id=data.organization_id,
        hashed_password=get_password_hash((data.password or "")[:64]),
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=data.date_of_birth,
        phone=data.phone,
        role=data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user  # UserInDB(id=db_user.id, email=db_user.email, tenant_id=db_user.tenant_id, hashed_password=db_user.hashed_password, first_name=db_user.first_name, last_name=db_user.last_name, date_of_birth=db_user.date_of_birth, phone=db_user.phone, role=db_user.role)


def create_first_login_token(db: Session, user: UserInDB ) -> str:
    """
     Create a single-use first-time login token for a user.
     Returns the RAW token (for emailing). stores only the hash.
    """
    id = str(uuid.uuid4())
    raw_token = secrets.token_urlsafe(32)
    token_hash = get_password_hash((raw_token or "")[:64]) 
    expires_at = datetime.utcnow() + timedelta(hours=24)
    first_token =  FirstLoginToken(
        id=id,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(first_token)
    db.commit()
    db.refresh(first_token)
    
    return raw_token

def get_users_by_email(email: str, db: Session) -> list[DBUser]:
    stmt = select(DBUser).where(DBUser.email == email)
    return list(db.exec(stmt).all())


def get_user_by_email(
    email: str,
    tenant_id: str,
    db: Session
) -> UserInDB | None:
    
    stmt = (
        select(DBUser)
        .where(DBUser.email == email)
        .where(DBUser.tenant_id == tenant_id)
    )
    db_user = db.exec(stmt).first()
    
    if not db_user:
        return None
    
    return UserInDB(
        id=db_user.id,
        email=db_user.email,
        tenant_id=db_user.tenant_id,
        hashed_password=db_user.hashed_password,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        date_of_birth=db_user.date_of_birth,
        phone=db_user.phone,
        role=db_user.role,
        is_active=db_user.is_active
    )

def login_tenant_request(
    body: LoginRequestTenant,
    db: Session
):
    # Make sure this email has a row for this tenant and is active
    stmt = (
        select(DBUser)
        .where(DBUser.email == body.email)
        .where(DBUser.tenant_id == body.tenant_id)
    )
    db_user = db.exec(stmt).first()
    if not db_user or not db_user.is_active:
         return None
    return db_user

def get_db_user_by_email(
    email: str,
    tenant_id: str,
    db: Session,
) -> DBUser | None:
    stmt = (
        select(DBUser)
        .where(DBUser.email == email)
        .where(DBUser.tenant_id == tenant_id)
    )
    return db.exec(stmt).first()


from Vector_setup.user.roles import UPLOAD_ROLES

def require_uploader(current_user: DBUser = Depends(get_current_db_user)) -> DBUser:
    if current_user.role not in UPLOAD_ROLES:
        raise HTTPException(status_code=403, detail="Not allowed to upload documents.")
    return current_user
    