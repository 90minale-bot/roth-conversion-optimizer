from retirement_optimizer.cashflow.roth_conversion import bracket_fill_conversion, convert_to_roth
from retirement_optimizer.models.household import Household


def test_conversion_preserves_rule_of_55_amount():
    household = Household()
    household.accounts["traditional_ira"].balance = 10_000
    household.accounts["employer_401k"].balance = 300_000
    household.preserve_rule_of_55_amount = 250_000
    converted = convert_to_roth(household, 100_000, preserve_rule_of_55=True)
    assert converted == 60_000
    assert household.accounts["employer_401k"].balance == 250_000


def test_bracket_fill_conversion_is_limited_by_bracket_room():
    household = Household()
    amount = bracket_fill_conversion(household, ordinary_income_before_conversion=80_000, target_rate=0.12, year=2026, age=55)
    assert amount == 53_000
