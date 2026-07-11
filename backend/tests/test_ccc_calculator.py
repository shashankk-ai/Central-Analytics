from datetime import date

import pandas as pd
import pytest

from app.calculators.ccc import compute_ccc, compute_dio, compute_dpo, compute_dso
from app.models.payment_terms import PaymentTermsMaster, suggest_payable_days


def test_suggest_payable_days_standard_term():
    entry = suggest_payable_days("Net 30")
    assert entry is not None
    assert entry.payable_days == 30
    assert entry.is_two_step is False


def test_suggest_payable_days_two_step_term_default_rate():
    entry = suggest_payable_days("2/10 Net 30", early_pay_rate=0.35)
    assert entry is not None
    assert entry.is_two_step is True
    # 0.35 * 10 + 0.65 * 30 = 3.5 + 19.5 = 23.0
    assert entry.payable_days == pytest.approx(23.0)


def test_suggest_payable_days_unrecognized_term_returns_none():
    assert suggest_payable_days("Whenever convenient") is None


def test_compute_dpo_weighted_average_and_unknown_term_flagging():
    master = PaymentTermsMaster()
    master.add(suggest_payable_days("Net 30"))
    master.add(suggest_payable_days("Net 60"))

    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 300_000, 50_000],
            "payment_term": ["Net 30", "Net 60", "Net 90"],  # Net 90 is unknown
        }
    )

    result = compute_dpo(po_df, master, value_col="po_value", term_col="payment_term")

    # DPO = (100000*30 + 300000*60) / (100000+300000) = 21,000,000 / 400,000 = 52.5
    assert result.dpo == pytest.approx(52.5)
    assert result.included_po_value == pytest.approx(400_000)
    assert result.excluded_po_value == pytest.approx(50_000)
    assert len(result.unknown_terms) == 1
    assert result.unknown_terms[0].term == "Net 90"
    assert result.unknown_terms[0].affected_po_value == pytest.approx(50_000)


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
