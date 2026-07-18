from __future__ import annotations

from retirement_optimizer.models.household import Household
from retirement_optimizer.tax.federal import calculate_federal_tax


def available_traditional_balance(household: Household, preserve_rule_of_55: bool = True) -> float:
    employer_available = household.accounts["employer_401k"].balance
    if preserve_rule_of_55:
        employer_available = max(0.0, employer_available - household.preserve_rule_of_55_amount)
    return employer_available + household.accounts["traditional_ira"].balance


def convert_to_roth(household: Household, amount: float, preserve_rule_of_55: bool = True) -> float:
    amount = min(max(amount, 0.0), available_traditional_balance(household, preserve_rule_of_55))
    remaining = amount
    ira_taken = household.accounts["traditional_ira"].withdraw(remaining)
    remaining -= ira_taken
    if remaining > 0:
        employer = household.accounts["employer_401k"]
        max_from_employer = employer.balance - (household.preserve_rule_of_55_amount if preserve_rule_of_55 else 0.0)
        remaining -= employer.withdraw(min(remaining, max(0.0, max_from_employer)))
    converted = amount - max(0.0, remaining)
    household.accounts["roth_ira"].deposit(converted)
    return converted


def bracket_fill_conversion(
    household: Household,
    ordinary_income_before_conversion: float,
    target_rate: float,
    year: int,
    age: int,
) -> float:
    data = calculate_federal_tax(
        ordinary_income=ordinary_income_before_conversion,
        filing_status=household.filing_status,
        year=year,
        age=age,
        spouse_age=household.spouse_age,
    )
    from retirement_optimizer.data.loader import federal_tax_data

    brackets = federal_tax_data(year)["filing_statuses"][household.filing_status]["ordinary_brackets"]
    target = next((b for b in brackets if float(b["rate"]) == target_rate), None)
    if not target or not target.get("upper"):
        return 0.0
    room = max(0.0, float(target["upper"]) - data.taxable_income)
    return min(room, available_traditional_balance(household))
