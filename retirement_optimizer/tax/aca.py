from __future__ import annotations

from dataclasses import dataclass


ACA_SOURCE_NOTE = (
    "ACA bridge model uses reviewable planning inputs: 2025 HHS poverty guidelines "
    "as the current bundled baseline, a simplified applicable-percentage table, "
    "and a user-entered benchmark silver premium."
)


POVERTY_GUIDELINES_BASELINE = {
    "contiguous": {
        1: 15_650,
        2: 21_150,
        3: 26_650,
        4: 32_150,
        5: 37_650,
        6: 43_150,
        7: 48_650,
        8: 54_150,
        "additional": 5_500,
    },
    "AK": {
        1: 19_550,
        2: 26_430,
        3: 33_310,
        4: 40_190,
        5: 47_070,
        6: 53_950,
        7: 60_830,
        8: 67_710,
        "additional": 6_880,
    },
    "HI": {
        1: 17_990,
        2: 24_320,
        3: 30_650,
        4: 36_980,
        5: 43_310,
        6: 49_640,
        7: 55_970,
        8: 62_300,
        "additional": 6_330,
    },
}


APPLICABLE_PERCENTAGE_TABLE_2026 = [
    (100.0, 0.0200),
    (133.0, 0.0300),
    (150.0, 0.0400),
    (200.0, 0.0630),
    (250.0, 0.0805),
    (300.0, 0.0950),
    (400.0, 0.0950),
]


@dataclass(frozen=True)
class AcaResult:
    gross_premium: float
    premium_tax_credit: float
    net_premium: float
    expected_contribution: float
    fpl_percent: float
    covered_people: int
    warning: str


def poverty_guideline(household_size: int, state: str = "IL") -> float:
    table = POVERTY_GUIDELINES_BASELINE.get(state.upper(), POVERTY_GUIDELINES_BASELINE["contiguous"])
    if household_size <= 8:
        return float(table[max(1, household_size)])
    return float(table[8] + (household_size - 8) * table["additional"])


def applicable_percentage(fpl_percent: float) -> float | None:
    if fpl_percent < 100.0 or fpl_percent > 400.0:
        return None
    previous_fpl, previous_pct = APPLICABLE_PERCENTAGE_TABLE_2026[0]
    if fpl_percent <= previous_fpl:
        return previous_pct
    for current_fpl, current_pct in APPLICABLE_PERCENTAGE_TABLE_2026[1:]:
        if fpl_percent <= current_fpl:
            span = current_fpl - previous_fpl
            weight = (fpl_percent - previous_fpl) / span if span else 0.0
            return previous_pct + weight * (current_pct - previous_pct)
        previous_fpl, previous_pct = current_fpl, current_pct
    return APPLICABLE_PERCENTAGE_TABLE_2026[-1][1]


def calculate_aca_premium(
    *,
    aca_magi: float,
    household_size: int,
    state: str,
    covered_people: int,
    benchmark_premium_monthly: float,
) -> AcaResult:
    if covered_people <= 0 or benchmark_premium_monthly <= 0:
        return AcaResult(0.0, 0.0, 0.0, 0.0, 0.0, max(0, covered_people), "")

    poverty = poverty_guideline(household_size, state)
    fpl_percent = (aca_magi / poverty) * 100 if poverty > 0 else 0.0
    gross_premium = benchmark_premium_monthly * 12
    pct = applicable_percentage(fpl_percent)
    warning = ""

    if pct is None:
        if fpl_percent < 100.0:
            warning = f"ACA MAGI is below 100% FPL; Medicaid eligibility and state rules are not modeled. {ACA_SOURCE_NOTE}"
        else:
            warning = f"ACA MAGI exceeds 400% FPL; baseline model assumes the post-2025 premium subsidy cliff applies. {ACA_SOURCE_NOTE}"
        return AcaResult(gross_premium, 0.0, gross_premium, 0.0, fpl_percent, covered_people, warning)

    expected_contribution = aca_magi * pct
    credit = max(0.0, gross_premium - expected_contribution)
    net_premium = gross_premium - credit
    if 390.0 <= fpl_percent <= 410.0:
        warning = f"ACA MAGI is close to the 400% FPL subsidy cliff; Roth conversions may change marketplace premium credits. {ACA_SOURCE_NOTE}"
    return AcaResult(gross_premium, credit, net_premium, expected_contribution, fpl_percent, covered_people, warning)
