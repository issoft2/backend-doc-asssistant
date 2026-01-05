import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, SQLModel
from sqlalchemy import text
from dotenv import load_dotenv

from Vector_setup.API.ingest_routes import router as ingest_router
from Vector_setup.API.query_routes import router as query_router
from Vector_setup.API.auth_router import router as user_router
from Vector_setup.API.query_stream_routes import router as query_stream_router
from Vector_setup.API.company_users_routes import router as company_user_router
from Vector_setup.API.google_drive_router import router as google_drive_router

from Vector_setup.user.db import init_db, DBUser, engine
from Vector_setup.user.password import get_password_hash
from Vector_setup.vector_store.store_manager import MultiTenantChromaStoreManager


load_dotenv()

app = FastAPI()

# --- DB init ---
init_db()  # create tables if they don't exist yet

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://127.0.0.1",
    FRONTEND_ORIGIN,
]

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(ingest_router, prefix="/api", tags=["ingest"])
app.include_router(query_router, prefix="/api", tags=["query"])
app.include_router(user_router, prefix="/api", tags=["user"])
app.include_router(query_stream_router, prefix="/api", tags=["query_stream"])
app.include_router(company_user_router, prefix="/api", tags=["company_users"])
app.include_router(google_drive_router, prefix="/api", tags=["google_drive_connections"])

# --- Env / constants ---
VENDOR_EMAIL = os.getenv("VENDOR_EMAIL", "vendor@example.com")
VENDOR_PASSWORD = os.getenv("VENDOR_PASSWORD", "change_me_vendor")
VENDOR_TENANT_ID = os.getenv("VENDOR_TENANT_ID", "vendor-root")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# --- Chroma manager (single instance) ---
chroma_manager = MultiTenantChromaStoreManager()

# --- Optional hard reset (dev only) ---

def str_to_bool(val: str) -> bool:
    return val.lower() in ("true", "1", "yes", "y")


def reset_sql() -> None:
    # Drop & recreate all tables from SQLModel metadata
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)


def reset_chroma() -> None:
    # Uses the same PersistentClient + Settings as the rest of the app
    chroma_manager.reset()


@app.on_event("startup")
def maybe_hard_reset() -> None:
    reset_flag = os.getenv("APP_RESET_DATA", "false")
    if str_to_bool(reset_flag):
        # WARNING: destructive – dev/use-once only
        reset_sql()
        reset_chroma()

# --- Vendor user seeding on startup ---
@app.on_event("startup")
def seed_vendor_user() -> None:
    with Session(engine) as session:
        stmt = select(DBUser).where(DBUser.email == VENDOR_EMAIL)
        existing = session.exec(stmt).first()
        if existing:
            return

        user = DBUser(
            id=str(os.urandom(16).hex()),
            email=VENDOR_EMAIL,
            tenant_id=VENDOR_TENANT_ID,
            hashed_password=get_password_hash(VENDOR_PASSWORD),
            first_name="Vendor",
            last_name="Admin",
            date_of_birth="1990-01-01",
            phone="",
            role="vendor",
        )
        session.add(user)
        session.commit()

# --- Schema tweaks on startup ---

@app.on_event("startup")
def ensure_chat_messages_schema() -> None:
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(chat_messages);"))
        cols = [row[1] for row in res.fetchall()]
        if "doc_id" not in cols:
            conn.execute(text("ALTER TABLE chat_messages ADD COLUMN doc_id TEXT;"))
            conn.commit()

@app.on_event("startup")
def add_to_user_schema() -> None:
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(users);"))
        cols = [row[1] for row in res.fetchall()]
        if "is_first_login" not in cols:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN is_first_login BOOLEAN;")
            )
            conn.commit()
