from __future__ import annotations

from dataclasses import asdict, replace

import pandas as pd

from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.objectives import ScenarioSummary, summarize_results
from retirement_optimizer.optimization.strategies import STRATEGIES
from retirement_optimizer.projections.annual_projection import project_household, results_frame


def compare_conversion_strategies(
    household: Household,
    *,
    fixed_conversion: float,
    max_conversion: float,
    preserve_rule_of_55: bool,
) -> pd.DataFrame:
    rows = []
    for strategy in STRATEGIES:
        df = results_frame(project_household(
            household,
            strategy=strategy,
            fixed_conversion=fixed_conversion,
            max_conversion=max_conversion,
            preserve_rule_of_55=preserve_rule_of_55,
        ))
        rows.append(asdict(summarize_results(df, name=strategy, strategy=strategy)))
    return pd.DataFrame(rows)


def recommend_strategy(
    household: Household,
    *,
    objective: str,
    fixed_conversion: float,
    max_conversion: float,
    preserve_rule_of_55: bool,
) -> ScenarioSummary:
    comparison = compare_conversion_strategies(
        household,
        fixed_conversion=fixed_conversion,
        max_conversion=max_conversion,
        preserve_rule_of_55=preserve_rule_of_55,
    )
    if objective == "Maximize ending assets":
        row = comparison.sort_values("ending_assets", ascending=False).iloc[0]
    elif objective == "Maximize Roth balance":
        row = comparison.sort_values("ending_roth", ascending=False).iloc[0]
    elif objective == "Minimize peak RMD":
        row = comparison.sort_values("peak_rmd", ascending=True).iloc[0]
    elif objective == "Minimize taxes + healthcare":
        row = comparison.sort_values("total_lifetime_tax_and_healthcare", ascending=True).iloc[0]
    else:
        row = comparison.sort_values("total_lifetime_tax", ascending=True).iloc[0]
    return ScenarioSummary(**row.to_dict())


def compare_relocation_scenarios(
    household: Household,
    *,
    states: list[str],
    move_ages: list[int],
    strategy: str,
    fixed_conversion: float,
    max_conversion: float,
    preserve_rule_of_55: bool,
) -> pd.DataFrame:
    rows = []
    for state in states:
        for move_age in sorted(set(move_ages)):
            scenario = replace(household, destination_state=state, move_age=int(move_age), include_relocation=True)
            df = results_frame(project_household(
                scenario,
                strategy=strategy,
                fixed_conversion=fixed_conversion,
                max_conversion=max_conversion,
                preserve_rule_of_55=preserve_rule_of_55,
            ))
            summary = summarize_results(df, name=f"Move to {state} at {move_age}", strategy=strategy)
            row = asdict(summary)
            row["destination_state"] = state
            row["move_age"] = move_age
            rows.append(row)
    return pd.DataFrame(rows)


def annualized_relocation_advantage(
    grid: pd.DataFrame,
    *,
    projection_years: int,
    baseline_state: str = "MD",
    metric: str = "total_lifetime_tax_and_healthcare",
) -> pd.DataFrame:
    if grid.empty or metric not in grid.columns:
        return pd.DataFrame()

    idx = grid.groupby("destination_state")[metric].idxmin()
    best_by_state = grid.loc[idx].copy()
    baseline_rows = best_by_state[best_by_state["destination_state"] == baseline_state]
    if baseline_rows.empty:
        return pd.DataFrame()

    baseline = baseline_rows.iloc[0]
    years = max(1, int(projection_years))
    best_by_state["baseline_state"] = baseline_state
    best_by_state["baseline_move_age"] = baseline["move_age"]
    best_by_state["baseline_lifetime_cost"] = float(baseline[metric])
    best_by_state["lifetime_dollars_vs_baseline"] = best_by_state["baseline_lifetime_cost"] - best_by_state[metric]
    best_by_state["additional_dollars_per_year_vs_baseline"] = best_by_state["lifetime_dollars_vs_baseline"] / years
    columns = [
        "destination_state",
        "move_age",
        "baseline_state",
        "baseline_move_age",
        metric,
        "baseline_lifetime_cost",
        "lifetime_dollars_vs_baseline",
        "additional_dollars_per_year_vs_baseline",
        "ending_assets",
    ]
    return best_by_state[columns].sort_values(
        "additional_dollars_per_year_vs_baseline",
        ascending=False,
    ).reset_index(drop=True)
