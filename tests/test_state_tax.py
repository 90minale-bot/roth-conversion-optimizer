from retirement_optimizer.tax.state import calculate_state_tax


def test_florida_has_no_income_tax():
    result = calculate_state_tax(
        state="FL",
        ordinary_income=250_000,
        pension_income=66_000,
        social_security=38_400,
        retirement_distributions=100_000,
        roth_conversion=100_000,
    )
    assert result.state_tax == 0


def test_illinois_excludes_retirement_income_in_baseline():
    result = calculate_state_tax(
        state="IL",
        ordinary_income=200_000,
        pension_income=66_000,
        social_security=38_400,
        retirement_distributions=50_000,
        roth_conversion=45_600,
    )
    assert result.taxable_income == 0


def test_pennsylvania_taxes_roth_conversion_but_not_retirement_distributions():
    result = calculate_state_tax(
        state="PA",
        ordinary_income=100_000,
        pension_income=0,
        social_security=0,
        retirement_distributions=40_000,
        roth_conversion=60_000,
    )
    assert round(result.state_tax, 2) == round(60_000 * 0.0307, 2)


def test_local_income_tax_uses_editable_rate_on_state_taxable_income():
    result = calculate_state_tax(
        state="PA",
        ordinary_income=100_000,
        pension_income=0,
        social_security=0,
        retirement_distributions=40_000,
        roth_conversion=60_000,
        local_tax_rate=0.01,
    )
    assert round(result.local_tax, 2) == 600.00
    assert result.marginal_rate == 0.0407
