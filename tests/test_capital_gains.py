from retirement_optimizer.tax.federal import calculate_federal_tax


def test_qualified_dividends_use_capital_gain_stack():
    result = calculate_federal_tax(
        ordinary_income=32_200,
        qualified_dividends=10_000,
        long_term_capital_gains=0,
        filing_status="married_joint",
    )
    assert result.ordinary_tax == 0
    assert result.capital_gains_tax == 0


def test_capital_gains_above_zero_percent_band_are_taxed():
    result = calculate_federal_tax(
        ordinary_income=140_000,
        qualified_dividends=0,
        long_term_capital_gains=20_000,
        filing_status="married_joint",
    )
    assert result.capital_gains_tax > 0
    assert result.total_tax == result.ordinary_tax + result.capital_gains_tax
