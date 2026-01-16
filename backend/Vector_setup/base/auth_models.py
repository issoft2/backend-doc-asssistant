from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)
    tenant_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone: str
    role: str
    is_active: bool = True
    
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # or date
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True   
    
class UserOut(BaseModel):
    id: str
    email: EmailStr
    tenant_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # or date
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    is_online: bool = False
    last_login_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    roles: List[str] = []
    permissions: List[str] = []
    organization_id: Optional[str] = None
    
    
    class Config:
        from_attributes = True
    
class UserInDB(UserOut):
    hashed_password: str        
    
    
class LoginRequestTenant(BaseModel):
    email: str
    tenant_id: str 
    
       