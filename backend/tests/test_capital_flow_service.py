import pandas as pd
import pytest

from app.models.payment_terms import PaymentTermUpsert
from app.services.capital_flow_service import (
    COL_ITEMKEY,
    COL_PAYMENT_TERM,
    COL_PO_VALUE,
    COL_PONO,
    apply_po_report_row_filter,
    calculate_dpo,
)
from app.services.payment_terms_service import upsert_manual


def _po_row(itemkey, pono, value=1000, term="30 Days PDC"):
    return {
        "Take Order Orddate": "2026-01-01",
        COL_PO_VALUE: value,
        "Dimension": "Pharma",
        "Description": "Test Product",
        COL_PAYMENT_TERM: term,
        "PO Vendor Name": "Test Vendor",
        COL_ITEMKEY: itemkey,
        COL_PONO: pono,
    }


def test_excludes_blank_itemkey_and_re_prefixed_pono():
    po_df = pd.DataFrame(
        [
            _po_row("ITEM1", "PO12345"),  # keep
            _po_row("", "PO12346"),  # blank itemkey -> exclude
            _po_row(None, "PO12347"),  # null itemkey -> exclude
            _po_row("ITEM2", "RE00001"),  # return -> exclude
            _po_row("ITEM3", "re00002"),  # case-insensitive return -> exclude
            _po_row("ITEM4", "PO12348"),  # keep
        ]
    )

    result = apply_po_report_row_filter(po_df)

    assert len(result) == 2
    assert set(result[COL_ITEMKEY]) == {"ITEM1", "ITEM4"}


def test_calculate_dpo_applies_filter_then_computes(db_session):
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="30 Days PDC", instrument="Clean Credit", weighted_payable_days=30),
    )
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="60 Days PDC", instrument="Clean Credit", weighted_payable_days=60),
    )

    po_df = pd.DataFrame(
        [
            _po_row("ITEM1", "PO1", value=100_000, term="30 Days PDC"),
            _po_row("ITEM2", "PO2", value=300_000, term="60 Days PDC"),
            _po_row("ITEM3", "RE1", value=999_999, term="30 Days PDC"),  # excluded: return
            _po_row("", "PO3", value=999_999, term="30 Days PDC"),  # excluded: blank itemkey
        ]
    )

    result = calculate_dpo(po_df, db_session)

    # Same figures as the known-terms DPO test: (100000*30 + 300000*60) / 400000 = 52.5
    assert result.dpo == pytest.approx(52.5)
    assert result.total_po_value == pytest.approx(400_000)
