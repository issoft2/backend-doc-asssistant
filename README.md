Company Policy Assistant – Multi‑Tenant RAG Platform
A production‑oriented, multi‑tenant policy assistant that lets multiple companies upload their internal policy documents and gives their employees AI‑powered answers strictly scoped to their own organisation’s policies.​

Table of Contents
Overview

Architecture

Backend

Frontend

Data & Multi‑Tenancy

Features

Project Structure

Setup & Installation

Backend Setup

Frontend Setup

Environment Configuration

Authentication & Authorization

Roles

Auth Flow

API Overview

Frontend UX

Development Workflow

Scaling & Production Considerations

License

Overview
This application is a full‑stack, multi‑tenant Retrieval‑Augmented Generation (RAG) platform focused on company policy guidance.​

Each tenant (company) can:

Provision its own “space” (identified by tenant_id) and configure collections of policy documents.​

Upload policy documents; content is chunked, embedded, and stored in a tenant‑scoped vector store.​

Allow employees to query policies through a chat‑style UI, with retrieval and answers strictly limited to their own tenant’s data.​

The platform supports a special vendor user that can onboard new companies and manage cross‑tenant resources in production.​

Architecture
Backend
Framework: FastAPI (Python 3.11).​

Persistence: SQLModel (SQLite by default, Postgres‑ready via DATABASE_URL).​

Vector Store: ChromaDB running as a single embedded instance on disk.​

Embeddings & Chunking: SentenceTransformers with token‑based chunking tailored for production RAG.​

Auth: JWT (via python-jose) with tenant_id embedded in the token; passwords hashed via Passlib.​

Key backend design points:

One Chroma client instance.

Multi‑tenancy implemented at the application level by prefixing collection names with tenant_id.​

Clear separation of concerns:

MultiTenantChromaStoreManager for vector operations.​

FastAPI routers for auth, ingest, and query.​

Frontend
Framework: Vue 3 with Vite.​

Routing: Vue Router with auth guards and role‑based access control on routes.​

HTTP Client: Axios with a central api.js configured for the backend URL and interceptors.​

Styling: Tailwind‑style utility classes for admin panels and chat UI.​

The frontend is a SPA that talks exclusively to the FastAPI backend.

Data & Multi‑Tenancy
All vector data is stored under a single Chroma persistence directory (e.g. backend/chromadb_multi_tenant/).​

Collections are named with a tenant prefix, e.g. acme_corp__policies, isolating tenants at the application level.​

Companies are discovered by scanning collections and stripping prefixes; /companies and /companies/{tenant_id}/collections derive from this.​

User accounts, roles, and tenant_id are persisted in DBUser via SQLModel and a relational DB (SQLite for dev).​

Features
Multi‑Tenant RAG
Tenant‑aware ingest and retrieval through a single Chroma instance.​

Token‑based chunking for better context shaping and retrieval quality.​

Optional collection_name parameter for queries; if omitted, all collections under the tenant are searched.​

Role‑Based Access Control
Vendor user:

Can provision companies (configure new tenant_id + first collection).​

Can see all companies and collections across tenants.​

Can create users for any tenant.​

HR / Executive / Management:

Can create users only within their own tenant.​

Can manage collections and uploads for their tenant.​

Employee:

Can access only the query/chat interface; no admin or user management capabilities.​

Vendor Bootstrap
On backend startup:

init_db() creates DB schema if needed.​

A startup event seeds a vendor user using env vars (VENDOR_EMAIL, VENDOR_PASSWORD, VENDOR_TENANT_ID) if that email does not exist.​

Document Ingestion
File upload endpoint (/documents/upload) accepts uploaded policy documents.​

Backend:

Extracts text.

Applies token‑based chunking.

Generates embeddings and stores chunks in the appropriate tenant collection.​

Response includes indexing metadata (e.g. doc_id, chunks_indexed, new_collection_count).​

Query & Answering
POST /query:

Uses the logged‑in user’s tenant_id from the JWT.​

Applies retrieval over one or all collections for the tenant.​

Builds a guarded system prompt and user prompt with retrieved context and user question.​

Returns:

answer: natural‑language response.

sources: de‑duplicated list of source docs from metadata (e.g. title, filename, doc_id).​

Frontend UX
Admin views:

Combined form to configure company (tenant_id) and its first collection in a single action.​

Company list showing all tenants (or own tenant only, depending on role) with their collections and per‑company “Add document” actions.​

User management modal for adding users with full profile and role selection.​

Employee chat view:

Clean chat layout with message history for the browser session.​

Simple question box; tenant/collection are inferred from auth, not typed by the user.​

Project Structure
High‑level layout (names illustrative):

text
project-root/
  backend/
    Vector_setup/
      base/
        db_setup_management.py     # MultiTenantChromaStoreManager and related models [memory:162]
      API/
        ingest_routes.py           # Configure companies+collections, upload, list endpoints [memory:171]
        query_routes.py            # /query and supporting models [memory:175]
        auth_router.py             # /auth/signup, /auth/login etc. [memory:163]
      user/
        db.py                      # DBUser, engine, init_db, get_db [memory:173][memory:191]
        password.py                # get_password_hash, verify_password [memory:173]
    LLM_Config/
      llm_pipeline.py              # RAG pipeline (retrieval + LLM prompt) [memory:175]
      prompt_templates.py          # SYSTEM_PROMPT & user prompt builder [memory:161]
    chromadb_multi_tenant/         # Chroma persistence (git-ignored) [memory:162]
    Users.db                       # SQLite DB for users (git-ignored) [memory:173]
    api_execute.py                 # FastAPI app, CORS, router includes, vendor seeding [memory:171][memory:173]

  frontend/
    src/
      api.js                       # Axios instance and API wrapper functions [memory:174]
      router/
        index.js                   # Routes + auth guards [memory:163]
      views/
        AdminCompaniesPage.vue     # List companies/collections, upload per company [memory:181]
        AdminIngestPage.vue        # Combined configure + upload admin workflow [memory:165][memory:171]
        ChatPage.vue               # Employee query/chat interface [memory:176]
        LoginPage.vue              # Login form [memory:163]
        (optional) SignupPage.vue  # For vendor/admin-created signups UI [memory:163][memory:188]
    vite.config.js
    index.html

  .gitignore                       # Ignores venv, node_modules, .env, local DB & Chroma [memory:133][memory:173]
  README.md
Setup & Installation
Backend Setup
Create and activate virtual environment

bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Dependencies include FastAPI, SQLModel, ChromaDB, SentenceTransformers, python‑jose, Passlib, Uvicorn, etc.​

Environment variables

Create backend/.env (see Environment Configuration).

Run the app

bash
uvicorn Vector_setup.API.api_execute:app --reload
API docs: http://localhost:8000/docs

On startup:

Tables are created if absent.​

Vendor user is seeded if VENDOR_EMAIL does not exist.​

Frontend Setup
Install Node dependencies

bash
cd frontend
npm install
Run dev server

bash
npm run dev
By default, Vite serves at http://localhost:5173. CORS is configured in FastAPI to allow this origin.​

Environment Configuration
Create backend/.env with at least:

text
# JWT / security
AUTH_SECRET_KEY=replace_with_a_long_random_string
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
DATABASE_URL=sqlite:///./Users.db   # For dev/local
# For Postgres:
# DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname

# Vendor bootstrap
VENDOR_EMAIL=vendor@example.com
VENDOR_PASSWORD=change_me_vendor
VENDOR_TENANT_ID=vendor-root

# Chroma
CHROMA_PERSIST_DIRECTORY=./chromadb_multi_tenant
Recommendations:

Use a long, random AUTH_SECRET_KEY (≥32 chars, ideally ≥64) and rotate per environment.​

Do not commit .env or any real secrets; they are excluded via .gitignore.​

For production, point DATABASE_URL to a managed Postgres or similar.​

Authentication & Authorization
Roles
Users are persisted as DBUser rows with at least:

id

email

hashed_password

tenant_id

role (vendor, HR, executive, management, employee)

Profile fields (first name, last name, date of birth, phone).​

Capabilities:

Role	Can login	Configure companies	See all companies	Create users (any tenant)	Create users (own tenant)	Query policies
vendor	Yes	Yes	Yes	Yes	Yes	Yes
HR	Yes	No	Own only	No	Yes	Yes
executive	Yes	No	Own only	No	Yes (if enabled)	Yes
management	Yes	No	Own only	No	Yes (if enabled)	Yes
employee	Yes	No	Own only (view only where exposed)	No	No	Yes
​

Auth Flow
Signup (admin/vendor)

Vendor or tenant admins call POST /auth/signup to create new users.

Vendor can assign any tenant_id; others can only assign their own tenant_id.​

Login

POST /auth/login verifies credentials, then creates a JWT with sub (user ID), email, and tenant_id.​

Token is returned to frontend and stored (e.g. localStorage).

Protected endpoints

Routes depend on get_current_user, which:

Decodes JWT using AUTH_SECRET_KEY.

Loads the corresponding DBUser from DB.​

Enforces role and tenant rules for each endpoint.

Frontend integration

Axios attaches Authorization: Bearer <token> to each request.​

A response interceptor logs out and redirects to login on 401/403.​

API Overview
High‑level list (paths grouped by intent):

Auth
POST /auth/signup

Create a user.

Role restrictions:

vendor: can create for any tenant.

Others (HR/executive/management): only their own tenant.

employee: forbidden.​

POST /auth/login

Input: email, password.

Output: access_token (JWT), token type.​

Company & Collections
GET /companies

Vendor: returns all companies discovered from Chroma collections.

Others: returns only their own tenant.​

POST /companies/configure

Create a company (tenant_id) and its first collection in one call.​

Vendor‑only; enforced via current_user.role.

GET /companies/{tenant_id}/collections

List collections for a given tenant.

Vendor can see any; others only their own tenant.​

Documents
POST /documents/upload

Multipart form:

tenant_id, collection_name (or inferred from role/vendor context depending on API design).

File field file, plus optional metadata such as title and doc_id.​

Backend:

Extracts text.

Token‑chunks content and embeds.

Stores in appropriate tenant collection.​

Query
POST /query

Request body: question, optionally collection_name, top_k.​

tenant_id resolved from current user (no tenant field in body from UI).​

Response:

answer: final generated answer.

sources: list of { title, filename, doc_id, ... }.​

Frontend UX
Authentication Views
LoginPage.vue

Email & password form.

On success, saves token and routes based on role (e.g. admin dashboard vs chat).​

Optional SignupPage.vue

For vendor or admin to create users with extended profile fields.​

Admin Area
Typical routes:

/admin/companies

Shows:

Configuration panel (“Configuration Panel” link) with a vendor/admin‑only RouterLink styled as a button.​

Table of companies and their collections.​

“Add document” buttons/modals scoped to each company, wiring to /documents/upload.​

/admin/ingest

Combined form:

tenant_id + collection_name context set once.​

Uses /companies/configure to create company+collection.​

Upload form reuses the same context for file uploads.​

Buttons and navigation are styled to be clearly clickable (borders, hover states, pill buttons, etc.).​

Employee Chat
/chat

Centered chat card with:

Scrollable list of all Q&A for the session.​

Question textarea + “Ask” button (disabled when loading).

On submit:

Calls queryPolicies({ question }) which posts to /query.​

Appends { question, answer, sources } into a messages array.​

Development Workflow
Clone the repo & set up Git

bash
git clone <your-repo-url>
cd project-root
Ensure .gitignore covers:

.venv/, venv/, __pycache__/, *.pyc.​

node_modules/, dist/, *.log.​

.env, .env.*, .DS_Store, IDE folders.​

backend/chromadb_multi_tenant/, backend/Users.db.​

Run backend and frontend in parallel in dev.

Testing with tools like Postman

Test /auth/login, /companies/configure, /documents/upload, /query independently before UI integration.​

Scaling & Production Considerations
Database

For serious production use, switch from SQLite to Postgres/MySQL via DATABASE_URL.​

SQLModel models stay the same; only the engine URL changes.

Secrets & config

Keep secrets in environment variables or a secret manager.

Rotate AUTH_SECRET_KEY and vendor credentials regularly.​

Chroma

Current design runs embedded Chroma with local disk persistence.​

For higher scale or horizontal scaling, move to Chroma server or Chroma Cloud and adjust the client configuration accordingly.

LLM / Embeddings

Ensure embedding model and LLM endpoints are reachable and configured with appropriate timeouts and retries.​

Consider caching frequent queries or answers if usage patterns demand it.

Security

All admin and vendor routes require auth and role checks on the backend; the frontend must not be trusted alone.​

CORS restricted to expected frontend origins; use HTTPS in production.​

License
 “All rights reserved” if you intend to keep it proprietary.



