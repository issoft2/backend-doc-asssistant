from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Vector_setup.user.db import get_db, DBUser
from Vector_setup.base.auth_models import UserOut, UserUpdate
from Vector_setup.API.admin_permission import require_user_admin


# Get all users
router = APIRouter(prefix="/admin/users", tags=["admin_users"])

@router.get("/", response_model=list[DBUser])
def list_users(
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_user_admin)  # Assume some admin authentication dependency
    
):
    return db.query(DBUser).all()

# Get user by ID
@router.get("/{user_id}", response_model=DBUser)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_user_admin)  # Assume some admin authentication dependency
    
):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user by ID
@router.put("/{user_id}", response_model=DBUser)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_user_admin)  # Assume some admin authentication dependency
    
):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.dict(exclude_unset=True).items(): 
        if value is not None:
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: DBUser = Depends(require_user_admin)  # Assume some admin authentication dependency
    
):
    user = db.query(DBUser).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user