import re
from io import BytesIO
from typing import List

import pandas as pd


# Simple regexes for date-like values (covers 2022/1/12, 2023-03-05, 01-2024, etc.)
DATE_VALUE_PATTERNS = [
    re.compile(r"\b20[0-3]\d[/-]\d{1,2}[/-]\d{1,2}\b"),  # 2022/1/12, 2023-03-05
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]20[0-3]\d\b"),  # 1/12/2023, 01-03-2024
    re.compile(r"\b20[0-3]\d[/-]\d{1,2}\b"),             # 2023-01, 2024/3
    re.compile(r"\b\d{1,2}[/-]20[0-3]\d\b"),             # 01-2023, 3/2024
]

# Common month name variants
MONTH_NAMES = {
    "jan", "january",
    "feb", "february",
    "mar", "march",
    "apr", "april",
    "may",
    "jun", "june",
    "jul", "july",
    "aug", "august",
    "sep", "sept", "september",
    "oct", "october",
    "nov", "november",
    "dec", "december",
}


def _looks_like_month(val: str) -> bool:
    v = str(val).strip().lower()
    return v in MONTH_NAMES


def _looks_like_date_string(val: str) -> bool:
    s = str(val).strip()
    if not s:
        return False
    # quick month-name check, e.g. "Jan-23"
    if any(m in s.lower() for m in MONTH_NAMES):
        return True
    # regex patterns
    for pat in DATE_VALUE_PATTERNS:
        if pat.search(s):
            return True
    return False




def _describe_excel_sheet_shape(df: pd.DataFrame) -> str:
    """
     Simple, format-agnostic heuristic that returns a one-line description
     of the sheet contents based on column types. 
    """
    if df.empty:
        return "This sheet is empty."
    
    num_cols = 0
    text_cols = 0
    for col in df.columns:
        series = df[col]
        # Check a sample to infer numeric-ness
        non_na = series.dropna()
        if non_na.empty:
            continue
        
        # Heuristic: if majority of non-NA values are numeric -> numeric col
        numeric_fraction = pd.to_numeric(non_na, errors="coerce").notna().mean()
        if numeric_fraction > 0.7:
            num_cols += 1
        else:
            text_cols += 1
            
    if num_cols >= 2 and text_cols >= 1:
        return (
            "This sheet contains tabular data with at least one label column and multiple numeric columns. "
            "Which can be used for aggregations, comparisons, and time-series style analysis."
        )
    
    if num_cols >= 1 and text_cols == 0:
        return "This sheet contains mainly numeric tabular data."
    if text_cols >= 1 and num_cols == 0:
        return "This sheet contains mainly text data"
    return "This sheet contains a mix of text and numeric data."



def _extract_excel_with_pandas(raw_bytes: bytes, filename: str) -> str:
    """
    Extracts human-readable text from an Excel file.

    - Reads all sheets using pandas.
    - Skips empty sheets.
    - For each sheet, add a one-line summary based on column types.
    - For each non-NaN row, emits `Column: value` pairs grouped by row.
      Date-like columns (Year/Month/Date/Period and date-ish values) are emitted first.
    - Inserts blank lines between year blocks when a Year-like column exists.
    - Separates sheets with a blank line.
    """
    buffer = BytesIO(raw_bytes)

    # sheet_name=None -> dict[str, DataFrame] for all sheets.
    sheets = pd.read_excel(buffer, sheet_name=None, engine="openpyxl")

    sheet_chunks: List[str] = []

    # Column names that strongly suggest date-like content
    DATE_COL_NAMES = {
        "year",
        "month",
        "date",
        "period",
        "posting_date",
        "txn_date",
        "transaction_date",
    }

    for sheet_name, df in sheets.items():
        if df.empty:
            continue

        df = df.copy()
        df.columns = [str(c).strip() for c in df.columns]

        shape_line = _describe_excel_sheet_shape(df)

        row_lines: List[str] = []

        # Detect if we have an explicit "Year" column
        lower_cols = [c.lower() for c in df.columns]
        has_year_col = any(c == "year" for c in lower_cols)

        last_year = None

        for _, row in df.iterrows():
            date_parts: List[str] = []
            other_parts: List[str] = []

            current_year = None

            for col, val in row.items():
                if pd.isna(val):
                    continue

                col_str = str(col).strip()
                val_str = str(val).strip()

                col_lower = col_str.lower()

                # Try to capture year value explicitly if column name looks like "year"
                if col_lower == "year":
                    current_year = val_str

                # Decide if this column/value pair is date-like
                is_date_col_name = col_lower in DATE_COL_NAMES
                is_date_value = (
                    _looks_like_month(val_str) or _looks_like_date_string(val_str)
                )

                if is_date_col_name or is_date_value:
                    date_parts.append(f"{col_str}: {val_str}")
                else:
                    other_parts.append(f"{col_str}: {val_str}")

            if not date_parts and not other_parts:
                continue

            # Insert a blank line when the year changes (for better year grouping)
            if has_year_col and last_year is not None and current_year is not None and current_year != last_year:
                row_lines.append("")

            ordered_parts = date_parts + other_parts
            row_lines.append("  |  ".join(ordered_parts))

            if current_year is not None:
                last_year = current_year if last_year is None else last_year

        if not row_lines:
            continue

        clean_sheet_name = str(sheet_name).strip()
        sheet_text = (
            f"Sheet: {clean_sheet_name}\n"
            f"{shape_line}\n"
            + "\n".join(row_lines)
        )
        sheet_chunks.append(sheet_text)

    return "\n\n".join(sheet_chunks)
