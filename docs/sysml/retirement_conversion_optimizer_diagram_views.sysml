package RetirementConversionOptimizerDiagramViews {
    item def DesignRequirement {
        attribute id;
        attribute title;
        attribute statement;
        attribute verificationMethod;
        attribute pytestReference;
    }
    item def VerificationCase {
        attribute id;
        attribute verifiesRequirement;
        attribute testFunction;
        attribute expectedResult;
    }
    item def HouseholdInputs {
        attribute currentAge;
        attribute spouseAge;
        attribute filingStatus;
        attribute currentResidenceState;
        attribute plannedMoveAge;
        attribute plannedRetirementAge;
        attribute baselineComparisonState;
    }
    item def AccountBalances {
        attribute traditional401kBalance;
        attribute traditionalIraBalance;
        attribute rothIraBalance;
        attribute taxableBrokerageBalance;
        attribute annualGrowthRate;
        attribute taxableDividendYield;
        attribute taxableCapitalGainRate;
    }
    item def IncomeSources {
        attribute wages;
        attribute pensionAmount;
        attribute pensionStartAge;
        attribute socialSecurityAmount;
        attribute socialSecurityStartAge;
        attribute longTermIncentiveIncome;
        attribute dividends;
        attribute longTermCapitalGains;
    }
    item def RetirementTimeline {
        attribute currentAge;
        attribute retirementAge;
        attribute projectionEndAge;
        attribute conversionStartAge;
        attribute conversionEndAge;
        attribute ruleOf55Eligible;
        attribute rmdStartAge;
    }
    item def TaxAssumptions {
        attribute taxYear;
        attribute standardDeduction;
        attribute federalBracketSet;
        attribute capitalGainsBracketSet;
        attribute irmaaThresholdSet;
        attribute acaSubsidyEnabled;
        attribute bracketInflationRate;
    }
    item def StateAssumptions {
        attribute modeledStates;
        attribute baselineState;
        attribute ordinaryIncomeRule;
        attribute retirementIncomeRule;
        attribute capitalGainRule;
        attribute localTaxRule;
    }
    item def HealthcareAssumptions {
        attribute acaCoverageStartAge;
        attribute medicareStartAge;
        attribute householdSize;
        attribute benchmarkPremium;
        attribute magiThresholds;
        attribute irmaaLookbackYears;
    }
    item def ConversionPolicy {
        attribute strategyName;
        attribute allowedStartAge;
        attribute allowedEndAge;
        attribute annualConversionLimit;
        attribute targetFederalBracket;
        attribute avoidIrmaaTier;
        attribute avoidAcaCliff;
        attribute minimizeLifetimeTax;
        attribute maximizeAfterTaxEstate;
    }
    item def AnnualCashFlow {
        attribute age;
        attribute wages;
        attribute pension;
        attribute socialSecurity;
        attribute dividends;
        attribute longTermCapitalGains;
        attribute rothConversion;
        attribute traditionalWithdrawal;
        attribute rothWithdrawal;
        attribute taxableWithdrawal;
        attribute totalTax;
        attribute availableSpending;
    }
    item def FederalTaxResult {
        attribute ordinaryIncome;
        attribute taxableIncome;
        attribute marginalBracket;
        attribute federalTax;
        attribute longTermCapitalGainTax;
        attribute effectiveRate;
    }
    item def StateTaxResult {
        attribute state;
        attribute taxableOrdinaryIncome;
        attribute taxableRetirementIncome;
        attribute stateIncomeTax;
        attribute additionalDollarsPerYearVsBaseline;
    }
    item def HealthcareCliffResult {
        attribute modifiedAdjustedGrossIncome;
        attribute acaSubsidy;
        attribute acaCliffCost;
        attribute irmaaTier;
        attribute irmaaPremiumCost;
    }
    item def RmdForecast {
        attribute rmdAge;
        attribute projectedTraditionalBalance;
        attribute distributionPeriod;
        attribute requiredDistribution;
        attribute projectedTaxImpact;
    }
    item def EstateValue {
        attribute endingTraditionalBalance;
        attribute endingRothBalance;
        attribute endingTaxableBalance;
        attribute embeddedTaxLiability;
        attribute afterTaxEstateValue;
    }
    item def RelocationResult {
        attribute state;
        attribute lifetimeStateTax;
        attribute annualTaxSavingsVsBaseline;
        attribute annualSpendableCashVsBaseline;
        attribute endingEstateVsBaseline;
    }
    item def MonteCarloResult {
        attribute scenarioCount;
        attribute returnAssumption;
        attribute successRate;
        attribute medianEndingAssets;
        attribute fifthPercentileEndingAssets;
        attribute ninetyFifthPercentileEndingAssets;
    }
    item def SavedScenario {
        attribute scenarioName;
        attribute savedTimestamp;
        attribute householdSnapshot;
        attribute strategySnapshot;
        attribute resultSnapshot;
    }
    item def ExportArtifact {
        attribute csvFile;
        attribute excelFile;
        attribute jsonFile;
        attribute generatedTimestamp;
    }

    part def PlannerUser;
    part def StreamlitApplication {
        port userInputs;
        port modelResults;
        port scenarioCommands;
        port exportDownloads;
    }
    part def SidebarInputPanel {
        port householdInputOut;
        port accountBalanceOut;
        port incomeSourceOut;
        port taxAssumptionOut;
        port stateAssumptionOut;
        port healthcareAssumptionOut;
        port conversionPolicyOut;
    }
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

    part def ProjectionEngine {
        port assumptionsIn;
        port cashFlowOut;
        port rmdForecastOut;
    }
    part def DynamicConversionOptimizer {
        port cashFlowIn;
        port taxResultsIn;
        port healthcareCliffsIn;
        port rmdForecastIn;
        port conversionPolicyOut;
        port estateValueOut;
    }
    part def TaxEngine {
        port annualCashFlowIn;
        port taxAssumptionsIn;
        port stateAssumptionsIn;
        port healthcareAssumptionsIn;
        port federalTaxOut;
        port stateTaxOut;
        port healthcareCliffOut;
    }
    part def FederalTaxModel;
    part def IllinoisTaxModel;
    part def RetirementStateTaxModel;
    part def HealthcareCliffModel;
    part def RmdModel;
    part def EstateModel;
    part def RelocationModel {
        port baselineStateIn;
        port comparisonStatesIn;
        port annualCashFlowIn;
        port relocationResultOut;
    }
    part def MonteCarloSimulator {
        port accountBalancesIn;
        port conversionPolicyIn;
        port marketScenarioIn;
        port monteCarloResultOut;
    }
    part def ScenarioStore {
        port saveScenarioIn;
        port savedScenarioOut;
    }
    part def ExportService {
        port annualProjectionIn;
        port scenarioIn;
        port exportArtifactOut;
    }
    part def GithubRepository;
    part def StreamlitCloudDeployment;
    part def IrsTaxDataSource;
    part def StateTaxDataSource;
    part def TaxDataStore {
        port federalBracketDataOut;
        port irmaaThresholdDataOut;
        port stateTaxRuleDataOut;
    }

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

    action def CalculateRmdForecast {
        in accountBalances: AccountBalances;
        in retirementTimeline: RetirementTimeline;
        out rmdForecast: RmdForecast;
    }

    action def EstimateEstateValue {
        in accountBalances: AccountBalances;
        in conversionPolicy: ConversionPolicy;
        in federalTaxResult: FederalTaxResult;
        in stateTaxResult: StateTaxResult;
        out estateValue: EstateValue;
    }

    action def OptimizeRothConversions {
        in annualCashFlow: AnnualCashFlow;
        in conversionConstraints: ConversionPolicy;
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
    action def VerifyRequirementsFileCoverage {
        in requirements: DesignRequirement;
        out verificationCase: VerificationCase;
    }

    action def VerifyConversionsStartAtRetirement {
        in retirementTimeline: RetirementTimeline;
        in conversionPolicy: ConversionPolicy;
        in annualCashFlow: AnnualCashFlow;
        out verificationCase: VerificationCase;
    }

    action def VerifyConversionsStopAfterEndAge {
        in retirementTimeline: RetirementTimeline;
        in conversionPolicy: ConversionPolicy;
        in annualCashFlow: AnnualCashFlow;
        out verificationCase: VerificationCase;
    }

    action def VerifyAvailableSpendingFormula {
        in annualCashFlow: AnnualCashFlow;
        out verificationCase: VerificationCase;
    }

    action def VerifyMarylandRelocationBaseline {
        in stateAssumptions: StateAssumptions;
        in relocationResult: RelocationResult;
        out verificationCase: VerificationCase;
    }

    action def VerifyModeledStateTaxFiles {
        in stateAssumptions: StateAssumptions;
        out verificationCase: VerificationCase;
    }

    action def VerifyDynamicOptimizerArtifacts {
        in conversionPolicy: ConversionPolicy;
        in annualCashFlow: AnnualCashFlow;
        out verificationCase: VerificationCase;
    }

    action def VerifyAfterTaxEstateObjective {
        in estateValue: EstateValue;
        out verificationCase: VerificationCase;
    }

    action def VerifyRmdForecastReported {
        in rmdForecast: RmdForecast;
        out verificationCase: VerificationCase;
    }
    part requirementsAndVerificationView {
        item reqConv001: DesignRequirement[1];
        item reqConv002: DesignRequirement[1];
        item reqCash001: DesignRequirement[1];
        item reqState001: DesignRequirement[1];
        item reqState002: DesignRequirement[1];
        item reqOpt001: DesignRequirement[1];
        item reqObj001: DesignRequirement[1];
        item reqRmd001: DesignRequirement[1];

        item verifyContractMetadata: VerificationCase[1];
        item verifyReqConv001: VerificationCase[1];
        item verifyReqConv002: VerificationCase[1];
        item verifyReqCash001: VerificationCase[1];
        item verifyReqState001: VerificationCase[1];
        item verifyReqState002: VerificationCase[1];
        item verifyReqOpt001: VerificationCase[1];
        item verifyReqObj001: VerificationCase[1];
        item verifyReqRmd001: VerificationCase[1];
    }

    action verificationContractView {
        action verifyRequirementsFileCoverage: VerifyRequirementsFileCoverage[1];
        action verifyConversionsStartAtRetirement: VerifyConversionsStartAtRetirement[1];
        action verifyConversionsStopAfterEndAge: VerifyConversionsStopAfterEndAge[1];
        action verifyAvailableSpendingFormula: VerifyAvailableSpendingFormula[1];
        action verifyMarylandRelocationBaseline: VerifyMarylandRelocationBaseline[1];
        action verifyModeledStateTaxFiles: VerifyModeledStateTaxFiles[1];
        action verifyDynamicOptimizerArtifacts: VerifyDynamicOptimizerArtifacts[1];
        action verifyAfterTaxEstateObjective: VerifyAfterTaxEstateObjective[1];
        action verifyRmdForecastReported: VerifyRmdForecastReported[1];
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
        flow updateInputs.conversionPolicy to optimizeRothConversions.conversionConstraints;
        flow projectAnnualCashFlow.rmdForecast to optimizeRothConversions.rmdForecast;
    }
    action userWorkflowView {
        action updateInputs: UpdateInputs[1];
        action projectAnnualCashFlow: ProjectAnnualCashFlow[1];
        action calculateFederalTaxes: CalculateFederalTaxes[1];
        action calculateStateTaxes: CalculateStateTaxes[1];
        action calculateHealthcareCliffs: CalculateHealthcareCliffs[1];
        action optimizeRothConversions: OptimizeRothConversions[1];
        action compareRetirementStates: CompareRetirementStates[1];
        action runReturnScenarios: RunReturnScenarios[1];
        action saveAndExportScenario: SaveAndExportScenario[1];

        flow updateInputs.householdInputs to projectAnnualCashFlow.householdInputs;
        flow projectAnnualCashFlow.annualCashFlow to calculateFederalTaxes.annualCashFlow;
        flow projectAnnualCashFlow.annualCashFlow to calculateStateTaxes.annualCashFlow;
        flow projectAnnualCashFlow.annualCashFlow to calculateHealthcareCliffs.annualCashFlow;
        flow calculateFederalTaxes.federalTaxResult to optimizeRothConversions.federalTaxResult;
        flow calculateStateTaxes.stateTaxResult to optimizeRothConversions.stateTaxResult;
        flow calculateHealthcareCliffs.healthcareCliffResult to optimizeRothConversions.healthcareCliffResult;
        flow updateInputs.conversionPolicy to optimizeRothConversions.conversionConstraints;
        flow projectAnnualCashFlow.annualCashFlow to compareRetirementStates.annualCashFlow;
        flow optimizeRothConversions.conversionPolicy to runReturnScenarios.conversionPolicy;
        flow runReturnScenarios.monteCarloResult to saveAndExportScenario.monteCarloResult;
    }

    action inputAssumptionsView {
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
        flow updateInputs.taxAssumptions to calculateFederalTaxes.taxAssumptions;
        flow updateInputs.stateAssumptions to calculateStateTaxes.stateAssumptions;
        flow updateInputs.healthcareAssumptions to calculateHealthcareCliffs.healthcareAssumptions;
        flow updateInputs.conversionPolicy to optimizeRothConversions.conversionConstraints;
    }

    action taxCalculationPipelineView {
        action updateInputs: UpdateInputs[1];
        action projectAnnualCashFlow: ProjectAnnualCashFlow[1];
        action calculateRmdForecast: CalculateRmdForecast[1];
        action calculateFederalTaxes: CalculateFederalTaxes[1];
        action calculateStateTaxes: CalculateStateTaxes[1];
        action calculateHealthcareCliffs: CalculateHealthcareCliffs[1];
        action optimizeRothConversions: OptimizeRothConversions[1];
        action estimateEstateValue: EstimateEstateValue[1];

        flow updateInputs.accountBalances to calculateRmdForecast.accountBalances;
        flow updateInputs.retirementTimeline to calculateRmdForecast.retirementTimeline;
        flow updateInputs.householdInputs to projectAnnualCashFlow.householdInputs;
        flow updateInputs.accountBalances to projectAnnualCashFlow.accountBalances;
        flow updateInputs.incomeSources to projectAnnualCashFlow.incomeSources;
        flow updateInputs.retirementTimeline to projectAnnualCashFlow.retirementTimeline;
        flow projectAnnualCashFlow.annualCashFlow to calculateFederalTaxes.annualCashFlow;
        flow updateInputs.taxAssumptions to calculateFederalTaxes.taxAssumptions;
        flow projectAnnualCashFlow.annualCashFlow to calculateStateTaxes.annualCashFlow;
        flow updateInputs.stateAssumptions to calculateStateTaxes.stateAssumptions;
        flow projectAnnualCashFlow.annualCashFlow to calculateHealthcareCliffs.annualCashFlow;
        flow updateInputs.healthcareAssumptions to calculateHealthcareCliffs.healthcareAssumptions;
        flow updateInputs.conversionPolicy to optimizeRothConversions.conversionConstraints;
        flow calculateFederalTaxes.federalTaxResult to optimizeRothConversions.federalTaxResult;
        flow calculateStateTaxes.stateTaxResult to optimizeRothConversions.stateTaxResult;
        flow calculateHealthcareCliffs.healthcareCliffResult to optimizeRothConversions.healthcareCliffResult;
        flow calculateRmdForecast.rmdForecast to optimizeRothConversions.rmdForecast;
        flow updateInputs.accountBalances to estimateEstateValue.accountBalances;
        flow optimizeRothConversions.conversionPolicy to estimateEstateValue.conversionPolicy;
        flow calculateFederalTaxes.federalTaxResult to estimateEstateValue.federalTaxResult;
        flow calculateStateTaxes.stateTaxResult to estimateEstateValue.stateTaxResult;
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
