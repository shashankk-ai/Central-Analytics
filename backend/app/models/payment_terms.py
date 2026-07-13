"""Payment Terms Master: resolves a raw payment-term description (as it
appears in PO_Report's "Terms Description" column) to a weighted payable
days figure and a DPO instrument classification (Clean Credit / Advance /
LC / DA), for use in the DPO calculation.

Persisted in the app's own SQLite database (not Zoho) so it can be edited
freely at any time, per the build brief's Unknown Payment Term Protocol.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.db import Base

INSTRUMENTS = ("Clean Credit", "Advance", "LC", "DA")


class PaymentTerm(Base):
    __tablename__ = "payment_terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    termskey: Mapped[str | None] = mapped_column(String, nullable=True)
    terms_description: Mapped[str] = mapped_column(String, nullable=False)
    normalized_description: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    instrument: Mapped[str | None] = mapped_column(String, nullable=True)
    weighted_payable_days: Mapped[float] = mapped_column(Float, nullable=False)
    calculation_trace: Mapped[str | None] = mapped_column(String, nullable=True)
    remarks: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)  # "seed" | "auto" | "manual"
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class PaymentTermOut(BaseModel):
    id: int
    termskey: str | None
    terms_description: str
    instrument: str | None
    weighted_payable_days: float
    calculation_trace: str | None
    remarks: str | None
    source: str
    needs_review: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentTermUpsert(BaseModel):
    terms_description: str
    instrument: str
    weighted_payable_days: float
    remarks: str | None = None


def normalize_description(text: str) -> str:
    return " ".join(text.strip().lower().split())
