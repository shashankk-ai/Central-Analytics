import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.payment_terms import PaymentTermOut, PaymentTermUpsert
from app.services.payment_terms_service import list_all, list_needing_review, upsert_manual

router = APIRouter(prefix="/payment-terms", tags=["payment-terms"])

EXPORT_COLUMNS = [
    "termskey",
    "terms_description",
    "instrument",
    "weighted_payable_days",
    "calculation_trace",
    "remarks",
    "source",
    "needs_review",
    "excluded_from_dpo",
    "updated_at",
]


@router.get("", response_model=list[PaymentTermOut])
def get_all(db: Session = Depends(get_db)):
    return list_all(db)


@router.get("/needing-review", response_model=list[PaymentTermOut])
def get_needing_review(db: Session = Depends(get_db)):
    return list_needing_review(db)


@router.get("/export")
def export_csv(db: Session = Depends(get_db)):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_COLUMNS)
    writer.writeheader()
    for term in list_all(db):
        writer.writerow({col: getattr(term, col) for col in EXPORT_COLUMNS})
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=payment_terms_master.csv"},
    )


@router.put("", response_model=PaymentTermOut)
def upsert(payload: PaymentTermUpsert, db: Session = Depends(get_db)):
    return upsert_manual(db, payload)
