from enum import Enum

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
        