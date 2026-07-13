from datetime import date

import pandas as pd
import pytest

from app.calculators.ccc import compute_ccc, compute_dio, compute_dpo, compute_dso
from app.models.payment_terms import PaymentTermUpsert
from app.services.payment_terms_service import upsert_manual


def test_compute_dpo_weighted_average_with_known_terms(db_session):
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="30 Days PDC", instrument="Clean Credit", weighted_payable_days=30),
    )
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="60 Days PDC", instrument="Clean Credit", weighted_payable_days=60),
    )

    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 300_000],
            "payment_term": ["30 Days PDC", "60 Days PDC"],
        }
    )

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term")

    # DPO = (100000*30 + 300000*60) / (100000+300000) = 21,000,000 / 400,000 = 52.5
    assert result.dpo == pytest.approx(52.5)
    assert result.total_po_value == pytest.approx(400_000)
    assert result.terms_needing_review == []


def test_compute_dpo_auto_creates_and_flags_unknown_term(db_session):
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="30 Days PDC", instrument="Clean Credit", weighted_payable_days=30),
    )

    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 50_000],
            "payment_term": ["30 Days PDC", "20% Advance and 80% after 90 days"],
        }
    )

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term")

    # New term auto-calculated as 20%x0 + 80%x90 /100 = 72.0
    # DPO = (100000*30 + 50000*72) / 150000 = (3,000,000 + 3,600,000) / 150,000 = 44.0
    assert result.dpo == pytest.approx(44.0)
    assert len(result.terms_needing_review) == 1
    flagged = result.terms_needing_review[0]
    assert flagged.terms_description == "20% Advance and 80% after 90 days"
    assert flagged.weighted_payable_days == pytest.approx(72.0)
    assert flagged.affected_po_value == pytest.approx(50_000)
    assert flagged.newly_auto_created is True


def test_compute_dpo_excludes_blank_payment_term(db_session):
    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 25_000],
            "payment_term": ["30 Days PDC", None],
        }
    )

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term")

    assert result.dpo == pytest.approx(30.0)
    assert result.total_po_value == pytest.approx(100_000)
    assert result.blank_term_po_value == pytest.approx(25_000)
    assert result.blank_term_po_count == 1


def test_compute_dso_weighted_average_with_uncollected_invoice():
    invoice_df = pd.DataFrame(
        {
            "invoice_value": [200_000, 100_000],
            "invoice_date": [date(2026, 1, 1), date(2026, 1, 1)],
            "collection_date": [date(2026, 1, 31), None],  # 30 days
        }
    )

    result = compute_dso(
        invoice_df,
        value_col="invoice_value",
        invoice_date_col="invoice_date",
        collection_date_col="collection_date",
        as_of=date(2026, 2, 20),  # 50 days from invoice date for the uncollected row
    )

    # DSO = (200000*30 + 100000*50) / 300000 = (6,000,000 + 5,000,000)/300,000 = 36.666...
    assert result.dso == pytest.approx(36.6667, rel=1e-4)
    assert result.total_invoice_value == pytest.approx(300_000)


def test_compute_dio_matches_formula():
    # DIO = Inventory Value / (COGS / Days) = 900,000 / (2,700,000/90) = 900,000/30,000 = 30
    dio = compute_dio(total_inventory_value=900_000, total_cogs=2_700_000, days_in_period=90)
    assert dio == pytest.approx(30.0)


def test_compute_ccc_sums_correctly():
    result = compute_ccc(dio=30.0, dso=36.6667, dpo=52.5)
    assert result.ccc == pytest.approx(30.0 + 36.6667 - 52.5)
