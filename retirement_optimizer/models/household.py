from __future__ import annotations

from dataclasses import dataclass, field

from .account import Account


DEFAULT_PROPERTY_TAX_RATES = {
    "IL": 0.0208,
    "PA": 0.0136,
    "MD": 0.0105,
    "DE": 0.0057,
    "VA": 0.0082,
    "FL": 0.0089,
}


DEFAULT_LOCAL_INCOME_TAX_RATES = {
    "IL": 0.0,
    "PA": 0.01,
    "MD": 0.032,
    "DE": 0.0,
    "VA": 0.0,
    "FL": 0.0,
}


@dataclass
class Household:
    current_age: int = 50
    spouse_age: int | None = None
    retirement_age: int = 55
    projection_end_age: int = 95
    filing_status: str = "married_joint"
    current_state: str = "IL"
    destination_state: str = "FL"
    move_age: int = 57
    annual_spending: float = 120_000
    spending_inflation: float = 0.025
    property_value: float = 1_000_000
    property_appreciation: float = 0.02
    property_tax_rates: dict[str, float] = field(default_factory=lambda: DEFAULT_PROPERTY_TAX_RATES.copy())
    local_income_tax_rates: dict[str, float] = field(default_factory=lambda: DEFAULT_LOCAL_INCOME_TAX_RATES.copy())
    household_size: int = 2
    aca_benchmark_premium_monthly: float = 1_800
    employment_income: float = 0.0
    spouse_income: float = 0.0
    pension_monthly: float = 5_500
    pension_start_age: int = 65
    social_security_monthly: float = 3_200
    social_security_start_age: int = 67
    qualified_dividends: float = 6_000
    long_term_capital_gains: float = 0.0
    taxable_turnover_rate: float = 0.02
    preserve_rule_of_55_amount: float = 240_000
    include_relocation: bool = True
    inflation: float = 0.025
    accounts: dict[str, Account] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.accounts:
            self.accounts = {
                "employer_401k": Account("Current employer traditional 401(k)", 1_250_000, 0.055, rollover_eligible=True, early_access_protected=True),
                "traditional_ira": Account("Traditional IRA", 750_000, 0.055),
                "roth_ira": Account("Roth IRA", 150_000, 0.06),
                "taxable": Account("Taxable brokerage", 250_000, 0.045, cost_basis=180_000),
                "cash": Account("Cash", 80_000, 0.02),
                "hsa": Account("HSA", 25_000, 0.05),
            }

    @property
    def birth_year(self) -> int:
        return 2026 - self.current_age
