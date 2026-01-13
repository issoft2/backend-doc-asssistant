
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlmodel import Session
from fastapi.responses import RedirectResponse, JSONResponse, Response
from urllib.parse import parse_qs, urlencode
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from Vector_setup.user.db import DBUser, TenantGoogleDriveConfig, IngestedDriveFile,  get_db, Tenant
from Vector_setup.API.admin_permission import require_tenant_admin
from Vector_setup.user.auth_jwt import get_current_user
import os
from pydantic import BaseModel
from typing import List, Optional
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
import uuid
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from Vector_setup.services.extraction_documents_service import extract_text_from_upload
from googleapiclient.errors import HttpError
import requests
from Vector_setup.user.auth_jwt import ensure_tenant_active





# Single shared store instance

import logging

logger = logging.getLogger(__name__)

from dotenv import load_dotenv


load_dotenv()

# Get the environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES", "")
FRONTEND_AFTER_CONNECT_URL = os.getenv("FRONTEND_AFTER_CONNECT_URL")


router = APIRouter(prefix="/google-drive", tags=["google-drive"])

@router.get("/auth-url")
def get_google_drive_auth_url(
    current_user: DBUser = Depends(require_tenant_admin),
    tenant: Tenant = Depends(ensure_tenant_active),
):
    tenant_id = current_user.tenant_id

    # Put tenant_id (and maybe user id) into state so callback knows where to store tokens
    state_data = {"tenant_id": tenant_id}
    state = urlencode(state_data)

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI],
            }
        },
        scopes=GOOGLE_SCOPES,
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
        prompt="consent",  # ensures refresh_token is returned
    )

    return JSONResponse({"auth_url": authorization_url})


@router.get("/callback")
def google_drive_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(ensure_tenant_active)

):
    # 1) Parse tenant_id from state
    state_params = parse_qs(state)
    tenant_ids = state_params.get("tenant_id")
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Missing tenant in state")
    tenant_id = tenant_ids[0]

    # 2) Build OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI],
            }
        },
        scopes=GOOGLE_SCOPES.split(),  # if you stored as space-separated string
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI

    # 3) Exchange code for tokens
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    if not creds.refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token from Google")

    # 4) Get account email
    drive_service = build("drive", "v3", credentials=creds)
    about = drive_service.about().get(fields="user(emailAddress)").execute()
    account_email = about["user"]["emailAddress"]

    # 5) Store per tenant
    cfg = (
        db.query(TenantGoogleDriveConfig)
        .filter_by(tenant_id=tenant_id)
        .first()
    )
    if not cfg:
        cfg = TenantGoogleDriveConfig(
            tenant_id=tenant_id,
            refresh_token=creds.refresh_token,
            account_email=account_email,
        )
        db.add(cfg)
    else:
        cfg.refresh_token = creds.refresh_token
        cfg.account_email = account_email
    print("Saving Google Drive config for tenant", tenant_id, account_email)
    db.commit()
    print("Saved config")

    return RedirectResponse(FRONTEND_AFTER_CONNECT_URL)



@router.get("/status")
def google_drive_status(
    current_user: DBUser = Depends(require_tenant_admin),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(ensure_tenant_active)

):
    cfg = (
        db.query(TenantGoogleDriveConfig)
        .filter_by(tenant_id=current_user.tenant_id)
        .first()
    )
    if not cfg:
        return {"connected": False, "account_email": None}
    return {"connected": True, "account_email": cfg.account_email}


# Added a helper that reconstructs credentials for the current tenant
def get_drive_service_for_tenant(
    tenant_id: str,
    db: Session
):
    cfg = (
        db.query(TenantGoogleDriveConfig)
        .filter_by(tenant_id=tenant_id)
        .first()
    )
    if not cfg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Drive is not Connected for this tenant.",
            )
        
    scopes = GOOGLE_SCOPES.split() if GOOGLE_SCOPES else [
        "https://www.googleapis.com/auth/drive.readonly"
    ]
    
    creds = Credentials(
        token=None, # Will be obtained using refresh_token
        refresh_token=cfg.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=scopes
    )
    
    try:
       service = build("drive", "v3", credentials=creds)   
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Google Drive client: {e}",
        )
        
    return service


# Endpoint List files from Drive
class DriveFileOut(BaseModel):
    id: str
    name: str
    mime_type: str
    is_folder: bool
    size: Optional[int] = None
    modified_time: Optional[str] = None
    already_ingested: bool = False
    is_supported: bool = True



@router.get("/files", response_model=List[DriveFileOut])
def list_drive_files(
    folder_id: Optional[str] = None,
    page_size: int = 100,
    recursive: bool = False,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(require_tenant_admin),
    tenant: Tenant = Depends(ensure_tenant_active),

    
):
    """
    
    List files in this tenant's connected Google Drive.
    If folder_id is provided, list that folder's children.
    - Otherwise, list items in 'My Drive' visible to this account.
    - If recursive=True, traverse subfolders and return all descendants.
    """
    tenant_id = current_user.tenant_id
    service = get_drive_service_for_tenant(tenant_id, db)
    
    def _list_page(q: str) -> list[dict]:
        # you can also set spaces="drive" explicitly if needed.
        results = (
            service.files()
            .list(
                q=q,
                pageSize=page_size,
                fields=(
                    "nextPageToken, "
                    "files(id, name, mimeType, parents, size, modifiedTime)"
                ),
                
            )
            .execute()
        )
        return results.get("files", [])
    
    # Base query: non-trashed files.
    q_parts = ["trashed = false"]
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    #else: omit parents filter to treat as root/visible.
        
        
    query = " and ".join(q_parts)
    
    if not recursive:
        files = _list_page(query)
    else:
        # BFS/DFS through subfolders using multiple list calls.
        files: list[dict] = []
        folders_to_visit = list[Optional[str]] =  [folder_id] if folder_id else [None]        
        visited_folders: set[str] = set()
        
        while folders_to_visit:
            current_folder = folders_to_visit.pop()
            q_parts = ["trashed = false"]
            if current_folder:
                q_parts.append(f"'{current_folder}' in parents")
                
            query = " and ".join(q_parts)
            
            page_files = _list_page(query)
            files.extend(page_files)
            
            # Add any child folders to the queue
            for f in page_files:
                if f.get("mimeType") == GOOGLE_FOLDER_MIME:
                    fid = f["id"]
                    if fid not in visited_folders:
                        visited_folders.add(fid)
                        folders_to_visit.append(fid)
                        
                        
    file_ids = [f["id"] for f in files]
    
    ingested_rows = (
        db.query(IngestedDriveFile.drive_file_id)
        .filter(
            IngestedDriveFile.tenant_id == tenant_id,
            IngestedDriveFile.drive_file_id.in_(file_ids),
        )
        .all()
    )
    ingested_ids = {row[0] for row in ingested_rows}
                                
    # Map raw Drive items to your schema, including mime_type.
    return [
        DriveFileOut(
            id=f["id"],
            name=f["name"],
            mime_type=f.get("mimeType", ""),
            is_folder=(f.get("mimeType") == GOOGLE_FOLDER_MIME),
            siz=int(f["size"]) if "size" in f else None,
            modified_time=f.get("modifiedTime"),
            already_ingested=f["id"] in ingested_ids,
            is_supported=(
                f.get("mimeType", "") in SUPPORTED_MIME_TYPES
                and f.get("mimeType") != GOOGLE_FOLDER_MIME
            ),
        )
        for f in files
    ]
    
    
 # Single shared store instance
vector_store = MultiTenantChromaStoreManager("./chromadb_multi_tenant")
   
def get_store() -> MultiTenantChromaStoreManager:
    return vector_store


class DriveIngestRequest(BaseModel):
    file_id: str
    collection_name: str
    title: Optional[str] = None
    

def mark_file_ingested(
    db: Session,
    tenant_id: str,
    drive_file_id: str,
    filename: str,
    mime_type: str,
)-> None:
    existing = (
        db.query(IngestedDriveFile)
        .filter_by(tenant_id=tenant_id, drive_file_id=drive_file_id)
        .first()
    )
    if existing:
        existing.filename = filename
        existing.mime_type = mime_type
    else:
        db.add(
            IngestedDriveFile(
                tenant_id=tenant_id,
                drive_file_id=drive_file_id,
                filename=filename,
                mime_type=mime_type
            )
        )
    db.commit()

# refine ingest function for google native documents supports
GOOGLE_DOC_MIME = "application/vnd.google-apps.document"
GOOGLE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"
GOOGLE_SLIDE_MIME = "application/vnd.google-apps.presentation"
GOOGLE_FOLDER_MIME = "application/vnd.google-apps.folder"

SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/plain",
    "text/markdown",
    # Google Workspace native types that you export:
    GOOGLE_DOC_MIME,
    GOOGLE_SHEET_MIME,
    GOOGLE_SLIDE_MIME,
}


@router.post("/ingest")
async def ingest_drive_file(
    req: DriveIngestRequest,
    db: Session = Depends(get_db),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    current_user: DBUser = Depends(require_tenant_admin),
    tenant: Tenant = Depends(ensure_tenant_active)

):
    """
    Download a file from Google Drive for this tenant, and ingest it into a collection.

    Supports:
    - Binary files (pdf, docx, txt, md, xlsx, etc.).
    - Google Docs/Sheet/Slides via export.
    """
    tenant_id = current_user.tenant_id
    service = get_drive_service_for_tenant(tenant_id=tenant_id, db=db)

    # 1) Get file metadata
    file_meta = (
        service.files()
        .get(fileId=req.file_id, fields="id, name, mimeType")
        .execute()
    )
    original_name = file_meta["name"]
    mime_type = file_meta.get("mimeType", "")

    buf = BytesIO()

    # 2) Decide how to download/export and what "filename" to pass to extractor
    if mime_type.startswith("application/vnd.google-apps"):
        # Google Workspace files: choose export target per type
        if mime_type == GOOGLE_DOC_MIME:
            export_mime = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            synthetic_filename = f"{original_name}.docx"
        elif mime_type == GOOGLE_SHEET_MIME:
            export_mime = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            synthetic_filename = f"{original_name}.xlsx"
        elif mime_type == GOOGLE_SLIDE_MIME:
            export_mime = "application/pdf"
            synthetic_filename = f"{original_name}.pdf"
        else:
            # Fallback: try PDF
            export_mime = "application/pdf"
            synthetic_filename = f"{original_name}.pdf"

        request = service.files().export_media(
            fileId=req.file_id,
            mimeType=export_mime,
        )
    else:
        # Normal Drive binary files (PDF, DOCX, etc.)
        synthetic_filename = original_name  # already has extension
        request = service.files().get_media(fileId=req.file_id)

    # 3) Download
    try:
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            status_chunk, done = downloader.next_chunk()
            logger.info("Download %d%%", int(status_chunk.progress() * 100))
    except HttpError as e:
        # Handle large file export limit
        if e.resp.status == 403 and "exportSizeLimitExceeded" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "This Google Drive file is too large to export. "
                    "Try splitting it into smaller documents."
                ),
            )

        # Re-raise other Drive errors
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to download file from Google Drive.",
        )

    raw_bytes = buf.getvalue()

    # 4) Extract text
    text = extract_text_from_upload(synthetic_filename, raw_bytes)
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text could be extracted from the Google Drive file.",
        )

    # 5) Index into vector store
    doc_id = str(uuid.uuid4())
    # Look up collection info
    collection_info = store.get_collection_info(tenant_id, req.collection_name) # to be implemented
    collection_display_name = collection_info.get("display_name", req.collection_name)
    high_level_topic = collection_info.get("topic") # e.g. "HR & Policies", "Engineering", etc.
    
    metadata = {
        "filename": original_name,
        "title": req.title or original_name,
        "content_type": mime_type,
        "size_bytes": len(raw_bytes),
        "source": "google_drive",
        "drive_file_id": req.file_id,
        "tenant_id": tenant_id,
        "collection": req.collection_name,
        "collection_display_name": collection_display_name,
        "high_level_topic": high_level_topic,
    }
    

    result = await store.add_document(
        tenant_id=tenant_id,
        collection_name=req.collection_name,
        doc_id=doc_id,
        text=text,
        metadata=metadata,
    )

    if result.get("status") != "ok":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Indexing failed!"),
        )

    # 6) Mark file as ingested for this tenant (for UX "already ingested" flag)
    mark_file_ingested(
        db=db,
        tenant_id=tenant_id,
        drive_file_id=req.file_id,
        filename=original_name,
        mime_type=mime_type,
    )

    return {"status": "ok", "doc_id": doc_id}


@router.post("/disconnect", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_google_drive(
    db: Session = Depends(get_db),
    current_user = Depends(require_tenant_admin),
) -> Response:
    """
    Disconnect the current tenant from Google Drive.

    - Optionally revoke the refresh token at Google.
    - Always delete the local TenantGoogleDriveConfig row.
    """
    tenant_id = current_user.tenant_id

    cfg = (
        db.query(TenantGoogleDriveConfig)
        .filter(TenantGoogleDriveConfig.tenant_id == tenant_id)
        .first()
    )
    if not cfg:
        # Already disconnected; return 204 with no body
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # Optional: revoke token at Google
    if cfg.refresh_token:
        try:
            creds = Credentials(
                token=None,
                refresh_token=cfg.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=["https://www.googleapis.com/auth/drive.readonly"],
            )
            requests.post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": creds.refresh_token},
                headers={"content-type": "application/x-www-form-urlencoded"},
                timeout=5,
            )
        except Exception:
            # Do not block disconnect on revoke failure
            pass

    db.delete(cfg)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
        

           
             
             
             
             