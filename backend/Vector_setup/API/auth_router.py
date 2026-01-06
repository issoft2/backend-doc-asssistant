from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select


from Vector_setup.base.auth_models import UserCreate, UserOut, LoginRequestTenant
from Vector_setup.user.auth_store import create_user, get_user_by_email, login_tenant_request, create_first_login_token
from Vector_setup.user.auth_jwt import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from Vector_setup.user.db import get_db, FirstLoginToken, engine, DBUser
from Vector_setup.user.auth_jwt import get_current_user
from Vector_setup.services.email_service import send_first_login_email  # your email helper
from Vector_setup.user.password import verify_password, get_password_hash
import os
import logging

logger = logging.getLogger(__name__)

FRONTEND_BASE_URL = os.getenv("FRONTEND_ORIGIN", "https://lexiscope.duckdns.org")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserOut)
def read_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.post("/signup", response_model=UserOut)
def signup(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
) -> UserOut:
     # 1) Block employees completely
    if current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees are not allowed to create users",
        )

    # 2) Vendor can create for any tenant; other roles only for their own tenant
    if current_user.role != "vendor" and user_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create user for this tenant",
        )

    # 3) Check email uniqueness
    existing = get_user_by_email(user_in.email, user_in.tenant_id, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 4) Create user (ensure is_first_login default to True in create_user)
    user = create_user(user_in, db)
    
    # 5) Generate first-time login token
    raw_token = create_first_login_token(db, user)
    
    # 6) Queue email sending
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
            detail="Your Account has been disabled!",
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
):
    user = login_tenant_request(body, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this tenant",
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "tenant_id": user.tenant_id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}   

from pydantic import BaseModel
class FirstLoginVerifyRequest(BaseModel):
    token: str

@router.post("/first-login/verify")
def verify_first_login(payload: FirstLoginVerifyRequest):
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
            matched.used_at = now  # optionally mark as used/invalid
            session.add(matched)
            session.commit()
            raise HTTPException(status_code=400, detail="Invalid or expired")

        # 3) Load user
        user = session.get(DBUser, matched.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired")

        # 4) Mark first login complete and token as used
        user.is_first_login = False
        matched.used_at = now
        session.add(user)
        session.add(matched)
        session.commit()

        return {"status": "ok"}
 
 
class FirstLoginSetPasswordRequest(BaseModel):
    token: str
    new_password: str
    

@router.post("/first-login/set-password")
def set_first_login_password(payload: FirstLoginSetPasswordRequest):
    raw_token = payload.token
    new_password = payload.new_password

    logger.info("Set password payloads:::: %s", payload.dict())

    if not new_password or len(new_password) < 8:
        logger.info("set-password error: password too short")
        raise HTTPException(status_code=400, detail="Password too short")

    with Session(engine) as session:
        stmt = select(FirstLoginToken).where(FirstLoginToken.used_at.is_(None))
        candidates = session.exec(stmt).all()
        logger.info("set-password candidates count: %s", len(candidates))

        matched = None
        for t in candidates:
            if verify_password((raw_token or "")[:64], t.token_hash):
                matched = t
                break

        if not matched:
            logger.info("set-password error: token not matched %s", raw_token)
            raise HTTPException(status_code=400, detail="Invalid or expired")

        now = datetime.now(timezone.utc)
        expires_at = matched.expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            logger.info("set-password error: token expired %s", matched.id)
            matched.used_at = now
            session.add(matched)
            session.commit()
            raise HTTPException(status_code=400, detail="Invalid or expired")

        user = session.get(DBUser, matched.user_id)
        if not user:
            logger.info("set-password error: user not found %s", matched.user_id)
            raise HTTPException(status_code=400, detail="Invalid or expired")



        # Set new password and mark first login complete
        user.hashed_password = get_password_hash(new_password)
        user.is_first_login = False
        matched.used_at = now

        session.add(user)
        session.add(matched)
        session.commit()

        return {"status": "ok"}     