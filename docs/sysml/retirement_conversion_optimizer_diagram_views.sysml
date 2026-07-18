package RetirementConversionOptimizerDiagramViews {
    item def HouseholdInputs;
    item def AccountBalances;
    item def IncomeSources;
    item def RetirementTimeline;
    item def TaxAssumptions;
    item def StateAssumptions;
    item def HealthcareAssumptions;
    item def ConversionPolicy;
    item def AnnualCashFlow;
    item def FederalTaxResult;
    item def StateTaxResult;
    item def HealthcareCliffResult;
    item def RmdForecast;
    item def EstateValue;
    item def RelocationResult;
    item def MonteCarloResult;
    item def SavedScenario;
    item def ExportArtifact;

    part def PlannerUser;
    part def StreamlitApplication;
    part def SidebarInputPanel;
    part def ExecutiveSummary;
    part def RecommendedConversionPlan;
    part def AnnualCashFlowTable;
    part def FederalTaxView;
    part def StateTaxView;
    part def RelocationComparisonView;
    part def MedicareAcaView;
    part def MonteCarloView;
    part def ScenarioComparisonView;
    part def TaxDataAndSourcesView;

    part def ProjectionEngine;
    part def DynamicConversionOptimizer;
    part def TaxEngine;
    part def FederalTaxModel;
    part def IllinoisTaxModel;
    part def RetirementStateTaxModel;
    part def HealthcareCliffModel;
    part def RmdModel;
    part def EstateModel;
    part def RelocationModel;
    part def MonteCarloSimulator;
    part def ScenarioStore;
    part def ExportService;
    part def GithubRepository;
    part def StreamlitCloudDeployment;
    part def IrsTaxDataSource;
    part def StateTaxDataSource;

    action def UpdateInputs {
        out householdInputs: HouseholdInputs;
        out accountBalances: AccountBalances;
        out incomeSources: IncomeSources;
        out retirementTimeline: RetirementTimeline;
        out taxAssumptions: TaxAssumptions;
        out stateAssumptions: StateAssumptions;
        out healthcareAssumptions: HealthcareAssumptions;
        out conversionPolicy: ConversionPolicy;
    }

    action def ProjectAnnualCashFlow {
        in householdInputs: HouseholdInputs;
        in accountBalances: AccountBalances;
        in incomeSources: IncomeSources;
        in retirementTimeline: RetirementTimeline;
        in conversionPolicy: ConversionPolicy;
        out annualCashFlow: AnnualCashFlow;
        out rmdForecast: RmdForecast;
    }

    action def CalculateFederalTaxes {
        in annualCashFlow: AnnualCashFlow;
        in taxAssumptions: TaxAssumptions;
        out federalTaxResult: FederalTaxResult;
    }

    action def CalculateStateTaxes {
        in annualCashFlow: AnnualCashFlow;
        in stateAssumptions: StateAssumptions;
        out stateTaxResult: StateTaxResult;
    }

    action def CalculateHealthcareCliffs {
        in annualCashFlow: AnnualCashFlow;
        in healthcareAssumptions: HealthcareAssumptions;
        out healthcareCliffResult: HealthcareCliffResult;
    }

    action def OptimizeRothConversions {
        in annualCashFlow: AnnualCashFlow;
        in federalTaxResult: FederalTaxResult;
        in stateTaxResult: StateTaxResult;
        in healthcareCliffResult: HealthcareCliffResult;
        in rmdForecast: RmdForecast;
        out conversionPolicy: ConversionPolicy;
        out estateValue: EstateValue;
    }

    action def CompareRetirementStates {
        in annualCashFlow: AnnualCashFlow;
        in federalTaxResult: FederalTaxResult;
        in stateAssumptions: StateAssumptions;
        out relocationResult: RelocationResult;
    }

    action def RunReturnScenarios {
        in accountBalances: AccountBalances;
        in conversionPolicy: ConversionPolicy;
        out monteCarloResult: MonteCarloResult;
    }

    action def SaveAndExportScenario {
        in householdInputs: HouseholdInputs;
        in accountBalances: AccountBalances;
        in conversionPolicy: ConversionPolicy;
        in annualCashFlow: AnnualCashFlow;
        in federalTaxResult: FederalTaxResult;
        in stateTaxResult: StateTaxResult;
        in relocationResult: RelocationResult;
        in monteCarloResult: MonteCarloResult;
        out savedScenario: SavedScenario;
        out exportArtifact: ExportArtifact;
    }

    part systemContextView {
        part planner: PlannerUser[1];
        part application: StreamlitApplication[1];
        part repository: GithubRepository[1];
        part deployment: StreamlitCloudDeployment[1];
        part irsData: IrsTaxDataSource[1];
        part stateTaxData: StateTaxDataSource[1];
    }

    part applicationArchitectureView {
        part application: StreamlitApplication[1] {
            part sidebar: SidebarInputPanel[1];
            part executiveSummary: ExecutiveSummary[1];
            part conversionPlan: RecommendedConversionPlan[1];
            part cashFlow: AnnualCashFlowTable[1];
            part federalTaxes: FederalTaxView[1];
            part stateTaxes: StateTaxView[1];
            part relocation: RelocationComparisonView[1];
            part medicareAca: MedicareAcaView[1];
            part monteCarlo: MonteCarloView[1];
            part scenarios: ScenarioComparisonView[1];
            part taxSources: TaxDataAndSourcesView[1];
        }

        part projectionEngine: ProjectionEngine[1];
        part optimizer: DynamicConversionOptimizer[1];
        part taxEngine: TaxEngine[1];
        part relocationModel: RelocationModel[1];
        part monteCarloSimulator: MonteCarloSimulator[1];
        part scenarioStore: ScenarioStore[1];
        part exportService: ExportService[1];
    }

    part taxEngineView {
        part taxEngine: TaxEngine[1] {
            part federalTaxModel: FederalTaxModel[1];
            part illinoisTaxModel: IllinoisTaxModel[1];
            part retirementStateTaxModel: RetirementStateTaxModel[1];
            part healthcareCliffModel: HealthcareCliffModel[1];
            part rmdModel: RmdModel[1];
            part estateModel: EstateModel[1];
        }
    }

    action optimizationFlowView {
        action updateInputs: UpdateInputs[1];
        action projectAnnualCashFlow: ProjectAnnualCashFlow[1];
        action calculateFederalTaxes: CalculateFederalTaxes[1];
        action calculateStateTaxes: CalculateStateTaxes[1];
        action calculateHealthcareCliffs: CalculateHealthcareCliffs[1];
        action optimizeRothConversions: OptimizeRothConversions[1];

        flow updateInputs.householdInputs to projectAnnualCashFlow.householdInputs;
        flow updateInputs.accountBalances to projectAnnualCashFlow.accountBalances;
        flow updateInputs.incomeSources to projectAnnualCashFlow.incomeSources;
        flow updateInputs.retirementTimeline to projectAnnualCashFlow.retirementTimeline;
        flow updateInputs.conversionPolicy to projectAnnualCashFlow.conversionPolicy;

        flow projectAnnualCashFlow.annualCashFlow to calculateFederalTaxes.annualCashFlow;
        flow updateInputs.taxAssumptions to calculateFederalTaxes.taxAssumptions;

        flow projectAnnualCashFlow.annualCashFlow to calculateStateTaxes.annualCashFlow;
        flow updateInputs.stateAssumptions to calculateStateTaxes.stateAssumptions;

        flow projectAnnualCashFlow.annualCashFlow to calculateHealthcareCliffs.annualCashFlow;
        flow updateInputs.healthcareAssumptions to calculateHealthcareCliffs.healthcareAssumptions;

        flow projectAnnualCashFlow.annualCashFlow to optimizeRothConversions.annualCashFlow;
        flow calculateFederalTaxes.federalTaxResult to optimizeRothConversions.federalTaxResult;
        flow calculateStateTaxes.stateTaxResult to optimizeRothConversions.stateTaxResult;
        flow calculateHealthcareCliffs.healthcareCliffResult to optimizeRothConversions.healthcareCliffResult;
        flow projectAnnualCashFlow.rmdForecast to optimizeRothConversions.rmdForecast;
    }

    action relocationComparisonFlowView {
        action updateInputs: UpdateInputs[1];
        action projectAnnualCashFlow: ProjectAnnualCashFlow[1];
        action calculateFederalTaxes: CalculateFederalTaxes[1];
        action compareRetirementStates: CompareRetirementStates[1];

        flow updateInputs.householdInputs to projectAnnualCashFlow.householdInputs;
        flow updateInputs.accountBalances to projectAnnualCashFlow.accountBalances;
        flow updateInputs.incomeSources to projectAnnualCashFlow.incomeSources;
        flow updateInputs.retirementTimeline to projectAnnualCashFlow.retirementTimeline;
        flow updateInputs.conversionPolicy to projectAnnualCashFlow.conversionPolicy;
        flow projectAnnualCashFlow.annualCashFlow to calculateFederalTaxes.annualCashFlow;
        flow updateInputs.taxAssumptions to calculateFederalTaxes.taxAssumptions;
        flow projectAnnualCashFlow.annualCashFlow to compareRetirementStates.annualCashFlow;
        flow calculateFederalTaxes.federalTaxResult to compareRetirementStates.federalTaxResult;
        flow updateInputs.stateAssumptions to compareRetirementStates.stateAssumptions;
    }

    action monteCarloFlowView {
        action updateInputs: UpdateInputs[1];
        action optimizeRothConversions: OptimizeRothConversions[1];
        action runReturnScenarios: RunReturnScenarios[1];
        action saveAndExportScenario: SaveAndExportScenario[1];

        flow updateInputs.accountBalances to runReturnScenarios.accountBalances;
        flow optimizeRothConversions.conversionPolicy to runReturnScenarios.conversionPolicy;
        flow updateInputs.householdInputs to saveAndExportScenario.householdInputs;
        flow updateInputs.accountBalances to saveAndExportScenario.accountBalances;
        flow optimizeRothConversions.conversionPolicy to saveAndExportScenario.conversionPolicy;
        flow runReturnScenarios.monteCarloResult to saveAndExportScenario.monteCarloResult;
    }
}
