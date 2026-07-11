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

from app.models.payment_terms import PaymentTermsMaster, UnknownPaymentTerm


class DpoResult(BaseModel):
    dpo: float | None
    included_po_value: float
    excluded_po_value: float
    unknown_terms: list[UnknownPaymentTerm]


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
    terms_master: PaymentTermsMaster,
    value_col: str,
    term_col: str,
) -> DpoResult:
    """DPO = SUM(PO Value x Payable Days) / SUM(PO Value), excluding rows
    whose payment term is not in the master (flagged as unknown, not
    silently dropped without a trace)."""
    resolved_days = po_df[term_col].map(lambda term: terms_master.resolve(term))
    is_known = resolved_days.notna()

    known_df = po_df[is_known]
    known_days = resolved_days[is_known].map(lambda entry: entry.payable_days)
    included_value = float(known_df[value_col].sum())
    weighted_days = float((known_df[value_col] * known_days).sum())
    dpo = weighted_days / included_value if included_value > 0 else None

    unknown_df = po_df[~is_known]
    excluded_value = float(unknown_df[value_col].sum())
    unknown_terms = [
        UnknownPaymentTerm(
            term=term,
            affected_po_value=float(group[value_col].sum()),
            affected_po_count=int(len(group)),
        )
        for term, group in unknown_df.groupby(term_col)
    ]

    return DpoResult(
        dpo=dpo,
        included_po_value=included_value,
        excluded_po_value=excluded_value,
        unknown_terms=unknown_terms,
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
