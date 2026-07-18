# Retirement Rollover And Roth Conversion Optimizer

A Streamlit planning app for comparing retirement cash-flow, Roth conversion, tax, healthcare, estate, and relocation scenarios.

This project is built as an educational planning model. It is not tax, legal, investment, benefits, or relocation advice. The tax logic is intentionally transparent and reviewable, but simplified enough that real decisions should be checked against current rules and qualified professionals.

## What It Does

- Projects annual retirement cash flow from the current age through the selected end age.
- Models traditional 401(k), traditional IRA, Roth IRA, taxable brokerage, cash, and HSA balances.
- Compares Roth conversion strategies, including no conversions, fixed annual conversions, bracket-fill conversions, and an aggressive pre-pension strategy.
- Starts Roth conversions only at the modeled retirement age and inside the selected conversion window, defaulting to ages 52 through 75.
- Estimates federal income tax, long-term capital gain tax, qualified dividend treatment, NIIT, Medicare IRMAA, state income tax, local tax, property tax, ACA bridge premiums, and estate exposure.
- Compares relocation scenarios against a Maryland baseline and estimates additional dollars per year available in each modeled state.
- Runs fixed-conversion grid searches with constraints for marginal tax rate, IRMAA, and ending cash.
- Builds a first-pass dynamic Roth conversion schedule with candidate heat maps by age.
- Runs Monte Carlo simulations with random returns, bear-market stress scenarios, inflation shock, and dynamic spending guardrails.
- Saves scenario summaries and exports full scenario packages for review.

## Current Defaults

The sidebar defaults are tuned for the current working case:

- Current age: 50
- Retirement age: 55
- Traditional 401(k): $2,000,000
- Traditional IRA: $100,000
- Roth IRA: $350,000
- Taxable brokerage: $500,000
- Cash: $80,000
- HSA: $25,000
- Annual spending: $120,000
- Modeled states: IL, PA, MD, DE, VA, FL

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Local URL:

```text
http://localhost:8502/
```

## Live App

```text
https://roth-conversion-optimizer-xudhnzknmbzx8mezdf5wta.streamlit.app/
```

## Test

```bash
pytest
```

## App Tabs

- Executive Summary: headline recommendation, lifetime tax/healthcare/estate metrics, and the annual projection table.
- Recommended Conversion Plan: annual Roth conversions, dynamic conversion optimization, heat maps, and fixed-conversion grid search.
- Annual Cash Flow: full annual projection and CSV/Excel export.
- Federal Taxes: federal tax, capital gains, qualified dividends, and NIIT views.
- State Taxes: state income tax, local tax, and estimated property tax by year.
- Relocation Comparison: state-by-state comparison against Maryland, including additional dollars per year available.
- Account Balances: projected cash, taxable, traditional, and Roth balances.
- RMD Forecast: required minimum distribution projection.
- ACA and Medicare: ACA bridge premiums, premium tax credits, IRMAA, and NIIT.
- Estate and Legacy: estimated estate value and federal/state estate exposure.
- Monte Carlo: randomized retirement outcomes and stress testing.
- Scenario Comparison: strategy comparison, saved scenarios, and full JSON scenario packages.
- Tax Data and Sources: reviewable tax inputs bundled with the app.
- Assumptions and Warnings: model warnings and planning caveats.

## Tax Data

Tax inputs live in `tax_data/` as reviewable JSON files. The app currently includes 2026 planning data for:

- Federal tax
- Delaware
- Florida
- Illinois
- Maryland
- Pennsylvania
- Virginia

To create draft updates:

```bash
python scripts/update_tax_data.py --year 2026
python scripts/validate_tax_data.py
```

The updater is conservative by design. It creates draft files for review rather than silently replacing reviewed tax assumptions.

## Add A State

Add a file at:

```text
tax_data/states/<STATE>/<YEAR>.json
```

Use the same schema as the existing state files. The state tax engine reads state files generically, so many flat-rate and bracketed state rules can be added through data instead of code.

## Known Limitations

- The model is a planning estimate, not a tax engine.
- 2026 tax values are bundled planning assumptions and should be manually reviewed.
- State tax rules are simplified and may not capture every retirement-income exclusion or local rule.
- Local tax uses editable state-level planning rates; actual city, county, school-district, and earned-income taxes should be verified separately.
- ACA estimates use simplified premium tax credit logic, user-entered benchmark premiums, and bundled poverty-guideline assumptions.
- IRMAA uses a simplified two-year MAGI lookback; the first two projection years use modeled MAGI when prior tax-return MAGI is not provided.
- NIIT uses the 3.8% federal rule with simplified net investment income.
- Estate exposure is a warning-level estimate. It does not model trusts, portability elections, basis step-up, beneficiary-specific inheritance tax, marital or charitable deductions, lifetime taxable gifts, or titling.
- Property tax uses editable state-level effective rates against modeled home value; real bills depend on county, municipality, exemptions, and assessments.
- Monte Carlo uses simplified normal-return assumptions and basic stress overlays rather than full asset-class correlations or stochastic tax law.
- Uploaded scenario JSON is preview-only; applying uploads back into every sidebar widget remains a future state-management enhancement.

## Practical Next Enhancements

The detailed roadmap is tracked in [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md).
The starter SysML v2 design model for Eclipse SysON is in [docs/sysml](docs/sysml).

- Make uploaded scenario JSON fully restore sidebar inputs.
- Add more detailed state retirement-income exclusions.
- Add prior-year MAGI inputs for more precise IRMAA lookback modeling.
- Add beneficiary-level legacy summaries.
- Add official-source validation fixtures for tax data updates.
- Expand the optimizer beyond fixed-conversion grid search.

## Repository

GitHub:

```text
https://github.com/90minale-bot/roth-conversion-optimizer
```
