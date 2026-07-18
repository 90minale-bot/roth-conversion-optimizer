package RetirementConversionOptimizer {
    item def HouseholdInputs;
    item def AccountBalances;
    item def TaxAssumptions;
    item def RelocationAssumptions;
    item def ConversionWindow;
    item def ConversionStrategy;
    item def AnnualProjection;
    item def DynamicConversionSchedule;
    item def FixedConversionGrid;
    item def RelocationComparison;
    item def MonteCarloResults;
    item def ScenarioPackage;
    item def ExportFiles;

    part def StreamlitUserInterface;
    part def SidebarInputPanel;
    part def ExecutiveSummaryTab;
    part def ConversionPlanTab;
    part def AnnualCashFlowTab;
    part def FederalTaxesTab;
    part def StateTaxesTab;
    part def RelocationComparisonTab;
    part def AccountBalancesTab;
    part def RmdForecastTab;
    part def AcaAndMedicareTab;
    part def EstateAndLegacyTab;
    part def MonteCarloTab;
    part def ScenarioComparisonTab;
    part def TaxDataAndSourcesTab;
    part def AssumptionsAndWarningsTab;

    part def ProjectionEngine;
    part def DynamicConversionOptimizer;
    part def FixedConversionSearch;
    part def TaxEngine;
    part def FederalTaxModel;
    part def StateTaxModel;
    part def HealthcareTaxModel;
    part def EstateExposureModel;
    part def RelocationModel;
    part def MonteCarloSimulator;
    part def ScenarioStore;
    part def ExportService;
    part def TaxDataStore;

    action def UpdateDefaultInput {
        out householdInputs: HouseholdInputs;
        out accountBalances: AccountBalances;
        out taxAssumptions: TaxAssumptions;
        out relocationAssumptions: RelocationAssumptions;
        out conversionWindow: ConversionWindow;
        out conversionStrategy: ConversionStrategy;
    }

    action def ProjectAnnualPlan {
        in householdInputs: HouseholdInputs;
        in accountBalances: AccountBalances;
        in taxAssumptions: TaxAssumptions;
        in relocationAssumptions: RelocationAssumptions;
        in conversionWindow: ConversionWindow;
        in conversionStrategy: ConversionStrategy;
        out annualProjection: AnnualProjection;
    }

    action def OptimizeDynamicConversions {
        in annualProjection: AnnualProjection;
        in conversionWindow: ConversionWindow;
        out dynamicConversionSchedule: DynamicConversionSchedule;
    }

    action def SearchFixedConversions {
        in householdInputs: HouseholdInputs;
        in accountBalances: AccountBalances;
        in taxAssumptions: TaxAssumptions;
        in conversionWindow: ConversionWindow;
        out fixedConversionGrid: FixedConversionGrid;
    }

    action def CompareRelocationStates {
        in householdInputs: HouseholdInputs;
        in accountBalances: AccountBalances;
        in taxAssumptions: TaxAssumptions;
        in relocationAssumptions: RelocationAssumptions;
        out relocationComparison: RelocationComparison;
    }

    action def RunMonteCarloSimulation {
        in householdInputs: HouseholdInputs;
        in accountBalances: AccountBalances;
        in taxAssumptions: TaxAssumptions;
        in conversionStrategy: ConversionStrategy;
        in conversionWindow: ConversionWindow;
        out monteCarloResults: MonteCarloResults;
    }

    action def SaveScenario {
        in householdInputs: HouseholdInputs;
        in accountBalances: AccountBalances;
        in taxAssumptions: TaxAssumptions;
        in relocationAssumptions: RelocationAssumptions;
        in conversionStrategy: ConversionStrategy;
        in conversionWindow: ConversionWindow;
        out scenarioPackage: ScenarioPackage;
    }

    action def ExportResults {
        in annualProjection: AnnualProjection;
        in monteCarloResults: MonteCarloResults;
        in scenarioPackage: ScenarioPackage;
        out exportFiles: ExportFiles;
    }

    action useRetirementOptimizer {
        action updateDefaultInput: UpdateDefaultInput[1];
        action projectAnnualPlan: ProjectAnnualPlan[1];
        action optimizeDynamicConversions: OptimizeDynamicConversions[1];
        action searchFixedConversions: SearchFixedConversions[1];
        action compareRelocationStates: CompareRelocationStates[1];
        action runMonteCarloSimulation: RunMonteCarloSimulation[1];
        action saveScenario: SaveScenario[1];
        action exportResults: ExportResults[1];

        flow updateDefaultInput.householdInputs to projectAnnualPlan.householdInputs;
        flow updateDefaultInput.accountBalances to projectAnnualPlan.accountBalances;
        flow updateDefaultInput.taxAssumptions to projectAnnualPlan.taxAssumptions;
        flow updateDefaultInput.relocationAssumptions to projectAnnualPlan.relocationAssumptions;
        flow updateDefaultInput.conversionWindow to projectAnnualPlan.conversionWindow;
        flow updateDefaultInput.conversionStrategy to projectAnnualPlan.conversionStrategy;

        flow projectAnnualPlan.annualProjection to optimizeDynamicConversions.annualProjection;
        flow updateDefaultInput.conversionWindow to optimizeDynamicConversions.conversionWindow;

        flow updateDefaultInput.householdInputs to searchFixedConversions.householdInputs;
        flow updateDefaultInput.accountBalances to searchFixedConversions.accountBalances;
        flow updateDefaultInput.taxAssumptions to searchFixedConversions.taxAssumptions;
        flow updateDefaultInput.conversionWindow to searchFixedConversions.conversionWindow;

        flow updateDefaultInput.householdInputs to compareRelocationStates.householdInputs;
        flow updateDefaultInput.accountBalances to compareRelocationStates.accountBalances;
        flow updateDefaultInput.taxAssumptions to compareRelocationStates.taxAssumptions;
        flow updateDefaultInput.relocationAssumptions to compareRelocationStates.relocationAssumptions;

        flow updateDefaultInput.householdInputs to runMonteCarloSimulation.householdInputs;
        flow updateDefaultInput.accountBalances to runMonteCarloSimulation.accountBalances;
        flow updateDefaultInput.taxAssumptions to runMonteCarloSimulation.taxAssumptions;
        flow updateDefaultInput.conversionStrategy to runMonteCarloSimulation.conversionStrategy;
        flow updateDefaultInput.conversionWindow to runMonteCarloSimulation.conversionWindow;

        flow updateDefaultInput.householdInputs to saveScenario.householdInputs;
        flow updateDefaultInput.accountBalances to saveScenario.accountBalances;
        flow updateDefaultInput.taxAssumptions to saveScenario.taxAssumptions;
        flow updateDefaultInput.relocationAssumptions to saveScenario.relocationAssumptions;
        flow updateDefaultInput.conversionStrategy to saveScenario.conversionStrategy;
        flow updateDefaultInput.conversionWindow to saveScenario.conversionWindow;

        flow projectAnnualPlan.annualProjection to exportResults.annualProjection;
        flow runMonteCarloSimulation.monteCarloResults to exportResults.monteCarloResults;
        flow saveScenario.scenarioPackage to exportResults.scenarioPackage;
    }

    part retirementConversionOptimizer {
        part userInterface: StreamlitUserInterface[1] {
            part sidebar: SidebarInputPanel[1];
            part executiveSummary: ExecutiveSummaryTab[1];
            part conversionPlan: ConversionPlanTab[1];
            part annualCashFlow: AnnualCashFlowTab[1];
            part federalTaxes: FederalTaxesTab[1];
            part stateTaxes: StateTaxesTab[1];
            part relocationComparison: RelocationComparisonTab[1];
            part accountBalances: AccountBalancesTab[1];
            part rmdForecast: RmdForecastTab[1];
            part acaAndMedicare: AcaAndMedicareTab[1];
            part estateAndLegacy: EstateAndLegacyTab[1];
            part monteCarlo: MonteCarloTab[1];
            part scenarioComparison: ScenarioComparisonTab[1];
            part taxDataAndSources: TaxDataAndSourcesTab[1];
            part assumptionsAndWarnings: AssumptionsAndWarningsTab[1];
        }

        part projectionEngine: ProjectionEngine[1];
        part dynamicOptimizer: DynamicConversionOptimizer[1];
        part fixedConversionSearch: FixedConversionSearch[1];
        part taxEngine: TaxEngine[1] {
            part federalTaxModel: FederalTaxModel[1];
            part stateTaxModel: StateTaxModel[1];
            part healthcareTaxModel: HealthcareTaxModel[1];
            part estateExposureModel: EstateExposureModel[1];
        }
        part relocationModel: RelocationModel[1];
        part monteCarloSimulator: MonteCarloSimulator[1];
        part scenarioStore: ScenarioStore[1];
        part exportService: ExportService[1];
        part taxDataStore: TaxDataStore[1];
    }
}
