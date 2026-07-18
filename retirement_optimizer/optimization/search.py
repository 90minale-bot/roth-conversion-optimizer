from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from retirement_optimizer.models.household import Household
from retirement_optimizer.optimization.objectives import summarize_results
from retirement_optimizer.projections.annual_projection import project_household, results_frame


OBJECTIVE_COLUMNS = {
    "Minimize lifetime taxes": ("total_lifetime_tax", True),
    "Minimize taxes + healthcare": ("total_lifetime_tax_and_healthcare", True),
    "Maximize ending assets": ("ending_assets", False),
    "Maximize Roth balance": ("ending_roth", False),
    "Minimize peak RMD": ("peak_rmd", True),
    "Maximize after-tax estate value": ("after_tax_estate_value", False),
}


def _conversion_grid(max_conversion: float, step: float) -> list[float]:
    if step <= 0:
        step = max_conversion if max_conversion > 0 else 1.0
    values = []
    current = 0.0
    while current < max_conversion:
        values.append(round(current, 2))
        current += step
    values.append(round(max_conversion, 2))
    return sorted(set(values))


def _summary_row(df: pd.DataFrame, *, name: str, strategy: str) -> dict[str, float | str]:
    summary = asdict(summarize_results(df, name=name, strategy=strategy))
    summary["after_tax_estate_value"] = (
        float(summary["ending_estate_value"])
        - float(summary["estimated_federal_estate_tax"])
        - float(summary["estimated_state_estate_tax"])
    )
    return summary


def _constraint_notes(
    df: pd.DataFrame,
    *,
    max_marginal_federal_rate: float | None,
    max_annual_irmaa: float | None,
    min_ending_cash: float | None,
) -> tuple[bool, str, float, float, float]:
    max_rate = float(df["marginal_federal_rate"].max()) if "marginal_federal_rate" in df else 0.0
    max_irmaa = float(df["irmaa_surcharge"].max()) if "irmaa_surcharge" in df else 0.0
    ending_cash = float(df.iloc[-1]["ending_cash"]) if "ending_cash" in df else 0.0
    feasible = True
    reasons = []
    if max_marginal_federal_rate is not None and max_rate > max_marginal_federal_rate:
        feasible = False
        reasons.append("federal bracket")
    if max_annual_irmaa is not None and max_irmaa > max_annual_irmaa:
        feasible = False
        reasons.append("IRMAA")
    if min_ending_cash is not None and ending_cash < min_ending_cash:
        feasible = False
        reasons.append("ending cash")
    return feasible, ", ".join(reasons), max_rate, max_irmaa, ending_cash


def search_fixed_conversion_grid(
    household: Household,
    *,
    objective: str,
    max_conversion: float,
    step: float,
    preserve_rule_of_55: bool,
    max_marginal_federal_rate: float | None = None,
    max_annual_irmaa: float | None = None,
    min_ending_cash: float | None = None,
) -> pd.DataFrame:
    rows = []
    for fixed_conversion in _conversion_grid(max_conversion, step):
        df = results_frame(project_household(
            household,
            strategy="Fixed annual conversion",
            fixed_conversion=fixed_conversion,
            max_conversion=max_conversion,
            preserve_rule_of_55=preserve_rule_of_55,
        ))
        summary = _summary_row(
            df,
            name=f"Fixed ${fixed_conversion:,.0f}",
            strategy="Fixed annual conversion",
        )
        feasible, notes, max_rate, max_irmaa, ending_cash = _constraint_notes(
            df,
            max_marginal_federal_rate=max_marginal_federal_rate,
            max_annual_irmaa=max_annual_irmaa,
            min_ending_cash=min_ending_cash,
        )
        summary.update({
            "fixed_conversion": fixed_conversion,
            "max_marginal_federal_rate": max_rate,
            "max_annual_irmaa": max_irmaa,
            "ending_cash": ending_cash,
            "feasible": feasible,
            "constraint_notes": notes,
        })
        rows.append(summary)

    out = pd.DataFrame(rows)
    objective_col, ascending = OBJECTIVE_COLUMNS.get(objective, OBJECTIVE_COLUMNS["Minimize lifetime taxes"])
    feasible = out[out["feasible"]].copy()
    if feasible.empty:
        out["rank"] = pd.NA
        return out.sort_values("fixed_conversion").reset_index(drop=True)

    ranked = feasible.sort_values(objective_col, ascending=ascending).copy()
    ranked["rank"] = range(1, len(ranked) + 1)
    out = out.merge(ranked[["fixed_conversion", "rank"]], on="fixed_conversion", how="left")
    return out.sort_values(["rank", "fixed_conversion"], na_position="last").reset_index(drop=True)


def optimize_dynamic_conversion_schedule(
    household: Household,
    *,
    objective: str,
    start_age: int,
    end_age: int,
    max_conversion: float,
    step: float,
    preserve_rule_of_55: bool,
    max_marginal_federal_rate: float | None = None,
    max_annual_irmaa: float | None = None,
    min_ending_cash: float | None = None,
) -> dict[str, pd.DataFrame]:
    objective_col, ascending = OBJECTIVE_COLUMNS.get(objective, OBJECTIVE_COLUMNS["Minimize lifetime taxes"])
    candidate_amounts = _conversion_grid(max_conversion, step)
    first_age = max(int(start_age), int(household.retirement_age), int(household.current_age))
    last_age = min(int(end_age), int(household.projection_end_age))
    schedule: dict[int, float] = {}
    chosen_rows: list[dict[str, float | str | bool]] = []
    heatmap_rows: list[dict[str, float | str | bool]] = []

    for age in range(first_age, last_age + 1):
        candidate_rows: list[dict[str, float | str | bool]] = []
        for candidate in candidate_amounts:
            trial_schedule = {**schedule, age: candidate}
            df = results_frame(project_household(
                household,
                strategy="No Roth conversions",
                fixed_conversion=0.0,
                max_conversion=max_conversion,
                preserve_rule_of_55=preserve_rule_of_55,
                conversion_schedule=trial_schedule,
            ))
            summary = _summary_row(
                df,
                name=f"Dynamic age {age} ${candidate:,.0f}",
                strategy="Dynamic optimized schedule",
            )
            feasible, notes, max_rate, max_irmaa, ending_cash = _constraint_notes(
                df,
                max_marginal_federal_rate=max_marginal_federal_rate,
                max_annual_irmaa=max_annual_irmaa,
                min_ending_cash=min_ending_cash,
            )
            row = {
                **summary,
                "age": age,
                "candidate_conversion": candidate,
                "objective_value": float(summary[objective_col]),
                "max_marginal_federal_rate": max_rate,
                "max_annual_irmaa": max_irmaa,
                "ending_cash": ending_cash,
                "feasible": feasible,
                "constraint_notes": notes,
            }
            candidate_rows.append(row)
            heatmap_rows.append(row)

        candidates = pd.DataFrame(candidate_rows)
        pool = candidates[candidates["feasible"]].copy()
        if pool.empty:
            pool = candidates
        selected = pool.sort_values(["objective_value", "candidate_conversion"], ascending=[ascending, True]).iloc[0].to_dict()
        selected_conversion = float(selected["candidate_conversion"])
        schedule[age] = selected_conversion
        selected["selected_conversion"] = selected_conversion
        chosen_rows.append(selected)

    final_df = results_frame(project_household(
        household,
        strategy="No Roth conversions",
        fixed_conversion=0.0,
        max_conversion=max_conversion,
        preserve_rule_of_55=preserve_rule_of_55,
        conversion_schedule=schedule,
    ))
    final_summary = pd.DataFrame([_summary_row(
        final_df,
        name="Dynamic optimized schedule",
        strategy="Dynamic optimized schedule",
    )])
    schedule_df = pd.DataFrame(chosen_rows)
    if not schedule_df.empty:
        schedule_df = schedule_df[[
            "age",
            "selected_conversion",
            "objective_value",
            "total_lifetime_tax",
            "total_lifetime_tax_and_healthcare",
            "after_tax_estate_value",
            "ending_assets",
            "ending_roth",
            "ending_traditional",
            "peak_rmd",
            "max_marginal_federal_rate",
            "max_annual_irmaa",
            "feasible",
            "constraint_notes",
        ]]
    return {
        "schedule": schedule_df,
        "heatmap": pd.DataFrame(heatmap_rows),
        "projection": final_df,
        "summary": final_summary,
    }
