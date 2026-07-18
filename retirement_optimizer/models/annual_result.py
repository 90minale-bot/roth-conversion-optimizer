from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class AnnualResult:
    year: int
    age: int
    state: str
    employment_income: float
    pension_income: float
    social_security: float
    qualified_dividends: float
    long_term_capital_gains: float
    traditional_withdrawals: float
    roth_conversion: float
    roth_withdrawals: float
    taxable_withdrawals: float
    cash_withdrawals: float
    gross_income: float
    agi: float
    taxable_income: float
    federal_ordinary_tax: float
    federal_capital_gains_tax: float
    federal_tax: float
    niit: float
    irmaa_surcharge: float
    irmaa_lookback_magi: float
    medicare_people: int
    aca_magi: float
    aca_fpl_percent: float
    aca_gross_premium: float
    aca_premium_tax_credit: float
    aca_net_premium: float
    aca_covered_people: int
    state_tax: float
    local_tax: float
    property_tax: float
    spending: float
    total_income: float
    total_withdrawals: float
    total_taxes: float
    available_spending_after_taxes: float
    spending_surplus_shortfall: float
    ending_cash: float
    ending_taxable: float
    ending_traditional: float
    ending_roth: float
    estimated_estate_value: float
    federal_estate_exposure: float
    estimated_federal_estate_tax: float
    state_estate_exposure: float
    estimated_state_estate_tax: float
    rmd: float
    effective_tax_rate: float
    marginal_federal_rate: float
    marginal_state_rate: float
    remaining_bracket_capacity: float
    warning: str = ""

    def to_dict(self) -> dict[str, float | int | str]:
        return asdict(self)
