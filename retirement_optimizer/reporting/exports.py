from __future__ import annotations

from io import BytesIO

import pandas as pd


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Annual Plan")
    return buffer.getvalue()
