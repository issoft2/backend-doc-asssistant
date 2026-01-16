from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel,  Field, validator
from Vector_setup.user.db import CollectionVisibility # or re-declare enum



class CollectionOut(BaseModel):
    id: str
    tenant_id: str
    organization_id: Optional[str] = None

    name: str
    doc_count: int

    visibility: CollectionVisibility
    allowed_roles: Optional[List[str]] = None
    allowed_user_ids: Optional[List[str]] = None

    created_at: datetime
    updated_at: datetime


class CompanyOut(BaseModel):
    tenant_id: str
    display_name: str | None = None
    created_at: datetime
    plan: str
    subscription_status: str
    trial_ends_at: datetime | None
    

class TenantCollectionConfigOut(BaseModel):
    status: str
    tenant_id: str
    collection_name: str
    
    


class CollectionCreateIn(BaseModel):
    tenant_id: str
    organization_id: Optional[str] = None

    name: str = Field(..., min_length=1, max_length=64)

    visibility: CollectionVisibility = CollectionVisibility.tenant
    allowed_roles: Optional[List[str]] = None
    allowed_user_ids: Optional[List[str]] = None

    @validator("name")
    def safe_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Collection name must be alphanumeric and may include '-' or '_'.")
        return v


class CollectionUpdateIn(BaseModel):
    organization_id: Optional[str] = None
    visibility: Optional[CollectionVisibility] = None
    allowed_roles: Optional[List[str]] = None
    allowed_user_ids: Optional[List[str]] = None
    
    

class OrganizationCreateIn(BaseModel):
    tenant_id: str
    name: str
    
class OrganizationUpdate(SQLModel):
    name: Optional[str] = None    

class OrganizationOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    
class UserCreateIn(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    tenant_id: str
    organization_id: Optional[str]
    role: str
    date_of_birth: Optional[str] = None   # ← add thi
    phone: Optional[str] = None
    # ... other fields ...

        