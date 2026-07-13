"""Auto-calculates weighted payable days for a payment-term description
that is not yet in the Payment Terms Master, mirroring the %x days / 100
weighted-average method used throughout the Scimplify-curated master.

Algorithm: scan the text for percentage tokens ("40%") and day-count tokens
("15 days"). Each percentage is paired with the first day-count token that
appears after it and before the next percentage token (or end of string) —
i.e. "the days that apply to this tranche". A percentage with no following
day-count before the next tranche defaults to 0 days (an advance/immediate
portion). If no percentage is found at all, the term is a flat credit
period: 100% of the value at the single day-count found (or 0 if none).

This is a best-effort convenience for brand-new terms, not a source of
truth — every auto-calculated entry is flagged for human review before
being trusted long-term, though it is applied to DPO immediately so a
single unrecognized term never blocks the calculation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_DAYS = re.compile(r"(\d+(?:\.\d+)?)\s*days?\b", re.IGNORECASE)


@dataclass
class ParsedPaymentTerm:
    weighted_payable_days: float
    calculation_trace: str
    is_confident: bool


def auto_calculate_weighted_days(term_description: str) -> ParsedPaymentTerm:
    percents = [(m.start(), float(m.group(1))) for m in _PERCENT.finditer(term_description)]
    days = [(m.start(), float(m.group(1))) for m in _DAYS.finditer(term_description)]

    if not percents:
        # Flat credit term: 100% of the value at the one day-count found.
        day_value = days[0][1] if days else 0.0
        weighted = day_value
        trace = f"{day_value:g} days" if days else "no % or day figures found in text"
        return ParsedPaymentTerm(weighted, trace, is_confident=bool(days))

    tranches: list[tuple[float, float]] = []
    for i, (pct_pos, pct) in enumerate(percents):
        next_pct_pos = percents[i + 1][0] if i + 1 < len(percents) else None
        tranche_days = next(
            (d for d_pos, d in days if d_pos > pct_pos and (next_pct_pos is None or d_pos < next_pct_pos)),
            0.0,
        )
        tranches.append((pct, tranche_days))

    weighted = sum(pct * tranche_days for pct, tranche_days in tranches) / 100
    trace = " + ".join(f"{pct:g}%×{d:g}" for pct, d in tranches) + " /100"
    return ParsedPaymentTerm(weighted, trace, is_confident=any(d > 0 for _, d in tranches))
