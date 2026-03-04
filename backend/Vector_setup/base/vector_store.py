


from backend.Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager


vector_store = MultiTenantChromaStoreManager("./chromadb_multi_tenant")


def get_store() -> MultiTenantChromaStoreManager:
    return vector_store