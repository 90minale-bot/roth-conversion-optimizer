# SysML v2 Design Model

This folder contains a starter SysML v2 textual model for Eclipse SysON:

```text
retirement_conversion_optimizer.sysml
```

## What The Model Documents

- The Streamlit user interface and its major tabs.
- The sidebar input path for household, account, tax, relocation, and conversion assumptions.
- The annual projection engine.
- The tax models for federal, state, healthcare-related cliffs, and estate exposure.
- Dynamic Roth conversion optimization.
- Fixed conversion grid search.
- Relocation comparison.
- Monte Carlo simulation.
- Scenario save/export workflows.

## How To Import Into Eclipse SysON

1. Open your SysON project.
2. In the Explorer view, click the upload model icon.
3. Select `retirement_conversion_optimizer.sysml`.
4. Upload it as a model.
5. Use SysON diagrams/views to create graphical views from the imported package.

The file is intentionally standalone and does not require third-party SysML libraries to be imported first.

## Suggested Views To Create

- System Context: user, Streamlit app, GitHub repo, Streamlit Cloud deployment, and local tax data.
- Logical Architecture: UI tabs, projection engine, tax engine, optimizer, simulator, scenario store, and export service.
- Activity/Data Flow: update inputs, project annual plan, optimize conversions, compare states, run Monte Carlo, save/export results.
- Data Model: household inputs, account balances, tax assumptions, conversion window, annual projection, scenario package, and exports.

## Next Modeling Pass

- Add requirement elements once the SysON workspace confirms the supported textual requirement syntax.
- Add more detailed item attributes for balances, taxes, MAGI, RMDs, and spendable cash flow.
- Add views for external systems such as IRS tax data sources, Streamlit Cloud, and GitHub.
