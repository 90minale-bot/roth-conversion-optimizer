from __future__ import annotations

from retirement_optimizer.models.household import DEFAULT_PROPERTY_TAX_RATES, Household


def estimate_property_value(household: Household, offset: int) -> float:
    return max(0.0, household.property_value * ((1.0 + household.property_appreciation) ** offset))


def estimate_property_tax(household: Household, state: str, offset: int) -> float:
    rate = household.property_tax_rates.get(state.upper(), DEFAULT_PROPERTY_TAX_RATES.get(state.upper(), 0.0))
    return estimate_property_value(household, offset) * max(0.0, rate)
