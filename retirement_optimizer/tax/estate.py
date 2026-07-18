from __future__ import annotations

from dataclasses import dataclass


FEDERAL_ESTATE_EXEMPTION_2026 = 15_000_000
FEDERAL_ESTATE_TOP_RATE = 0.40

STATE_ESTATE_RULES = {
    "IL": {
        "exemption": 4_000_000,
        "rate": 0.16,
        "warning": "Illinois estate tax is approximated. Illinois has a cliff-style estate tax, so professional review is important near the exemption.",
    },
    "MD": {
        "exemption": 5_000_000,
        "rate": 0.16,
        "warning": "Maryland estate tax is approximated and inheritance-tax rules may also apply depending on beneficiary.",
    },
}

INHERITANCE_TAX_WARNINGS = {
    "PA": "Pennsylvania inheritance tax is beneficiary-specific and is not fully modeled.",
    "MD": "Maryland inheritance-tax rules may apply depending on beneficiary and relationship.",
}


@dataclass(frozen=True)
class EstateExposureResult:
    estate_value: float
    federal_exposure: float
    federal_estimated_tax: float
    state_exposure: float
    state_estimated_tax: float
    warning: str


def estimate_estate_exposure(
    *,
    estate_value: float,
    state: str,
    married: bool = True,
) -> EstateExposureResult:
    federal_exemption = FEDERAL_ESTATE_EXEMPTION_2026 * (2 if married else 1)
    federal_exposure = max(0.0, estate_value - federal_exemption)
    federal_tax = federal_exposure * FEDERAL_ESTATE_TOP_RATE

    state_code = state.upper()
    state_rule = STATE_ESTATE_RULES.get(state_code)
    state_exposure = 0.0
    state_tax = 0.0
    warnings = []
    if state_rule:
        state_exposure = max(0.0, estate_value - float(state_rule["exemption"]))
        state_tax = state_exposure * float(state_rule["rate"])
        if estate_value >= float(state_rule["exemption"]) * 0.9:
            warnings.append(str(state_rule["warning"]))
    if federal_exposure > 0:
        warnings.append("Federal estate exposure is estimated using the 2026 planning exemption and top rate.")
    inheritance_warning = INHERITANCE_TAX_WARNINGS.get(state_code)
    if inheritance_warning:
        warnings.append(inheritance_warning)

    return EstateExposureResult(
        estate_value=estate_value,
        federal_exposure=federal_exposure,
        federal_estimated_tax=federal_tax,
        state_exposure=state_exposure,
        state_estimated_tax=state_tax,
        warning="; ".join(warnings),
    )
