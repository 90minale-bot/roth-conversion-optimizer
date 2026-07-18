from retirement_optimizer.tax.aca import applicable_percentage, calculate_aca_premium, poverty_guideline


def test_poverty_guideline_uses_household_size():
    assert poverty_guideline(2, "IL") == 21_150
    assert poverty_guideline(9, "IL") == 59_650


def test_applicable_percentage_returns_none_outside_subsidy_range():
    assert applicable_percentage(99.9) is None
    assert applicable_percentage(400.1) is None


def test_aca_premium_credit_reduces_benchmark_premium():
    result = calculate_aca_premium(
        aca_magi=42_300,
        household_size=2,
        state="IL",
        covered_people=2,
        benchmark_premium_monthly=1_800,
    )
    assert round(result.fpl_percent, 1) == 200.0
    assert result.premium_tax_credit > 0
    assert result.net_premium < result.gross_premium


def test_aca_subsidy_cliff_above_400_percent_fpl():
    result = calculate_aca_premium(
        aca_magi=100_000,
        household_size=2,
        state="IL",
        covered_people=2,
        benchmark_premium_monthly=1_800,
    )
    assert result.premium_tax_credit == 0
    assert result.net_premium == result.gross_premium
    assert "400% FPL" in result.warning
