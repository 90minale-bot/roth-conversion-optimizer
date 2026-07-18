from retirement_optimizer.models.household import Household
from retirement_optimizer.simulation.monte_carlo import run_monte_carlo, summarize_monte_carlo


def test_monte_carlo_returns_requested_number_of_runs():
    household = Household(current_age=55, projection_end_age=58, retirement_age=55)
    results = run_monte_carlo(
        household,
        strategy="No Roth conversions",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
        simulations=10,
        volatility=0.10,
        seed=123,
    )
    assert len(results) == 10
    assert {"ending_assets", "success", "total_lifetime_tax_and_healthcare"}.issubset(results.columns)


def test_monte_carlo_is_reproducible_with_seed():
    household = Household(current_age=55, projection_end_age=56, retirement_age=55)
    first = run_monte_carlo(
        household,
        strategy="Fixed annual conversion",
        fixed_conversion=25_000,
        max_conversion=50_000,
        preserve_rule_of_55=True,
        simulations=5,
        volatility=0.10,
        seed=99,
    )
    second = run_monte_carlo(
        household,
        strategy="Fixed annual conversion",
        fixed_conversion=25_000,
        max_conversion=50_000,
        preserve_rule_of_55=True,
        simulations=5,
        volatility=0.10,
        seed=99,
    )
    assert first["ending_assets"].tolist() == second["ending_assets"].tolist()


def test_monte_carlo_summary_includes_success_rate():
    household = Household(current_age=55, projection_end_age=56, retirement_age=55)
    results = run_monte_carlo(
        household,
        strategy="No Roth conversions",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
        simulations=5,
    )
    summary = summarize_monte_carlo(results)
    assert summary.simulations == 5
    assert 0 <= summary.success_rate <= 1


def test_monte_carlo_records_stress_controls():
    household = Household(current_age=55, projection_end_age=56, retirement_age=55)
    results = run_monte_carlo(
        household,
        strategy="No Roth conversions",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
        simulations=3,
        stress_scenario="Early bear market",
        inflation_shock=True,
        spending_guardrail=True,
    )
    assert set(results["stress_scenario"]) == {"Early bear market"}
    assert results["inflation_shock"].all()
    assert results["spending_guardrail"].all()
