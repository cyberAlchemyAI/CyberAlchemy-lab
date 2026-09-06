export {
  derivePureFixtures,
  EXHAUSTIVE_FINITE_RULESET,
  type PartitionDiagnostic,
  type PartitionDiagnosticCode,
  type PartitionDomain,
  type PartitionRuleSet,
  type PureFixtureDerivationInput,
  type PureFixtureDerivationResult,
} from "./partitions/index.js";

export {
  deriveMutationAdequacy,
  SFOL_MUTATION_CATALOG_VERSION,
  type MutationAdequacyInput,
  type MutationAdequacyReceipt,
  type MutationAdequacyResult,
  type SfolMutantResult,
} from "./mutations/index.js";

export {
  evaluateNegativeControls,
  NEGATIVE_CONTROL_PROFILE_VERSION,
  type DetectionMatrixReceipt,
  type DetectionMatrixRow,
  type FaultModel,
  type NegativeControl,
  type NegativeControlDiagnostic,
  type NegativeControlEvaluationInput,
  type NegativeControlEvaluationResult,
  type NegativeControlObservation,
  type NegativeControlSeam,
} from "./negative-controls/index.js";

export {
  challengeTestClosure,
  closeTestClosure,
  decodeAndTypecheckModule,
  derivePartitions,
  replayPure,
  SFOL_TDE_API_VERSION,
  SFOL_TDE_OPTIONAL_EVF_API_VERSION,
  verifyContentAddressedReceipt,
  type DerivePartitionsRequest,
  type DerivePartitionsResponse,
  type CloseTestClosureRequest,
  type CloseTestClosureV1Request,
  type CloseTestClosureV2Request,
  type CloseTestClosureResult,
  type ReceiptVerificationResult,
  type ReplayPureRequest,
} from "./api/index.js";

export {
  resolveSfolTargetProfile,
  SFOL_TARGET_PROFILES,
  SFOL_TARGET_PROFILE_REGISTRY_VERSION,
  type SfolTargetProfile,
} from "./target-profiles/index.js";
