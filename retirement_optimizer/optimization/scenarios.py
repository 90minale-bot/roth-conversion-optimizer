from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd

from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.objectives import summarize_results
from retirement_optimizer.projections.annual_projection import project_household, results_frame


def saved_scenario_row(
    *,
    name: str,
    household: Household,
    strategy: str,
    fixed_conversion: float,
    max_conversion: float,
    preserve_rule_of_55: bool,
) -> dict[str, float | str]:
    df = results_frame(project_household(
        household,
        strategy=strategy,
        fixed_conversion=fixed_conversion,
        max_conversion=max_conversion,
        preserve_rule_of_55=preserve_rule_of_55,
    ))
    return asdict(summarize_results(df, name=name, strategy=strategy))


def scenario_table(rows: list[dict[str, float | str]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def household_to_inputs(household: Household) -> dict[str, Any]:
    data = asdict(household)
    data["accounts"] = {
        key: asdict(account)
        for key, account in household.accounts.items()
    }
    return data


def scenario_package(
    *,
    name: str,
    household: Household,
    strategy: str,
    objective: str,
    fixed_conversion: float,
    max_conversion: float,
    preserve_rule_of_55: bool,
    grid_step: float,
    max_search_federal_rate: float,
    max_search_irmaa: float,
    min_search_cash: float,
    monte_carlo_runs: int,
    monte_carlo_volatility: float,
    monte_carlo_seed: int,
    stress_scenario: str,
    inflation_shock: bool,
    spending_guardrail: bool,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "name": name,
        "household": household_to_inputs(household),
        "settings": {
            "strategy": strategy,
            "objective": objective,
            "fixed_conversion": fixed_conversion,
            "max_conversion": max_conversion,
            "preserve_rule_of_55": preserve_rule_of_55,
            "grid_step": grid_step,
            "max_search_federal_rate": max_search_federal_rate,
            "max_search_irmaa": max_search_irmaa,
            "min_search_cash": min_search_cash,
            "monte_carlo_runs": monte_carlo_runs,
            "monte_carlo_volatility": monte_carlo_volatility,
            "monte_carlo_seed": monte_carlo_seed,
            "stress_scenario": stress_scenario,
            "inflation_shock": inflation_shock,
            "spending_guardrail": spending_guardrail,
        },
    }


def scenario_package_summary(package: dict[str, Any]) -> dict[str, Any]:
    household = package.get("household", {})
    accounts = household.get("accounts", {})
    settings = package.get("settings", {})
    return {
        "name": package.get("name", ""),
        "current_age": household.get("current_age"),
        "retirement_age": household.get("retirement_age"),
        "current_state": household.get("current_state"),
        "destination_state": household.get("destination_state"),
        "strategy": settings.get("strategy"),
        "objective": settings.get("objective"),
        "traditional_401k": accounts.get("employer_401k", {}).get("balance"),
        "traditional_ira": accounts.get("traditional_ira", {}).get("balance"),
        "roth_ira": accounts.get("roth_ira", {}).get("balance"),
        "taxable": accounts.get("taxable", {}).get("balance"),
    }
