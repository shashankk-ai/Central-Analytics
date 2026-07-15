"""Seeds the excluded-vendors list from the JW (job-work) locations excel.

Usage:
    .venv/bin/python -m scripts.seed_excluded_vendors [path/to/file.xlsx]

Safe to re-run: each row is upserted by its normalized vendor name.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from app.models.db import SessionLocal, init_db
from app.services.excluded_vendors_service import upsert_seed_vendor

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "seed" / "jw_excluded_vendors.xlsx"


def seed(path: Path) -> None:
    init_db()
    df = pd.read_excel(path)

    db = SessionLocal()
    created_or_updated = 0
    try:
        for row in df.to_dict("records"):
            company_name = str(row["Company Name"]).strip()
            if not company_name:
                continue
            upsert_seed_vendor(db, vendor_name=company_name, reason="Job-work (JW) vendor")
            created_or_updated += 1
    finally:
        db.close()

    print(f"Seeded {created_or_updated} excluded vendors from {path}")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    seed(path)
