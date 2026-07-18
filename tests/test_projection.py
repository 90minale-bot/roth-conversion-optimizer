from retirement_optimizer.models.household import Household
from retirement_optimizer.projections.annual_projection import project_household, results_frame


def test_projection_runs_to_end_age_and_exports_columns():
    household = Household(current_age=55, projection_end_age=60, retirement_age=55)
    results = project_household(household, strategy="No Roth conversions")
    df = results_frame(results)
    assert len(df) == 6
    assert {"federal_tax", "niit", "irmaa_surcharge", "aca_net_premium", "aca_premium_tax_credit", "estimated_estate_value", "state_tax", "ending_traditional", "ending_roth"}.issubset(df.columns)


def test_fill_22_strategy_converts_some_amount():
    household = Household(current_age=55, projection_end_age=55, retirement_age=55)
    results = project_household(household, strategy="Fill 22% bracket")
    assert results[0].roth_conversion > 0


def test_projection_includes_editable_local_income_tax():
    household = Household(
        current_age=55,
        projection_end_age=55,
        retirement_age=55,
        current_state="PA",
        include_relocation=False,
        local_income_tax_rates={"PA": 0.01},
    )
    results = project_household(household, strategy="Fixed annual conversion", fixed_conversion=60_000)
    assert results[0].local_tax > 0


def test_projection_uses_current_and_destination_states():
    household = Household(
        current_age=49,
        projection_end_age=55,
        retirement_age=55,
        current_state="IL",
        destination_state="PA",
        include_relocation=True,
        move_age=52,
    )

    df = results_frame(project_household(household, strategy="No Roth conversions"))

    assert df.loc[df["age"] == 49, "state"].iloc[0] == "IL"
    assert df.loc[df["age"] == 52, "state"].iloc[0] == "PA"
    assert df.loc[df["age"] == 55, "state"].iloc[0] == "PA"


def test_roth_conversions_start_at_retirement_age():
    household = Household(current_age=53, projection_end_age=55, retirement_age=55)

    df = results_frame(project_household(household, strategy="Fixed annual conversion", fixed_conversion=60_000))

    assert df.loc[df["age"] == 53, "roth_conversion"].iloc[0] == 0
    assert df.loc[df["age"] == 54, "roth_conversion"].iloc[0] == 0
    assert df.loc[df["age"] == 55, "roth_conversion"].iloc[0] > 0
