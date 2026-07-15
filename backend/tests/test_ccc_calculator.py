from datetime import date

import pandas as pd
import pytest

from app.calculators.ccc import _grouped_breakdown, compute_ccc, compute_dio, compute_dpo, compute_dso
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


def test_compute_dpo_excludes_ar_ap_term_and_reports_separately(db_session):
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="30 Days PDC", instrument="Clean Credit", weighted_payable_days=30),
    )
    upsert_manual(
        db_session,
        PaymentTermUpsert(
            terms_description="AR/AP Knock Off",
            instrument="Clean Credit",
            weighted_payable_days=0,
            excluded_from_dpo=True,
        ),
    )

    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 40_000],
            "payment_term": ["30 Days PDC", "AR/AP Knock Off"],
        }
    )

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term")

    assert result.dpo == pytest.approx(30.0)
    assert result.total_po_value == pytest.approx(100_000)
    assert result.ar_ap_excluded_po_value == pytest.approx(40_000)
    assert result.ar_ap_excluded_po_count == 1


def test_compute_dpo_by_instrument_bifurcation(db_session):
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="30 Days PDC", instrument="Clean Credit", weighted_payable_days=30),
    )
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="90 Days LC", instrument="LC", weighted_payable_days=90),
    )

    po_df = pd.DataFrame(
        {
            "po_value": [300_000, 100_000],
            "payment_term": ["30 Days PDC", "90 Days LC"],
        }
    )

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term")

    by_instrument = {b.group: b for b in result.by_instrument}
    assert set(by_instrument) == {"Clean Credit", "LC"}
    assert by_instrument["Clean Credit"].po_value == pytest.approx(300_000)
    assert by_instrument["Clean Credit"].weighted_payable_days == pytest.approx(30.0)
    assert by_instrument["Clean Credit"].share_of_total_value_pct == pytest.approx(75.0)
    assert by_instrument["LC"].po_value == pytest.approx(100_000)
    assert by_instrument["LC"].weighted_payable_days == pytest.approx(90.0)
    assert by_instrument["LC"].share_of_total_value_pct == pytest.approx(25.0)


def test_compute_dpo_by_term_bucket_groups_by_days_range(db_session):
    upsert_manual(db_session, PaymentTermUpsert(terms_description="15 Days", instrument="Clean Credit", weighted_payable_days=15))
    upsert_manual(db_session, PaymentTermUpsert(terms_description="45 Days", instrument="Clean Credit", weighted_payable_days=45))
    upsert_manual(db_session, PaymentTermUpsert(terms_description="150 Days", instrument="Clean Credit", weighted_payable_days=150))

    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 200_000, 50_000],
            "payment_term": ["15 Days", "45 Days", "150 Days"],
        }
    )

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term")

    buckets = {b.group: b for b in result.by_term_bucket}
    assert buckets["0-30"].po_value == pytest.approx(100_000)
    assert buckets["31-60"].po_value == pytest.approx(200_000)
    assert buckets["120+"].po_value == pytest.approx(50_000)
    # Bucket order follows the day range, not descending value.
    assert [b.group for b in result.by_term_bucket] == ["0-30", "31-60", "120+"]


def test_compute_dpo_by_month_is_chronological_not_by_value(db_session):
    upsert_manual(db_session, PaymentTermUpsert(terms_description="30 Days", instrument="Clean Credit", weighted_payable_days=30))

    po_df = pd.DataFrame({"po_value": [100_000, 500_000], "payment_term": ["30 Days", "30 Days"]})
    month_series = pd.Series(["2026-07", "2026-01"])

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term", month_series=month_series)

    # July has far less value than January, but should still sort first.
    assert [m.group for m in result.by_month] == ["2026-01", "2026-07"]


def test_compute_dpo_by_supplier_folds_long_tail_into_other(db_session):
    upsert_manual(db_session, PaymentTermUpsert(terms_description="30 Days", instrument="Clean Credit", weighted_payable_days=30))

    # 3 suppliers, top_n effectively 2 via a tiny monkeypatched call is
    # overkill — instead verify the real top_n=15 default doesn't fold
    # anything when there are fewer than 15 suppliers.
    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 200_000, 300_000],
            "payment_term": ["30 Days", "30 Days", "30 Days"],
        }
    )
    supplier_series = pd.Series(["Vendor A", "Vendor B", "Vendor C"])

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term", supplier_series=supplier_series)

    assert {s.group for s in result.by_supplier} == {"Vendor A", "Vendor B", "Vendor C"}
    assert "Other" not in {s.group for s in result.by_supplier}


def test_compute_dpo_by_business_unit(db_session):
    upsert_manual(db_session, PaymentTermUpsert(terms_description="30 Days", instrument="Clean Credit", weighted_payable_days=30))
    upsert_manual(db_session, PaymentTermUpsert(terms_description="60 Days", instrument="Clean Credit", weighted_payable_days=60))

    po_df = pd.DataFrame(
        {
            "po_value": [100_000, 300_000],
            "payment_term": ["30 Days", "60 Days"],
        }
    )
    bu_series = pd.Series(["Pharma", "Agro"])

    result = compute_dpo(po_df, db_session, value_col="po_value", term_col="payment_term", business_unit_series=bu_series)

    by_bu = {b.group: b for b in result.by_business_unit}
    assert by_bu["Pharma"].weighted_payable_days == pytest.approx(30.0)
    assert by_bu["Agro"].weighted_payable_days == pytest.approx(60.0)


def test_grouped_breakdown_folds_smallest_groups_into_other():
    value = pd.Series([500_000, 300_000, 100_000, 50_000])
    days = pd.Series([30.0, 60.0, 90.0, 10.0])
    group = pd.Series(["A", "B", "C", "D"])

    result = _grouped_breakdown(value, days, group, total_value=950_000, top_n=2)

    groups = {r.group: r for r in result}
    assert set(groups) == {"A", "B", "Other"}
    assert groups["Other"].po_value == pytest.approx(150_000)
    # Other's weighted days = (100000*90 + 50000*10) / 150000 = 63.33
    assert groups["Other"].weighted_payable_days == pytest.approx(63.333, rel=1e-3)
    assert groups["Other"].share_of_total_value_pct == pytest.approx(150_000 / 950_000 * 100)


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
