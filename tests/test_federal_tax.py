from retirement_optimizer.tax.federal import calculate_federal_tax, taxable_social_security


def test_standard_deduction_removes_low_income_tax():
    result = calculate_federal_tax(ordinary_income=32_200, filing_status="married_joint")
    assert result.taxable_income == 0
    assert result.ordinary_tax == 0


def test_married_joint_first_bracket_boundary():
    result = calculate_federal_tax(ordinary_income=32_200 + 24_000, filing_status="married_joint")
    assert result.taxable_income == 24_000
    assert round(result.ordinary_tax, 2) == 2_400


def test_married_joint_second_bracket_boundary():
    result = calculate_federal_tax(ordinary_income=32_200 + 100_800, filing_status="married_joint")
    expected = 24_000 * 0.10 + (100_800 - 24_000) * 0.12
    assert round(result.ordinary_tax, 2) == round(expected, 2)


def test_social_security_taxability_caps_at_85_percent():
    taxable = taxable_social_security(benefits=40_000, other_agi=200_000, filing_status="married_joint")
    assert taxable == 34_000
