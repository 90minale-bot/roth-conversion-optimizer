from retirement_optimizer.cashflow.rollover import direct_rollover_to_ira, rule_of_55_warning
from retirement_optimizer.models.household import Household


def test_direct_rollover_preserves_employer_plan_amount():
    household = Household()
    household.accounts["employer_401k"].balance = 500_000
    household.accounts["traditional_ira"].balance = 0
    moved = direct_rollover_to_ira(household, preserve_amount=200_000)
    assert moved == 300_000
    assert household.accounts["employer_401k"].balance == 200_000
    assert household.accounts["traditional_ira"].balance == 300_000


def test_rule_of_55_warning_when_preserved_balance_is_low():
    warning = rule_of_55_warning(age=56, retirement_age=55, employer_balance=100_000, preserve_amount=200_000)
    assert "Rule of 55" in warning
