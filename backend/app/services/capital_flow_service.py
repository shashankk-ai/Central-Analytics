"""Capital Flow (CCC) pillar — currently DPO only, sourced from PO_Report.

Column mapping confirmed with the business:
  PO date            -> "Take Order Orddate"
  PO value           -> "NEW LineNet"
  Business vertical  -> "Dimension"
  Product            -> "Description"
  Payment term       -> "Terms Description"
  Supplier            -> "PO Vendor Name"
  Row filter columns  -> "itemkey", "PONO"

Row filter: exclude rows where itemkey is blank, or PONO starts with "RE"
(a return, not a purchase order) instead of "PO".
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.calculators.ccc import DpoResult, compute_dpo
from app.connectors.zoho import ZohoAnalyticsConnector

PO_REPORT_VIEW_ID = "398702000006337002"

COL_PO_DATE = "Take Order Orddate"
COL_PO_VALUE = "NEW LineNet"
COL_BUSINESS_VERTICAL = "Dimension"
COL_PRODUCT = "Description"
COL_PAYMENT_TERM = "Terms Description"
COL_SUPPLIER = "PO Vendor Name"
COL_ITEMKEY = "itemkey"
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
