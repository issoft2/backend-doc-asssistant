from datetime import datetime

def get_current_tenant_with_billing():
    tenant = '' # existing resolution
    now = datetime.utcnow()
    
    #if tenant.sc