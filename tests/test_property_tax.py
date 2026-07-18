from retirement_optimizer.models.household import Household
from retirement_optimizer.projections.annual_projection import project_household, results_frame
from retirement_optimizer.tax.property_tax import estimate_property_tax, estimate_property_value


def test_property_tax_defaults_to_one_million_property():
    household = Household(property_value=1_000_000, property_appreciation=0.0)
    assert estimate_property_tax(household, "IL", 0) == 20_800


def test_property_value_appreciates_by_offset():
    household = Household(property_value=1_000_000, property_appreciation=0.02)
    assert round(estimate_property_value(household, 2), 2) == 1_040_400


def test_projection_includes_property_tax_column_and_cashflow():
    household = Household(current_age=55, projection_end_age=55, retirement_age=55, property_value=1_000_000, property_appreciation=0.0)
    df = results_frame(project_household(household, strategy="No Roth conversions"))
    assert "property_tax" in df.columns
    assert df.iloc[0]["property_tax"] > 0
