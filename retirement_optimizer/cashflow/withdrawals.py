from __future__ import annotations

from retirement_optimizer.models.household import Household


def fund_spending(household: Household, spending_need: float, age: int) -> dict[str, float]:
    remaining = max(0.0, spending_need)
    result = {"cash": 0.0, "taxable": 0.0, "traditional": 0.0, "roth": 0.0}
    for key, label in [("cash", "cash"), ("taxable", "taxable")]:
        taken = household.accounts[key].withdraw(remaining)
        result[label] += taken
        remaining -= taken
    if remaining > 0 and age >= 59.5:
        taken = household.accounts["traditional_ira"].withdraw(remaining)
        result["traditional"] += taken
        remaining -= taken
    if remaining > 0:
        taken = household.accounts["roth_ira"].withdraw(remaining)
        result["roth"] += taken
        remaining -= taken
    return result
