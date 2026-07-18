from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ScenarioSummary:
    name: str
    strategy: str
    lifetime_federal_tax: float
    lifetime_niit: float
    lifetime_irmaa: float
    lifetime_aca_net_premium: float
    lifetime_aca_premium_tax_credit: float
    lifetime_state_tax: float
    lifetime_local_tax: float
    lifetime_property_tax: float
    total_lifetime_tax: float
    total_lifetime_tax_and_healthcare: float
    ending_assets: float
    ending_roth: float
    ending_traditional: float
    ending_estate_value: float
    estimated_federal_estate_tax: float
    estimated_state_estate_tax: float
    peak_rmd: float
    average_effective_tax_rate: float


def summarize_results(df: pd.DataFrame, *, name: str, strategy: str) -> ScenarioSummary:
    ending_assets = float(df.iloc[-1][["ending_cash", "ending_taxable", "ending_traditional", "ending_roth"]].sum())
    property_tax = float(df["property_tax"].sum()) if "property_tax" in df else 0.0
    niit = float(df["niit"].sum()) if "niit" in df else 0.0
    irmaa = float(df["irmaa_surcharge"].sum()) if "irmaa_surcharge" in df else 0.0
    aca_net_premium = float(df["aca_net_premium"].sum()) if "aca_net_premium" in df else 0.0
    aca_credit = float(df["aca_premium_tax_credit"].sum()) if "aca_premium_tax_credit" in df else 0.0
    total_tax = float(df["federal_tax"].sum() + niit + irmaa + df["state_tax"].sum() + df["local_tax"].sum() + property_tax)
    agi_total = float(df["agi"].sum())
    return ScenarioSummary(
        name=name,
        strategy=strategy,
        lifetime_federal_tax=float(df["federal_tax"].sum()),
        lifetime_niit=niit,
        lifetime_irmaa=irmaa,
        lifetime_aca_net_premium=aca_net_premium,
        lifetime_aca_premium_tax_credit=aca_credit,
        lifetime_state_tax=float(df["state_tax"].sum()),
        lifetime_local_tax=float(df["local_tax"].sum()),
        lifetime_property_tax=property_tax,
        total_lifetime_tax=total_tax,
        total_lifetime_tax_and_healthcare=total_tax + aca_net_premium,
        ending_assets=ending_assets,
        ending_roth=float(df.iloc[-1]["ending_roth"]),
        ending_traditional=float(df.iloc[-1]["ending_traditional"]),
        ending_estate_value=float(df.iloc[-1].get("estimated_estate_value", ending_assets)),
        estimated_federal_estate_tax=float(df.iloc[-1].get("estimated_federal_estate_tax", 0.0)),
        estimated_state_estate_tax=float(df.iloc[-1].get("estimated_state_estate_tax", 0.0)),
        peak_rmd=float(df["rmd"].max()),
        average_effective_tax_rate=total_tax / agi_total if agi_total > 0 else 0.0,
    )
