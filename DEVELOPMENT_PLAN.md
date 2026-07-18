# Development Plan

This plan tracks the next evolution of the Retirement Rollover And Roth Conversion Optimizer. The app is already useful as a working planning prototype, but the next major improvement is to move from fixed annual conversions to dynamic year-by-year conversion optimization.

## Current Status

### Already Implemented

- Annual retirement cash-flow projection.
- Traditional 401(k), traditional IRA, Roth IRA, taxable brokerage, cash, and HSA balances.
- Roth conversions begin only at the modeled retirement age.
- Federal income tax estimates using bundled 2026 planning brackets.
- Long-term capital gain and qualified dividend treatment.
- NIIT estimates.
- Medicare IRMAA estimates with a simplified two-year lookback.
- ACA bridge premium and premium tax credit estimates.
- Illinois, Maryland, Pennsylvania, Delaware, Virginia, and Florida state comparisons.
- Editable local income tax planning rates.
- Property tax estimates using editable effective rates.
- Pension, Social Security, dividends, and capital gains inputs.
- Rule of 55 preservation warning.
- RMD projection.
- Deterministic strategy comparison.
- Fixed annual Roth conversion grid search.
- Lifetime tax and taxes-plus-healthcare objectives.
- Estate exposure estimates.
- Relocation comparison against Maryland baseline.
- Relocation heat map by state and move age.
- Monte Carlo return simulations.
- Early/late bear market stress tests, inflation shock, and spending guardrail.
- CSV, Excel, Monte Carlo, and scenario JSON exports.
- First-pass dynamic year-by-year Roth conversion optimizer.
- Dynamic conversion heat map showing objective value by age and candidate conversion amount.

### Partially Implemented

- Tax data import/update flow exists, but the app does not automatically import fresh IRS brackets every year without review.
- State tax rules are data-driven, but retirement-income exclusions are simplified.
- Rule of 55 is modeled as a warning and preservation constraint, not a full employer-plan withdrawal simulator.
- Estate exposure is estimated, but after-tax estate optimization is not yet the primary optimizer target.
- Roth conversion heat maps exist, but they are based on the first-pass greedy optimizer and should become richer as the optimizer matures.
- Dynamic conversion optimization exists, but it is currently greedy by year rather than a full global dynamic-programming or mixed-integer solution.

## Main Change To Make

The current optimizer can produce repeated annual conversion amounts, such as converting the same amount every year. That is easy to understand, but it is rarely the true optimum.

The next version should produce a dynamic Roth conversion schedule that changes year by year based on:

- current federal tax brackets
- IRMAA thresholds
- ACA subsidy cliffs
- Illinois and selected retirement-state tax rules
- future RMD projections
- remaining traditional balance
- future pension start date and amount
- future Social Security start date and amount
- dividends and capital gains
- portfolio returns and sequence risk
- after-tax estate value

## Phase 1: Dynamic Conversion Optimizer

Goal: replace "same conversion every year" as the main recommendation with a year-by-year conversion schedule.

Status: first-pass implementation started. The app now tests candidate conversion amounts for each eligible age, chooses the best value for the selected objective, and builds a dynamic schedule plus heat map. The next step is to make the candidate generation smarter around tax brackets, IRMAA thresholds, ACA cliffs, and RMD pressure.

Tasks:

- Add optimizer settings for conversion start age and end age, defaulting to 52 through 75.
- Allow conversion amounts to vary by year.
- Add candidate conversion bands tied to bracket ceilings, IRMAA thresholds, ACA cliffs, and max annual conversion.
- Score each candidate schedule using lifetime taxes, healthcare costs, ending assets, RMDs, and estate value.
- Keep fixed-conversion grid search as a simple comparison mode.
- Add tests that prove the optimizer can choose different conversion amounts in different years.

Expected output:

- A recommended conversion amount for every year from age 52 to 75.
- A table showing why each year was chosen.
- A comparison against no conversions and fixed annual conversions.

## Phase 2: Tax-Bracket And Threshold Data Refresh

Goal: make annual tax data updates easier and more trustworthy.

Tasks:

- Improve tax-data scripts so current IRS brackets can be imported into reviewable draft files.
- Add validation fixtures for federal brackets, standard deductions, long-term capital gain brackets, NIIT thresholds, IRMAA thresholds, and ACA/FPL assumptions.
- Keep all imported data reviewable before it replaces bundled app data.
- Add an in-app tax-data freshness indicator.

Expected output:

- A clear "tax data year" indicator in the app.
- A repeatable process for updating IRS and planning thresholds each year.

## Phase 3: State Tax Depth

Goal: improve selected state modeling while preserving side-by-side comparisons.

Tasks:

- Expand Illinois tax treatment documentation and tests.
- Add deeper retirement-income exclusion logic for Maryland, Pennsylvania, Delaware, Virginia, Florida, and other selected states.
- Let the user compare retirement states side by side without changing the core household scenario.
- Add state-specific warnings where the model is simplified.

Expected output:

- More reliable state comparison tables.
- Better treatment of pension, Social Security, IRA distributions, and Roth conversions by state.

## Phase 4: Rule Of 55 And Withdrawal Strategy

Goal: make pre-59.5 and post-retirement withdrawals more realistic.

Tasks:

- Model employer 401(k) assets preserved for Rule of 55 access.
- Add explicit withdrawal-source ordering options.
- Separate living-spending withdrawals from tax-payment withdrawals in the UI.
- Add warnings when the plan uses assets that may not be accessible without penalties.
- Add tests for retirement ages 52 through 59.

Expected output:

- Clearer early-retirement bridge modeling.
- Better explanation of when taxable, cash, 401(k), traditional IRA, and Roth assets are used.

## Phase 5: After-Tax Estate Optimization

Goal: optimize not just for taxes paid during life, but for after-tax wealth transferred.

Tasks:

- Add an "Maximize after-tax estate value" objective.
- Estimate after-tax value of traditional, Roth, taxable, cash, HSA, and property balances.
- Add beneficiary-level assumptions where useful.
- Compare lifetime taxes saved against estate taxes and embedded income-tax liability.

Expected output:

- A legacy-focused recommendation that may differ from the lowest-lifetime-tax recommendation.

## Phase 6: Roth Conversion Heat Maps

Goal: make the optimizer easier to inspect visually.

Tasks:

- Add a heat map of conversion amount by age/year.
- Add a heat map of lifetime tax impact by conversion window.
- Add a heat map of IRMAA/ACA cliff exposure by year.
- Add hover details for AGI, MAGI, marginal bracket, IRMAA tier, ACA premium credit, RMD, and ending traditional balance.

Expected output:

- A visual map of when conversions help, hurt, or become constrained by tax cliffs.

## Phase 7: Monte Carlo Enhancements

Goal: test whether dynamic conversion schedules stay robust under different market paths.

Tasks:

- Run Monte Carlo against the dynamic optimizer result.
- Compare fixed conversions, dynamic conversions, and no conversions across market paths.
- Add asset-class assumptions and correlations.
- Show success rate, tax distribution, ending assets, and after-tax estate distribution.

Expected output:

- A risk-aware comparison of conversion strategies, not just deterministic projections.

## Working Priority

Recommended next build order:

1. Dynamic year-by-year conversion optimizer from age 52 through 75.
2. Conversion heat map by year.
3. After-tax estate objective.
4. Deeper state tax rules.
5. IRS/tax-data refresh automation.
6. Rule of 55 withdrawal strategy detail.
7. Monte Carlo comparison of dynamic vs fixed conversion schedules.

## Definition Of Done For The Next Major Version

- The app recommends different Roth conversion amounts by year when the tax situation calls for it.
- The recommendation accounts for federal brackets, IRMAA, ACA, state tax, RMDs, pension, Social Security, dividends, capital gains, and remaining traditional balance.
- The app can optimize for lifetime taxes and after-tax estate value.
- The app shows heat maps that explain the conversion tradeoffs.
- Tests cover the new dynamic optimizer and the main cliff constraints.
