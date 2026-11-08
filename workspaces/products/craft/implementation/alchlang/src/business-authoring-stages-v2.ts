// GENERATED from Core business-authoring-stages-v2.ts; canonical owner is Core.
/** Prospective U0 producer signatures. Interfaces never mint original owner custody.
 * Implementations are assigned by docs/U0-SHARED-CONTRACTS.md; no native assets yet.
 * Open Questions: docs/U0-SHARED-CONTRACTS.md. Alch mirror is generated. */
import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import type {BusinessSpecDataV2,ParsedBusinessSourceV2,ResolvedBusinessSpecV2,DirectExecutableProjectionV2,OptionalAssuranceProjectionV2} from './business-authoring-protocol-v2.js';
import type {BusinessSelectedModelV2,BusinessRecipeSelectionV2,BusinessReviewSubjectV2,BusinessEarlyRequestsV2,AuthoringBusinessInputV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessCoverageInventoryV2,BusinessCoverageOriginV2,BusinessOutputPlanV2,BusinessOutputResultV2,BusinessOutputKindV2} from './business-authoring-coverage-contract-v2.js';
import type {U0ResolvedNativeBasis,U0RealizedApplicationSubject,U0PureInvoke,U0InjectedHandler,U0Submission,U0ProcessOutcome,U0AdapterFailureCode,U0WireConfiguration} from './u0-realization-contract.js';

export const BUSINESS_STAGES_V2='craft.business-authoring-stages/v2-candidate' as const;
export interface BusinessParserOwnerV2 {
 parse(text:string,sourceName?:string):ParsedBusinessSourceV2;
 assertCurrent(parsed:ParsedBusinessSourceV2):void;
}
export interface BusinessResolverOwnerV2 {
 resolve(parsed:ParsedBusinessSourceV2):ResolvedBusinessSpecV2;
 prepareFile(root:string,relative:string):ResolvedBusinessSpecV2;
 assertCurrent(resolved:ResolvedBusinessSpecV2):void;
 dispose(resolved:ResolvedBusinessSpecV2):void;
}
export interface LoweredDirectBusinessV2 {
 readonly kind:'lowered-direct-business-v2';readonly business:ResolvedBusinessSpecV2;
 readonly executable:DirectExecutableProjectionV2;readonly assurance:OptionalAssuranceProjectionV2;
 readonly review:BusinessReviewSubjectV2;readonly authority_effect:'none';
}
export interface BusinessDirectLoweringOwnerV2 {
 lower(resolved:ResolvedBusinessSpecV2):LoweredDirectBusinessV2;
 assertCurrent(lowered:LoweredDirectBusinessV2):void;
}
/** The recipe owner checks original native basis and independently rereads source.
 * A source DTO or a structurally matching basis alone is insufficient. */
export interface BusinessCoreRecipeOwnerV2 {
 select(models:readonly BusinessSelectedModelV2[],basis:U0ResolvedNativeBasis):BusinessRecipeSelectionV2;
 assertCurrent(selection:BusinessRecipeSelectionV2):void;
 dispose(selection:BusinessRecipeSelectionV2):void;
}
export interface U0TypedClosureOriginV2 {
 readonly role:'Entity'|'Rule'|'Operation'|'Interface'|'Mapping';readonly selector:string;
 readonly typed_closure_sha256:string;readonly origins:readonly BusinessCoverageOriginV2[];
}
/** Underlying compiled project and selected node handles stay in the actual owner's
 * private registry. Whole-project graph serialization alone does not check a Rule. */
export interface U0CheckedBusinessGraphV2 {
 readonly kind:'checked-u0-business-graph-v2';readonly input:AuthoringBusinessInputV2;
 readonly graph_sha256:string;readonly closures:readonly U0TypedClosureOriginV2[];readonly authority_effect:'none';
}
export interface DirectConditionBindingV2 {
 readonly kind:'direct-condition-binding-v2';readonly graph:U0CheckedBusinessGraphV2;
 readonly rule_ref:string;readonly parameter:string;readonly entity_ref:string;
 readonly field_name:string;readonly property_selector:string;readonly condition_sha256:string;
 readonly authority_effect:'none';
}
export interface CheckedDirectApplicationV2 {
 readonly kind:'checked-direct-application-v2';readonly input:AuthoringBusinessInputV2;
 readonly graph:U0CheckedBusinessGraphV2;readonly condition:DirectConditionBindingV2;
 readonly operation_ref:string;readonly plan_sha256:string;readonly authority_effect:'none';
}
export interface BusinessDirectApplicationOwnerV2 {
 check(input:AuthoringBusinessInputV2):CheckedDirectApplicationV2;
 assertCurrent(application:CheckedDirectApplicationV2):void;
 assertConditionCurrent(condition:DirectConditionBindingV2):void;
}
export interface U0SourceArtifactV2 {readonly path:string;readonly content:string;readonly sha256:string}
export interface U0FileArtifactV2 {readonly path:string;readonly sha256:string;readonly bytes:number}
export interface GeneratedU0CallableSourceV2 {
 readonly kind:'generated-u0-callable-source-v2';readonly application:CheckedDirectApplicationV2;
 readonly abi:'craft.u0.pure-submission/v1-candidate';readonly export_name:'invoke';
 readonly files:readonly U0SourceArtifactV2[];readonly source_sha256:string;readonly authority_effect:'none';
}
/** Actual generated/imported callable, not a user-supplied evaluator callback. */
export interface ImportedU0CallableV2 {
 readonly kind:'imported-u0-callable-v2';readonly source:GeneratedU0CallableSourceV2;
 readonly artifact:U0FileArtifactV2;readonly invoke:U0PureInvoke<string>;readonly authority_effect:'none';
}
export interface BusinessPureGenerationOwnerV2 {
 generate(application:CheckedDirectApplicationV2):GeneratedU0CallableSourceV2;
 importGenerated(source:GeneratedU0CallableSourceV2,absoluteModulePath:string):Promise<ImportedU0CallableV2>;
 assertCurrent(callable:ImportedU0CallableV2):void;
}
export interface BoundU0EntryV2 {
 readonly kind:'bound-u0-entry-v2';readonly early:BusinessEarlyRequestsV2;
 readonly callable:ImportedU0CallableV2;readonly basis:U0ResolvedNativeBasis;
 readonly handler_artifact:U0FileArtifactV2;readonly handler:U0InjectedHandler;
 readonly subject:U0RealizedApplicationSubject;readonly authority_effect:'none';
}
export interface BusinessRequestStagesOwnerV2 {
 prepareEarly(selection:BusinessRecipeSelectionV2):BusinessEarlyRequestsV2;
 assertEarlyCurrent(early:BusinessEarlyRequestsV2):void;
 bindLate(early:BusinessEarlyRequestsV2,callable:ImportedU0CallableV2,basis:U0ResolvedNativeBasis):Promise<BoundU0EntryV2>;
 assertBoundCurrent(bound:BoundU0EntryV2):void;
}
/** U06a token shape is separate from U06b exact value formation. */
export interface U0DecodedRecordV2 {readonly id:string;readonly verified:boolean}
/** Authored rejection is captured from the checked Operation, not a runtime hook.
 * U06c must calculate its bound; C03's 59-byte value is the first fixture only. */
export interface U0ResponseDomainV2 {readonly rejection_code:string}
export interface U0WireBoundsV2 {readonly request:number;readonly completed:number;readonly rejected:number;readonly adapter_error:number}
export interface U0DecoderOwnerV2 {decode(bytes:Uint8Array,maximumBytes:number):U0DecodedRecordV2}
export interface U0ValueOwnerV2 {form(record:U0DecodedRecordV2):U0Submission;copy(input:U0Submission):U0Submission}
export interface U0EncoderOwnerV2 {
 request(value:U0Submission):Uint8Array;
 outcome(value:U0ProcessOutcome<string>,domain:U0ResponseDomainV2):Uint8Array;
 error(code:U0AdapterFailureCode):Uint8Array;
 bounds(domain:U0ResponseDomainV2):U0WireBoundsV2;
 checkConfiguration(configuration:U0WireConfiguration,domain:U0ResponseDomainV2):U0WireConfiguration;
}
/** Native infrastructure seam. Only the late owner binds a genuine generated import;
 * accepting a test callable here cannot qualify application generation. */
export interface U0HandlerAssetOwnerV2 {
 create(invoke:U0PureInvoke<string>,configuration:U0WireConfiguration,domain:U0ResponseDomainV2):U0InjectedHandler;
}
export interface BusinessCheckedCoverageV2 {
 readonly kind:'checked-business-coverage-v2';readonly inventory:BusinessCoverageInventoryV2;
 readonly application:CheckedDirectApplicationV2;readonly bound:BoundU0EntryV2|null;
 readonly owners:readonly Readonly<{obligation_id:string;owner_selector:string;owner_sha256:string}>[];
 readonly coverage_sha256:string;readonly authority_effect:'none';
}
export interface BusinessCheckedViewsV2 {
 readonly kind:'checked-business-views-v2';readonly coverage:BusinessCheckedCoverageV2;
 readonly files:readonly Readonly<{kind:'business-graph'|'system-graph'|'business-system-bridge';artifact:U0SourceArtifactV2}>[];
 readonly views_sha256:string;readonly authority_effect:'none';
}
export interface BusinessCoverageViewsOwnerV2 {
 inventory(input:AuthoringBusinessInputV2):BusinessCoverageInventoryV2;
 check(application:CheckedDirectApplicationV2,bound?:BoundU0EntryV2):BusinessCheckedCoverageV2;
 project(coverage:BusinessCheckedCoverageV2):BusinessCheckedViewsV2;
 assertCurrent(views:BusinessCheckedViewsV2):void;
}
export interface BusinessOutputArtifactInputV2 {
 readonly kind:BusinessOutputKindV2;readonly artifact:U0SourceArtifactV2;
 readonly checked_owner_sha256:string;readonly producer_sha256:string;
}
export interface BusinessFreshOutputRequestV2 {
 readonly target:string;readonly plan:BusinessOutputPlanV2;readonly application:CheckedDirectApplicationV2;
 readonly bound:BoundU0EntryV2;readonly views:BusinessCheckedViewsV2;
 readonly artifacts:readonly BusinessOutputArtifactInputV2[];
}
export interface BusinessOutputWriterOwnerV2 {
 publish(request:BusinessFreshOutputRequestV2):BusinessOutputResultV2;
 check(request:BusinessFreshOutputRequestV2):BusinessOutputResultV2;
}
/** Explicit source-only transfer to Core; neither JSON nor this type authenticates it. */
export interface BusinessDirectSourceTransferV2 {
 readonly source:BusinessSourceCapture;readonly spec:BusinessSpecDataV2;
 readonly executable:DirectExecutableProjectionV2;readonly assurance:OptionalAssuranceProjectionV2;
}
