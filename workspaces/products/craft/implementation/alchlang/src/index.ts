import { createHash } from "node:crypto";
import type { CompilationResult } from "./model.js";
import { validateAndNormalize } from "./validate.js";
import { lower } from "./lower.js";
import { renderTypeScript } from "./render-typescript.js";

function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.entries(value as Record<string, unknown>).sort(([a], [b]) => a.localeCompare(b)).map(([key, item]) => `${JSON.stringify(key)}:${canonical(item)}`).join(",")}}`;
  return JSON.stringify(value);
}

const digest = (value: unknown): string => createHash("sha256").update(canonical(value)).digest("hex");

export function compileCarrier(input: unknown): CompilationResult {
  const model = validateAndNormalize(input);
  const plan = lower(model);
  return { plan, files: renderTypeScript(plan), source_digest: digest(input), plan_digest: digest(plan), authority_effect: "none" };
}

export { CompilationRejected } from "./model.js";
export {prepareProfileProject,planProfileProject,generateProfileProject,verifyProfileProject,disposeProfileProject,runProfileProjectCommand,type PreparedProfileProject} from './profile-engine.js';
export { parseDomainSource } from "./parser.js";
export { parseBusinessSource, assertParsedBusinessSourceCurrent } from "./business-authoring-parser.js";
export { resolveBusinessSpec, assertResolvedBusinessSpecCurrent, prepareBusinessSpecFile, disposeResolvedBusinessSpec } from "./business-authoring-resolve.js";
export { BusinessSourceRejected } from "./business-authoring-model.js";
export type { BusinessSpecData, ParsedBusinessSource, ResolvedBusinessSpec } from "./business-authoring-protocol.js";
export { lowerBusinessFormalSemantics, assertBusinessFormalSemanticsCurrent, type BusinessFormalSemantics } from "./business-authoring-semantics.js";
export { lowerBusinessBehavior, assertBusinessBehaviorCurrent, type BusinessBehavior } from "./business-authoring-behavior.js";
export type { BusinessFormalData, BusinessBehaviorData, BusinessRecipeModelInput, BusinessRecipeRequirements } from "./business-authoring-normalization-protocol.js";
export { prepareBusinessRecipeSelection, assertPreparedBusinessRecipeSelectionCurrent } from "./business-authoring-profile-selection.js";
export type { BusinessRecipeEngine, BusinessRecipeSelectionSurface, PreparedBusinessRecipeSelection } from "./business-authoring-profile-selection.js";
export {previewBusinessSemantics, assertBusinessSemanticPreviewCurrent, materializeAcceptedBusinessApplication, assertMaterializedBusinessApplicationCurrent} from './business-authoring-carriers.js';
export type {BusinessPreviewSelection, BusinessMeaningDraft, BusinessDeclarationDraft, BusinessClaimDraft, BusinessOperationBehaviorDraft, BusinessSemanticProjections, DetailedBusinessSemanticPreview} from './business-authoring-carriers.js';
export {insertBusinessRequestMappings, assertInsertedBusinessRequestMappingsCurrent} from './business-authoring-request.js';
export type {BusinessRequestMappingSurface, BusinessRequestPreparationSurface, BusinessRequestPreparationEngine, InsertedBusinessRequestMappings} from './business-authoring-request.js';
export * from './business-authoring-review.js';
export {prepareBusinessAuthoringApplication, assertPreparedBusinessAuthoringApplicationCurrent, disposePreparedBusinessAuthoringApplication} from './business-authoring-prepare.js';
export type {PreparedBusinessAuthoringApplication, BusinessAuthoringApplicationLineage} from './business-authoring-prepare.js';
export type {BusinessMaterializationRequestSurface, BusinessAcceptedClaim, BusinessApplicationSemantics, BusinessMaterializationEngine, MaterializedBusinessApplication} from './business-authoring-carriers.js';
export { parseFormalProposition, type FormalSignature, type FormalTerm, type FormalProposition, type FormalClaimDeclaration, type ApplicationFormalSource } from "./formal-claim.js";
export { parseApplicationType, type ApplicationType, type ApplicationDeclaration } from "./application-source.js";
export { lowerApplicationFormalClaims, resolveExactFormalSource, FORMAL_IDENTITY_ALGORITHM_BYTES, type ExactFormalSourceRef } from "./formal-claim-lowering.js";
export { projectApplicationFormalClaimsToV2, assertApplicationFormalClaimV2ProjectionCurrent } from "./formal-claim-v2-projection.js";
export { joinApplicationEvfEvidence, assertApplicationEvfEvidenceCurrent } from "./application-evf-evidence.js";
export type { ApplicationEvfCausalOutcome, ApplicationEvfRouteKind, ApplicationEvfExactRef } from "./application-evf-evidence.js";
export { joinApplicationEvfCaseClaims, assertApplicationEvfCaseClaimsCurrent } from "./application-evf-case-claims.js";
export type { CaseClaimRef } from "./application-evf-case-claims.js";
export { joinApplicationRuntimeObservations, assertApplicationRuntimeObservationsCurrent } from "./application-runtime-observation.js";
export type { ApplicationRuntimeExactRef, ApplicationRuntimeStageKey } from "./application-runtime-observation.js";
export { lowerApplicationDomain, assertApplicationDomainCurrent } from "./application-domain-lowering.js";
export { lowerApplicationRuntimeProfiles, assertApplicationRuntimeProfilesCurrent } from "./application-runtime-profile.js";
export type { ApplicationRuntimeProfile, RuntimeProfileCompiler } from "./application-runtime-profile.js";
export { lowerApplicationVerificationProfiles, assertApplicationVerificationProfilesCurrent } from "./application-verification-profile.js";
export { finalizeApplicationExecutionRequest } from "./application-execution-request.js";
export { observeApplicationNativeCases, assertApplicationNativeCasesCurrent } from "./application-native-case-observation.js";
export type { NativeCaseObservationInput } from "./application-native-case-observation.js";
export { linkApplicationNativeCaseClaims } from "./application-native-case-claim-link.js";
export type { NativeCaseClaimLinkInput } from "./application-native-case-claim-link.js";
export type { ApplicationVerificationProfile, ApplicationVerificationRuntimeBounds, ApplicationVerificationProfileBinding } from "./application-verification-profile.js";
export type { ApplicationRuntimeContext } from "./application-domain-lowering.js";
export { compileApplicationWhole, assertApplicationWholeCurrent } from "./application-whole.js";
export { loadApplicationEvidenceFiles } from "./application-evidence-files.js";
export { loadApplicationFile, assertApplicationFileCurrent, type ApplicationFileOptions } from "./application-file-input.js";
export { checkApplicationFile } from "./application-file-check.js";
export { buildApplicationFile, verifyApplicationFile } from "./application-file-build.js";
export { lowerApplicationRuleProjections, assertApplicationRuleProjectionCurrent } from "./application-rule-projection.js";
export { prepareApplicationExecutable, compileApplicationExecutable } from "./application-executable.js";
export type { ApplicationIntegration, ApplicationSubscription, ApplicationPublication, ApplicationInboundEndpoint, ApplicationOutboundCall, ApplicationOutboundWrite, ApplicationPersistence } from "./application-integration.js";
export { deriveApplicationExternalWriteBindings } from "./application-external-write.js";
export { loadAlchLangSource } from "./source-file.js";
export { ALCH_SOURCE_PROFILE_ARCHITECTURE, selectAlchSourceProfile } from "./profile-architecture.js";
export type { AlchSourceProfileDescriptor, ProfileArchitectureRole, ProfileParserOwner, SelectedAlchSourceProfile } from "./profile-architecture.js";
export { qualifyBehavioralClaim } from "./behavioral-qualification.js";
export type { BehavioralClaim } from "./behavioral-qualification.js";
export { parsePredicate, parseSfolFormula, translateLegacyPredicate } from "./predicate-parser.js";
export { evaluateExpression, evaluateRule, evaluateSfolFormula, executeAction } from "./runtime.js";
export { evaluateCalculation, evaluateMapping, evaluatePolicy, evaluateQuery } from "./typed-backend.js";
export { FetchHttpTransport, HttpActionAdapter, MemoryActionAdapter, SqliteActionAdapter } from "./adapters.js";
export { resolveSqliteTransactionalOutboxEffect, SqliteTransactionalOutboxActionAdapter } from "./effect-adapters.js";
export { CollectingStdoutOutboxTransport, SqliteTransactionalOutbox, TransactionalOutboxWorker, sqliteOutboxMigrationSql, validateAtomicStateAndOutboxRequest } from "./sqlite-outbox-runtime.js";
export { CollectingOutboxTelemetry, DurableOutboxWorker, DurableSqliteTransactionalOutbox } from "./durable-outbox-runtime.js";
export { FetchOutboxHttpClient, HttpOutboxTransport, SqliteIdempotentInbox } from "./outbox-integrations.js";
export { writeCompilation } from "./writer.js";
export { deriveAvailability, listOperationPatterns, operationPatterns, requireGeneratablePattern } from "./pattern-registry.js";
export { renderSqliteTransactionalOutbox } from "./sqlite-outbox-generator.js";
export { compileOperationPatternRegistry, compileRegistryConfig, writeRegistryCompilation } from "./registry-compiler.js";
export type { CompilationPlan, CompilationResult, CompilerIssue, NormalizedAction, NormalizedCalculation, NormalizedDomain, NormalizedEnum, NormalizedInterface, NormalizedMapping, NormalizedPolicy, NormalizedQuery, NormalizedValueObject, NormalizedWorkflow, SfolFormula, SfolTerm, SfolUInt64Term, UInt64Expression } from "./model.js";
export type { AlchLangFileFormat, LoadedAlchLangSource } from "./source-file.js";
export type { ActionAdapter, ActionAdapterRegistry, ActionExecutionResult, ActionRequest } from "./runtime.js";
export type { AtomicStateAndOutboxRequest, OutboxMessage, OutboxTransport, PendingOutboxMessage } from "./sqlite-outbox-runtime.js";
export type { DurableCommitRequest, DurableOutboxMessage, DurableOutboxRecord, DurableOutboxStatus, DurableOutboxTransport, DurableWorkerOptions, OutboxTelemetryEvent, OutboxTelemetrySink } from "./durable-outbox-runtime.js";
export type { OperationPattern, PatternAvailability, PrerequisiteStatus } from "./pattern-registry.js";

export { DOMAINSPEC_PACKAGE, DOMAINSPEC_VERSION, loadDomainSpecCompiler, runDomainSpecCli } from "./domainspec-cli.js";
export type { DomainSpecCompiler, DomainSpecGraph, DomainSpecIo } from "./domainspec-cli.js";

export { lowerDomainSpec } from "./lower-domainspec.js";
export { buildDomainSpec, checkDomainSpec } from "./domainspec-project-writer.js";

export {parseComputationSource, lowerComputationSource, parseComputationCompanion, serializeComputationCompanion, COMPUTATION_CAPABILITY, COMPUTATION_BINDINGS, COMPUTATION_SEMANTICS} from "./computation-source.js";
export type {ComputationCompanionIdentityKind, LoweredComputationSource} from "./computation-source.js";
export {checkAlchComputation, buildAlchComputation, verifyAlchComputation} from "./commands/computation.js";

export {prepareBusinessAuthoringProject,assertPreparedBusinessAuthoringProjectCurrent,planBusinessAuthoringProject,viewBusinessAuthoringProject,generateBusinessAuthoringProject,verifyBusinessAuthoringProject,disposeBusinessAuthoringProject,initializeBusinessAuthoringProject,selectBusinessAuthoringProjectProfile,recordBusinessAuthoringProjectDecision,runBusinessAuthoringCommand} from './business-authoring-project.js';
export type {PreparedBusinessAuthoringProject} from './business-authoring-project.js';
export * from './business-authoring-public-v2.js';

export * from './business-authoring-project-v2.js';
export type {U0RuntimeBridgeV4} from './u0-runtime-bridge.js';

export * from './business-authoring-command-v2.js';

export * as commerce from './commerce.js';
