from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/filters", tags=["filters"])


class FilterOptions(BaseModel):
    products: list[str] = []
    suppliers: list[str] = []
    customers: list[str] = []


@router.get("/options", response_model=FilterOptions)
async def get_filter_options() -> FilterOptions:
    # Returns empty until the Phase 1 data source spec (PO/AR datasets and
    # column names) is confirmed and wired in app/services.
    return FilterOptions()
