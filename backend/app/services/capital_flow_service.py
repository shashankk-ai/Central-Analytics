"""Capital Flow (CCC) pillar — currently DPO only, sourced from PO_Report.

Column mapping confirmed with the business (verified against the live
PO_Report schema on 2026-07-13 — several of the business's plain-English
names didn't match the actual Zoho column names, e.g. "NEW LineNet" is
really "Linenet in INR"):
  PO date            -> "OrderDate"
  PO value           -> "Linenet in INR" (currency-normalized; PO_Report
                         also has a raw "Linenet" in the vendor's original
                         currency, which would be wrong to sum directly)
  Business vertical  -> "Dimension"
  Product            -> "Description"
  Payment term       -> "Terms Description"
  Supplier           -> "Vendname"
  Row filter columns -> "ItemKey", "PONO"

Row filter: exclude rows where ItemKey is blank, or PONO starts with "RE"
(a return, not a purchase order) instead of "PO".
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.calculators.ccc import DpoResult, compute_dpo
from app.connectors.zoho import ZohoAnalyticsConnector

PO_REPORT_VIEW_ID = "398702000006337002"

COL_PO_DATE = "OrderDate"
COL_PO_VALUE = "Linenet in INR"
COL_BUSINESS_VERTICAL = "Dimension"
COL_PRODUCT = "Description"
COL_PAYMENT_TERM = "Terms Description"
COL_SUPPLIER = "Vendname"
COL_ITEMKEY = "ItemKey"
COL_PONO = "PONO"

PO_REPORT_COLUMNS = [
    COL_PO_DATE,
    COL_PO_VALUE,
    COL_BUSINESS_VERTICAL,
    COL_PRODUCT,
    COL_PAYMENT_TERM,
    COL_SUPPLIER,
    COL_ITEMKEY,
    COL_PONO,
]


def apply_po_report_row_filter(po_df: pd.DataFrame) -> pd.DataFrame:
    """Excludes rows with a blank itemkey or a PONO starting with "RE"."""
    itemkey_present = po_df[COL_ITEMKEY].notna() & (po_df[COL_ITEMKEY].astype(str).str.strip() != "")
    is_return = po_df[COL_PONO].astype(str).str.strip().str.upper().str.startswith("RE")
    return po_df[itemkey_present & ~is_return]


async def fetch_po_report(connector: ZohoAnalyticsConnector) -> pd.DataFrame:
    rows = await connector.fetch_view_data(PO_REPORT_VIEW_ID, selected_columns=PO_REPORT_COLUMNS)
    return pd.DataFrame(rows, columns=PO_REPORT_COLUMNS)


def calculate_dpo(po_df: pd.DataFrame, db: Session) -> DpoResult:
    filtered = apply_po_report_row_filter(po_df)
    filtered = filtered.copy()
    filtered[COL_PO_VALUE] = pd.to_numeric(filtered[COL_PO_VALUE], errors="coerce").fillna(0)
    return compute_dpo(filtered, db, value_col=COL_PO_VALUE, term_col=COL_PAYMENT_TERM)
