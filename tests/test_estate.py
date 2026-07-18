from retirement_optimizer.tax.estate import estimate_estate_exposure


def test_federal_estate_exposure_uses_married_exemption():
    result = estimate_estate_exposure(
        estate_value=35_000_000,
        state="FL",
        married=True,
    )
    assert result.federal_exposure == 5_000_000
    assert result.federal_estimated_tax == 2_000_000


def test_illinois_state_estate_exposure_is_flagged_near_threshold():
    result = estimate_estate_exposure(
        estate_value=4_500_000,
        state="IL",
        married=True,
    )
    assert result.state_exposure == 500_000
    assert result.state_estimated_tax == 80_000
    assert "Illinois estate tax" in result.warning

