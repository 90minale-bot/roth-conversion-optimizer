from __future__ import annotations

from math import inf

from retirement_optimizer.data.loader import federal_tax_data


def capital_gain_brackets(filing_status: str, year: int = 2026) -> list[dict[str, float]]:
    data = federal_tax_data(year)
    return data["filing_statuses"][filing_status]["long_term_capital_gain_brackets"]


def calculate_ltcg_tax(
    *,
    ordinary_taxable_income: float,
    qualified_dividends: float,
    long_term_capital_gains: float,
    filing_status: str,
    year: int = 2026,
) -> float:
    """Apply federal capital-gain stacking after ordinary taxable income."""
    preferential_income = max(0.0, qualified_dividends + long_term_capital_gains)
    if preferential_income == 0:
        return 0.0
    tax = 0.0
    remaining = preferential_income
    stack_start = max(0.0, ordinary_taxable_income)
    for bracket in capital_gain_brackets(filing_status, year):
        lower = float(bracket["lower"])
        upper = float(bracket.get("upper") or inf)
        rate = float(bracket["rate"])
        available = max(0.0, upper - max(stack_start, lower)) if upper < inf else remaining
        taxed = min(remaining, available)
        tax += taxed * rate
        remaining -= taxed
        stack_start += taxed
        if remaining <= 0:
            break
    return tax
