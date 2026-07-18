from retirement_optimizer.tax.niit import calculate_niit


def test_niit_is_zero_below_magi_threshold():
    result = calculate_niit(
        magi=240_000,
        qualified_dividends=10_000,
        long_term_capital_gains=20_000,
        filing_status="married_joint",
    )
    assert result.tax == 0


def test_niit_uses_lesser_of_investment_income_or_excess_magi():
    result = calculate_niit(
        magi=260_000,
        qualified_dividends=8_000,
        long_term_capital_gains=20_000,
        filing_status="married_joint",
    )
    assert round(result.tax, 2) == 380.00
