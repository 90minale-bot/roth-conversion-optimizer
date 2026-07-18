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
        summary = asdict(summarize_results(
            df,
            name=f"Fixed ${fixed_conversion:,.0f}",
            strategy="Fixed annual conversion",
        ))
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
        summary.update({
            "fixed_conversion": fixed_conversion,
            "max_marginal_federal_rate": max_rate,
            "max_annual_irmaa": max_irmaa,
            "ending_cash": ending_cash,
            "feasible": feasible,
            "constraint_notes": ", ".join(reasons),
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
