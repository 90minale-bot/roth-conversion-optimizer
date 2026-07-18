from __future__ import annotations

from dataclasses import dataclass


NIIT_RATE = 0.038
NIIT_THRESHOLDS = {
    "single": 200_000,
    "head_of_household": 200_000,
    "married_joint": 250_000,
    "married_separate": 125_000,
}


@dataclass(frozen=True)
class NiitResult:
    tax: float
    threshold: float
    excess_magi: float
    net_investment_income: float


def calculate_niit(
    *,
    magi: float,
    qualified_dividends: float,
    long_term_capital_gains: float,
    filing_status: str = "married_joint",
) -> NiitResult:
    """Estimate the 3.8% Net Investment Income Tax for planning purposes."""
    threshold = float(NIIT_THRESHOLDS.get(filing_status, NIIT_THRESHOLDS["single"]))
    net_investment_income = max(0.0, qualified_dividends + long_term_capital_gains)
    excess_magi = max(0.0, magi - threshold)
    tax = min(net_investment_income, excess_magi) * NIIT_RATE
    return NiitResult(tax, threshold, excess_magi, net_investment_income)
