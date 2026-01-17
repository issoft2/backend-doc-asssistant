from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from Vector_setup.user.db import get_db
from Vector_setup.user.db import DBUser, Collection
from Vector_setup.user.auth_store import get_current_db_user
from Vector_setup.access.collections_acl import user_can_access_collection
from Vector_setup.user.roles import COLLECTION_MANAGE_ROLES

router = APIRouter(prefix="/debug", tags=["debug"])


def _ensure_debug_admin(user: DBUser) -> None:
    if user.role not in COLLECTION_MANAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to inspect ACL.",
        )


@router.get("/acl")
def debug_acl(
    user_id: str,
    collection_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_db_user),
):
    """
    Admin-only: check whether a given user can access a given collection.
    """
    _ensure_debug_admin(current_user)

    user = db.get(DBUser, user_id)
    collection = db.get(Collection, collection_id)

    if not user or not collection:
        raise HTTPException(status_code=404, detail="User or collection not found")

    allowed = user_can_access_collection(user, collection)
    return {
        "user_id": user_id,
        "collection_id": collection_id,
        "allowed": allowed,
        "user_role": user.role,
        "user_org": user.organization_id,
        "collection_visibility": collection.visibility,
        "collection_org": collection.organization_id,
    }
