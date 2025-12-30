# auth_store.py
from sqlmodel import Session, select
from  Vector_setup.base.auth_models  import UserCreate, UserInDB, LoginRequestTenant
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

def get_users_by_email(email: str, db: Session) -> list[DBUser]:
    stmt = select(DBUser).where(DBUser.email == email)
    return list(db.exec(stmt).all())


def get_user_by_email(
    email: str,
    tenant_id: str,
    db: Session
) -> UserInDB | None:
    
    stmt = select (
        (DBUser)
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