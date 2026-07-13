from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import capital_flow, filters, health, payment_terms
from app.models.db import init_db
from config.settings import get_settings

settings = get_settings()

app = FastAPI(title="Scimplify Central Analytics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health.router)
app.include_router(filters.router)
app.include_router(payment_terms.router)
app.include_router(capital_flow.router)
