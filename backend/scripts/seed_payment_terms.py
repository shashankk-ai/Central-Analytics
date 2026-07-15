"""Seeds the Payment Terms Master from the Scimplify-curated excel.

Usage:
    .venv/bin/python -m scripts.seed_payment_terms [path/to/file.xlsx]

Safe to re-run: each row is upserted by its normalized Terms Description.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from app.models.db import SessionLocal, init_db
from app.models.payment_terms import INSTRUMENTS, normalize_description
from app.services.payment_terms_service import upsert_seed_row

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "seed" / "payment_terms_master.xlsx"

# Netting/non-cash arrangements that are not a real payable and must not
# enter the DPO sum at all (excluded, not just given 0 days).
EXCLUDED_FROM_DPO_TERMS = {normalize_description("AR/AP Knock Off")}


def seed(path: Path) -> None:
    init_db()
    df = pd.read_excel(path)

    unknown_instruments = set(df["Instrument"].dropna().unique()) - set(INSTRUMENTS)
    if unknown_instruments:
        raise ValueError(f"Unrecognized instrument(s) in seed file: {unknown_instruments}. Expected one of {INSTRUMENTS}.")

    db = SessionLocal()
    created_or_updated = 0
    try:
        for row in df.to_dict("records"):
            terms_description = str(row["Terms Description"])
            upsert_seed_row(
                db,
                termskey=str(row["termskey"]) if pd.notna(row["termskey"]) else None,
                terms_description=terms_description,
                instrument=str(row["Instrument"]),
                weighted_payable_days=float(row["Weighted Payable Days"]),
                calculation_trace=str(row["Calculation"]) if pd.notna(row["Calculation"]) else None,
                remarks=str(row["Remarks"]) if pd.notna(row["Remarks"]) else None,
                excluded_from_dpo=normalize_description(terms_description) in EXCLUDED_FROM_DPO_TERMS,
            )
            created_or_updated += 1
    finally:
        db.close()

    print(f"Seeded {created_or_updated} payment terms from {path}")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    seed(path)
