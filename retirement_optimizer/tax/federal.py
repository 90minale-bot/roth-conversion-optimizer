from __future__ import annotations

from dataclasses import dataclass
from math import inf

from retirement_optimizer.data.loader import federal_tax_data
from retirement_optimizer.tax.capital_gains import calculate_ltcg_tax


@dataclass(frozen=True)
class FederalTaxResult:
    ordinary_tax: float
    capital_gains_tax: float
    total_tax: float
    taxable_income: float
    ordinary_taxable_income: float
    agi: float
    standard_deduction: float
    marginal_rate: float
    remaining_bracket_capacity: float
    taxable_social_security: float


def taxable_social_security(benefits: float, other_agi: float, filing_status: str) -> float:
    if benefits <= 0:
        return 0.0
    base1, base2 = ((32_000, 44_000) if filing_status == "married_joint" else (25_000, 34_000))
    provisional = other_agi + 0.5 * benefits
    if provisional <= base1:
        return 0.0
    if provisional <= base2:
        return min(0.5 * benefits, 0.5 * (provisional - base1))
    lower_taxable = min(0.5 * benefits, 0.5 * (base2 - base1))
    return min(0.85 * benefits, lower_taxable + 0.85 * (provisional - base2))


def tax_on_brackets(taxable_income: float, brackets: list[dict[str, float]]) -> tuple[float, float, float]:
    tax = 0.0
    marginal = 0.0
    capacity = inf
    for bracket in brackets:
        lower = float(bracket["lower"])
        upper = float(bracket.get("upper") or inf)
        rate = float(bracket["rate"])
        if taxable_income > lower:
            tax += max(0.0, min(taxable_income, upper) - lower) * rate
            marginal = rate
        if lower <= taxable_income < upper:
            capacity = upper - taxable_income if upper < inf else inf
            marginal = rate
            break
    return tax, marginal, capacity


def calculate_federal_tax(
    *,
    ordinary_income: float,
    social_security: float = 0.0,
    qualified_dividends: float = 0.0,
    long_term_capital_gains: float = 0.0,
    filing_status: str = "married_joint",
    year: int = 2026,
    age: int = 49,
    spouse_age: int | None = None,
) -> FederalTaxResult:
    data = federal_tax_data(year)
    status_data = data["filing_statuses"][filing_status]
    senior_count = int(age >= 65) + int(bool(spouse_age and spouse_age >= 65 and filing_status == "married_joint"))
    deduction = float(status_data["standard_deduction"]) + senior_count * float(status_data.get("additional_senior_standard_deduction", 0))
    taxable_ss = taxable_social_security(social_security, ordinary_income + qualified_dividends + long_term_capital_gains, filing_status)
    agi = ordinary_income + taxable_ss + qualified_dividends + long_term_capital_gains
    taxable_income = max(0.0, agi - deduction)
    preferential_income = max(0.0, qualified_dividends + long_term_capital_gains)
    ordinary_taxable_income = max(0.0, taxable_income - preferential_income)
    ordinary_tax, marginal, capacity = tax_on_brackets(ordinary_taxable_income, status_data["ordinary_brackets"])
    capital_gains_tax = calculate_ltcg_tax(
        ordinary_taxable_income=ordinary_taxable_income,
        qualified_dividends=qualified_dividends,
        long_term_capital_gains=long_term_capital_gains,
        filing_status=filing_status,
        year=year,
    )
    return FederalTaxResult(ordinary_tax, capital_gains_tax, ordinary_tax + capital_gains_tax, taxable_income, ordinary_taxable_income, agi, deduction, marginal, capacity, taxable_ss)


def bracket_capacity_for_rate(filing_status: str, target_rate: float, ordinary_income: float, year: int = 2026) -> float:
    data = federal_tax_data(year)
    brackets = data["filing_statuses"][filing_status]["ordinary_brackets"]
    target = next((b for b in brackets if float(b["rate"]) == target_rate), None)
    if target is None or not target.get("upper"):
        return 0.0
    taxable_income = max(0.0, ordinary_income - data["filing_statuses"][filing_status]["standard_deduction"])
    return max(0.0, float(target["upper"]) - taxable_income)
