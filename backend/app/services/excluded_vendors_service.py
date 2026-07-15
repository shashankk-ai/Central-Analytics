from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.excluded_vendors import ExcludedVendor, normalize_vendor_name


def upsert_seed_vendor(db: Session, vendor_name: str, reason: str | None) -> ExcludedVendor:
    normalized = normalize_vendor_name(vendor_name)
    existing = db.scalar(select(ExcludedVendor).where(ExcludedVendor.normalized_name == normalized))
    if existing is not None:
        existing.vendor_name = vendor_name
        existing.reason = reason
        db.commit()
        db.refresh(existing)
        return existing

    vendor = ExcludedVendor(vendor_name=vendor_name, normalized_name=normalized, reason=reason, source="seed")
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def list_all(db: Session) -> list[ExcludedVendor]:
    return list(db.scalars(select(ExcludedVendor).order_by(ExcludedVendor.vendor_name)))


def normalized_name_set(db: Session) -> set[str]:
    return set(db.scalars(select(ExcludedVendor.normalized_name)))
