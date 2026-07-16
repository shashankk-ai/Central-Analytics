from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.calculators.ccc import DpoResult
from app.connectors.zoho import get_shared_connector
from app.models.db import get_db
from app.services.capital_flow_service import CapitalFlowFilters, calculate_dpo, fetch_po_report
from config.settings import Settings, get_settings

router = APIRouter(prefix="/capital-flow", tags=["capital-flow"])


@router.get("/dpo", response_model=DpoResult)
async def get_dpo(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    business_verticals: list[str] = Query([]),
    products: list[str] = Query([]),
    suppliers: list[str] = Query([]),
):
    connector = get_shared_connector(settings)
    po_df = await fetch_po_report(connector)
    filters = CapitalFlowFilters(
        date_from=date_from,
        date_to=date_to,
        business_verticals=business_verticals,
        products=products,
        suppliers=suppliers,
    )
    return calculate_dpo(po_df, db, filters)
