from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.payment_terms import PaymentTermOut, PaymentTermUpsert
from app.services.payment_terms_service import list_all, list_needing_review, upsert_manual

router = APIRouter(prefix="/payment-terms", tags=["payment-terms"])


@router.get("", response_model=list[PaymentTermOut])
def get_all(db: Session = Depends(get_db)):
    return list_all(db)


@router.get("/needing-review", response_model=list[PaymentTermOut])
def get_needing_review(db: Session = Depends(get_db)):
    return list_needing_review(db)


@router.put("", response_model=PaymentTermOut)
def upsert(payload: PaymentTermUpsert, db: Session = Depends(get_db)):
    return upsert_manual(db, payload)
