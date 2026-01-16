from typing import List
from .roles import (
    VENDOR_ROLES,
    GROUP_ROLES,
    SUB_ROLES,
    UPLOAD_ROLES,
    COLLECTION_ADMIN_ROLES,
    ORG_ADMIN_ROLES,
    USER_CREATOR_ROLES,
)

def map_role_to_permissions(role: str) -> list[str]:
  perms: list[str] = []

  # Vendor: full control in platform/tenant scope
  if role in VENDOR_ROLES:
      perms.extend([
          "USER:CREATE", "USER:UPDATE", "USER:DEACTIVATE",
          "DOC:UPLOAD", "DOC:DELETE",
          "ORG:CREATE:GROUP", "ORG:CREATE:SUB", "ORG:UPDATE",
          "COLLECTION:CREATE", "COLLECTION:UPDATE", "COLLECTION:DELETE",
      ])
      return perms

  # Group-level
  if role in {"group_admin", "group_exe", "group_gmd"}:
      perms.extend([
          "USER:CREATE", "USER:UPDATE", "USER:DEACTIVATE",
          "DOC:UPLOAD",
          "ORG:CREATE:SUB", "ORG:UPDATE",
          "COLLECTION:CREATE", "COLLECTION:UPDATE", "COLLECTION:DELETE",
      ])
  elif role == "group_hr":
      perms.extend([
          "USER:CREATE", "USER:UPDATE", "USER:DEACTIVATE",
          "DOC:UPLOAD",  # for HR docs
      ])
  elif role in {
      "group_finance", "group_operation", "group_production",
      "group_marketing", "group_legal"
  }:
      perms.extend([
          "DOC:UPLOAD",
          "COLLECTION:CREATE", "COLLECTION:UPDATE",
      ])

  # Subsidiary-level
  if role in {"sub_md", "sub_admin", "sub_exec"}:
      perms.extend([
          "USER:CREATE", "USER:UPDATE", "USER:DEACTIVATE",
          "DOC:UPLOAD",
          "COLLECTION:CREATE", "COLLECTION:UPDATE",
      ])
  elif role == "sub_hr":
      perms.extend([
          "USER:CREATE", "USER:UPDATE", "USER:DEACTIVATE",
          "DOC:UPLOAD",
      ])
  elif role in {
      "sub_finance", "sub_operations", "sub_production",
      "sub_legal", "sub_marketing"
  }:
      perms.extend([
          "DOC:UPLOAD",
          "COLLECTION:CREATE", "COLLECTION:UPDATE",
      ])

  # Employee: no config perms
  if role == "employee":
      # no config permissions; collection ACLs control view access
      pass

  return perms
