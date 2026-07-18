from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.scenarios import saved_scenario_row, scenario_package, scenario_package_summary, scenario_table


def test_saved_scenario_row_can_be_tabulated():
    row = saved_scenario_row(
        name="Baseline",
        household=Household(current_age=55, projection_end_age=56, retirement_age=55),
        strategy="No Roth conversions",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
    )
    table = scenario_table([row])
    assert table.iloc[0]["name"] == "Baseline"
    assert "total_lifetime_tax" in table.columns


def test_scenario_package_includes_inputs_and_settings():
    household = Household(current_age=55, projection_end_age=56, retirement_age=55)
    package = scenario_package(
        name="Baseline",
        household=household,
        strategy="No Roth conversions",
        objective="Minimize lifetime taxes",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
        grid_step=25_000,
        max_search_federal_rate=0.24,
        max_search_irmaa=20_000,
        min_search_cash=0,
        monte_carlo_runs=100,
        monte_carlo_volatility=0.12,
        monte_carlo_seed=42,
        stress_scenario="Random returns",
        inflation_shock=False,
        spending_guardrail=False,
    )
    summary = scenario_package_summary(package)
    assert package["household"]["current_age"] == 55
    assert package["settings"]["strategy"] == "No Roth conversions"
    assert summary["name"] == "Baseline"
