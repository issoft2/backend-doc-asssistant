# db.py
from sqlmodel import SQLModel, Field, create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class DBUser(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    tenant_id: str
    hashed_password: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone: str
    role: str

def init_db():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session
