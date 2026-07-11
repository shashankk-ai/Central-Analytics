"""Payment terms master: the lookup table that resolves a raw payment-term
string (as it appears on a PO) to a number of payable days for DPO.

Terms not present in the master are "unknown" and must be surfaced to the
user via the Unknown Payment Term Protocol rather than silently dropped or
guessed at.
"""

from __future__ import annotations

import re

from pydantic import BaseModel

_STANDARD_TERM = re.compile(r"^\s*net\s*(\d+)\s*$", re.IGNORECASE)
_TWO_STEP_TERM = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*/\s*(\d+)\s+net\s*(\d+)\s*$", re.IGNORECASE)


class PaymentTermEntry(BaseModel):
    term: str
    payable_days: float
    is_two_step: bool = False
    discount_days: int | None = None
    base_days: int | None = None


class UnknownPaymentTerm(BaseModel):
    term: str
    affected_po_value: float
    affected_po_count: int


class PaymentTermsMaster:
    """In-memory lookup of payment-term string -> resolved payable days.

    Phase 1 will back this with the actual master dataset (Excel or Zoho
    Analytics table, location TBD) once the user confirms where it lives.
    """

    def __init__(self, entries: dict[str, PaymentTermEntry] | None = None) -> None:
        self._entries: dict[str, PaymentTermEntry] = entries or {}

    def resolve(self, term: str) -> PaymentTermEntry | None:
        return self._entries.get(_normalize(term))

    def add(self, entry: PaymentTermEntry) -> None:
        self._entries[_normalize(entry.term)] = entry

    def all(self) -> list[PaymentTermEntry]:
        return list(self._entries.values())


def _normalize(term: str) -> str:
    return " ".join(term.strip().lower().split())


def suggest_payable_days(term: str, early_pay_rate: float = 0.35) -> PaymentTermEntry | None:
    """Auto-suggests payable days for a common term pattern.

    Recognizes:
      - Standard terms, e.g. "Net 30" -> 30 payable days.
      - Two-step early-payment terms, e.g. "2/10 Net 30" ->
        Effective Days = early_pay_rate * discount_days + (1 - early_pay_rate) * base_days.

    Returns None if the term does not match either pattern — the caller
    must then treat it as unknown and prompt the user for the payable days.
    """
    two_step = _TWO_STEP_TERM.match(term)
    if two_step:
        discount_days = int(two_step.group(2))
        base_days = int(two_step.group(3))
        effective_days = early_pay_rate * discount_days + (1 - early_pay_rate) * base_days
        return PaymentTermEntry(
            term=term,
            payable_days=effective_days,
            is_two_step=True,
            discount_days=discount_days,
            base_days=base_days,
        )

    standard = _STANDARD_TERM.match(term)
    if standard:
        base_days = int(standard.group(1))
        return PaymentTermEntry(term=term, payable_days=float(base_days), is_two_step=False, base_days=base_days)

    return None
