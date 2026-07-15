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
(a return, not a purchase order) instead of "PO". Vendors in the excluded
list (job-work vendors) are dropped entirely — see ExcludedVendor.
"""

from __future__ import annotations

import time
from datetime import date

import pandas as pd
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.calculators.ccc import DpoResult, compute_dpo
from app.connectors.zoho import ZohoAnalyticsConnector
from app.models.excluded_vendors import normalize_vendor_name
from app.services.excluded_vendors_service import normalized_name_set

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

_PO_REPORT_CACHE_TTL_SECONDS = 120.0
_po_report_cache: dict[str, object] = {"data": None, "fetched_at": 0.0}


class CapitalFlowFilters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    business_verticals: list[str] = []
    products: list[str] = []
    suppliers: list[str] = []


class FilterOptions(BaseModel):
    business_verticals: list[str]
    products: list[str]
    suppliers: list[str]


def apply_po_report_row_filter(po_df: pd.DataFrame) -> pd.DataFrame:
    """Excludes rows with a blank itemkey or a PONO starting with "RE"."""
    itemkey_present = po_df[COL_ITEMKEY].notna() & (po_df[COL_ITEMKEY].astype(str).str.strip() != "")
    is_return = po_df[COL_PONO].astype(str).str.strip().str.upper().str.startswith("RE")
    return po_df[itemkey_present & ~is_return]


def apply_vendor_exclusion(po_df: pd.DataFrame, db: Session) -> pd.DataFrame:
    """Drops rows for vendors in the excluded-vendors list (job-work
    vendors whose commercial arrangement isn't a standard payable)."""
    excluded_names = normalized_name_set(db)
    if not excluded_names:
        return po_df
    is_excluded = po_df[COL_SUPPLIER].map(lambda v: normalize_vendor_name(str(v)) in excluded_names)
    return po_df[~is_excluded]


PO_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"


def apply_global_filters(po_df: pd.DataFrame, filters: CapitalFlowFilters) -> pd.DataFrame:
    mask = pd.Series(True, index=po_df.index)
    if filters.date_from or filters.date_to:
        # OrderDate is DD/MM/YYYY — pandas' default parser assumes MM/DD and
        # would silently swap month/day for any day <= 12 without an
        # explicit format. Verified against the live PO_Report export that
        # every row matches this exact format (2026-07-15).
        order_dates = pd.to_datetime(po_df[COL_PO_DATE], format=PO_DATE_FORMAT)
        if filters.date_from:
            mask &= order_dates >= pd.Timestamp(filters.date_from)
        if filters.date_to:
            mask &= order_dates <= pd.Timestamp(filters.date_to)
    if filters.business_verticals:
        mask &= po_df[COL_BUSINESS_VERTICAL].isin(filters.business_verticals)
    if filters.products:
        mask &= po_df[COL_PRODUCT].isin(filters.products)
    if filters.suppliers:
        mask &= po_df[COL_SUPPLIER].isin(filters.suppliers)
    return po_df[mask]


async def fetch_po_report(connector: ZohoAnalyticsConnector, force_refresh: bool = False) -> pd.DataFrame:
    """Fetches PO_Report, cached briefly in-process — a full export takes
    several seconds, and a single page load can trigger several calls
    (DPO, filter options, drill-downs)."""
    now = time.monotonic()
    cached = _po_report_cache["data"]
    if not force_refresh and cached is not None and (now - _po_report_cache["fetched_at"]) < _PO_REPORT_CACHE_TTL_SECONDS:
        return cached  # type: ignore[return-value]

    rows = await connector.fetch_view_data(PO_REPORT_VIEW_ID, selected_columns=PO_REPORT_COLUMNS)
    df = pd.DataFrame(rows, columns=PO_REPORT_COLUMNS)
    _po_report_cache["data"] = df
    _po_report_cache["fetched_at"] = now
    return df


def get_base_filtered_po_df(po_df: pd.DataFrame, db: Session) -> pd.DataFrame:
    """The row/vendor filters that always apply, regardless of the user's
    selected global filters — used both for the DPO calculation and for
    deriving the filter dropdown options."""
    filtered = apply_po_report_row_filter(po_df)
    return apply_vendor_exclusion(filtered, db)


def get_filter_options(po_df: pd.DataFrame, db: Session) -> FilterOptions:
    base = get_base_filtered_po_df(po_df, db)
    return FilterOptions(
        business_verticals=sorted(base[COL_BUSINESS_VERTICAL].dropna().astype(str).unique().tolist()),
        products=sorted(base[COL_PRODUCT].dropna().astype(str).unique().tolist()),
        suppliers=sorted(base[COL_SUPPLIER].dropna().astype(str).unique().tolist()),
    )


def calculate_dpo(po_df: pd.DataFrame, db: Session, filters: CapitalFlowFilters | None = None) -> DpoResult:
    filtered = get_base_filtered_po_df(po_df, db)
    if filters is not None:
        filtered = apply_global_filters(filtered, filters)
    filtered = filtered.copy()
    filtered[COL_PO_VALUE] = pd.to_numeric(filtered[COL_PO_VALUE], errors="coerce").fillna(0)

    month_series = pd.to_datetime(filtered[COL_PO_DATE], format=PO_DATE_FORMAT).dt.strftime("%Y-%m")

    return compute_dpo(
        filtered,
        db,
        value_col=COL_PO_VALUE,
        term_col=COL_PAYMENT_TERM,
        month_series=month_series,
        supplier_series=filtered[COL_SUPPLIER],
        business_unit_series=filtered[COL_BUSINESS_VERTICAL],
    )
