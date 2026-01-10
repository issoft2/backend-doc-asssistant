
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from fastapi.responses import RedirectResponse, JSONResponse, Response
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager
from Vector_setup.user.db import DBUser, get_db
from Vector_setup.API.admin_permission import require_tenant_admin

vector_store = MultiTenantChromaStoreManager("./chromadb_multi_tenant")
   
def get_store() -> MultiTenantChromaStoreManager:
    return vector_store




@router.post("/ingest-db")
async def ingest_db_source(
    req: DBIngestRequest,
    db: Session = Depends(get_db),
    store: MultiTenantChromaStoreManager = Depends(get_store),
    current_user: DBUser = Depends(require_tenant_admin),
):
    """
    Read from a tenant's database (preconfigured connection + view)
    and ingest rows into a collection.
    """
    tenant_id = current_user.tenant_id

    # 1) Resolve connection + config for this tenant and source
    conn_info = get_tenant_db_connection(tenant_id=tenant_id, db=db, source_name=req.source_name)
    view_cfg = get_tenant_db_view_config(tenant_id=tenant_id, source_name=req.source_name)
    # e.g. view_cfg: { "view_name": "hr_policies_view", "pk_column": "policy_id",
    #                  "title_column": "title", "body_column": "body", "extra_meta_cols": ["category","department"] }

    engine = create_engine(conn_info.dsn)  # or async equivalent

    # 2) Pull rows
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT * FROM {view_cfg.view_name}")).mappings().all()

    if not rows:
        return {"status": "ok", "ingested": 0}

    # 3) Collection info
    collection_info = store.get_collection_info(tenant_id, req.collection_name)
    collection_display_name = collection_info.get("display_name", req.collection_name)
    high_level_topic = collection_info.get("topic")

    ingested = 0
    for row in rows:
        pk = str(row[view_cfg.pk_column])
        title = str(row.get(view_cfg.title_column) or f"Record {pk}")

        # 4) Render row into text
        # You can tailor this per source (policies vs financials)
        body = str(row.get(view_cfg.body_column) or "").strip()
        if not body:
            continue

        text = f"{title}\n\n{body}"

        # 5) Build metadata
        extra_meta = {
            col: row.get(col)
            for col in view_cfg.extra_meta_cols
        }

        doc_id = f"db:{view_cfg.view_name}:{pk}"

        metadata = {
            "title": title,
            "source": "database",
            "db_view": view_cfg.view_name,
            "db_pk": pk,
            "tenant_id": tenant_id,
            "collection": req.collection_name,
            "collection_display_name": collection_display_name,
            "high_level_topic": high_level_topic,
            **extra_meta,
        }

        result = await store.add_document(
            tenant_id=tenant_id,
            collection_name=req.collection_name,
            doc_id=doc_id,
            text=text,
            metadata=metadata,
        )

        if result.get("status") == "ok":
            ingested += 1

    return {"status": "ok", "ingested": ingested}
