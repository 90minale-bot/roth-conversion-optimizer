from __future__ import annotations

from retirement_optimizer.models.household import Household


def direct_rollover_to_ira(household: Household, preserve_amount: float) -> float:
    employer = household.accounts["employer_401k"]
    ira = household.accounts["traditional_ira"]
    amount = max(0.0, employer.balance - preserve_amount)
    moved = employer.withdraw(amount)
    ira.deposit(moved)
    return moved


def rule_of_55_warning(age: int, retirement_age: int, employer_balance: float, preserve_amount: float) -> str:
    if retirement_age <= age <= 59 and employer_balance < preserve_amount:
        return "Rule of 55 access risk: employer-plan balance is below the preserved early-access amount."
    if retirement_age <= 55 and preserve_amount > 0:
        return "Confirm employer plan partial-withdrawal rules before rolling assets out; Rule of 55 access may depend on plan terms."
    return ""
