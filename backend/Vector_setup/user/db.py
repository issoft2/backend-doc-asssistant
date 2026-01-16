# db.py
from sqlmodel import SQLModel, Field, create_engine, Session, UniqueConstraint, Column, JSON
from typing import Optional, Dict, Any
import os
from datetime import datetime
from enum import Enum


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/users.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})


class Tenant(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Billing / subscription 
    plan: str = Field(default="free_trial")
    subscription_status: str = Field(default="trialing") # trialing, active, expired, cancelled
    trial_ends_at: datetime | None = Field(default=None)
    
class CollectionVisibility(str, Enum):
    tenant = "tenant" # visible to all users in tenant (subject to role rules)
    org = "org" # only users in same organization
    role = "role" # specific roles
    user = "user" # specific users
        
    
class Collection(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: str = Field(index=True, foreign_key="tenant.id")
    organization_id: Optional[str] = Field(default=None, index=True) # Fk to Organization.id
    name: str = Field(index=True)
    visibility: CollectionVisibility = Field(default=CollectionVisibility.tenant)
    
    # Simple JSON fields for now; can normalize later if needed.
    allowed_roles: Optional[list[str]] = Field(sa_column=Column(JSON), default=None)
    allowed_user_ids: Optional[list[str]] = Field(sa_column=Column(JSON), default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    doc_count: int = Field(default=0)
    
     
class DBUser(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(primary_key=True, index=True)
    email: str = Field(index=True)
    tenant_id: str
    hashed_password: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone: str
    role: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_first_login: bool = Field(default=True)
    # last_login_at: Optional[datetime] = None
    # Newly added 
    is_online: bool = Field(default=False, index=True)
    last_login_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    organization_id: Optional[str] = Field(default=None, index=True)
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    
class ChatMessage(SQLModel, table=True):
    
    __tablename__ = "chat_messages"
    
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: str = Field(index=True)
    user_id: str = Field(index=True)
    organization_id: int | None = Field(default=None, index=True)   
    collection_id: int | None = Field(default=None, index=True)   
    role: str # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    conversation_id: str | None = Field(nullable=False, index=True)
    doc_id: str | None
        
        
class TenantGoogleDriveConfig(SQLModel, table=True):
    __tablename__ = "tenant_google_drive_config"

    id: int | None = Field(default=None, primary_key=True)
    tenant_id: str = Field(index=True)
    refresh_token: str
    account_email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("tenant_id", name="uq_drivecfg_tenant"),
    )
        
        
class IngestedDriveFile(SQLModel, table=True):
    __tablename__ = "ingested_drive_files"
    
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: str = Field(index=True)
    drive_file_id: str = Field(index=True)
    filename: str
    mime_type: str
    # Optional: has/versioning fields later
    # content_has: Optional[str] = None
    last_ingested_at: datetime = Field(default_factory=datetime.utcnow)        

class FirstLoginToken(SQLModel, table=True):
    __tablename__ = "first_login_tokens"
    id: str = Field(primary_key=True, index=True)
    user_id: str = Field(index=True, foreign_key="users.id")
    token_hash: str = Field(index=True)
    expires_at: datetime
    used_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

    
class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    
    id: str = Field(primary_key=True, index=True)
    tenant_id: str = Field(index=True)
    name: str = Field(index=True)    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)    
    
class AuditLog(SQLModel, table=True):
     __tablename__ = "audit_logs"
     
     id: str = Field(primary_key=True, index=True)
     tenant_id: str = Field(index=True)
     user_id: str = Field(index=True)
     action: str = Field(index=True)
     resource_type: str = Field(index=True)
     resource_id: Optional[str] = Field(default=None, index=True)
     
     # Small, flexible metadata
     meta: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column('metadata', JSON, nullable=True),
    )
     
     created: datetime = Field(default_factory=datetime.utcnow)
        