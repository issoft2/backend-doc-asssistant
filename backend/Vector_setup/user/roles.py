from enum import Enum
from typing import Set


class GroupRole(str, Enum):
    group_gmd = "group_gmd"
    group_exec = "group_exe"
    group_hr = "group_hr"
    group_admin = "group_admin"
    group_finance = "group_finance"
    group_operation = "group_operation"
    group_production = "group_production"
    group_marketing = "group_marketing",
    group_legal = "group_legal"
    
    
class SubsidiaryRole(str, Enum):
    sub_md = "sub_md"
    sub_exec = "sub_exec"
    sub_admin = "sub_admin"
    sub_operations = "sub_operations"
    sub_hr = "sub_hr"
    sub_finance = "sub_finance"
    sub_production = "sub_production"
    employee = "employee"
    sub_legal = "sub_legal"
    sub_marketing = "sub_marketing"
    
    


GROUP_ROLES: Set[str] = {
    "group_gmd",
    "group_exe",
    "group_hr",
    "group_admin",
    "group_finance",
    "group_operation",
    "group_production",
    "group_marketing",
    "group_legal",
}

SUB_ROLES: Set[str] = {
    "sub_md",
    "sub_exec",
    "sub_admin",
    "sub_operations",
    "sub_hr",
    "sub_finance",
    "sub_production",
    "sub_legal",
    "sub_marketing",
    "employee",
}

VENDOR_ROLES: Set[str] = {
    "vendor",
    "system_manager"
}

UPLOAD_ROLES: Set[str] = {
    # who can upload/ingest docs
    "group_hr",
    "group_admin",
    "group_finance",
    "group_operation",
    "group_production",
    "sub_admin",
    "sub_hr",
    "sub_finance",
    "sub_operations",
}

COLLECTION_ADMIN_ROLES: Set[str] = {
    "group_admin",
    "group_exe",
    "sub_admin",
    "sub_md",
}

ORG_ADMIN_ROLES: Set[str] = {
    "group_admin",
    "group_exe",
    "vendor",
}


USER_CREATOR_ROLES: set[str] = {
    # Group-level
    "group_admin",
    "group_exe",
    "group_hr",

    # Subsidiary-level
    "sub_admin",
    "sub_md",
    "sub_hr",

    # Vendor ops
    "vendor",
}

    
        