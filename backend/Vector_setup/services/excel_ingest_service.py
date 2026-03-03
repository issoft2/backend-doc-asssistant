import logging
import pandas as pd
from io import BytesIO
from fastapi import HTTPException, status

from Vector_setup.services.extracting_excel_document_service import _extract_excel_with_pandas
from Vector_setup.base.db_setup_management import MultiTenantChromaStoreManager

logger = logging.getLogger(__name__)

EXCEL_EXTENSIONS = (".xlsx", ".xlsm", ".xls")


# Allow the spreadsheet extracted to by ingested sheet by sheet 
# especially when the data is hug
async def ingest_excel_by_sheet(
        *,
        raw_bytes: bytes,
        original_name: str,
        synthetic_filename: str,
        doc_id: str,
        metadata: dict,
        tenant_id: str,
        collection_name: str,
        store: MultiTenantChromaStoreManager,
) -> list[str]:
    """
    Ingest an Excel file sheet by sheet into the vector store.
    Returns a list of successfully ingested sheet names.
    Raises HTTPExecption if no sheets could be ingested.
    """
    sheets: dict = pd.read_excel(
        BytesIO(raw_bytes),
        sheet_name=None,
        engine="openpyxl"
    )

    ingested_sheets = []

    for sheet_name, df in sheets.items():
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            continue

        sheet_name = sheet_name[:31]   
        # Write sheet back to bytes so we can reuse the existing extractor
        sheet_bytes = BytesIO()
        with pd.ExcelWriter(sheet_bytes, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)

        sheet_text = _extract_excel_with_pandas(sheet_bytes.getvalue(), synthetic_filename)
        if not sheet_text.strip():
            continue

        sheet_doc_id = f"{doc_id}_{sheet_name.replace(' ', '_')}"

        result = await store.add_document(
            tenant_id=tenant_id,
            collection_name=collection_name,
            doc_id=sheet_doc_id,
            text=sheet_text,
            metadata={
                **metadata,
                "sheet_name": sheet_name,
                "doc_id": sheet_doc_id,
                "filename": f"{original_name} > {sheet_name}"
            },
        )

        if result.get("status") != "ok":
            logger.warning(f"Sheet '{sheet_name}' failed to index: {result.get('message')}")
            continue

        ingested_sheets.append(sheet_name)


    if not ingested_sheets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No sheets could be ingested from the Excel file."
        )
    return ingested_sheets             
             