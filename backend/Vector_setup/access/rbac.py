from dataclasses import dataclass
from typing import Tuple
from Vector_setup.user.db import DBUser, Collection, CollectionVisibility
from Vector_setup.user.roles import GROUP_ROLES, SUB_ROLES, SUPER_ROLES


@dataclass
class AccessDecision:
    allowed: bool
    reason: str


def user_can_access_collection(
    user: DBUser,
    collection: Collection,
) -> bool:
    decision = evaluate_collection_access(user, collection)
    return decision.allowed


def evaluate_collection_access(
    user: DBUser,
    collection: Collection,
) -> AccessDecision:
    """
    Production-grade RBAC evaluation for collection access.
    """

    # ─────────────────────────────────────────────
    # 1) Tenant Isolation (Hard Boundary)
    # ─────────────────────────────────────────────
    if collection.tenant_id != user.tenant_id:
        return AccessDecision(False, "cross_tenant_denied")

    # ─────────────────────────────────────────────
    # 2) Normalize ACL
    # ─────────────────────────────────────────────
    allowed_roles = set(_to_list(collection.allowed_roles))
    allowed_user_ids = set(_to_list(collection.allowed_user_ids))

    explicit_user_allow = str(user.id) in allowed_user_ids
    explicit_role_allow = user.role in allowed_roles

    # ─────────────────────────────────────────────
    # 3) Private (User Visibility)
    # ─────────────────────────────────────────────
    if collection.visibility == CollectionVisibility.user:
        if explicit_user_allow:
            return AccessDecision(True, "private_user_match")
        return AccessDecision(False, "private_user_denied")

    # ─────────────────────────────────────────────
    # 4) Super Roles (Full Tenant Scope)
    # ─────────────────────────────────────────────
    if user.role in SUPER_ROLES:
        return AccessDecision(True, "super_role_full_access")

    # ─────────────────────────────────────────────
    # 5) Explicit ACL Always Wins
    # ─────────────────────────────────────────────
    # Explicit ACL overrides visibility restrictions
    if explicit_user_allow:
        return AccessDecision(True, "explicit_user_acl")

    if explicit_role_allow:
        # Role ACL still subject to org scope for safety
        if collection.visibility == CollectionVisibility.tenant:
            return AccessDecision(True, "explicit_role_acl_tenant")

        if collection.visibility in (
            CollectionVisibility.org,
            CollectionVisibility.role,
        ):
            if (
                user.organization_id is not None
                and user.organization_id == collection.organization_id
            ):
                return AccessDecision(True, "explicit_role_acl_org_match")

        # Do NOT allow cross-org via role ACL
        return AccessDecision(False, "explicit_role_acl_scope_mismatch")

    # ─────────────────────────────────────────────
    # 6) Visibility-Based Access
    # ─────────────────────────────────────────────

    # Tenant-wide visibility
    if collection.visibility == CollectionVisibility.tenant:
        # Only leadership roles can see tenant-wide by default
        if user.role in GROUP_ROLES:
            return AccessDecision(True, "group_role_tenant_visibility")
        return AccessDecision(False, "tenant_visibility_denied")

    # Org-scoped visibility
    if collection.visibility in (
        CollectionVisibility.org,
        CollectionVisibility.role,
    ):
        if (
            user.organization_id is not None
            and user.organization_id == collection.organization_id
        ):
            # Subsidiary roles allowed inside own org
            if user.role in SUB_ROLES:
                return AccessDecision(True, "sub_role_org_visibility")

            # Group roles allowed inside own org
            if user.role in GROUP_ROLES:
                return AccessDecision(True, "group_role_org_visibility")

        return AccessDecision(False, "org_scope_denied")

    # ─────────────────────────────────────────────
    # 7) Default Deny
    # ─────────────────────────────────────────────
    return AccessDecision(False, "default_deny")