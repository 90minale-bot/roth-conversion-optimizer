from __future__ import annotations

from dataclasses import dataclass
from math import inf

from retirement_optimizer.data.loader import state_tax_data
from retirement_optimizer.tax.federal import tax_on_brackets


@dataclass(frozen=True)
class StateTaxResult:
    state_tax: float
    local_tax: float
    taxable_income: float
    marginal_rate: float
    warning: str


def calculate_state_tax(
    *,
    state: str,
    ordinary_income: float,
    pension_income: float,
    social_security: float,
    retirement_distributions: float,
    roth_conversion: float,
    qualified_dividends: float = 0.0,
    long_term_capital_gains: float = 0.0,
    filing_status: str = "married_joint",
    year: int = 2026,
    local_tax_rate: float | None = None,
) -> StateTaxResult:
    data = state_tax_data(state, year)
    taxable = ordinary_income + qualified_dividends + long_term_capital_gains
    if not data["treatment"].get("social_security_taxable", False):
        taxable -= social_security
    if not data["treatment"].get("pension_taxable", True):
        taxable -= pension_income
    if not data["treatment"].get("retirement_distributions_taxable", True):
        taxable -= retirement_distributions
    if not data["treatment"].get("roth_conversion_taxable", True):
        taxable -= roth_conversion
    if not data["treatment"].get("capital_gains_taxable", True):
        taxable -= long_term_capital_gains
    taxable = max(0.0, taxable - float(data.get("deductions", {}).get(filing_status, 0)))
    local_rate = float(local_tax_rate if local_tax_rate is not None else data.get("local_tax", {}).get("default_rate", 0.0))
    local_tax = taxable * max(0.0, local_rate)
    if data["tax_type"] == "none":
        return StateTaxResult(0.0, local_tax, taxable, 0.0, data.get("warning", ""))
    if data["tax_type"] == "flat":
        rate = float(data["flat_rate"])
        return StateTaxResult(taxable * rate, local_tax, taxable, rate + max(0.0, local_rate), data.get("warning", ""))
    brackets = data["brackets"][filing_status]
    tax, marginal, _ = tax_on_brackets(taxable, brackets)
    return StateTaxResult(tax, local_tax, taxable, marginal + max(0.0, local_rate), data.get("warning", ""))
