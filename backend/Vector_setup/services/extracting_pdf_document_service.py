

from typing import List
import fitz  # PyMuPDF


#  ---------- Pdf Text extraction helpers ----------

def _extract_pdf_with_pymupdf(raw_bytes: bytes) -> str:
    parts: List[str] = []

    with fitz.open(stream=raw_bytes, filetype="pdf") as doc:  # type: ignore[arg-type]
        for page_idx, page  in  enumerate(doc, start=1):
            text = page.get_text("text") or ""
            if text.strip():
                parts.append(text.strip())

            try:
                tables = page.find_tables()
            except Exception:
                tables = None

            if tables:
                for table_idx, table in enumerate(tables.tables, start=1):
                    try:
                        md = table.to_markdown()
                    except Exception:
                        rows = []
                        for row in table.extract():
                            rows.append(" | ".join(cell or "" for cell in row))
                        md = "\n".join(rows)

                    if md.strip():
                        header = (
                            f"Table on page {page_idx}, index {table_idx}. "
                            "This is tabular data that can be used for lookups, comparisons, or aggregations."
                        )
                        parts.append(header)
                        parts.append(md.strip())

    return "\n\n".join(parts)
