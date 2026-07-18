# SysML v2 Design Model

This folder contains a starter SysML v2 textual model for Eclipse SysON:

```text
retirement_conversion_optimizer.sysml
retirement_conversion_optimizer_diagram_views.sysml
requirements.json
```

Use `retirement_conversion_optimizer_diagram_views.sysml` first if you want a cleaner SysON diagramming experience. It breaks the design into smaller view-oriented elements that are easier to drag onto diagrams. Use `requirements.json` as the machine-readable regression contract that maps design requirements to pytest checks.

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
3. Select `retirement_conversion_optimizer_diagram_views.sysml` for the easiest visual walkthrough, or `retirement_conversion_optimizer.sysml` for the full starter model.
4. Upload it as a model.
5. Use SysON diagrams/views to create graphical views from the imported package.

The file is intentionally standalone and does not require third-party SysML libraries to be imported first.

## Suggested Views To Create

- System Context: user, Streamlit app, GitHub repo, Streamlit Cloud deployment, and local tax data.
- Logical Architecture: UI tabs, projection engine, tax engine, optimizer, simulator, scenario store, and export service.
- Activity/Data Flow: update inputs, project annual plan, optimize conversions, compare states, run Monte Carlo, save/export results.
- Data Model: household inputs, account balances, tax assumptions, conversion window, annual projection, scenario package, and exports.

## Diagram-Friendly Elements

After importing `retirement_conversion_optimizer_diagram_views.sysml`, expand the package and drag these elements onto separate SysON views:

- `systemContextView`
- `applicationArchitectureView`
- `taxEngineView`
- `optimizationFlowView`
- `userWorkflowView`
- `inputAssumptionsView`
- `taxCalculationPipelineView`
- `requirementsAndVerificationView`
- `verificationContractView`
- `relocationComparisonFlowView`
- `monteCarloFlowView`

## Current Modeling Detail

The diagram-friendly model now includes:

- Item attributes for household inputs, account balances, income sources, timelines, federal tax assumptions, state assumptions, healthcare assumptions, cash flow, tax results, RMD forecasts, relocation results, Monte Carlo results, scenarios, and export artifacts.
- Action inputs and outputs for the end-to-end optimization pipeline.
- Component ports for the Streamlit app, sidebar, projection engine, tax engine, optimizer, relocation model, Monte Carlo simulator, scenario store, export service, and tax data store.
- Separate view anchors for user workflow, input assumptions, tax calculation pipeline, relocation comparison, Monte Carlo analysis, and requirements verification.
- A requirements.json contract that maps design requirements to tests/test.py regression checks.

## Next Modeling Pass

- Add formal requirement elements once the SysON workspace confirms the supported textual requirement syntax.
- Add constraint equations for bracket filling, IRMAA thresholds, ACA subsidy cliffs, RMD calculations, and after-tax estate value.
- Add more explicit state-specific tax rule tables for Illinois, Maryland, Pennsylvania, Delaware, Virginia, and Florida.
