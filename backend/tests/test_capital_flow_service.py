import pandas as pd
import pytest

from app.models.payment_terms import PaymentTermUpsert
from app.services.capital_flow_service import (
    COL_BUSINESS_VERTICAL,
    COL_ITEMKEY,
    COL_PAYMENT_TERM,
    COL_PO_DATE,
    COL_PO_VALUE,
    COL_PONO,
    COL_PRODUCT,
    COL_SUPPLIER,
    CapitalFlowFilters,
    apply_global_filters,
    apply_po_report_row_filter,
    apply_vendor_exclusion,
    calculate_dpo,
    get_filter_options,
)
from app.services.excluded_vendors_service import upsert_seed_vendor
from app.services.payment_terms_service import upsert_manual


def _po_row(itemkey, pono, value=1000, term="30 Days PDC", vendor="Test Vendor", vertical="Pharma", product="Test Product", order_date="2026-01-01"):
    return {
        COL_PO_DATE: order_date,
        COL_PO_VALUE: value,
        COL_BUSINESS_VERTICAL: vertical,
        COL_PRODUCT: product,
        COL_PAYMENT_TERM: term,
        COL_SUPPLIER: vendor,
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


def test_apply_vendor_exclusion_drops_excluded_vendors(db_session):
    upsert_seed_vendor(db_session, vendor_name="JW Test Vendor", reason="Job-work (JW) vendor")

    po_df = pd.DataFrame(
        [
            _po_row("ITEM1", "PO1", vendor="Regular Vendor"),
            _po_row("ITEM2", "PO2", vendor="JW Test Vendor"),
            _po_row("ITEM3", "PO3", vendor="jw test vendor"),  # case-insensitive match
        ]
    )

    result = apply_vendor_exclusion(po_df, db_session)

    assert len(result) == 1
    assert result.iloc[0][COL_SUPPLIER] == "Regular Vendor"


def test_apply_global_filters_by_date_vertical_product_supplier():
    po_df = pd.DataFrame(
        [
            _po_row("ITEM1", "PO1", order_date="2026-01-15", vertical="Pharma", product="A", vendor="Vendor A"),
            _po_row("ITEM2", "PO2", order_date="2026-02-15", vertical="Agro", product="B", vendor="Vendor B"),
        ]
    )

    by_date = apply_global_filters(po_df, CapitalFlowFilters(date_from="2026-02-01"))
    assert len(by_date) == 1 and by_date.iloc[0][COL_PRODUCT] == "B"

    by_vertical = apply_global_filters(po_df, CapitalFlowFilters(business_verticals=["Pharma"]))
    assert len(by_vertical) == 1 and by_vertical.iloc[0][COL_PRODUCT] == "A"

    by_product = apply_global_filters(po_df, CapitalFlowFilters(products=["B"]))
    assert len(by_product) == 1 and by_product.iloc[0][COL_SUPPLIER] == "Vendor B"

    by_supplier = apply_global_filters(po_df, CapitalFlowFilters(suppliers=["Vendor A"]))
    assert len(by_supplier) == 1 and by_supplier.iloc[0][COL_PRODUCT] == "A"


def test_calculate_dpo_applies_filter_then_computes(db_session):
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="30 Days PDC", instrument="Clean Credit", weighted_payable_days=30),
    )
    upsert_manual(
        db_session,
        PaymentTermUpsert(terms_description="60 Days PDC", instrument="Clean Credit", weighted_payable_days=60),
    )
    upsert_seed_vendor(db_session, vendor_name="Excluded Co", reason="Job-work (JW) vendor")

    po_df = pd.DataFrame(
        [
            _po_row("ITEM1", "PO1", value=100_000, term="30 Days PDC"),
            _po_row("ITEM2", "PO2", value=300_000, term="60 Days PDC"),
            _po_row("ITEM3", "RE1", value=999_999, term="30 Days PDC"),  # excluded: return
            _po_row("", "PO3", value=999_999, term="30 Days PDC"),  # excluded: blank itemkey
            _po_row("ITEM4", "PO4", value=999_999, term="30 Days PDC", vendor="Excluded Co"),  # excluded: vendor
        ]
    )

    result = calculate_dpo(po_df, db_session)

    # Same figures as the known-terms DPO test: (100000*30 + 300000*60) / 400000 = 52.5
    assert result.dpo == pytest.approx(52.5)
    assert result.total_po_value == pytest.approx(400_000)


def test_calculate_dpo_with_active_vertical_filter(db_session):
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
            _po_row("ITEM1", "PO1", value=100_000, term="30 Days PDC", vertical="Pharma"),
            _po_row("ITEM2", "PO2", value=300_000, term="60 Days PDC", vertical="Agro"),
        ]
    )

    result = calculate_dpo(po_df, db_session, filters=CapitalFlowFilters(business_verticals=["Pharma"]))

    assert result.dpo == pytest.approx(30.0)
    assert result.total_po_value == pytest.approx(100_000)


def test_get_filter_options_excludes_vendor_list_rows(db_session):
    upsert_seed_vendor(db_session, vendor_name="Excluded Co", reason="Job-work (JW) vendor")

    po_df = pd.DataFrame(
        [
            _po_row("ITEM1", "PO1", vendor="Vendor A", vertical="Pharma", product="Widget"),
            _po_row("ITEM2", "PO2", vendor="Excluded Co", vertical="Agro", product="Gadget"),
        ]
    )

    options = get_filter_options(po_df, db_session)

    assert options.suppliers == ["Vendor A"]
    assert options.business_verticals == ["Pharma"]
    assert options.products == ["Widget"]
