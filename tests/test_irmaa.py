from retirement_optimizer.tax.irmaa import calculate_irmaa


def test_irmaa_is_zero_without_medicare_people():
    result = calculate_irmaa(
        lookback_magi=800_000,
        filing_status="married_joint",
        medicare_people=0,
    )
    assert result.surcharge == 0
    assert result.tier == 0


def test_irmaa_applies_joint_first_surcharge_tier_for_two_people():
    result = calculate_irmaa(
        lookback_magi=250_000,
        filing_status="married_joint",
        medicare_people=2,
    )
    expected = (81.20 + 14.50) * 12 * 2
    assert round(result.surcharge, 2) == round(expected, 2)
    assert result.tier == 1
