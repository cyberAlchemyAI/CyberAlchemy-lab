// GENERATED Alch API mirror; canonical owner is Core; interfaces implement no owner.
/** EC05 prospective owner/component APIs. These interfaces implement no owner.
 * Open Questions: docs/COMMERCE-CONTRACTS.md. */
import type {
 ApplicationContractV1, ArtifactIdentityV1, ComputationContractV1, EntryContractV1,
 EffectPlanV1, ExpressionFailureV1, ModuleContractV1, NativeObligationV1,
 ProfilePackageV1, ReadPlanV1, RoleSelectorV1, SourceIdentityV1,
 ValueSchemaV1, WorkflowContractV1, RealizationScopeV1, ValueTypeV1,
} from './commerce-data-v1.js';

export const COMMERCE_STAGES_V1='craft.commerce-stages/v1-candidate' as const;
export const COMMERCE_EXPRESSION_SCHEMA_V2='domainspec.iteration-expression/v2-candidate' as const;
export const COMMERCE_SEMANTICS_V2='ordered-metered-commerce-v2-candidate' as const;
/** Configured positive bounds; exhausted runtime fuel is a separate counter. */
export const COMMERCE_REQUIRED_LIMITS_V2=Object.freeze({
 max_input_bytes:1048576,max_output_bytes:524288,max_value_bytes:524288,
 max_items:100,max_iterations:100,max_ast_nodes:4096,max_ast_depth:32,
 max_call_depth:32,fuel:100000,
} as const);
export const COMMERCE_TYPE_LIMITS_V1=Object.freeze({
 reachable_records_per_expression:64,fields_per_record:64,variants_per_enum:64,
 typed_value_depth:32,source_schema_depth:32,parameters_per_callable:128,
} as const);

/** Deliberately absent at runtime. Each implementation must also recognize its
 * own original object in a private registry. TypeScript casts/JSON/hashes are
 * never custody. Inspection records below cannot be fed back as a handle. */
declare const ORIGINAL_COMMERCE_OWNER:unique symbol;
export interface CommerceHandle<K extends string> {
 readonly [ORIGINAL_COMMERCE_OWNER]:K;
}
export type CommerceSourceHandle=CommerceHandle<'source'>;
export type CommerceTechnicalModelHandle=CommerceHandle<'technical-model'>;
export type CommerceDerivedFamilyHandle=CommerceHandle<'derived-family'>;
export type CommerceProfileHandle=CommerceHandle<'loaded-profile'>;
export type CommerceBindingAssemblyHandle=CommerceHandle<'private-late-binding-assembly'>;
export type CommerceOperationInvocationHandle=CommerceHandle<'private-generated-operation-invocation'>;
export type CommerceNativeBasisHandle=CommerceHandle<'native-basis'>;
export type CommerceSelectionHandle=CommerceHandle<'selection'>;
export type CommerceEarlyRequestHandle=CommerceHandle<'early-request'>;
export type CommerceReviewHandle=CommerceHandle<'review'>;
export type CommerceDecisionHandle=CommerceHandle<'captured-decision'>;
export type CommerceInputHandle=CommerceHandle<'authoring-input'>;
export type CommerceApplicationHandle=CommerceHandle<'checked-application'>;
export type CommerceGeneratedHandle=CommerceHandle<'generated-source'>;
export type CommerceImportedHandle=CommerceHandle<'actual-imported-output'>;
export type CommerceBoundHandle=CommerceHandle<'bound-application'>;
export type CommerceViewsHandle=CommerceHandle<'checked-views'>;
export type CommerceEntryContextHandle=CommerceHandle<'private-entry-context'>;
export type CommerceActorHandle=CommerceHandle<'private-authentication-evidence'>;
export type CommerceCausalHandle=CommerceHandle<'private-causal-call'>;
export type CommerceWorkerHandle=CommerceHandle<'private-worker-lifecycle'>;

/** Display/transfer data, never a serialized owner. */
export interface CommerceInspection {
 readonly stage:string; readonly source_sha256:string;
 readonly profile_sha256:string|null; readonly native_basis_sha256:string|null;
 readonly output_sha256:string|null; readonly authority_effect:'none';
}
export interface CommerceSourceText {
 readonly identity:SourceIdentityV1; readonly text:string;
}
export interface CommerceSourceInspection extends CommerceInspection {
 readonly application:ApplicationContractV1;readonly modules:readonly CommerceSourceText[];
}
export interface CommerceDiagnostic {
 readonly code:'Syntax'|'UnknownReference'|'AmbiguousReference'|'DuplicateSymbol'|
 'TypeMismatch'|'MissingMapping'|'NonExhaustive'|'UnsupportedCapability'|
 'InvalidContract'|'ResourceLimit'|'NativeImplementationUnavailable'|
 'StaleOwner'|'ForeignOwner'|'DisposedOwner'|'RequiredOutputUnavailable';
 readonly path:string;readonly start:number;readonly end:number;readonly message:string;
}
export type CommerceResult<T>={readonly ok:true;readonly value:T}|
 {readonly ok:false;readonly diagnostics:readonly CommerceDiagnostic[]};

/** EC06 parser component parses only supplied source data. Source capture and
 * source-currentness remain separately implemented owners. */
export interface CommerceParserComponent {
 parse(text:string,relativePath:string):CommerceResult<ModuleContractV1>;
 parseValues(sources:readonly CommerceSourceText[],root:ValueTypeV1):CommerceResult<ValueSchemaV1>;
 parseComputation(sources:readonly CommerceSourceText[],selector:RoleSelectorV1):CommerceResult<ComputationContractV1>;
 parseRead(sources:readonly CommerceSourceText[],selector:RoleSelectorV1):CommerceResult<ReadPlanV1>;
 parseEffects(sources:readonly CommerceSourceText[],selector:RoleSelectorV1):CommerceResult<EffectPlanV1>;
 parseWorkflow(sources:readonly CommerceSourceText[],selector:RoleSelectorV1):CommerceResult<WorkflowContractV1>;
 parseEntry(sources:readonly CommerceSourceText[],entry:string):CommerceResult<EntryContractV1>;
}
export interface CommerceSourceOwner {
 prepare(root:string,applicationRelativePath:string):Promise<CommerceSourceHandle>;
 inspect(source:CommerceSourceHandle):CommerceSourceInspection;
 assertCurrent(source:CommerceSourceHandle):void;
 dispose(source:CommerceSourceHandle):void;
}
export interface CommerceSemanticComponent {
 checkModule(module:ModuleContractV1,closure:readonly ModuleContractV1[]):CommerceResult<ModuleContractV1>;
 checkComputation(contract:ComputationContractV1):CommerceResult<ComputationContractV1>;
 checkRead(plan:ReadPlanV1,values:ValueSchemaV1):CommerceResult<ReadPlanV1>;
 checkEffects(plan:EffectPlanV1,values:ValueSchemaV1):CommerceResult<EffectPlanV1>;
 checkWorkflow(plan:WorkflowContractV1,entries:readonly EntryContractV1[]):CommerceResult<WorkflowContractV1>;
}
export interface CommerceFamilyOwner {
 checkTechnicalSource(root:string,relativePath:string):Promise<CommerceTechnicalModelHandle>;
 derive(model:CommerceTechnicalModelHandle,parameters:ProfilePackageV1['parameters'],scope:RealizationScopeV1):CommerceDerivedFamilyHandle;
 obligations(family:CommerceDerivedFamilyHandle):readonly NativeObligationV1[];
 assertCurrent(family:CommerceDerivedFamilyHandle):void;
}
/** Only actual original producer output may satisfy obligations. No supplied
 * JS function, comparator, SQL string, graph JSON or fake digest implements one. */
export interface CommerceNativeOwner {
 capture(family:CommerceDerivedFamilyHandle,producedRoot:string):Promise<CommerceNativeBasisHandle>;
 load(family:CommerceDerivedFamilyHandle,basis:CommerceNativeBasisHandle):Promise<CommerceProfileHandle>;
 inspect(basis:CommerceNativeBasisHandle):CommerceInspection;
 assertCurrent(basis:CommerceNativeBasisHandle):void;
}
export interface CommerceSelectionOwner {
 select(source:CommerceSourceHandle,profile:CommerceProfileHandle,basis:CommerceNativeBasisHandle):CommerceSelectionHandle;
 prepareEarly(selection:CommerceSelectionHandle):CommerceEarlyRequestHandle;
 assertCurrent(selection:CommerceSelectionHandle):void;
}
export interface CommerceReviewOwner {
 review(source:CommerceSourceHandle,selection:CommerceSelectionHandle):CommerceReviewHandle;
 recordDecision(review:CommerceReviewHandle,decision:'accept'|'reject'):CommerceDecisionHandle;
 assertCurrent(decision:CommerceDecisionHandle):void;
}
export interface CommerceApplicationOwner {
 formInput(source:CommerceSourceHandle,selection:CommerceSelectionHandle,early:CommerceEarlyRequestHandle,decision:CommerceDecisionHandle):CommerceInputHandle;
 check(input:CommerceInputHandle):CommerceApplicationHandle;
 inspect(application:CommerceApplicationHandle):CommerceInspection;
 assertCurrent(application:CommerceApplicationHandle):void;
}
export interface CommerceSourceArtifact {
 readonly identity:ArtifactIdentityV1;readonly content:string;
}
/** Pure data emitters qualify only the supplied component plan. Full generated
 * application imports require the independent original application owner. */
export interface CommerceGeneratorComponents {
 computation(contract:ComputationContractV1):CommerceResult<readonly CommerceSourceArtifact[]>;
 read(plan:ReadPlanV1,values:ValueSchemaV1):CommerceResult<readonly CommerceSourceArtifact[]>;
 effects(plan:EffectPlanV1,values:ValueSchemaV1):CommerceResult<readonly CommerceSourceArtifact[]>;
 workflow(plan:WorkflowContractV1):CommerceResult<readonly CommerceSourceArtifact[]>;
}
export interface CommerceGenerationOwner {
 generate(application:CommerceApplicationHandle):CommerceGeneratedHandle;
 files(generated:CommerceGeneratedHandle):readonly CommerceSourceArtifact[];
 importGenerated(generated:CommerceGeneratedHandle,absoluteRoot:string):Promise<CommerceImportedHandle>;
 bindLate(early:CommerceEarlyRequestHandle,application:CommerceApplicationHandle,output:CommerceImportedHandle,basis:CommerceNativeBasisHandle):Promise<CommerceBoundHandle>;
 assertCurrent(bound:CommerceBoundHandle):void;
}
/** Actual public observations must come from the imported/bound generated
 * module. These interfaces expose no caller-provided business invoke hook. */
export interface CommerceRuntimeOwner {
 handle(bound:CommerceBoundHandle,request:Request):Promise<Response>;
 invokeEntry(bound:CommerceBoundHandle,entry:string,inputBytes:Uint8Array,context:CommerceEntryContextHandle):Promise<Uint8Array>;
 resume(bound:CommerceBoundHandle,worker:CommerceWorkerHandle):Promise<void>;
 dispose(bound:CommerceBoundHandle):Promise<void>;
}
export interface CommerceAuthOwner {
 authorize(bound:CommerceBoundHandle,entry:string,inputBytes:Uint8Array,actor:CommerceActorHandle,causal:CommerceCausalHandle|null):Promise<CommerceResult<CommerceEntryContextHandle>>;
 consume(context:CommerceEntryContextHandle,entry:string):void;
 dispose(context:CommerceEntryContextHandle):void;
}
export interface CommerceViewOwner {
 project(application:CommerceApplicationHandle,bound:CommerceBoundHandle):CommerceViewsHandle;
 files(views:CommerceViewsHandle):readonly CommerceSourceArtifact[];
 assertCurrent(views:CommerceViewsHandle):void;
}
export interface CommerceOutputOwner {
 check(bound:CommerceBoundHandle,views:CommerceViewsHandle,required:readonly string[]):CommerceResult<readonly CommerceSourceArtifact[]>;
 writeFresh(bound:CommerceBoundHandle,views:CommerceViewsHandle,absoluteTarget:string):Promise<readonly ArtifactIdentityV1[]>;
}
/** Formal language export is optional and separate from executable bodies. */
export interface CommerceOptionalAssuranceComponent {
 exportModel(application:CommerceApplicationHandle,language:'lean4'|'smtlib2'|'alloy'|'tla-plus'|'souffle',required:boolean):CommerceResult<readonly CommerceSourceArtifact[]>;
}
export type CommerceEvaluationResult =
 {readonly ok:true;readonly wire:Uint8Array;readonly fuel_used:number}|
 {readonly ok:false;readonly error:ExpressionFailureV1;readonly fuel_used:number};
export interface CommerceComputationComponent {
 evaluate(contract:ComputationContractV1,input:Uint8Array):CommerceEvaluationResult;
}
export interface CommerceSelectedRoleInspection {
 readonly selector:RoleSelectorV1;readonly typed_closure_sha256:string;
 readonly source:SourceIdentityV1;readonly authority_effect:'none';
}
