from retirement_optimizer.tax.rmd import calculate_rmd, rmd_start_age


def test_rmd_starts_at_75_for_1960_or_later_birth_years():
    assert rmd_start_age(1977) == 75
    assert calculate_rmd(74, 1977, 1_000_000) == 0
    assert round(calculate_rmd(75, 1977, 1_000_000), 2) == round(1_000_000 / 24.6, 2)
