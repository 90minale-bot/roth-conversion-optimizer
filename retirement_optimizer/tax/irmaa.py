from __future__ import annotations

from dataclasses import dataclass
from math import inf


IRMAA_SOURCE_NOTE = (
    "2026 IRMAA planning table based on published Medicare planning summaries; "
    "verify against official CMS/Medicare notices before real decisions."
)


IRMAA_BRACKETS_2026 = {
    "single": [
        {"upper": 109_000, "part_b_monthly": 0.0, "part_d_monthly": 0.0},
        {"upper": 136_000, "part_b_monthly": 81.20, "part_d_monthly": 14.50},
        {"upper": 171_000, "part_b_monthly": 203.10, "part_d_monthly": 37.50},
        {"upper": 205_000, "part_b_monthly": 324.90, "part_d_monthly": 60.40},
        {"upper": 500_000, "part_b_monthly": 446.70, "part_d_monthly": 83.30},
        {"upper": inf, "part_b_monthly": 487.00, "part_d_monthly": 91.00},
    ],
    "married_joint": [
        {"upper": 218_000, "part_b_monthly": 0.0, "part_d_monthly": 0.0},
        {"upper": 274_000, "part_b_monthly": 81.20, "part_d_monthly": 14.50},
        {"upper": 342_000, "part_b_monthly": 203.10, "part_d_monthly": 37.50},
        {"upper": 410_000, "part_b_monthly": 324.90, "part_d_monthly": 60.40},
        {"upper": 750_000, "part_b_monthly": 446.70, "part_d_monthly": 83.30},
        {"upper": inf, "part_b_monthly": 487.00, "part_d_monthly": 91.00},
    ],
    "head_of_household": [
        {"upper": 109_000, "part_b_monthly": 0.0, "part_d_monthly": 0.0},
        {"upper": 136_000, "part_b_monthly": 81.20, "part_d_monthly": 14.50},
        {"upper": 171_000, "part_b_monthly": 203.10, "part_d_monthly": 37.50},
        {"upper": 205_000, "part_b_monthly": 324.90, "part_d_monthly": 60.40},
        {"upper": 500_000, "part_b_monthly": 446.70, "part_d_monthly": 83.30},
        {"upper": inf, "part_b_monthly": 487.00, "part_d_monthly": 91.00},
    ],
}


@dataclass(frozen=True)
class IrmaaResult:
    surcharge: float
    monthly_part_b: float
    monthly_part_d: float
    lookback_magi: float
    medicare_people: int
    tier: int
    warning: str


def calculate_irmaa(
    *,
    lookback_magi: float,
    filing_status: str,
    medicare_people: int,
    has_two_year_lookback: bool = True,
) -> IrmaaResult:
    if medicare_people <= 0:
        return IrmaaResult(0.0, 0.0, 0.0, lookback_magi, 0, 0, "")

    brackets = IRMAA_BRACKETS_2026.get(filing_status, IRMAA_BRACKETS_2026["single"])
    selected_tier = 0
    selected = brackets[-1]
    for idx, bracket in enumerate(brackets):
        if lookback_magi <= float(bracket["upper"]):
            selected_tier = idx
            selected = bracket
            break

    monthly_part_b = float(selected["part_b_monthly"])
    monthly_part_d = float(selected["part_d_monthly"])
    annual = (monthly_part_b + monthly_part_d) * 12 * medicare_people
    warning = ""
    if annual > 0:
        warning = f"IRMAA tier {selected_tier} estimated from MAGI lookback; {IRMAA_SOURCE_NOTE}"
    if not has_two_year_lookback and medicare_people > 0:
        warning = "; ".join(filter(None, [warning, "First two projection years use current modeled MAGI as an IRMAA placeholder because prior-year tax returns were not provided."]))
    return IrmaaResult(annual, monthly_part_b, monthly_part_d, lookback_magi, medicare_people, selected_tier, warning)
