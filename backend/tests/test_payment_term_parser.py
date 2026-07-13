import pytest

from app.calculators.payment_term_parser import auto_calculate_weighted_days

# (term description, expected weighted payable days) — pulled directly from
# Payment_Terms_Mapped_Weighted_Standardized_Corrected.xlsx, covering every
# distinct calculation shape in the sheet.
KNOWN_ROWS = [
    ("10% Advance TT, 90% OA 90 Days from BL Date", 81.0),  # 10B
    ("10% Advance & The Balance 15 Days After Dispatch", 1.5),  # 10O — see test_implied_balance_percentage_is_not_recovered
    ("15% of value as advance and balance 15 days credit", 2.25),  # 15C — see test_implied_balance_percentage_is_not_recovered
    ("30% Advance and 70% 45 Days PDC", 31.5),  # 30E
    ("30% Advance and 70% on 30 Days Credit", 21.0),  # 30O
    ("50 % ADVANCE &50% AFTER 30 DAYS PDC", 15.0),  # 50D
    ("50% Advance And Remaining 30 Days Credit", 15.0),  # 50E
    ("50% before dispatch & 50% after 45 days", 22.5),  # 50H
    ("50% advance & remaining in 10 days after receiving", 5.0),  # 50I
    ("50% Advance and 50% after 15 days", 7.5),  # 50R
    ("20% ADVANCE and BALANCE 80% on 30 Days PDC", 24.0),  # 80P
    ("40% ADV & BAL AGNST AFTER 15 DAYS ARRIVAL OF CARGO", 6.0),  # 40F
    ("95% on 15 days & then 5% on 30 days credit", 15.75),  # 95O
    ("50% On 5 Day PDC & 50% On 10 Days PDC", 7.5),  # 5P
    ("5% adv and remaining 95% LC 90 days", 85.5),  # AD5
    ("120 Days LC", 120.0),  # 12L
    ("30 Days LC", 30.0),  # 30L
    ("LC at sight", 0.0),  # LC
    ("D/A 105 Days From B/L Date", 105.0),  # 105
    ("DA 30 Days from BL Date", 30.0),  # 30D
    ("180 Days from BL date", 180.0),  # 180
    ("30 Days PDC", 30.0),  # PDC
]


@pytest.mark.parametrize("term,expected_days", KNOWN_ROWS)
def test_matches_sheet_weighted_days(term, expected_days):
    result = auto_calculate_weighted_days(term)
    assert result.weighted_payable_days == pytest.approx(expected_days)


def test_implied_balance_percentage_is_not_recovered():
    # 10O's corrected sheet value is 13.5 = (10%x0 + 90%x15)/100 — but the
    # text only states one percentage (10%); "the balance" implies the
    # other 90% without a number the parser can read. It associates the
    # single stated 10% with the 15-day figure instead (10%x15/100=1.5),
    # which is why every auto-created term is flagged for human review
    # rather than trusted blindly.
    result = auto_calculate_weighted_days("10% Advance & The Balance 15 Days After Dispatch")
    assert result.weighted_payable_days == pytest.approx(1.5)


def test_flat_term_with_no_percentage():
    result = auto_calculate_weighted_days("90 days credit from BL date")
    assert result.weighted_payable_days == pytest.approx(90.0)
    assert result.is_confident is True


def test_term_with_no_numbers_defaults_to_zero_and_is_not_confident():
    result = auto_calculate_weighted_days("Against Barter")
    assert result.weighted_payable_days == pytest.approx(0.0)
    assert result.is_confident is False


def test_advance_only_term_with_no_day_count_defaults_to_zero():
    result = auto_calculate_weighted_days("30% Advance")
    assert result.weighted_payable_days == pytest.approx(0.0)
