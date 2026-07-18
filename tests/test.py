from __future__ import annotations

import json
from pathlib import Path

import pytest

from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.deterministic import (
    annualized_relocation_advantage,
    compare_conversion_strategies,
    compare_relocation_scenarios,
)
from retirement_optimizer.optimization.search import optimize_dynamic_conversion_schedule
from retirement_optimizer.projections.annual_projection import project_household, results_frame


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "sysml" / "requirements.json"
MODELED_STATES = {"DE", "FL", "IL", "MD", "PA", "VA"}


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def test_design_contract_metadata_is_traceable():
    contract = load_contract()
    requirements = contract["requirements"]

    assert contract["source_model"].endswith("retirement_conversion_optimizer_diagram_views.sysml")
    assert len(requirements) >= 8

    ids = [requirement["id"] for requirement in requirements]
    assert len(ids) == len(set(ids))

    for requirement in requirements:
        assert requirement["id"].startswith("REQ-")
        assert requirement["statement"]
        assert requirement["sysml_elements"]
        assert requirement["verification"]["method"] == "pytest"
        assert requirement["verification"]["pytest"].startswith("tests/test.py::test_req_")


def test_req_conv_001_conversions_start_at_retirement():
    """Verifies REQ-CONV-001."""
    household = Household(current_age=52, projection_end_age=56, retirement_age=55)

    df = results_frame(project_household(
        household,
        strategy="Fixed annual conversion",
        fixed_conversion=75_000,
        max_conversion=150_000,
        conversion_start_age=52,
        conversion_end_age=75,
    ))

    assert (df[df["age"] < household.retirement_age]["roth_conversion"] == 0).all()
    assert df.loc[df["age"] == household.retirement_age, "roth_conversion"].iloc[0] > 0


def test_req_conv_002_conversions_stop_after_end_age():
    """Verifies REQ-CONV-002."""
    household = Household(current_age=55, projection_end_age=78, retirement_age=55)

    df = results_frame(project_household(
        household,
        strategy="Fixed annual conversion",
        fixed_conversion=75_000,
        max_conversion=150_000,
        conversion_start_age=55,
        conversion_end_age=60,
    ))

    assert (df[(df["age"] >= 55) & (df["age"] <= 60)]["roth_conversion"] > 0).any()
    assert (df[df["age"] > 60]["roth_conversion"] == 0).all()


def test_req_cash_001_available_spending_formula():
    """Verifies REQ-CASH-001."""
    household = Household(
        current_age=55,
        projection_end_age=58,
        retirement_age=55,
        annual_spending=110_000,
        property_value=500_000,
        aca_benchmark_premium_monthly=1_200,
        include_relocation=False,
    )

    df = results_frame(project_household(household, strategy="No Roth conversions"))
    expected = (
        df["total_income"]
        + df["total_withdrawals"]
        - df["total_taxes"]
        - df["property_tax"]
        - df["aca_net_premium"]
    ).clip(lower=0.0)

    assert pytest.approx(expected.tolist(), abs=0.01) == df["available_spending_after_taxes"].tolist()
    assert pytest.approx(
        (df["available_spending_after_taxes"] - df["spending"]).tolist(),
        abs=0.01,
    ) == df["spending_surplus_shortfall"].tolist()


def test_req_state_001_maryland_relocation_baseline():
    """Verifies REQ-STATE-001."""
    household = Household(current_age=55, projection_end_age=60, retirement_age=55)
    grid = compare_relocation_scenarios(
        household,
        states=["MD", "FL", "IL"],
        move_ages=[55, 57],
        strategy="No Roth conversions",
        fixed_conversion=0,
        max_conversion=0,
        preserve_rule_of_55=True,
    )

    summary = annualized_relocation_advantage(grid, projection_years=6, baseline_state="MD")
    maryland = summary[summary["destination_state"] == "MD"].iloc[0]

    assert maryland["baseline_state"] == "MD"
    assert maryland["additional_dollars_per_year_vs_baseline"] == 0
    assert maryland["lifetime_dollars_vs_baseline"] == 0


def test_req_state_002_modeled_state_tax_files_exist():
    """Verifies REQ-STATE-002."""
    state_data_dir = REPO_ROOT / "tax_data" / "states"
    discovered_states = {path.name for path in state_data_dir.iterdir() if path.is_dir()}

    assert MODELED_STATES.issubset(discovered_states)
    for state in MODELED_STATES:
        assert (state_data_dir / state / "2026.json").exists()


def test_req_opt_001_dynamic_optimizer_outputs_schedule_and_heatmap():
    """Verifies REQ-OPT-001."""
    household = Household(current_age=52, projection_end_age=58, retirement_age=55)

    result = optimize_dynamic_conversion_schedule(
        household,
        objective="Minimize lifetime taxes",
        start_age=52,
        end_age=57,
        max_conversion=100_000,
        step=50_000,
        preserve_rule_of_55=True,
    )

    schedule = result["schedule"]
    heatmap = result["heatmap"]

    assert {"schedule", "heatmap", "projection", "summary"}.issubset(result)
    assert not schedule.empty
    assert not heatmap.empty
    assert schedule["age"].min() >= household.retirement_age
    assert schedule["age"].max() <= 57
    assert {"age", "selected_conversion", "objective_value"}.issubset(schedule.columns)
    assert {"age", "candidate_conversion", "objective_value"}.issubset(heatmap.columns)


def test_req_obj_001_after_tax_estate_value_is_reported():
    """Verifies REQ-OBJ-001."""
    household = Household(current_age=55, projection_end_age=58, retirement_age=55)

    comparison = compare_conversion_strategies(
        household,
        fixed_conversion=50_000,
        max_conversion=150_000,
        preserve_rule_of_55=True,
    )

    expected = (
        comparison["ending_estate_value"]
        - comparison["estimated_federal_estate_tax"]
        - comparison["estimated_state_estate_tax"]
    )
    assert "after_tax_estate_value" in comparison.columns
    assert pytest.approx(expected.tolist(), abs=0.01) == comparison["after_tax_estate_value"].tolist()


def test_req_rmd_001_projection_reports_rmd_forecast():
    """Verifies REQ-RMD-001."""
    household = Household(current_age=72, projection_end_age=75, retirement_age=55)

    df = results_frame(project_household(household, strategy="No Roth conversions"))

    assert "rmd" in df.columns
    assert (df["rmd"] >= 0).all()
    assert df.loc[df["age"] == 75, "rmd"].iloc[0] > 0

