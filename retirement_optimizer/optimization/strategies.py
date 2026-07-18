from __future__ import annotations

from retirement_optimizer.cashflow.roth_conversion import bracket_fill_conversion
from retirement_optimizer.models.household import Household


STRATEGIES = [
    "No Roth conversions",
    "Fixed annual conversion",
    "Fill 12% bracket",
    "Fill 22% bracket",
    "Aggressive before pension",
]


def conversion_for_strategy(
    strategy: str,
    household: Household,
    ordinary_income_before_conversion: float,
    year: int,
    age: int,
    fixed_amount: float,
    max_conversion: float,
) -> float:
    if age < household.retirement_age:
        return 0.0

    if strategy == "No Roth conversions":
        amount = 0.0
    elif strategy == "Fixed annual conversion":
        amount = fixed_amount
    elif strategy == "Fill 12% bracket":
        amount = bracket_fill_conversion(household, ordinary_income_before_conversion, 0.12, year, age)
    elif strategy == "Fill 22% bracket":
        amount = bracket_fill_conversion(household, ordinary_income_before_conversion, 0.22, year, age)
    elif strategy == "Aggressive before pension":
        amount = max_conversion if age < household.pension_start_age else bracket_fill_conversion(household, ordinary_income_before_conversion, 0.22, year, age)
    else:
        amount = 0.0
    return min(max(amount, 0.0), max_conversion)
