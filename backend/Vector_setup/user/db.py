# db.py
from sqlmodel import SQLModel, Field, create_engine, Session, UniqueConstraint
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/users.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

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
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    
class ChatMessage(SQLModel, table=True):
    
    __tablename__ = "chat_messages"
    
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: str = Field(index=True)
    user_id: str = Field(index=True)
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
