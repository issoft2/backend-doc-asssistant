from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
import os

from Vector_setup.API.ingest_routes import router as ingest_router
from Vector_setup.API.query_routes import router as query_router
from Vector_setup.API.auth_router import router as user_router
from Vector_setup.API.query_stream_routes import router as query_stream_router

from Vector_setup.user.db import init_db, DBUser, engine
from Vector_setup.user.password import get_password_hash
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- DB init ---
init_db()  # create tables if they don't exist yet


FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

origins = [
    "http://localhost:5173",          # Vue dev
    "http://localhost",               # generic local
    "http://127.0.0.1",               # generic local
    FRONTEND_ORIGIN,                  # production, e.g. https://your-domain.com
]

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # explicit list keeps credentials safe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(ingest_router, prefix="/api", tags=["ingest"])
app.include_router(query_router, prefix="/api", tags=["query"])
app.include_router(user_router, prefix="/api", tags=["user"])
app.include_router(query_stream_router, prefix="/api", tags=["query_stream"])



# --- Vendor user seeding on startup ---

VENDOR_EMAIL = os.getenv("VENDOR_EMAIL", "vendor@example.com")
VENDOR_PASSWORD = os.getenv("VENDOR_PASSWORD", "change_me_vendor")
VENDOR_TENANT_ID = os.getenv("VENDOR_TENANT_ID", "vendor-root")  # special tenant_id

@app.on_event("startup")
def seed_vendor_user():
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
            date_of_birth="1970-01-01",
            phone="",
            role="vendor",
        )
        session.add(user)
        session.commit()
