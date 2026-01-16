from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select


from Vector_setup.base.auth_models import UserCreate, UserOut, LoginRequestTenant
from Vector_setup.user.auth_store import create_user, get_user_by_email, login_tenant_request, create_first_login_token, get_current_db_user
from Vector_setup.user.jwt_core import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from Vector_setup.user.db import get_db, FirstLoginToken, engine, DBUser,Organization, Tenant
from Vector_setup.services.email_service import send_first_login_email  # your email helper
from Vector_setup.user.password import verify_password, get_password_hash
from Vector_setup.schema.schema_signature import UserCreateIn

from Vector_setup.user.roles import USER_CREATOR_ROLES, VENDOR_ROLES





import os
import logging
from pydantic import BaseModel
from Vector_setup.user.permissions import map_role_to_permissions
        

logger = logging.getLogger(__name__)

FRONTEND_BASE_URL = os.getenv("FRONTEND_ORIGIN", "https://lexiscope.duckdns.org")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
def read_me(current_user: DBUser = Depends(get_current_db_user)) -> UserOut:
    """
    Return the current user's profile, including tenant, org, and role.
    """
    perms = map_role_to_permissions(current_user.role)
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        tenant_id=current_user.tenant_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        date_of_birth=current_user.date_of_birth,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        create_at=current_user.created_at,
        is_online=current_user.is_online,
        last_login_at=current_user.last_login_at,
        last_seen_at=current_user.last_seen_at,
        roles=[current_user.role],
        permissions=perms,
        organization_id=current_user.organization_id,
    )


@router.post("/signup", response_model=UserOut)
def signup(
    body: UserCreateIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
) -> UserOut:
    # 1) Only certain roles can create users
    if current_user.role not in USER_CREATOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create users.",
        )

    # 2) Vendor can create for any tenant; others only for their own tenant
    if current_user.role not in VENDOR_ROLES and body.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create user for this tenant",
        )

    # 3) Validate organization for non-vendor users
    is_vendor_user = body.role in VENDOR_ROLES
    if not is_vendor_user and body.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="organization_id is required for non-vendor users",
        )

    if body.organization_id is not None:
        org = db.get(Organization, body.organization_id)
        if not org or org.tenant_id != body.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization_id for this tenant",
            )

    # 4) Restrict which roles current_user may assign
    # Example rule: subsidiaries cannot assign group_* roles
    if current_user.role.startswith("sub_") and body.role.startswith("group_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subsidiary admins cannot assign group-level roles",
        )

    # Optional: prevent assigning vendor role except by vendor or group_admin
    if body.role in VENDOR_ROLES and current_user.role not in VENDOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to assign vendor roles",
        )

    # 5) Check email uniqueness
    existing = get_user_by_email(body.email, body.tenant_id, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 6) Create user
    user = create_user(body, db)

    # 7) Generate first-time login token
    raw_token = create_first_login_token(db, user)

    # 8) Queue email sending
    login_link = f"{FRONTEND_BASE_URL}/first-login?token={raw_token}"
    background_tasks.add_task(
        send_first_login_email,
        to_email=user.email,
        first_name=user.first_name,
        tenant_id=user.tenant_id,
        login_link=login_link,
    )

    return UserOut(
        id=user.id,
        email=user.email,
        tenant_id=user.tenant_id,
        role=user.role,
        # add organization_id if present in UserOut
    )


    

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # form_data.username holds the email
    auth_result = authenticate_user(form_data.username, form_data.password, db)
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
    user, tenant_rows = auth_result    
    # 👇 block deactivated users
    if not user.is_active:  # or user.disabled, or user.status == "inactive"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your Account has been deactivated, Please contact an administrator for help.!",
        )
        
    # Distinct tenant ids from rows
    tenant_ids = {row.tenant_id for row in tenant_rows}
    
  
    # Phase 2 not needed only one tenant
    if len(tenant_ids) == 1:
        tenant_id = next(iter(tenant_ids))

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "tenant_id": tenant_id},
            expires_delta=access_token_expires,
        )
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "requires_tenant_selection": False
        }
        

    # Phase needed: multiple tenants
    # Map to something frontend friendly (you likely have a company/Tenant table to join)
    return {
        "requires_tenant_selection": True,
        "tenants": [
            {"tenant_id": row.tenant_id, "role": row.role} for row in tenant_rows
        ],
    }
    
# Tenant login when the user select a tenant
@router.post("/login/tenant")
def login_tenant(
    body: LoginRequestTenant,
    db: Session = Depends(get_db),
    # tenant: Tenant = Depends(ensure_tenant_active),

):
    user = login_tenant_request(body, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this tenant",
        )
    
    now = datetime.utcnow()
    user.last_login_at = now
    user.last_seen_at = now
    user.is_online = True
    db.add(user)
    db.commit()
    db.refresh(user)  
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "tenant_id": user.tenant_id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}   

class FirstLoginVerifyRequest(BaseModel):
    token: str

@router.post("/first-login/verify")
def verify_first_login(payload: FirstLoginVerifyRequest
):
    raw_token = payload.token

    with Session(engine) as session:
        # 1) Find all not-yet-used tokens (should be 0 or 1) and verify hash
        stmt = select(FirstLoginToken).where(FirstLoginToken.used_at.is_(None))
        candidates = session.exec(stmt).all()

        matched = None
        for t in candidates:
            if verify_password((raw_token or "")[:64], t.token_hash):
                matched = t
                break

        if not matched:
            raise HTTPException(status_code=400, detail="Invalid or expired")

        # 2) Check expiry
        now = datetime.now(timezone.utc)
        expires_at = matched.expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            matched.used_at = None  # optionally mark as used/invalid
            session.add(matched)
            session.commit()
            raise HTTPException(status_code=400, detail="Invalid or expired")

        # 3) Load user
        user = session.get(DBUser, matched.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired")

        # 4) Mark first login complete and token as used
        user.is_first_login = True
        matched.used_at = None
        session.add(user)
        session.add(matched)
        session.commit()

        return {"status": "ok"}
 
 
class FirstLoginSetPasswordRequest(BaseModel):
    token: str
    new_password: str
    

@router.post("/first-login/set-password")
def set_first_login_password(payload: FirstLoginSetPasswordRequest
):
    raw_token = payload.token
    new_password = payload.new_password


    if not new_password or len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password too short")

    with Session(engine) as session:
        stmt = select(FirstLoginToken).where(FirstLoginToken.used_at.is_(None))
        candidates = session.exec(stmt).all()

        matched = None
        for t in candidates:
            if verify_password((raw_token or "")[:64], t.token_hash):
                matched = t
                break

        if not matched:
            raise HTTPException(status_code=400, detail="Invalid or expired")
        

        now = datetime.now(timezone.utc)
        expires_at = matched.expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            matched.used_at = now
            session.add(matched)
            session.commit()
            raise HTTPException(status_code=400, detail="Invalid or expired")

        user = session.get(DBUser, matched.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired")



        # Set new password and mark first login complete
        user.hashed_password = get_password_hash(new_password)
        user.is_first_login = False
        matched.used_at = now

        session.add(user)
        session.add(matched)
        session.commit()

        return {"status": "ok"}     
    

@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
):
    # mark user as offline
    current_user.is_online = False
    current_user.last_seen_at = datetime.utcnow()

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    # frontend must also clear stored access token (localStorage/cookie)
    return {"detail": "Logged out"}    


@router.post("/users/heartbeat")
def heartbeat(
    current_user: DBUser = Depends(get_current_db_user),
    db: Session = Depends(get_db),
):
    current_user.last_seen_at = datetime.utcnow()
    try:
        
        current_user.is_online = True
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        logger.warning("Error marking the use status to online")    
    