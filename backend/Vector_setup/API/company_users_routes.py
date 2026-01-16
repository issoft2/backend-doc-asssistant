from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from Vector_setup.user.db import get_db, DBUser, Tenant
from Vector_setup.base.auth_models import UserOut, UserUpdate
from Vector_setup.API.admin_permission import require_user_admin
from Vector_setup.user.auth_jwt import ensure_tenant_active

from Vector_setup.user.roles import USER_CREATOR_ROLES, VENDOR_ROLES
from Vector_setup.user.permissions import is_sub_role
from sqlmodel import select




router = APIRouter(prefix="/company/users", tags=["company_users"])

@router.get("", include_in_schema=False)
@router.get("/", response_model=List[UserOut])  # ✅ List[UserOut] for frontend array
def list_users(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(require_user_admin)  # ✅ DBUser, not UserOut
):
    stmt = select(DBUser).where(
        DBUser.tenant_id == current_user.tenant_id,
        DBUser.role != "vendor",
    )
    
    if is_sub_role(current_user.role):
        # Subsidiary roles only see THEIR org
        if current_user.organization_id is None:
            # no org -> no visibility
            stmt = stmt.where(DBUser.id == current_user.id)
        else:
            stmt = stmt.where(DBUser.organization_id == current_user.organization_id)
            
    users = db.exec(stmt).all()       
    return [UserOut.from_orm(user) for user in users]  # ✅ Convert to Pydantic for frontend


@router.get("/{user_id}", response_model=UserOut)  # ✅ UserOut, not DBUser
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_user_admin),
     tenant: Tenant = Depends(ensure_tenant_active),
):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.from_orm(user)  # ✅ Convert to Pydantic

@router.put("/{user_id}", response_model=UserOut)  # ✅ UserOut response
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_user_admin),
    tenant: Tenant = Depends(ensure_tenant_active),

):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ✅ Update fields safely
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.from_orm(user)  # ✅ Convert to Pydantic

@router.post("/{user_id}/toggle-active", response_model=UserOut)  # ✅ toggle-active for frontend
def toggle_user_active(  # ✅ renamed from deactivate_user
    user_id: str,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_user_admin),
     tenant: Tenant = Depends(ensure_tenant_active),
):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()  # ✅ consistent .first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active  # ✅ toggle both ways
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.from_orm(user)  # ✅ Convert to Pydantic
