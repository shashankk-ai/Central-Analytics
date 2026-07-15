"""Cash Conversion Cycle calculation engine: DPO, DSO, DIO -> CCC.

Formulas are as specified in the build brief:
  DPO = SUM(PO Value x Payable Days) / SUM(PO Value)
  DSO = SUM(Invoice Value x Days Outstanding) / SUM(Invoice Value)
  DIO = Total Inventory Value / (Total COGS / Days in Period)
  CCC = DIO + DSO - DPO
"""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.payment_terms_service import resolve_or_autocreate


class TermNeedingReview(BaseModel):
    terms_description: str
    weighted_payable_days: float
    affected_po_value: float
    affected_po_count: int
    newly_auto_created: bool


class GroupedDpo(BaseModel):
    group: str
    po_value: float
    weighted_payable_days: float | None
    share_of_total_value_pct: float


TERM_BUCKET_BINS = [-0.01, 30, 60, 90, 120, float("inf")]
TERM_BUCKET_LABELS = ["0-30", "31-60", "61-90", "91-120", "120+"]


class DpoResult(BaseModel):
    dpo: float | None
    total_po_value: float
    blank_term_po_value: float
    blank_term_po_count: int
    ar_ap_excluded_po_value: float
    ar_ap_excluded_po_count: int
    terms_needing_review: list[TermNeedingReview]
    by_instrument: list[GroupedDpo]
    by_month: list[GroupedDpo]
    by_supplier: list[GroupedDpo]
    by_business_unit: list[GroupedDpo]
    by_term_bucket: list[GroupedDpo]


def _grouped_breakdown(
    value_series: pd.Series,
    days_series: pd.Series,
    group_series: pd.Series,
    total_value: float,
    top_n: int | None = None,
) -> list[GroupedDpo]:
    """Groups PO value + weighted payable days by an arbitrary category
    series aligned to the same index (instrument, month, supplier, ...).
    When `top_n` is set, the smallest groups by value are folded into
    "Other" rather than silently omitted."""
    frame = pd.DataFrame({"_value": value_series, "_days": days_series, "_group": group_series})
    results: list[GroupedDpo] = []
    for group, rows in frame.groupby("_group"):
        group_value = float(rows["_value"].sum())
        weighted_days = float((rows["_value"] * rows["_days"]).sum()) / group_value if group_value > 0 else None
        results.append(
            GroupedDpo(
                group=str(group),
                po_value=group_value,
                weighted_payable_days=weighted_days,
                share_of_total_value_pct=(group_value / total_value * 100) if total_value > 0 else 0.0,
            )
        )
    results.sort(key=lambda r: r.po_value, reverse=True)

    if top_n is not None and len(results) > top_n:
        kept, folded = results[:top_n], results[top_n:]
        other_value = sum(r.po_value for r in folded)
        other_weighted = sum(r.po_value * (r.weighted_payable_days or 0) for r in folded)
        kept.append(
            GroupedDpo(
                group="Other",
                po_value=other_value,
                weighted_payable_days=(other_weighted / other_value) if other_value > 0 else None,
                share_of_total_value_pct=(other_value / total_value * 100) if total_value > 0 else 0.0,
            )
        )
        return kept
    return results


class DsoResult(BaseModel):
    dso: float | None
    total_invoice_value: float


class CccResult(BaseModel):
    dio: float
    dso: float
    dpo: float
    ccc: float


def compute_dpo(
    po_df: pd.DataFrame,
    db: Session,
    value_col: str,
    term_col: str,
    month_series: pd.Series | None = None,
    supplier_series: pd.Series | None = None,
    business_unit_series: pd.Series | None = None,
) -> DpoResult:
    """DPO = SUM(PO Value x Payable Days) / SUM(PO Value).

    Every distinct payment term in `po_df` is resolved against the
    persistent Payment Terms Master; a term seen for the first time is
    auto-calculated from its text (see payment_term_parser) and inserted
    immediately, flagged for review, so a single new term never blocks or
    excludes rows from the calculation. Rows with a blank payment term, or
    a term explicitly flagged `excluded_from_dpo` (e.g. AR/AP Knock Off —
    a netting arrangement, not a real payable), are excluded and reported
    separately rather than silently dropped.

    `month_series`/`supplier_series`/`business_unit_series` are optional,
    already-derived grouping columns (aligned to `po_df`'s index) used to
    build the corresponding breakdowns — kept out of this function's own
    concern of parsing dates or knowing PO_Report's column names.
    """
    has_term = po_df[term_col].notna() & (po_df[term_col].astype(str).str.strip() != "")
    blank_df = po_df[~has_term]
    with_term_df = po_df[has_term]

    resolved: dict[str, object] = {}
    needing_review: list[TermNeedingReview] = []
    for term in with_term_df[term_col].unique():
        payment_term, newly_created = resolve_or_autocreate(db, term)
        resolved[term] = payment_term
        if payment_term.needs_review:
            group = with_term_df[with_term_df[term_col] == term]
            needing_review.append(
                TermNeedingReview(
                    terms_description=term,
                    weighted_payable_days=payment_term.weighted_payable_days,
                    affected_po_value=float(group[value_col].sum()),
                    affected_po_count=int(len(group)),
                    newly_auto_created=newly_created,
                )
            )

    is_ar_ap_excluded = with_term_df[term_col].map(lambda t: resolved[t].excluded_from_dpo)
    ar_ap_df = with_term_df[is_ar_ap_excluded]
    scoped_df = with_term_df[~is_ar_ap_excluded]

    days_series = scoped_df[term_col].map(lambda t: resolved[t].weighted_payable_days)
    total_value = float(scoped_df[value_col].sum())
    weighted_days = float((scoped_df[value_col] * days_series).sum())
    dpo = weighted_days / total_value if total_value > 0 else None

    instrument_series = scoped_df[term_col].map(lambda t: resolved[t].instrument or "Unclassified")
    by_instrument = _grouped_breakdown(scoped_df[value_col], days_series, instrument_series, total_value)

    bucket_series = pd.cut(days_series, bins=TERM_BUCKET_BINS, labels=TERM_BUCKET_LABELS)
    by_term_bucket = _grouped_breakdown(scoped_df[value_col], days_series, bucket_series, total_value)
    # pd.cut orders by bucket, not value — restore the day-range order for a bucket table.
    bucket_order = {label: i for i, label in enumerate(TERM_BUCKET_LABELS)}
    by_term_bucket.sort(key=lambda r: bucket_order.get(r.group, len(TERM_BUCKET_LABELS)))

    by_month = (
        _grouped_breakdown(scoped_df[value_col], days_series, month_series.loc[scoped_df.index], total_value)
        if month_series is not None
        else []
    )
    by_month.sort(key=lambda r: r.group)  # chronological, not by value

    by_supplier = (
        _grouped_breakdown(scoped_df[value_col], days_series, supplier_series.loc[scoped_df.index], total_value, top_n=15)
        if supplier_series is not None
        else []
    )

    by_business_unit = (
        _grouped_breakdown(scoped_df[value_col], days_series, business_unit_series.loc[scoped_df.index], total_value)
        if business_unit_series is not None
        else []
    )

    return DpoResult(
        dpo=dpo,
        total_po_value=total_value,
        blank_term_po_value=float(blank_df[value_col].sum()),
        blank_term_po_count=int(len(blank_df)),
        ar_ap_excluded_po_value=float(ar_ap_df[value_col].sum()),
        ar_ap_excluded_po_count=int(len(ar_ap_df)),
        terms_needing_review=needing_review,
        by_instrument=by_instrument,
        by_month=by_month,
        by_supplier=by_supplier,
        by_business_unit=by_business_unit,
        by_term_bucket=by_term_bucket,
    )


def compute_dso(
    invoice_df: pd.DataFrame,
    value_col: str,
    invoice_date_col: str,
    collection_date_col: str,
    as_of: date | None = None,
) -> DsoResult:
    """DSO = SUM(Invoice Value x Days Outstanding) / SUM(Invoice Value).

    Days Outstanding runs from the invoice date to its collection date, or
    to `as_of` (defaults to today) when the invoice is still uncollected.
    """
    if invoice_df.empty:
        return DsoResult(dso=None, total_invoice_value=0.0)

    # dayfirst=True: Scimplify's Zoho date columns are DD/MM/YYYY (confirmed
    # for PO_Report's OrderDate) — without this, pandas' default MM/DD
    # assumption silently swaps month/day for any day <= 12.
    as_of_ts = pd.Timestamp(as_of or datetime.now().date())
    invoice_dates = pd.to_datetime(invoice_df[invoice_date_col], dayfirst=True)
    collection_dates = pd.to_datetime(invoice_df[collection_date_col], dayfirst=True)
    end_dates = collection_dates.fillna(as_of_ts)
    days_outstanding = (end_dates - invoice_dates).dt.days

    total_value = float(invoice_df[value_col].sum())
    weighted_days = float((invoice_df[value_col] * days_outstanding).sum())
    dso = weighted_days / total_value if total_value > 0 else None

    return DsoResult(dso=dso, total_invoice_value=total_value)


def compute_dio(total_inventory_value: float, total_cogs: float, days_in_period: int) -> float:
    """DIO = Total Inventory Value / (Total COGS / Days in Period)."""
    if total_cogs <= 0 or days_in_period <= 0:
        return 0.0
    daily_cogs = total_cogs / days_in_period
    return total_inventory_value / daily_cogs


def compute_ccc(dio: float, dso: float, dpo: float) -> CccResult:
    """CCC = DIO + DSO - DPO."""
    return CccResult(dio=dio, dso=dso, dpo=dpo, ccc=dio + dso - dpo)
