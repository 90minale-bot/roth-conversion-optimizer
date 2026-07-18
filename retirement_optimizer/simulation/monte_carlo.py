from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from retirement_optimizer.models.account import Account
from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.objectives import summarize_results
from retirement_optimizer.projections.annual_projection import project_household, results_frame


@dataclass(frozen=True)
class MonteCarloSummary:
    simulations: int
    success_rate: float
    median_ending_assets: float
    p10_ending_assets: float
    p90_ending_assets: float
    median_lifetime_tax_and_healthcare: float
    p10_lifetime_tax_and_healthcare: float
    p90_lifetime_tax_and_healthcare: float


def _account_return_params(account_key: str, account: Account, volatility: float) -> tuple[float, float]:
    if account_key == "cash":
        return account.expected_return, max(0.005, volatility * 0.10)
    if account_key == "hsa":
        return account.expected_return, max(0.03, volatility * 0.55)
    if account_key == "taxable":
        return account.expected_return, max(0.04, volatility * 0.65)
    return account.expected_return, volatility


def run_monte_carlo(
    household: Household,
    *,
    strategy: str,
    fixed_conversion: float,
    max_conversion: float,
    preserve_rule_of_55: bool,
    conversion_start_age: int = 52,
    conversion_end_age: int = 75,
    simulations: int = 200,
    volatility: float = 0.12,
    seed: int = 42,
    stress_scenario: str = "Random returns",
    inflation_shock: bool = False,
    spending_guardrail: bool = False,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for simulation_id in range(1, simulations + 1):
        yearly_returns: dict[tuple[int, str], float] = {}

        def return_provider(offset: int, age: int, account_key: str, account: Account) -> float:
            key = (offset, account_key)
            if key not in yearly_returns:
                if stress_scenario == "Early bear market" and offset in (0, 1) and account_key != "cash":
                    yearly_returns[key] = -0.25 if offset == 0 else -0.10
                    return yearly_returns[key]
                if stress_scenario == "Late bear market" and offset in (10, 11) and account_key != "cash":
                    yearly_returns[key] = -0.25 if offset == 10 else -0.10
                    return yearly_returns[key]
                mean, stdev = _account_return_params(account_key, account, volatility)
                yearly_returns[key] = max(-0.80, float(rng.normal(mean, stdev)))
            return yearly_returns[key]

        def spending_growth_provider(offset: int, age: int, current_spending: float) -> float:
            if inflation_shock and offset < 3:
                return 0.07
            return household.spending_inflation

        initial_portfolio = sum(account.balance for account in household.accounts.values())

        def spending_adjustment_provider(offset: int, age: int, current_spending: float, portfolio_value: float) -> float:
            if not spending_guardrail or initial_portfolio <= 0:
                return current_spending
            if portfolio_value < initial_portfolio * 0.75:
                return current_spending * 0.95
            if portfolio_value > initial_portfolio * 1.25:
                return current_spending * 1.02
            return current_spending

        df = results_frame(project_household(
            household,
            strategy=strategy,
            fixed_conversion=fixed_conversion,
            max_conversion=max_conversion,
            preserve_rule_of_55=preserve_rule_of_55,
            conversion_start_age=conversion_start_age,
            conversion_end_age=conversion_end_age,
            return_provider=return_provider,
            spending_growth_provider=spending_growth_provider,
            spending_adjustment_provider=spending_adjustment_provider,
        ))
        summary = summarize_results(df, name=f"Simulation {simulation_id}", strategy=strategy)
        ending_assets = summary.ending_assets
        rows.append({
            "simulation": simulation_id,
            "ending_assets": ending_assets,
            "ending_roth": summary.ending_roth,
            "ending_traditional": summary.ending_traditional,
            "ending_estate_value": summary.ending_estate_value,
            "total_lifetime_tax": summary.total_lifetime_tax,
            "total_lifetime_tax_and_healthcare": summary.total_lifetime_tax_and_healthcare,
            "peak_rmd": summary.peak_rmd,
            "stress_scenario": stress_scenario,
            "inflation_shock": inflation_shock,
            "spending_guardrail": spending_guardrail,
            "success": ending_assets > 0,
        })
    return pd.DataFrame(rows)


def summarize_monte_carlo(results: pd.DataFrame) -> MonteCarloSummary:
    if results.empty:
        return MonteCarloSummary(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ending_assets = results["ending_assets"]
    tax_healthcare = results["total_lifetime_tax_and_healthcare"]
    return MonteCarloSummary(
        simulations=int(len(results)),
        success_rate=float(results["success"].mean()),
        median_ending_assets=float(ending_assets.quantile(0.50)),
        p10_ending_assets=float(ending_assets.quantile(0.10)),
        p90_ending_assets=float(ending_assets.quantile(0.90)),
        median_lifetime_tax_and_healthcare=float(tax_healthcare.quantile(0.50)),
        p10_lifetime_tax_and_healthcare=float(tax_healthcare.quantile(0.10)),
        p90_lifetime_tax_and_healthcare=float(tax_healthcare.quantile(0.90)),
    )
