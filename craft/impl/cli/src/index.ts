export {
  AUTHORITY_EFFECT,
  CLI_IDENTITY,
  CLI_PACKAGE_NAME,
  CLI_VERSION,
  FOUNDATION_CONTRACT_SCHEMA,
  SUPPORTED_ARCH,
  SUPPORTED_NODE_VERSION,
  SUPPORTED_PLATFORM
} from "./version.js";

export { runCli, type CliIo } from "./cli/main.js";
export {
  addOperation,
  addRule,
  SourceAuthoringError,
  type AddOperationInput,
  type AddOperationResult,
  type AddRuleInput,
  type AddRuleResult,
} from "./authoring/add-operation.js";
export {
  observeTarget,
  observeTargetReceipt,
  ConformanceError,
  type TargetObservationV1,
  type TargetObservationFailureV1,
  type TargetObservationReceiptV1,
} from "./conformance/observe-target.js";
export {
  readInstantiationReceipt,
  validateInstantiationReceipt,
  ReceiptError,
  type InstantiationReceiptV1,
} from "./conformance/receipt.js";
export { planInstantiation } from "./generation/plan-instantiation.js";
export { publishInstantiation, PublicationError, type PublicationResult } from "./generation/publish-instantiation.js";
export {
  planProjectBuild,
  publishProjectBuild,
  verifyProjectBuild,
  ProjectBuildError,
  type ProjectBuildPlanV1,
  type ProjectBuildReceiptV1,
  type ProjectBuildVerificationV1,
} from "./generation/project-build.js";
export {
  compileProject,
  createCompiledProjectCertificate,
  materializeCompiledProjectCertificate,
  validateCompiledProjectCertificate,
  CompilationCertificateError,
  type CompiledProjectCertificateV1,
} from "./compilation/certificate.js";
export {
  checkLeanMetaTypeFormalization,
  createMetaTypeFormalizationProjection,
  formalizationProjectionSha256,
  materializeLeanMetaTypeFormalization,
  renderLeanMetaTypeFormalization,
  FormalizationProjectionError,
  type FormalizationMaterializationResult,
  type FormalizationRenderPayload,
  type MetaTypeFormalizationProjection,
  type ObligationFamily,
} from "./formalization/projection.js";
export {
  type CompilerRefinementOutput,
  type FormalizationSourceIdentity,
  type GraphBoundCertificate,
  type TypeScriptProjectionPayload,
} from "./formalization/refinement.js";
export { FORMALIZATION_LEAN_MODULE_FILENAMES, formalizationLeanModuleSources } from "./formalization/kernel.js";
export {
  createCheckedInterchange,
  validateCheckedInterchange,
  CheckedInterchangeError,
  type CheckedInterchangeV1,
} from "./assurance/checked-interchange.js";
export {
  certifyProject,
  checkCertifiedProject,
  CertificationError,
  CERTIFY_LEAN_TOOLCHAIN,
  CERTIFY_LEAN_VERSION,
  type AssuranceCertificateV1,
  type CertificationCheckV1,
} from "./assurance/certify.js";
export {
  loadCompiledProjectGraph,
  loadProjectNode,
  validateCompiledProjectGraphObligations,
  ProjectModelError,
  type CompiledProjectGraph,
  type CompiledObligationApplicability,
  type CompiledRelationshipObligationWitness,
  type DecodedProjectNode,
} from "./input/project-model.js";
export { FROZEN_META_TYPE_CATALOG, selectRealization } from "./meta-types/catalog.js";
export {
  FROZEN_RELATIONSHIP_AUTHORITY,
  RELATIONSHIP_AUTHORITY_SHA256,
  RELATIONSHIP_SIGNATURES,
  RelationshipAuthorityError,
  deprecatedRelationship,
  generatedRelationshipView,
  relationshipSignature,
} from "./relationships/authority.js";
export {
  SystemIntegrationError,
  compileSystemIntegrationManifest,
  generatedSystemIntegrationPath,
  loadSystemIntegrationSelection,
  renderSystemIntegrationContract,
  validateSystemIntegrationBindingSet,
  validateSystemIntegrationManifest,
} from "./system-integration/compiler.js";
export { FROZEN_SYSTEM_INTEGRATION, validateFrozenSystemIntegrationProfile } from "./system-integration/profile.js";
export { runInMemoryProject } from "./runtime/in-memory.js";
export { runDurableOperation, type DurableCommitRequestV1, type DurableOperationInvocationV1, type DurableOperationReceiptV1, type TransactionalOutboxPortV1 } from "./runtime/durable.js";
export { FetchPostgresOutboxHttpClient, HttpPostgresOutboxTransport, PostgresOutboxWorker, PostgresTransactionalOutbox, type PostgresOutboxConfig, type PostgresOutboxHttpClient, type PostgresOutboxRecord, type PostgresOutboxStatus, type PostgresOutboxTransport } from "./runtime/postgres-outbox.js";
export { materializeRuntimeReceipt, validateRuntimeReceiptBinding } from "./runtime/receipt.js";
export { compareIndependentRuntimeTarget, type IndependentRuntimeTarget, type RuntimeConformanceResultV1 } from "./runtime/conformance.js";
export {
  decodeRuntimeInvocation,
  runtimeRequestSha256,
  RuntimeContractError,
  type RuntimeInvocationV1,
  type RuntimeStepV1,
  type RuntimeStepOutcomeV1,
  type RuntimeCoverageV1,
  type RuntimeReceiptV1,
} from "./runtime/contracts.js";
export type {
  SystemIntegrationBindingManifestV1,
  SystemIntegrationProfileV1,
  SystemIntegrationReceiptBindingV1,
  SystemIntegrationSelectionV1,
} from "./system-integration/types.js";
