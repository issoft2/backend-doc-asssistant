from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import parse_qs, urlencode
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from Vector_setup.user.db import DBUser, TenantGoogleDriveConfig, get_db
from Vector_setup.API.admin_permission import require_tenant_admin

from dotenv import load_dotenv


load_dotenv()

# Get the environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES")
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



@router.get("callback")
def google_drive_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
 
    # parse state back to get tenant_id
    state_params = parse_qs(state)
    tenant_ids = state_params.get("tenant_id")
    if not tenant_ids:
        raise HTTPException(status_code=400, detail="Missing tenant in state")
    
    tenant_id = tenant_ids[0]
    
    flow = Flow.fron_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID, # provide from env
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI] # env
            }
        },
        
        scopes=GOOGLE_SCOPES
    )
    flow.redirect_url = GOOGLE_REDIRECT_URI
    
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    
    creds = flow.credentials
    if not creds.refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token from Google")
    
    # Optional: get account email via Drive or People API
    drive_service = build("dive", "v3", credentials=creds)
    about = drive_service.about().get(fields="user(emailAddress)").execute()
    account_email = about["user"]["emailAddress"]
    
    # Store refresh_token + account_email per tenant
    cfg = db.query(TenantGoogleDriveConfig).filter_by(tenant_id=tenant_id).first()
    if not cfg:
        cfg = TenantGoogleDriveConfig(
            tenant_id=tenant_id,
            refresh_token=creds.refresh_token,
            account_email=account_email,
        )
        db.add(cfg)
        
    else:
        cfg.refresh_token=creds.refresh_token
        cfg.account_email=creds.account_email
        
    db.commit()        
        
    return RedirectResponse(FRONTEND_AFTER_CONNECT_URL)


@router.get("/google-drive/status")
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
