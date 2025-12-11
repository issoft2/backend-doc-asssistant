from pydantic import BaseModel, Field, validator

class AddDocumentRequest(BaseModel):
    """
    Payload for adding a document to a tenant's collection.
    """
    tenant_id: str
    collection_name: str
    doc_id: str
    text: str
    metadata: dict | None = None

    @validator("tenant_id")
    def safe_tenant_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("tenant_id must be alphanumeric and may include '-' or '_'.")
        return v

    @validator("collection_name")
    def safe_collection_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("collection_name must be alphanumeric and may include '-' or '_'.")
        return v
