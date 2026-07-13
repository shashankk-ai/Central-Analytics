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


class DpoResult(BaseModel):
    dpo: float | None
    total_po_value: float
    blank_term_po_value: float
    blank_term_po_count: int
    terms_needing_review: list[TermNeedingReview]


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
) -> DpoResult:
    """DPO = SUM(PO Value x Payable Days) / SUM(PO Value).

    Every distinct payment term in `po_df` is resolved against the
    persistent Payment Terms Master; a term seen for the first time is
    auto-calculated from its text (see payment_term_parser) and inserted
    immediately, flagged for review, so a single new term never blocks or
    excludes rows from the calculation. Rows with a blank payment term are
    excluded and reported separately, since there's no text to resolve.
    """
    has_term = po_df[term_col].notna() & (po_df[term_col].astype(str).str.strip() != "")
    blank_df = po_df[~has_term]
    scoped_df = po_df[has_term]

    resolved_days: dict[str, float] = {}
    needing_review: list[TermNeedingReview] = []
    for term in scoped_df[term_col].unique():
        payment_term, newly_created = resolve_or_autocreate(db, term)
        resolved_days[term] = payment_term.weighted_payable_days
        if payment_term.needs_review:
            group = scoped_df[scoped_df[term_col] == term]
            needing_review.append(
                TermNeedingReview(
                    terms_description=term,
                    weighted_payable_days=payment_term.weighted_payable_days,
                    affected_po_value=float(group[value_col].sum()),
                    affected_po_count=int(len(group)),
                    newly_auto_created=newly_created,
                )
            )

    days_series = scoped_df[term_col].map(resolved_days)
    total_value = float(scoped_df[value_col].sum())
    weighted_days = float((scoped_df[value_col] * days_series).sum())
    dpo = weighted_days / total_value if total_value > 0 else None

    return DpoResult(
        dpo=dpo,
        total_po_value=total_value,
        blank_term_po_value=float(blank_df[value_col].sum()),
        blank_term_po_count=int(len(blank_df)),
        terms_needing_review=needing_review,
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

    as_of_ts = pd.Timestamp(as_of or datetime.now().date())
    invoice_dates = pd.to_datetime(invoice_df[invoice_date_col])
    collection_dates = pd.to_datetime(invoice_df[collection_date_col])
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
