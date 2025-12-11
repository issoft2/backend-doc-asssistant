# auth_store.py
from sqlmodel import Session, select
from  Vector_setup.base.auth_models  import UserCreate, UserInDB
from .password import get_password_hash 
from .db import DBUser
import uuid

def create_user(data: UserCreate, db: Session) -> UserInDB:
    user_id = str(uuid.uuid4())
    db_user = DBUser(
        id=user_id,
        email=data.email,
        tenant_id=data.tenant_id,
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
    return UserInDB(id=db_user.id, email=db_user.email, tenant_id=db_user.tenant_id, hashed_password=db_user.hashed_password, first_name=db_user.first_name, last_name=db_user.last_name, date_of_birth=db_user.date_of_birth, phone=db_user.phone, role=db_user.role)

def get_user_by_email(email: str, db: Session) -> UserInDB | None:
    stmt = select(DBUser).where(DBUser.email == email)
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
        role=db_user.role
    )
