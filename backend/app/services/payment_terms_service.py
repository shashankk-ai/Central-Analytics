from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.calculators.payment_term_parser import auto_calculate_weighted_days
from app.models.payment_terms import PaymentTerm, PaymentTermUpsert, normalize_description


def get_by_description(db: Session, terms_description: str) -> PaymentTerm | None:
    normalized = normalize_description(terms_description)
    return db.scalar(select(PaymentTerm).where(PaymentTerm.normalized_description == normalized))


def resolve_or_autocreate(db: Session, terms_description: str) -> tuple[PaymentTerm, bool]:
    """Looks up a term in the master; if missing, auto-calculates its
    weighted payable days from the text and inserts it, flagged for
    review. Returns (term, was_newly_created)."""
    existing = get_by_description(db, terms_description)
    if existing is not None:
        return existing, False

    parsed = auto_calculate_weighted_days(terms_description)
    term = PaymentTerm(
        termskey=None,
        terms_description=terms_description,
        normalized_description=normalize_description(terms_description),
        instrument=None,
        weighted_payable_days=parsed.weighted_payable_days,
        calculation_trace=parsed.calculation_trace,
        remarks="Auto-calculated on first sighting; needs instrument classification and review.",
        source="auto",
        needs_review=True,
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return term, True


def upsert_seed_row(
    db: Session,
    termskey: str | None,
    terms_description: str,
    instrument: str,
    weighted_payable_days: float,
    calculation_trace: str | None,
    remarks: str | None,
    excluded_from_dpo: bool = False,
) -> PaymentTerm:
    normalized = normalize_description(terms_description)
    existing = db.scalar(select(PaymentTerm).where(PaymentTerm.normalized_description == normalized))
    if existing is not None:
        existing.termskey = termskey
        existing.instrument = instrument
        existing.weighted_payable_days = weighted_payable_days
        existing.calculation_trace = calculation_trace
        existing.remarks = remarks
        existing.source = "seed"
        existing.needs_review = False
        existing.excluded_from_dpo = excluded_from_dpo
        db.commit()
        db.refresh(existing)
        return existing

    term = PaymentTerm(
        termskey=termskey,
        terms_description=terms_description,
        normalized_description=normalized,
        instrument=instrument,
        weighted_payable_days=weighted_payable_days,
        calculation_trace=calculation_trace,
        remarks=remarks,
        source="seed",
        needs_review=False,
        excluded_from_dpo=excluded_from_dpo,
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return term


def upsert_manual(db: Session, payload: PaymentTermUpsert) -> PaymentTerm:
    normalized = normalize_description(payload.terms_description)
    existing = db.scalar(select(PaymentTerm).where(PaymentTerm.normalized_description == normalized))
    if existing is not None:
        existing.instrument = payload.instrument
        existing.weighted_payable_days = payload.weighted_payable_days
        existing.remarks = payload.remarks
        existing.source = "manual"
        existing.needs_review = False
        existing.excluded_from_dpo = payload.excluded_from_dpo
        db.commit()
        db.refresh(existing)
        return existing

    term = PaymentTerm(
        termskey=None,
        terms_description=payload.terms_description,
        normalized_description=normalized,
        instrument=payload.instrument,
        weighted_payable_days=payload.weighted_payable_days,
        calculation_trace=None,
        remarks=payload.remarks,
        source="manual",
        needs_review=False,
        excluded_from_dpo=payload.excluded_from_dpo,
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return term


def list_all(db: Session) -> list[PaymentTerm]:
    return list(db.scalars(select(PaymentTerm).order_by(PaymentTerm.terms_description)))


def list_needing_review(db: Session) -> list[PaymentTerm]:
    return list(db.scalars(select(PaymentTerm).where(PaymentTerm.needs_review.is_(True))))
