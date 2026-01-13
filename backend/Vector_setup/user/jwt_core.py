# jwt_core.py
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from sqlmodel import Session

from Vector_setup.user.password import verify_password
from .auth_store import  get_users_by_email
from Vector_setup.base.auth_models import  UserInDB
from .db import DBUser
import os



SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "CHANGE_ME_SUPER_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Put at least: {"sub": user.email, "tenant_id": user.tenant_id}
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(
    email: str,
    password: str,
    db: Session,
) -> tuple[UserInDB, list[DBUser]] | None:
    users = get_users_by_email(email, db)
    if not users:
        return None

    ref = users[0]
    if not verify_password(password, ref.hashed_password):
        return None

    return UserInDB.from_orm(ref), users
