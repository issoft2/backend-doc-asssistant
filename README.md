# Company Policy Assistant  
**Multi-Tenant RAG Platform for Internal Company Policies**

A production-oriented, multi-tenant **Retrieval-Augmented Generation (RAG)** platform that enables organizations to upload internal policy documents and provide employees with AI-powered answers strictly scoped to their own company data.

Each tenant is logically isolated at the application layer, ensuring that policy retrieval and answers never cross organizational boundaries.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Data & Multi-Tenancy](#data--multi-tenancy)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Configuration](#environment-configuration)
- [Authentication & Authorization](#authentication--authorization)
  - [Roles](#roles)
  - [Auth Flow](#auth-flow)
- [API Overview](#api-overview)
- [Frontend UX](#frontend-ux)
- [Development Workflow](#development-workflow)
- [Scaling & Production Considerations](#scaling--production-considerations)
- [License](#license)

---

## Overview

The **Company Policy Assistant** is a full-stack, SaaS-ready RAG system designed for organizations that want secure, AI-assisted access to internal data.

Each company (tenant):

- Has an isolated workspace identified by `tenant_id`
- Uploads and manages its own policy document collections
- Allows employees to query policies via a chat interface
- Receives answers generated exclusively from that tenant’s data

A privileged **vendor role** exists to onboard and manage tenants in production environments.

---

## Architecture

### Backend

- **Framework:** FastAPI (Python 3.11)
- **Database:** SQLModel  
  - SQLite (development)  
  - Postgres-ready via `DATABASE_URL`
- **Vector Store:** ChromaDB (embedded, disk-backed)
- **Embeddings:** SentenceTransformers
- **Chunking:** Token-based chunking optimized for RAG
- **Authentication:** JWT (python-jose)
- **Password Hashing:** Passlib

#### Key Design Principles

- Single Chroma client instance
- Application-level multi-tenancy using tenant-prefixed collections
- Clear separation of concerns:
  - Vector operations handled by `MultiTenantChromaStoreManager`
  - API logic split into auth, ingest, and query routers
- Stateless API with tenant context resolved from JWT claims

---

### Frontend

- **Framework:** Vue 3 + Vite
- **Routing:** Vue Router with role-based route guards
- **HTTP Client:** Axios with centralized configuration
- **Styling:** Utility-first (Tailwind-style)

The frontend is a **Single-Page Application (SPA)** that communicates exclusively with the FastAPI backend.

---

## Data & Multi-Tenancy

- A single Chroma persistence directory (e.g. `backend/chromadb_multi_tenant/`)
- Collections are tenant-scoped using prefixes:

```text
acme_corp__policies
globex__employee_handbook


Tenant discovery is derived from collection names

User accounts, roles, and tenant ownership are stored in a relational database

tenant_id is embedded in JWTs and enforced server-side

Tenant identifiers are never supplied by the UI during queries.

Key Features
Multi-Tenant RAG

Tenant-aware document ingestion and retrieval

Token-based chunking for improved retrieval quality

Optional per-collection querying

Safe default: search all tenant collections if none specified

Role-Based Access Control

Vendor

Provision companies and collections

View all tenants

Create users across tenants

HR / Executive / Management

Manage users within their own tenant

Upload and manage documents

Employee

Query policies only

No administrative privileges

Vendor Bootstrap

On backend startup:

Database schema is created automatically

Vendor account is seeded if missing

Document Ingestion

Upload endpoint accepts PDFs, DOCX, and similar formats

Backend pipeline:

Text extraction

Token-based chunking

Embedding generation

Storage in tenant-scoped collections

Indexing metadata returned for auditing

Query & Answering

/query endpoint:

Tenant resolved from JWT

Guarded system prompt construction

Source attribution included

Response includes:

Natural-language answer

Deduplicated list of source documents

## Project Structure
project-root/
  backend/
    Vector_setup/
      base/
        db_setup_management.py
      API/
        auth_router.py
        ingest_routes.py
        query_routes.py
      user/
        db.py
        password.py
    LLM_Config/
      llm_pipeline.py
      prompt_templates.py
    chromadb_multi_tenant/   # git-ignored
    Users.db                 # git-ignored
    api_execute.py

  frontend/
    src/
      api.js
      router/
        index.js
      views/
        AdminCompaniesPage.vue
        AdminIngestPage.vue
        ChatPage.vue
        LoginPage.vue
    vite.config.js
    index.html

  .gitignore
  README.md

##Setup & Installation

###Backend Setup
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Run the ApI
uvicorn Vector_setup.API.api_execute:app --reload

API documentation:
http://localhost:8000/docs

## Frontend Setup

cd frontend
npm install
npm run dev

##Environment Configuration

Create backend/.env:

DATABASE_URL=sqlite:///./Users.db
AUTH_SECRET_KEY=your-long-random-secret

##License

All rights reserved.
This project is proprietary unless explicitly stated otherwise.


---

If you want, next I can:
- Rewrite this for **investors / enterprise buyers**
- Add **architecture diagrams (Mermaid)**
- Produce a **marketing landing-page README**
- Split into **OSS core + SaaS enterprise README**

Just tell me 👌
::contentReference[oaicite:0]{index=0}




