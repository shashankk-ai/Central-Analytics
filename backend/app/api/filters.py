from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.connectors.zoho import ZohoAnalyticsConnector
from app.models.db import get_db
from app.services.capital_flow_service import fetch_po_report, get_filter_options
from config.settings import Settings, get_settings

router = APIRouter(prefix="/filters", tags=["filters"])


class FilterOptions(BaseModel):
    business_verticals: list[str] = []
    products: list[str] = []
    suppliers: list[str] = []
    customers: list[str] = []


@router.get("/options", response_model=FilterOptions)
async def get_global_filter_options(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> FilterOptions:
    # Sourced from PO_Report for now — the only pillar with live data.
    # Will pick up AR/inventory dimensions (and customers) once those
    # pillars are wired.
    connector = ZohoAnalyticsConnector(settings)
    po_df = await fetch_po_report(connector)
    capital_flow_options = get_filter_options(po_df, db)
    return FilterOptions(
        business_verticals=capital_flow_options.business_verticals,
        products=capital_flow_options.products,
        suppliers=capital_flow_options.suppliers,
        customers=[],
    )
