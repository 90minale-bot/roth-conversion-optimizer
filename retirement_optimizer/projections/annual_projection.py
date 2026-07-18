from __future__ import annotations

from copy import deepcopy
from collections.abc import Callable

import pandas as pd

from retirement_optimizer.cashflow.rollover import direct_rollover_to_ira, rule_of_55_warning
from retirement_optimizer.cashflow.roth_conversion import convert_to_roth
from retirement_optimizer.cashflow.withdrawals import fund_spending
from retirement_optimizer.models.annual_result import AnnualResult
from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.strategies import conversion_for_strategy
from retirement_optimizer.tax.aca import calculate_aca_premium
from retirement_optimizer.tax.estate import estimate_estate_exposure
from retirement_optimizer.tax.federal import calculate_federal_tax
from retirement_optimizer.tax.irmaa import calculate_irmaa
from retirement_optimizer.tax.niit import calculate_niit
from retirement_optimizer.tax.property_tax import estimate_property_tax, estimate_property_value
from retirement_optimizer.tax.rmd import calculate_rmd
from retirement_optimizer.tax.state import calculate_state_tax


def state_for_age(household: Household, age: int) -> str:
    if household.include_relocation and age >= household.move_age:
        return household.destination_state
    return household.current_state


def project_household(
    household: Household,
    *,
    start_year: int = 2026,
    tax_year: int = 2026,
    strategy: str = "Fill 22% bracket",
    fixed_conversion: float = 50_000,
    max_conversion: float = 250_000,
    preserve_rule_of_55: bool = True,
    conversion_schedule: dict[int, float] | None = None,
    return_provider: Callable[[int, int, str, object], float] | None = None,
    spending_growth_provider: Callable[[int, int, float], float] | None = None,
    spending_adjustment_provider: Callable[[int, int, float, float], float] | None = None,
) -> list[AnnualResult]:
    hh = deepcopy(household)
    direct_rollover_to_ira(hh, hh.preserve_rule_of_55_amount if preserve_rule_of_55 else 0.0)
    results: list[AnnualResult] = []
    spending = hh.annual_spending
    for offset, age in enumerate(range(hh.current_age, hh.projection_end_age + 1)):
        year = start_year + offset
        state = state_for_age(hh, age)
        for key, account in hh.accounts.items():
            annual_return = return_provider(offset, age, key, account) if return_provider else None
            account.grow(annual_return)
        portfolio_value = sum(account.balance for account in hh.accounts.values())
        if spending_adjustment_provider:
            spending = max(0.0, spending_adjustment_provider(offset, age, spending, portfolio_value))
        traditional_start = hh.accounts["traditional_ira"].balance + hh.accounts["employer_401k"].balance
        rmd = calculate_rmd(age, hh.birth_year, traditional_start)
        employment = hh.employment_income + hh.spouse_income if age < hh.retirement_age else 0.0
        pension = hh.pension_monthly * 12 if age >= hh.pension_start_age else 0.0
        social_security = hh.social_security_monthly * 12 if age >= hh.social_security_start_age else 0.0
        income_available_for_cash_flow = employment + pension + social_security
        property_tax = estimate_property_tax(hh, state, offset)
        qualified_dividends = min(hh.qualified_dividends * ((1.0 + hh.inflation) ** offset), hh.accounts["taxable"].balance * 0.04)
        long_term_capital_gains = hh.long_term_capital_gains + hh.accounts["taxable"].balance * hh.taxable_turnover_rate
        pre_tax_cash_need = spending + property_tax
        withdrawals = fund_spending(hh, max(0.0, pre_tax_cash_need - income_available_for_cash_flow), age)
        if rmd > withdrawals["traditional"]:
            extra_rmd = hh.accounts["traditional_ira"].withdraw(rmd - withdrawals["traditional"])
            withdrawals["traditional"] += extra_rmd
            hh.accounts["cash"].deposit(extra_rmd)
        ordinary_before_conversion = employment + pension + withdrawals["traditional"]
        if conversion_schedule is not None and age in conversion_schedule:
            planned_conversion = 0.0 if age < hh.retirement_age else float(conversion_schedule[age])
            planned_conversion = min(max(planned_conversion, 0.0), max_conversion)
        else:
            planned_conversion = conversion_for_strategy(strategy, hh, ordinary_before_conversion, tax_year, age, fixed_conversion, max_conversion)
        roth_conversion = convert_to_roth(hh, planned_conversion, preserve_rule_of_55)
        ordinary_income = ordinary_before_conversion + roth_conversion
        fed = calculate_federal_tax(
            ordinary_income=ordinary_income,
            social_security=social_security,
            qualified_dividends=qualified_dividends,
            long_term_capital_gains=long_term_capital_gains,
            filing_status=hh.filing_status,
            year=tax_year,
            age=age,
            spouse_age=hh.spouse_age,
        )
        niit = calculate_niit(
            magi=fed.agi,
            qualified_dividends=qualified_dividends,
            long_term_capital_gains=long_term_capital_gains,
            filing_status=hh.filing_status,
        )
        spouse_projection_age = (hh.spouse_age + offset) if hh.spouse_age is not None else age
        medicare_people = int(age >= 65)
        if hh.filing_status == "married_joint":
            medicare_people += int(spouse_projection_age >= 65)
        aca_covered_people = int(age < 65)
        if hh.filing_status == "married_joint":
            aca_covered_people += int(spouse_projection_age < 65)
        aca_magi = fed.agi + max(0.0, social_security - fed.taxable_social_security)
        aca = calculate_aca_premium(
            aca_magi=aca_magi,
            household_size=hh.household_size,
            state=state,
            covered_people=aca_covered_people,
            benchmark_premium_monthly=hh.aca_benchmark_premium_monthly,
        )
        lookback_result = results[offset - 2] if offset >= 2 else None
        irmaa_lookback_magi = lookback_result.agi if lookback_result is not None else fed.agi
        irmaa = calculate_irmaa(
            lookback_magi=irmaa_lookback_magi,
            filing_status=hh.filing_status,
            medicare_people=medicare_people,
            has_two_year_lookback=lookback_result is not None,
        )
        state_tax = calculate_state_tax(
            state=state,
            ordinary_income=ordinary_income + fed.taxable_social_security,
            pension_income=pension,
            social_security=social_security,
            retirement_distributions=withdrawals["traditional"],
            roth_conversion=roth_conversion,
            qualified_dividends=qualified_dividends,
            long_term_capital_gains=long_term_capital_gains,
            filing_status=hh.filing_status,
            year=tax_year,
            local_tax_rate=hh.local_income_tax_rates.get(state, 0.0),
        )
        estimated_estate_value = (
            hh.accounts["cash"].balance
            + hh.accounts["taxable"].balance
            + hh.accounts["traditional_ira"].balance
            + hh.accounts["employer_401k"].balance
            + hh.accounts["roth_ira"].balance
            + hh.accounts["hsa"].balance
            + estimate_property_value(hh, offset)
        )
        estate = estimate_estate_exposure(
            estate_value=estimated_estate_value,
            state=state,
            married=hh.filing_status == "married_joint",
        )
        tax_payment = fed.total_tax + niit.tax + irmaa.surcharge + state_tax.state_tax + state_tax.local_tax
        total_healthcare_premiums = aca.net_premium
        income_available_for_tax = max(0.0, income_available_for_cash_flow - pre_tax_cash_need)
        tax_withdrawals = fund_spending(hh, max(0.0, tax_payment + total_healthcare_premiums - income_available_for_tax), age)
        withdrawals["cash"] += tax_withdrawals["cash"]
        withdrawals["taxable"] += tax_withdrawals["taxable"]
        withdrawals["traditional"] += tax_withdrawals["traditional"]
        withdrawals["roth"] += tax_withdrawals["roth"]
        total_income = income_available_for_cash_flow
        total_withdrawals = sum(withdrawals.values())
        total_taxes = tax_payment
        available_spending_after_taxes = max(0.0, total_income + total_withdrawals - total_taxes - property_tax - total_healthcare_premiums)
        spending_surplus_shortfall = available_spending_after_taxes - spending
        warning = "; ".join(filter(None, [
            rule_of_55_warning(age, hh.retirement_age, hh.accounts["employer_401k"].balance, hh.preserve_rule_of_55_amount if preserve_rule_of_55 else 0.0),
            state_tax.warning,
            aca.warning,
            irmaa.warning,
            estate.warning,
            "Property tax uses state-level estimated effective rates; actual bills depend on county, municipality, exemptions, and assessment rules.",
            "Cash and taxable assets depleted before all spending/taxes were funded." if total_income + total_withdrawals < spending + property_tax + total_taxes + total_healthcare_premiums else "",
        ]))
        results.append(AnnualResult(
            year=year,
            age=age,
            state=state,
            employment_income=employment,
            pension_income=pension,
            social_security=social_security,
            qualified_dividends=qualified_dividends,
            long_term_capital_gains=long_term_capital_gains,
            traditional_withdrawals=withdrawals["traditional"],
            roth_conversion=roth_conversion,
            roth_withdrawals=withdrawals["roth"],
            taxable_withdrawals=withdrawals["taxable"],
            cash_withdrawals=withdrawals["cash"],
            gross_income=ordinary_income + social_security + qualified_dividends + long_term_capital_gains,
            agi=fed.agi,
            taxable_income=fed.taxable_income,
            federal_ordinary_tax=fed.ordinary_tax,
            federal_capital_gains_tax=fed.capital_gains_tax,
            federal_tax=fed.total_tax,
            niit=niit.tax,
            irmaa_surcharge=irmaa.surcharge,
            irmaa_lookback_magi=irmaa.lookback_magi,
            medicare_people=irmaa.medicare_people,
            aca_magi=aca_magi,
            aca_fpl_percent=aca.fpl_percent,
            aca_gross_premium=aca.gross_premium,
            aca_premium_tax_credit=aca.premium_tax_credit,
            aca_net_premium=aca.net_premium,
            aca_covered_people=aca.covered_people,
            state_tax=state_tax.state_tax,
            local_tax=state_tax.local_tax,
            property_tax=property_tax,
            spending=spending,
            total_income=total_income,
            total_withdrawals=total_withdrawals,
            total_taxes=total_taxes,
            available_spending_after_taxes=available_spending_after_taxes,
            spending_surplus_shortfall=spending_surplus_shortfall,
            ending_cash=hh.accounts["cash"].balance,
            ending_taxable=hh.accounts["taxable"].balance,
            ending_traditional=hh.accounts["traditional_ira"].balance + hh.accounts["employer_401k"].balance,
            ending_roth=hh.accounts["roth_ira"].balance,
            estimated_estate_value=estate.estate_value,
            federal_estate_exposure=estate.federal_exposure,
            estimated_federal_estate_tax=estate.federal_estimated_tax,
            state_estate_exposure=estate.state_exposure,
            estimated_state_estate_tax=estate.state_estimated_tax,
            rmd=rmd,
            effective_tax_rate=(fed.total_tax + niit.tax + irmaa.surcharge + state_tax.state_tax + state_tax.local_tax + property_tax) / fed.agi if fed.agi > 0 else 0.0,
            marginal_federal_rate=fed.marginal_rate,
            marginal_state_rate=state_tax.marginal_rate,
            remaining_bracket_capacity=fed.remaining_bracket_capacity if fed.remaining_bracket_capacity != float("inf") else 0.0,
            warning=warning,
        ))
        spending_growth = spending_growth_provider(offset, age, spending) if spending_growth_provider else hh.spending_inflation
        spending *= 1.0 + spending_growth
    return results


def results_frame(results: list[AnnualResult]) -> pd.DataFrame:
    return pd.DataFrame([r.to_dict() for r in results])
