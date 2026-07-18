from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from retirement_optimizer.models.household import DEFAULT_LOCAL_INCOME_TAX_RATES, DEFAULT_PROPERTY_TAX_RATES, Household
from retirement_optimizer.optimization.deterministic import annualized_relocation_advantage, compare_conversion_strategies, compare_relocation_scenarios, recommend_strategy
from retirement_optimizer.optimization.objectives import summarize_results
from retirement_optimizer.optimization.scenarios import saved_scenario_row, scenario_package, scenario_package_summary, scenario_table
from retirement_optimizer.optimization.search import search_fixed_conversion_grid
from retirement_optimizer.optimization.strategies import STRATEGIES
from retirement_optimizer.projections.annual_projection import project_household, results_frame
from retirement_optimizer.reporting.exports import to_excel_bytes
from retirement_optimizer.simulation.monte_carlo import run_monte_carlo, summarize_monte_carlo


PROJECT_ROOT = Path(__file__).resolve().parent
STATES = ["IL", "PA", "MD", "DE", "VA", "FL"]


def money(value: float) -> str:
    return f"${value:,.0f}"


def sidebar_household() -> tuple[Household, str, str, float, float, bool, float, float, float, float, int, float, int, str, bool, bool]:
    st.sidebar.header("Personal")
    current_age = st.sidebar.number_input("Current age", 18, 100, 50)
    spouse_age_enabled = st.sidebar.checkbox("Include spouse age", value=False)
    spouse_age = st.sidebar.number_input("Spouse age", 18, 100, 49) if spouse_age_enabled else None
    filing_status = st.sidebar.selectbox("Filing status", ["married_joint", "single", "head_of_household"])
    retirement_age = st.sidebar.number_input("What age do you plan to retire?", 45, 75, 55)
    projection_end_age = st.sidebar.number_input("Projection end age", 70, 105, 95)

    st.sidebar.header("Accounts")
    employer_401k = st.sidebar.number_input("Traditional 401(k)", min_value=0.0, value=2_000_000.0, step=10_000.0)
    traditional_ira = st.sidebar.number_input("Traditional IRA", min_value=0.0, value=100_000.0, step=10_000.0)
    roth_ira = st.sidebar.number_input("Roth IRA", min_value=0.0, value=350_000.0, step=10_000.0)
    taxable = st.sidebar.number_input("Taxable brokerage", min_value=0.0, value=500_000.0, step=10_000.0)
    cash = st.sidebar.number_input("Cash", min_value=0.0, value=80_000.0, step=5_000.0)
    hsa = st.sidebar.number_input("HSA", min_value=0.0, value=25_000.0, step=1_000.0)

    st.sidebar.header("Income")
    employment_income = st.sidebar.number_input("Employment income before retirement", min_value=0.0, value=0.0, step=10_000.0)
    spouse_income = st.sidebar.number_input("Spouse income before retirement", min_value=0.0, value=0.0, step=10_000.0)
    pension_monthly = st.sidebar.number_input("Monthly pension", min_value=0.0, value=5_500.0, step=100.0)
    pension_start_age = st.sidebar.number_input("Pension start age", 50, 80, 65)
    social_security_monthly = st.sidebar.number_input("Monthly Social Security", min_value=0.0, value=3_200.0, step=100.0)
    social_security_start_age = st.sidebar.number_input("Social Security start age", 62, 70, 67)
    qualified_dividends = st.sidebar.number_input("Annual qualified dividends", min_value=0.0, value=6_000.0, step=500.0)
    long_term_capital_gains = st.sidebar.number_input("Manual annual long-term gains", min_value=0.0, value=0.0, step=1_000.0)
    taxable_turnover_rate = st.sidebar.slider("Taxable turnover rate", 0.0, 0.10, 0.02, 0.005)

    st.sidebar.header("Spending And Tax")
    annual_spending = st.sidebar.number_input("Annual spending in today's dollars", min_value=0.0, value=120_000.0, step=5_000.0)
    spending_inflation = st.sidebar.slider("Spending inflation", 0.0, 0.08, 0.025, 0.001)
    household_size = st.sidebar.number_input("ACA household size", 1, 8, 2)
    aca_benchmark_premium_monthly = st.sidebar.number_input("ACA benchmark premium / month", min_value=0.0, value=1_800.0, step=100.0)
    property_value = st.sidebar.number_input("Property value", min_value=0.0, value=1_000_000.0, step=25_000.0)
    property_appreciation = st.sidebar.slider("Property appreciation", 0.0, 0.08, 0.02, 0.001)
    st.sidebar.caption(f"Modeled states: {', '.join(STATES)}")
    current_state = st.sidebar.selectbox("Where do you live now?", STATES, index=5)
    include_relocation = st.sidebar.checkbox("Do you plan to move before retirement?", value=True)
    destination_state = st.sidebar.selectbox(
        "What state do you plan to move to?",
        STATES,
        index=STATES.index(current_state),
        disabled=not include_relocation,
    )
    move_age = st.sidebar.number_input(
        "At what age do you plan to move?",
        45,
        90,
        int(retirement_age),
        disabled=not include_relocation,
    )
    if not include_relocation:
        destination_state = current_state
    with st.sidebar.expander("Estimated property tax rates"):
        property_tax_rates = {
            state: st.number_input(
                f"{state} effective rate",
                min_value=0.0,
                max_value=0.05,
                value=float(DEFAULT_PROPERTY_TAX_RATES[state]),
                step=0.001,
                format="%.4f",
            )
            for state in STATES
        }
    with st.sidebar.expander("Estimated local income tax rates"):
        local_income_tax_rates = {
            state: st.number_input(
                f"{state} local income rate",
                min_value=0.0,
                max_value=0.05,
                value=float(DEFAULT_LOCAL_INCOME_TAX_RATES[state]),
                step=0.001,
                format="%.4f",
            )
            for state in STATES
        }

    st.sidebar.header("Optimization")
    objective = st.sidebar.selectbox("Objective", ["Minimize lifetime taxes", "Minimize taxes + healthcare", "Maximize ending assets", "Maximize Roth balance", "Minimize peak RMD"])
    strategy = st.sidebar.selectbox("Conversion strategy", STRATEGIES, index=3)
    fixed_conversion = st.sidebar.number_input("Fixed annual Roth conversion", min_value=0.0, value=50_000.0, step=5_000.0)
    max_conversion = st.sidebar.number_input("Maximum annual Roth conversion", min_value=0.0, value=250_000.0, step=10_000.0)
    grid_step = st.sidebar.number_input("Grid search step", min_value=5_000.0, value=25_000.0, step=5_000.0)
    max_search_federal_rate = st.sidebar.slider("Grid max federal marginal rate", 0.10, 0.50, 0.24, 0.01)
    max_search_irmaa = st.sidebar.number_input("Grid max annual IRMAA", min_value=0.0, value=20_000.0, step=1_000.0)
    min_search_cash = st.sidebar.number_input("Grid minimum ending cash", min_value=0.0, value=0.0, step=5_000.0)
    preserve_rule = st.sidebar.checkbox("Preserve Rule of 55 assets", value=True)
    preserve_amount = st.sidebar.number_input("Employer-plan amount to preserve", min_value=0.0, value=240_000.0, step=10_000.0)
    st.sidebar.header("Monte Carlo")
    monte_carlo_runs = st.sidebar.number_input("Simulation runs", min_value=25, max_value=1_000, value=200, step=25)
    monte_carlo_volatility = st.sidebar.slider("Portfolio volatility", 0.02, 0.30, 0.12, 0.01)
    monte_carlo_seed = st.sidebar.number_input("Random seed", min_value=1, value=42, step=1)
    stress_scenario = st.sidebar.selectbox("Stress scenario", ["Random returns", "Early bear market", "Late bear market"])
    inflation_shock = st.sidebar.checkbox("Inflation shock", value=False)
    spending_guardrail = st.sidebar.checkbox("Dynamic spending guardrail", value=False)

    hh = Household(
        current_age=int(current_age),
        spouse_age=int(spouse_age) if spouse_age is not None else None,
        filing_status=filing_status,
        retirement_age=int(retirement_age),
        projection_end_age=int(projection_end_age),
        current_state=current_state,
        destination_state=destination_state,
        include_relocation=include_relocation,
        move_age=int(move_age),
        annual_spending=annual_spending,
        spending_inflation=spending_inflation,
        household_size=int(household_size),
        aca_benchmark_premium_monthly=aca_benchmark_premium_monthly,
        property_value=property_value,
        property_appreciation=property_appreciation,
        property_tax_rates=property_tax_rates,
        local_income_tax_rates=local_income_tax_rates,
        employment_income=employment_income,
        spouse_income=spouse_income,
        pension_monthly=pension_monthly,
        pension_start_age=int(pension_start_age),
        social_security_monthly=social_security_monthly,
        social_security_start_age=int(social_security_start_age),
        qualified_dividends=qualified_dividends,
        long_term_capital_gains=long_term_capital_gains,
        taxable_turnover_rate=taxable_turnover_rate,
        preserve_rule_of_55_amount=preserve_amount,
    )
    hh.accounts["employer_401k"].balance = employer_401k
    hh.accounts["traditional_ira"].balance = traditional_ira
    hh.accounts["roth_ira"].balance = roth_ira
    hh.accounts["taxable"].balance = taxable
    hh.accounts["cash"].balance = cash
    hh.accounts["hsa"].balance = hsa
    return hh, strategy, objective, fixed_conversion, max_conversion, preserve_rule, grid_step, max_search_federal_rate, max_search_irmaa, min_search_cash, int(monte_carlo_runs), monte_carlo_volatility, int(monte_carlo_seed), stress_scenario, inflation_shock, spending_guardrail


def summarize(df: pd.DataFrame) -> dict[str, float]:
    summary = summarize_results(df, name="Current", strategy="Current")
    return {
        "federal_tax": summary.lifetime_federal_tax,
        "niit": summary.lifetime_niit,
        "irmaa": summary.lifetime_irmaa,
        "aca_net_premium": summary.lifetime_aca_net_premium,
        "aca_premium_tax_credit": summary.lifetime_aca_premium_tax_credit,
        "state_tax": summary.lifetime_state_tax,
        "property_tax": summary.lifetime_property_tax,
        "total_tax": summary.total_lifetime_tax,
        "total_tax_and_healthcare": summary.total_lifetime_tax_and_healthcare,
        "ending_assets": summary.ending_assets,
        "ending_roth": summary.ending_roth,
        "ending_traditional": summary.ending_traditional,
        "ending_estate_value": summary.ending_estate_value,
        "estimated_federal_estate_tax": summary.estimated_federal_estate_tax,
        "estimated_state_estate_tax": summary.estimated_state_estate_tax,
        "peak_rmd": summary.peak_rmd,
        "average_effective_tax_rate": summary.average_effective_tax_rate,
    }


st.set_page_config(page_title="Retirement Tax Optimizer", layout="wide")
st.title("Retirement Rollover And Roth Conversion Optimizer")
st.caption("Planning and educational baseline only. Recommendations are estimates, not guarantees or tax advice.")

if "saved_scenarios" not in st.session_state:
    st.session_state.saved_scenarios = []
if "saved_scenario_packages" not in st.session_state:
    st.session_state.saved_scenario_packages = []

household, strategy, objective, fixed_conversion, max_conversion, preserve_rule, grid_step, max_search_federal_rate, max_search_irmaa, min_search_cash, monte_carlo_runs, monte_carlo_volatility, monte_carlo_seed, stress_scenario, inflation_shock, spending_guardrail = sidebar_household()
results = project_household(household, strategy=strategy, fixed_conversion=fixed_conversion, max_conversion=max_conversion, preserve_rule_of_55=preserve_rule)
df = results_frame(results)
summary = summarize(df)
no_conversion_df = results_frame(project_household(household, strategy="No Roth conversions", preserve_rule_of_55=preserve_rule))
no_conversion_summary = summarize(no_conversion_df)
recommended = recommend_strategy(
    household,
    objective=objective,
    fixed_conversion=fixed_conversion,
    max_conversion=max_conversion,
    preserve_rule_of_55=preserve_rule,
)

tabs = st.tabs([
    "Executive Summary",
    "Recommended Conversion Plan",
    "Annual Cash Flow",
    "Federal Taxes",
    "State Taxes",
    "Relocation Comparison",
    "Account Balances",
    "RMD Forecast",
    "ACA and Medicare",
    "Estate and Legacy",
    "Monte Carlo",
    "Scenario Comparison",
    "Tax Data and Sources",
    "Assumptions and Warnings",
])

with tabs[0]:
    first = df.iloc[0]
    cols = st.columns(4)
    cols[0].metric("Recommended conversion this year", money(first["roth_conversion"]))
    cols[1].metric("Lifetime federal tax", money(summary["federal_tax"] + summary["niit"]))
    cols[2].metric("Lifetime hidden cliffs", money(summary["irmaa"] + summary["niit"]))
    cols[3].metric("Ending assets", money(summary["ending_assets"]))
    st.metric("Projected estate value", money(summary["ending_estate_value"]))
    st.metric("Lifetime state income tax", money(summary["state_tax"]))
    st.metric("Lifetime ACA net premiums", money(summary["aca_net_premium"]), delta=f"{money(summary['aca_premium_tax_credit'])} estimated credits")
    st.metric("Lifetime estimated IRMAA", money(summary["irmaa"]))
    st.success(f"Best strategy for '{objective}': {recommended.strategy}")
    st.metric("Estimated lifetime tax + healthcare savings vs no conversions", money(no_conversion_summary["total_tax_and_healthcare"] - summary["total_tax_and_healthcare"]))
    st.dataframe(df[["year", "age", "state", "roth_conversion", "federal_tax", "niit", "irmaa_surcharge", "aca_net_premium", "state_tax", "property_tax", "effective_tax_rate", "ending_traditional", "ending_roth", "warning"]], width="stretch")

with tabs[1]:
    st.plotly_chart(px.bar(df, x="age", y="roth_conversion", title="Annual Roth Conversions"), width="stretch")
    st.dataframe(df[["year", "age", "roth_conversion", "remaining_bracket_capacity", "marginal_federal_rate", "marginal_state_rate", "ending_traditional", "ending_roth"]], width="stretch")
    st.subheader("Fixed Conversion Grid Search")
    search_df = search_fixed_conversion_grid(
        household,
        objective=objective,
        max_conversion=max_conversion,
        step=grid_step,
        preserve_rule_of_55=preserve_rule,
        max_marginal_federal_rate=max_search_federal_rate,
        max_annual_irmaa=max_search_irmaa,
        min_ending_cash=min_search_cash,
    )
    best_search = search_df[search_df["rank"] == 1]
    if best_search.empty:
        st.warning("No grid-search rows met the selected constraints. Relax the federal rate, IRMAA, or ending-cash limits.")
    else:
        best_row = best_search.iloc[0]
        st.success(f"Best fixed conversion by '{objective}': {money(best_row['fixed_conversion'])}")
    st.dataframe(search_df[[
        "rank",
        "fixed_conversion",
        "feasible",
        "constraint_notes",
        "total_lifetime_tax",
        "total_lifetime_tax_and_healthcare",
        "ending_assets",
        "ending_roth",
        "peak_rmd",
        "max_marginal_federal_rate",
        "max_annual_irmaa",
        "ending_cash",
    ]], width="stretch")
    st.plotly_chart(px.scatter(
        search_df,
        x="fixed_conversion",
        y="total_lifetime_tax_and_healthcare",
        color="feasible",
        size="ending_assets",
        title="Grid Search: Fixed Conversion vs Taxes + Healthcare",
    ), width="stretch")

with tabs[2]:
    st.dataframe(df, width="stretch")
    st.download_button("Download CSV", df.to_csv(index=False), "annual_plan.csv", "text/csv")
    st.download_button("Download Excel", to_excel_bytes(df), "annual_plan.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tabs[3]:
    st.plotly_chart(px.bar(df, x="age", y="federal_tax", title="Federal Taxes By Year"), width="stretch")
    st.plotly_chart(px.bar(df, x="age", y=["federal_ordinary_tax", "federal_capital_gains_tax", "niit"], title="Federal Ordinary, Capital-Gain, And NIIT"), width="stretch")
    st.dataframe(df[["year", "age", "agi", "taxable_income", "qualified_dividends", "long_term_capital_gains", "federal_ordinary_tax", "federal_capital_gains_tax", "niit", "federal_tax", "remaining_bracket_capacity"]], width="stretch")

with tabs[4]:
    st.plotly_chart(px.bar(df, x="age", y="state_tax", color="state", title="State Taxes By Year"), width="stretch")
    st.plotly_chart(px.bar(df, x="age", y="property_tax", color="state", title="Estimated Property Taxes By Year"), width="stretch")
    st.dataframe(df[["year", "age", "state", "state_tax", "local_tax", "property_tax", "warning"]], width="stretch")

with tabs[5]:
    grid = compare_relocation_scenarios(
        household,
        states=STATES,
        move_ages=[household.retirement_age, 55, 57, 60, 65],
        strategy=strategy,
        fixed_conversion=fixed_conversion,
        max_conversion=max_conversion,
        preserve_rule_of_55=preserve_rule,
    )
    best_move = grid.sort_values("total_lifetime_tax").iloc[0]
    st.success(f"Lowest modeled lifetime tax, including estimated property tax: move to {best_move['destination_state']} at age {int(best_move['move_age'])}")
    projection_years = household.projection_end_age - household.current_age + 1
    annualized = annualized_relocation_advantage(
        grid,
        projection_years=projection_years,
        baseline_state="MD",
        metric="total_lifetime_tax_and_healthcare",
    )
    if not annualized.empty:
        st.subheader("Annual Dollars Available vs Maryland")
        st.caption("Positive values mean the state's best modeled move scenario leaves more dollars available per year than Maryland's best modeled move scenario.")
        best_state = annualized.iloc[0]
        st.metric(
            f"Best annual advantage vs MD: {best_state['destination_state']}",
            money(best_state["additional_dollars_per_year_vs_baseline"]),
            delta=f"{money(best_state['lifetime_dollars_vs_baseline'])} lifetime",
        )
        display_annualized = annualized.rename(columns={
            "destination_state": "state",
            "move_age": "best_move_age",
            "total_lifetime_tax_and_healthcare": "best_lifetime_tax_and_healthcare",
            "baseline_lifetime_cost": "md_best_lifetime_tax_and_healthcare",
            "lifetime_dollars_vs_baseline": "lifetime_dollars_vs_md",
            "additional_dollars_per_year_vs_baseline": "additional_dollars_per_year_vs_md",
        })
        st.plotly_chart(px.bar(
            display_annualized,
            x="state",
            y="additional_dollars_per_year_vs_md",
            color="state",
            title="Additional Dollars Per Year Available vs Maryland",
        ), width="stretch")
        st.dataframe(display_annualized[[
            "state",
            "best_move_age",
            "baseline_state",
            "baseline_move_age",
            "additional_dollars_per_year_vs_md",
            "lifetime_dollars_vs_md",
            "best_lifetime_tax_and_healthcare",
            "md_best_lifetime_tax_and_healthcare",
            "ending_assets",
        ]], width="stretch")
    st.plotly_chart(px.density_heatmap(grid, x="move_age", y="destination_state", z="total_lifetime_tax", title="Relocation Lifetime Tax Heat Map"), width="stretch")
    st.dataframe(grid, width="stretch")

with tabs[6]:
    balance_df = df.melt(id_vars=["year", "age"], value_vars=["ending_cash", "ending_taxable", "ending_traditional", "ending_roth"], var_name="Account", value_name="Balance")
    st.plotly_chart(px.line(balance_df, x="age", y="Balance", color="Account", title="Account Balances"), width="stretch")

with tabs[7]:
    st.plotly_chart(px.bar(df, x="age", y="rmd", title="Required Minimum Distributions"), width="stretch")
    st.dataframe(df[["year", "age", "rmd", "ending_traditional"]], width="stretch")

with tabs[8]:
    st.warning("ACA, Medicare IRMAA, and NIIT are planning estimates. Verify marketplace premiums, subsidy eligibility, Medicare notices, and tax rules before real decisions.")
    st.plotly_chart(px.bar(df, x="age", y=["aca_gross_premium", "aca_premium_tax_credit", "aca_net_premium"], title="ACA Bridge Premiums And Credits"), width="stretch")
    st.plotly_chart(px.bar(df, x="age", y="irmaa_surcharge", title="Estimated Medicare IRMAA Surcharge"), width="stretch")
    st.plotly_chart(px.bar(df, x="age", y="niit", title="Estimated Net Investment Income Tax"), width="stretch")
    st.dataframe(df[["year", "age", "agi", "aca_magi", "aca_fpl_percent", "aca_covered_people", "aca_gross_premium", "aca_premium_tax_credit", "aca_net_premium", "irmaa_lookback_magi", "medicare_people", "irmaa_surcharge", "qualified_dividends", "long_term_capital_gains", "niit", "warning"]], width="stretch")

with tabs[9]:
    st.warning("Estate and inheritance tax values are planning estimates. Confirm federal exemptions, state estate tax rules, beneficiary relationships, portability, trusts, and titling with qualified professionals.")
    estate_cols = st.columns(3)
    estate_cols[0].metric("Projected estate value", money(summary["ending_estate_value"]))
    estate_cols[1].metric("Estimated federal estate tax", money(summary["estimated_federal_estate_tax"]))
    estate_cols[2].metric("Estimated state estate tax", money(summary["estimated_state_estate_tax"]))
    st.plotly_chart(px.line(df, x="age", y="estimated_estate_value", title="Projected Estate Value"), width="stretch")
    st.plotly_chart(px.bar(df, x="age", y=["federal_estate_exposure", "state_estate_exposure"], title="Estate Tax Exposure"), width="stretch")
    st.dataframe(df[["year", "age", "state", "estimated_estate_value", "federal_estate_exposure", "estimated_federal_estate_tax", "state_estate_exposure", "estimated_state_estate_tax", "ending_traditional", "ending_roth", "ending_taxable", "warning"]], width="stretch")

with tabs[10]:
    st.warning("Monte Carlo uses randomized annual account returns around each account's expected return. Tax rules remain simplified planning estimates.")
    mc_df = run_monte_carlo(
        household,
        strategy=strategy,
        fixed_conversion=fixed_conversion,
        max_conversion=max_conversion,
        preserve_rule_of_55=preserve_rule,
        simulations=monte_carlo_runs,
        volatility=monte_carlo_volatility,
        seed=monte_carlo_seed,
        stress_scenario=stress_scenario,
        inflation_shock=inflation_shock,
        spending_guardrail=spending_guardrail,
    )
    mc_summary = summarize_monte_carlo(mc_df)
    mc_cols = st.columns(4)
    mc_cols[0].metric("Success rate", f"{mc_summary.success_rate:.1%}")
    mc_cols[1].metric("Median ending assets", money(mc_summary.median_ending_assets))
    mc_cols[2].metric("10th percentile assets", money(mc_summary.p10_ending_assets))
    mc_cols[3].metric("90th percentile assets", money(mc_summary.p90_ending_assets))
    active_stressors = ", ".join(filter(None, [
        stress_scenario if stress_scenario != "Random returns" else "",
        "inflation shock" if inflation_shock else "",
        "spending guardrail" if spending_guardrail else "",
    ])) or "random return paths"
    st.caption(f"Active simulation mode: {active_stressors}.")
    st.plotly_chart(px.histogram(mc_df, x="ending_assets", nbins=40, title="Monte Carlo Ending Assets"), width="stretch")
    st.plotly_chart(px.scatter(
        mc_df,
        x="ending_assets",
        y="total_lifetime_tax_and_healthcare",
        color="success",
        title="Monte Carlo Outcomes: Assets vs Taxes + Healthcare",
    ), width="stretch")
    st.dataframe(mc_df, width="stretch")
    st.download_button("Download Monte Carlo results", mc_df.to_csv(index=False), "monte_carlo_results.csv", "text/csv")

with tabs[11]:
    scenario_df = compare_conversion_strategies(
        household,
        fixed_conversion=fixed_conversion,
        max_conversion=max_conversion,
        preserve_rule_of_55=preserve_rule,
    )
    st.subheader("Strategy Comparison")
    st.dataframe(scenario_df, width="stretch")
    st.plotly_chart(px.bar(scenario_df, x="strategy", y="total_lifetime_tax", title="Lifetime Tax By Strategy"), width="stretch")
    st.subheader("Saved Scenarios")
    scenario_name = st.text_input("Scenario name", value=f"{strategy} from age {household.current_age}")
    if st.button("Save current scenario summary"):
        st.session_state.saved_scenarios.append(saved_scenario_row(
            name=scenario_name,
            household=household,
            strategy=strategy,
            fixed_conversion=fixed_conversion,
            max_conversion=max_conversion,
            preserve_rule_of_55=preserve_rule,
        ))
    if st.session_state.saved_scenarios:
        saved_df = scenario_table(st.session_state.saved_scenarios)
        st.dataframe(saved_df, width="stretch")
        st.download_button("Download saved scenarios", saved_df.to_csv(index=False), "saved_scenarios.csv", "text/csv")
    st.subheader("Full Scenario Packages")
    current_package = scenario_package(
        name=scenario_name,
        household=household,
        strategy=strategy,
        objective=objective,
        fixed_conversion=fixed_conversion,
        max_conversion=max_conversion,
        preserve_rule_of_55=preserve_rule,
        grid_step=grid_step,
        max_search_federal_rate=max_search_federal_rate,
        max_search_irmaa=max_search_irmaa,
        min_search_cash=min_search_cash,
        monte_carlo_runs=monte_carlo_runs,
        monte_carlo_volatility=monte_carlo_volatility,
        monte_carlo_seed=monte_carlo_seed,
        stress_scenario=stress_scenario,
        inflation_shock=inflation_shock,
        spending_guardrail=spending_guardrail,
    )
    package_json = json.dumps(current_package, indent=2)
    package_cols = st.columns(2)
    if package_cols[0].button("Save full scenario package"):
        st.session_state.saved_scenario_packages.append(current_package)
    package_cols[1].download_button(
        "Download current scenario JSON",
        package_json,
        f"{scenario_name.lower().replace(' ', '_')}_scenario.json",
        "application/json",
    )
    uploaded_package = st.file_uploader("Preview uploaded scenario JSON", type=["json"])
    if uploaded_package is not None:
        try:
            loaded_package = json.loads(uploaded_package.getvalue().decode("utf-8"))
            st.success(f"Loaded scenario preview: {loaded_package.get('name', 'Unnamed')}")
            st.json(scenario_package_summary(loaded_package))
            st.info("Preview only: applying uploaded values back into sidebar controls is planned for the next app-state pass.")
        except json.JSONDecodeError:
            st.error("That file is not valid JSON.")
    if st.session_state.saved_scenario_packages:
        package_summary = pd.DataFrame([
            scenario_package_summary(package)
            for package in st.session_state.saved_scenario_packages
        ])
        st.dataframe(package_summary, width="stretch")
        st.download_button(
            "Download all full scenario packages",
            json.dumps(st.session_state.saved_scenario_packages, indent=2),
            "full_scenario_packages.json",
            "application/json",
        )

with tabs[12]:
    st.subheader("Federal")
    st.json(json.loads((PROJECT_ROOT / "tax_data" / "federal" / "2026.json").read_text()))
    st.subheader("Phase 3 Tax-Like Costs")
    st.write("NIIT uses the stable 3.8% federal Net Investment Income Tax rule on the lesser of net investment income or MAGI above the filing-status threshold.")
    st.write("IRMAA uses a 2026 planning table with a two-year MAGI lookback. The first two projection years use current modeled MAGI if prior tax-return MAGI is not provided.")
    st.write("ACA premium credits use a simplified post-2025 baseline with 100%-400% FPL eligibility, bundled 2025 HHS poverty-guideline values as reviewable planning inputs, an applicable-percentage contribution table, and a user-entered benchmark silver premium.")
    st.subheader("States")
    for state in STATES:
        with st.expander(state):
            st.json(json.loads((PROJECT_ROOT / "tax_data" / "states" / state / "2026.json").read_text()))

with tabs[13]:
    warnings = sorted({w for w in df["warning"] if isinstance(w, str) and w})
    st.warning("This application is not tax, legal, investment, or benefits advice. Confirm tax data and employer plan rules with qualified professionals.")
    st.write("Incomplete rules after Phase 3B: ACA Medicaid eligibility, state-specific marketplace rules, local taxes, estate and inheritance taxes, parcel-level property taxes, detailed lot-level capital gains, full partial-year residency, and full mathematical optimizer search.")
    for warning in warnings:
        st.info(warning)
