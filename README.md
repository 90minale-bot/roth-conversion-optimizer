# Retirement Tax Optimizer

Phase 2 working baseline for rollover, Roth conversion, retirement cash-flow, federal/state tax, estimated property tax, capital-gain-aware projections, relocation comparison, and scenario comparison planning.

This is an educational planning tool, not tax, legal, investment, or benefits advice. Tax rules are simplified in this baseline and should be reviewed before use for real decisions.

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

## Test

```bash
pytest
```

## Update Tax Data

```bash
python scripts/update_tax_data.py --year 2026
python scripts/validate_tax_data.py
```

The updater is intentionally conservative. It creates reviewable draft files instead of silently replacing reviewed data.

## Add A State

Add `tax_data/states/<STATE>/<YEAR>.json` with the same schema as the existing state files. The core engine reads state files generically, so calculation code does not need to change for flat-rate or bracket states.

## Phase 3 Roadmap

### Phase 3A: Hidden Retirement Tax Cliffs

- Medicare IRMAA surcharge estimates with a two-year MAGI lookback.
- Net Investment Income Tax estimates for dividends and long-term capital gains.
- Summary and comparison tables that include tax-like cliff costs when ranking strategies.

### Phase 3B: Healthcare Bridge

- ACA subsidy and marketplace premium modeling before Medicare age.
- Household-size and user-entered benchmark premium assumptions.
- Warnings when Roth conversions create ACA subsidy cliffs.
- A healthcare-aware objective that compares taxes plus ACA net premiums.

### Phase 3C: More Realistic Tax Rules

- More detailed Social Security edge cases.
- Editable local income tax rate layer for county/city taxes.
- State-specific retirement-income exclusions.
- Partial-year relocation and residency handling.

### Phase 3D: Estate And Legacy Exposure

- Federal and selected state estate/inheritance tax warning layer.
- Beneficiary-oriented ending-account mix summaries.
- Roth-vs-traditional legacy value comparison.

### Phase 3E: Optimizer Engine

- Grid search across fixed annual conversion amounts and tax-cliff constraints.
- Constraints for max federal bracket, max annual IRMAA, and minimum ending cash.
- Future search across conversion windows, move ages, and minimum taxable liquidity.
- Future dynamic-programming or mixed-integer optimizer once the tax model is stable.

## Phase 4 Roadmap

### Phase 4A: Monte Carlo Outcomes

- Randomized annual account returns around each account's expected return.
- Success-rate, ending-asset percentile, and tax-plus-healthcare distributions.
- Downloadable simulation results for external review.

### Phase 4B: Stress Testing

- Early bear market and late bear market sequence-of-returns scenarios.
- Optional three-year inflation shock.
- Optional dynamic spending guardrail that trims spending after large portfolio drawdowns and modestly restores it after strong gains.

## Phase 5 Roadmap

### Phase 5A: Full Scenario Packages

- Export the full household, account, strategy, optimizer, and Monte Carlo settings to JSON.
- Save multiple full scenario packages in session state.
- Preview uploaded scenario JSON for review before re-entry or future state restoration.

## Known Limitations

- 2026 tax data is stored separately with source metadata, but the bundled values are baseline planning data and flagged for manual review.
- Estate and inheritance tax, Medicaid eligibility, state marketplace details, and lot-level capital-gain harvesting are approximate or warning-only in this baseline.
- Local income tax uses editable state-level planning rates. Actual county, city, school-district, and earned-income tax rules should be verified locally.
- Estate exposure uses planning estimates for federal estate tax and selected state estate taxes. It does not model trusts, portability elections, basis step-up, beneficiary-specific inheritance tax, marital/charitable deductions, lifetime taxable gifts, or titling.
- IRMAA uses a reviewable 2026 planning table and first two projection years use current modeled MAGI unless prior tax-return MAGI is supplied in a future version.
- NIIT uses the 3.8% federal rule on the lesser of net investment income or MAGI above the filing-status threshold, with simplified net investment income.
- ACA premium tax credits use a simplified post-2025 baseline with 100%-400% FPL eligibility, bundled 2025 HHS poverty-guideline values as reviewable planning inputs, interpolated expected contribution percentages, and a user-entered benchmark silver premium.
- Property tax uses editable state-level estimated effective rates against the modeled home value; actual bills depend on county, municipality, exemptions, and assessment rules.
- Social Security taxation is implemented with the federal provisional-income formula but not every edge case.
- Rule of 55 support warns about preserving employer-plan access; employer plan document restrictions must be confirmed manually.
- Optimizer compares deterministic strategies, relocation years, and objectives, but is not yet a full mixed-integer or dynamic-programming solver.
- Monte Carlo uses simplified normal-return assumptions and basic stress overlays. It does not model full asset-class correlations, stochastic tax law, behavioral spending choices, or detailed inflation baskets.
- Full scenario package import is preview-only in Phase 5A; applying uploaded JSON back into every sidebar widget is planned for a later state-management pass.

## Phase 2 Additions

- Federal long-term capital gain and qualified dividend stacking.
- Deterministic objective selector for lifetime tax, ending assets, Roth balance, and peak RMD.
- Reusable strategy and relocation comparison modules.
- Streamlit session-state scenario saving and CSV export.
- Relocation heat map driven by the shared comparison engine.
- Estimated property tax on a default $1M property, including editable appreciation and state rates.

## Recommended Next Phase

Phase 3A adds IRMAA and NIIT. Phase 3B adds simplified ACA bridge premium and subsidy modeling. Phase 3C starts with editable local income tax rates. Phase 3D adds first-pass estate exposure warnings. Phase 3E starts the constrained optimizer engine with fixed-conversion grid search. Phase 4A adds Monte Carlo outcome simulation. Phase 4B adds stress testing and spending guardrails. Phase 5A adds full scenario package export and preview import. The next phase should add more detailed Social Security, state-specific retirement exclusions, beneficiary-level legacy views, and official-source validation fixtures.
