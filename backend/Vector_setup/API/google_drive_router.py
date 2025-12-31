
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlmodel import Session
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import parse_qs, urlencode
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from Vector_setup.user.db import DBUser, TenantGoogleDriveConfig, get_db
from Vector_setup.API.admin_permission import require_tenant_admin
from Vector_setup.user.auth_jwt import get_current_user
import os
from pydantic import BaseModel
from typing import List, Optional
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
import uuid
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from Vector_setup.API.ingest_routes import extract_text_from_upload

# Single shared store instance



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
    https_authorization_url = authorization_response.replace("http://", "https://", 1)
    flow.fetch_token(authorization_response=https_authorization_url)
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
    

@router.get("/files", response_model=List[DriveFileOut])
def list_drive_files(
    folder_id: Optional[str] = None,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(require_tenant_admin),
    
):
    """
    Docstring for list_drive_files
    
    :param folder_id: Description
    :type folder_id: Optional[str]
    :param page_size: Description
    :type page_size: int
    :param db: Description
    :type db: Session
    :param current_user: Description
    :type current_user: DBUser
    
    List files in this tenant's connected Google Drive.
    If folder_id is provided, redirect to that folder; otherwise list root/visible files.
    """
    tenant_id = current_user.tenant_id
    service = get_drive_service_for_tenant(tenant_id, db)
    
    # Build Drive query: only non-trashed files; optionally in a folder
    q_parts = ["trashed = false"]
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
        
    query = " and ".join(q_parts)
    
    results = (
        service.files()
        .list(
            q=query,
            pageSize=page_size,
            fields="files(id, name, mimeType)",
        )
        .execute()
    )
    files = results.get("files", [])
    
    return [
        DriveFileOut(
            id=f["id"],
            name=f["name"],
            mime_type=f["mimeType"],
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


@router.post("/ingest")
async def ingest_drive_file(
    req: DriveIngestRequest,
    db: Session = Depends(get_db),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    current_user: DBUser = Depends(require_tenant_admin),
):
    """
    Download a file from Google Drive for this tenant and ingest it into a collection.
    """
    tenant_id = current_user.tenant_id
    service = get_drive_service_for_tenant(tenant_id, db)

    # 1) Get file metadata
    file_meta = (
        service.files()
        .get(fileId=req.file_id, fields="id, name, mimeType")
        .execute()
    )
    filename = file_meta["name"]
    mime_type = file_meta.get("mimeType", "")

    # 2) Download or export contents
    buf = BytesIO()
    if mime_type.startswith("application/vnd.google-apps"):
        # Google Docs/Sheets/Slides/etc → export to PDF
        export_mime = "application/pdf"
        request = service.files().export_media(
            fileId=req.file_id, mimeType=export_mime
        )
    else:
        # Normal Drive binary files (PDF, DOCX, etc.)
        request = service.files().get_media(fileId=req.file_id)

    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        status_chunk, done = downloader.next_chunk()
        # optional: log status_chunk.progress()

    raw_bytes = buf.getvalue()

    # 3) Run through your existing extraction pipeline
    text = extract_text_from_upload(filename, raw_bytes)
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text could be extracted from the Google Drive file.",
        )

    doc_id = str(uuid.uuid4())
    metadata = {
        "filename": filename,
        "title": req.title or filename,
        "content_type": mime_type,
        "source": "google_drive",
        "drive_file_id": req.file_id,
        "tenant_id": tenant_id,
        "collection": req.collection_name,
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
            detail=result.get("message", "Indexing failed"),
        )

    return {"status": "ok", "doc_id": doc_id}


           
             
             
             
             