from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.deterministic import annualized_relocation_advantage, compare_conversion_strategies, compare_relocation_scenarios, recommend_strategy
from retirement_optimizer.optimization.search import optimize_dynamic_conversion_schedule, search_fixed_conversion_grid


def test_strategy_comparison_returns_all_strategies():
    household = Household(current_age=55, projection_end_age=58, retirement_age=55)
    comparison = compare_conversion_strategies(
        household,
        fixed_conversion=50_000,
        max_conversion=150_000,
        preserve_rule_of_55=True,
    )
    assert len(comparison) >= 5
    assert "total_lifetime_tax" in comparison.columns
    assert "total_lifetime_tax_and_healthcare" in comparison.columns
    assert "lifetime_niit" in comparison.columns
    assert "lifetime_irmaa" in comparison.columns
    assert "lifetime_aca_net_premium" in comparison.columns
    assert "ending_estate_value" in comparison.columns
    assert "estimated_state_estate_tax" in comparison.columns


def test_recommend_strategy_returns_named_strategy():
    household = Household(current_age=55, projection_end_age=58, retirement_age=55)
    recommendation = recommend_strategy(
        household,
        objective="Minimize lifetime taxes",
        fixed_conversion=50_000,
        max_conversion=150_000,
        preserve_rule_of_55=True,
    )
    assert recommendation.strategy


def test_relocation_comparison_covers_state_and_move_age_grid():
    household = Household(current_age=55, projection_end_age=58, retirement_age=55)
    grid = compare_relocation_scenarios(
        household,
        states=["IL", "FL"],
        move_ages=[55, 57],
        strategy="No Roth conversions",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
    )
    assert len(grid) == 4
    assert {"destination_state", "move_age", "ending_assets"}.issubset(grid.columns)


def test_annualized_relocation_advantage_compares_against_maryland():
    household = Household(current_age=55, projection_end_age=58, retirement_age=55)
    grid = compare_relocation_scenarios(
        household,
        states=["MD", "FL"],
        move_ages=[55, 57],
        strategy="No Roth conversions",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
    )
    summary = annualized_relocation_advantage(grid, projection_years=4, baseline_state="MD")
    assert {"destination_state", "additional_dollars_per_year_vs_baseline"}.issubset(summary.columns)
    md_row = summary[summary["destination_state"] == "MD"].iloc[0]
    assert md_row["additional_dollars_per_year_vs_baseline"] == 0


def test_fixed_conversion_grid_search_ranks_feasible_rows():
    household = Household(current_age=55, projection_end_age=58, retirement_age=55)
    grid = search_fixed_conversion_grid(
        household,
        objective="Minimize lifetime taxes",
        max_conversion=100_000,
        step=50_000,
        preserve_rule_of_55=True,
        max_marginal_federal_rate=0.35,
        max_annual_irmaa=100_000,
        min_ending_cash=0,
    )
    assert len(grid) == 3
    assert "rank" in grid.columns
    assert grid["feasible"].any()


def test_dynamic_conversion_optimizer_returns_schedule_and_heatmap():
    household = Household(current_age=52, projection_end_age=58, retirement_age=52)

    result = optimize_dynamic_conversion_schedule(
        household,
        objective="Minimize lifetime taxes",
        start_age=52,
        end_age=55,
        max_conversion=100_000,
        step=50_000,
        preserve_rule_of_55=True,
    )

    assert {"schedule", "heatmap", "projection", "summary"}.issubset(result)
    assert len(result["schedule"]) == 4
    assert {"age", "selected_conversion", "objective_value"}.issubset(result["schedule"].columns)
    assert {"age", "candidate_conversion", "objective_value"}.issubset(result["heatmap"].columns)


def test_dynamic_conversion_optimizer_can_choose_different_annual_amounts():
    household = Household(
        current_age=52,
        projection_end_age=75,
        retirement_age=52,
        pension_start_age=55,
        pension_monthly=8_000,
        social_security_start_age=62,
        social_security_monthly=4_000,
    )

    result = optimize_dynamic_conversion_schedule(
        household,
        objective="Maximize Roth balance",
        start_age=52,
        end_age=60,
        max_conversion=150_000,
        step=75_000,
        preserve_rule_of_55=True,
        max_marginal_federal_rate=0.24,
    )

    conversions = result["schedule"]["selected_conversion"].tolist()
    assert len(set(conversions)) > 1
