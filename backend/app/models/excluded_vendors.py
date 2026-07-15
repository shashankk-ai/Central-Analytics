"""Vendors excluded from DPO (and other capital-flow calculations) — e.g.
job-work (JW) vendors, whose commercial arrangement isn't a standard
payable and would distort the calculation if included.

Persisted like the Payment Terms Master so the list can be edited without
a code change.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.db import Base
from app.models.payment_terms import normalize_description


class ExcludedVendor(Base):
    __tablename__ = "excluded_vendors"

    id: Mapped[int] = mapped_column(primary_key=True)
    vendor_name: Mapped[str] = mapped_column(String, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)  # "seed" | "manual"
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ExcludedVendorOut(BaseModel):
    id: int
    vendor_name: str
    reason: str | None
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


def normalize_vendor_name(name: str) -> str:
    return normalize_description(name)
