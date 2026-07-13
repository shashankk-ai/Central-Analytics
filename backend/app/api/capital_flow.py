from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.calculators.ccc import DpoResult
from app.connectors.zoho import ZohoAnalyticsConnector
from app.models.db import get_db
from app.services.capital_flow_service import calculate_dpo, fetch_po_report
from config.settings import Settings, get_settings

router = APIRouter(prefix="/capital-flow", tags=["capital-flow"])


@router.get("/dpo", response_model=DpoResult)
async def get_dpo(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    connector = ZohoAnalyticsConnector(settings)
    po_df = await fetch_po_report(connector)
    return calculate_dpo(po_df, db)
