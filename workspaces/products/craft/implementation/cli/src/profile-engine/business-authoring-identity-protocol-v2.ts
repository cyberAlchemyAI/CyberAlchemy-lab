/** Core-owned stage contracts. Data/digests/types do not register original handles.
 * Open Questions: docs/BUSINESS-IDENTITIES-V2.md. Alch copy is generated. */
import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import type {BusinessSpecDataV2,DirectBusinessRuleV2,DirectExecutableProjectionV2,OptionalAssuranceProjectionV2} from './business-authoring-protocol-v2.js';
export const BUSINESS_IDENTITY_V2='craft.business-identity/v2-candidate' as const;
export const BUSINESS_EXECUTABLE_CANONICALIZATION_V2='craft.direct-executable-keysort-id-sort/v2' as const;
export const BUSINESS_ASSURANCE_CANONICALIZATION_V2='craft.optional-assurance-keysort-id-sort/v2' as const;
export const BUSINESS_REVIEW_CANONICALIZATION_V2='craft.business-review-keysort/v2' as const;
export interface BusinessDigestV2 {readonly algorithm:'sha256';readonly canonicalization:string;readonly sha256:string}
export interface BusinessCaptureManifestV2 {
 readonly schema_version:'craft.business-capture/v2-candidate';readonly recipe_ref:'direct-entity-bool-operation/v2-candidate';
 readonly source:Readonly<{path:string;sha256:string;bytes:number}>;
 readonly profiles:readonly Readonly<{id:string;version:string;sha256:string}>[];
 readonly tools:readonly Readonly<{id:string;sha256:string}>[];readonly authority_effect:'none';
}
export interface BusinessCaptureIdentityV2 extends BusinessCaptureManifestV2 {readonly capture_sha256:string}
/** These are references to actual later owner outputs, never a resolver or readiness flag. */
export interface BusinessNativeBasisReferenceV2 {
 readonly kind:'native-basis-reference-v2';readonly descriptor:'node-http-entry-u0-v4';readonly abi:'craft.u0.pure-submission/v1-candidate';
 readonly sdk_sha256:string;readonly basis_sha256:string;readonly configuration_sha256:string;
}
export interface BusinessSelectedModelV2 {
 readonly model_id:string;readonly source:BusinessSourceCapture;readonly spec:BusinessSpecDataV2;
 readonly executable_sha256:string;readonly assurance_sha256:string;readonly capture:BusinessCaptureIdentityV2;
}
export interface BusinessRecipeSelectionV2 {
 readonly kind:'business-recipe-selection-v2';readonly models:readonly BusinessSelectedModelV2[];
 readonly native_basis:BusinessNativeBasisReferenceV2;readonly selection_sha256:string;readonly authority_effect:'none';
}
export interface BusinessEarlyEntryIntentV2 {
 readonly model_id:string;readonly entry_id:string;readonly operation_ref:string;readonly rule_ref:string;
 readonly permission:Readonly<{kind:'public'}>;readonly payload:Readonly<{kind:'whole-input';parameter:string;type_ref:string}>;
 readonly unresolved_native_obligations:readonly Readonly<{producer:'generated-callable'|'exact-codec'|'injected-handler'|'request-graph';abi_ref:string}>[];
}
export interface BusinessEarlyRequestsV2 {
 readonly kind:'business-early-requests-v2';readonly selection:BusinessRecipeSelectionV2;
 readonly entries:readonly BusinessEarlyEntryIntentV2[];readonly request_sha256:string;readonly authority_effect:'none';
}
export interface BusinessReviewSubjectV2 {
 readonly schema_version:'craft.business-review/v2-candidate';readonly normalization_contract:'craft.business-authoring-contracts/2-candidate';
 readonly model_id:string;readonly owner:string;readonly version:string;readonly authored_rules:readonly DirectBusinessRuleV2[];
 readonly executable:DirectExecutableProjectionV2;readonly executable_sha256:string;
 readonly assurance:OptionalAssuranceProjectionV2;readonly assurance_sha256:string;readonly authority_effect:'none';
}
export interface BusinessDecisionV2 {
 readonly schema_version:'craft.business-decision/v2-candidate';readonly decision_id:string;readonly owner:string;
 readonly outcome:'accepted'|'declined';readonly subject:Readonly<{algorithm:'sha256';canonicalization:typeof BUSINESS_REVIEW_CANONICALIZATION_V2;sha256:string}>;
 readonly capture_sha256:string;readonly executable_sha256:string;readonly assurance_sha256:string;readonly authority_effect:'none';
}
/** Early lock excludes callable/handler/application bytes; the complete realization is produced at U08. */
export interface BusinessAuthoringLockV2 {
 readonly schema_version:'craft.business-authoring-lock/v2-candidate';readonly model_id:string;
 readonly capture_sha256:string;readonly executable_sha256:string;readonly assurance_sha256:string;readonly basis_sha256:string;
 readonly selection_sha256:string;readonly review_sha256:string;readonly decision_file_sha256:string;readonly entry_intent_sha256:string;readonly lock_sha256:string;
 readonly authority_effect:'none';
}
export interface PreparedBusinessReviewV2 {
 readonly kind:'prepared-business-review-v2';readonly selection:BusinessRecipeSelectionV2;readonly model_id:string;
 readonly subject:BusinessReviewSubjectV2;readonly source_capture:BusinessCaptureIdentityV2;readonly review_sha256:string;readonly authority_effect:'none';
}
export interface CapturedBusinessDecisionV2 {
 readonly kind:'captured-business-decision-v2';readonly review:PreparedBusinessReviewV2;readonly decision:BusinessDecisionV2;
 readonly file:Readonly<{path:string;sha256:string;bytes:number;device:string;inode:string;mtime_ns:string}>;readonly authority_effect:'none';
}
export interface AcceptedBusinessReviewV2 {
 readonly kind:'accepted-business-review-v2';readonly review:PreparedBusinessReviewV2;readonly decision:CapturedBusinessDecisionV2;readonly authority_effect:'none';
}
export interface AuthoringBusinessInputV2 {
 readonly kind:'authoring-business-input-v2';readonly selection:BusinessRecipeSelectionV2;readonly model_id:string;readonly spec:BusinessSpecDataV2;
 readonly accepted:AcceptedBusinessReviewV2;readonly early_requests:BusinessEarlyRequestsV2;
 readonly capture:BusinessCaptureIdentityV2;readonly input_sha256:string;readonly authority_effect:'none';
}
/** K01/L02 implement original private registries. A matching JSON object or TypeScript cast never passes. */
export interface BusinessReviewOwnerV2 {
 prepare(selection:BusinessRecipeSelectionV2,modelId:string,subject:BusinessReviewSubjectV2):PreparedBusinessReviewV2;
 assertCurrent(review:PreparedBusinessReviewV2):void;
 captureDecision(review:PreparedBusinessReviewV2,file:string):CapturedBusinessDecisionV2;
 assertDecisionCurrent(decision:CapturedBusinessDecisionV2):void;
 requireAccepted(review:PreparedBusinessReviewV2,decision:CapturedBusinessDecisionV2):AcceptedBusinessReviewV2;
 assertAcceptedCurrent(accepted:AcceptedBusinessReviewV2):void;
}
export interface BusinessInputOwnerV2 {
 form(selection:BusinessRecipeSelectionV2,modelId:string,accepted:AcceptedBusinessReviewV2,requests:BusinessEarlyRequestsV2):AuthoringBusinessInputV2;
 assertCurrent(input:AuthoringBusinessInputV2):void;
}
export type BusinessCurrentnessFailureV2='foreign-handle'|'disposed'|'source-drift'|'profile-drift'|'tool-drift'|'implementation-drift'|'decision-drift'|'subject-mismatch';
/** U1 future contract only. No native AST, parser, model export or proof is produced here. */
export interface OptionalBaseModelIdentityV2 {
 readonly format:'tptp-tff0';readonly profile:Readonly<{id:string;version:string;abi:string;sha256:string}>;
 readonly executable_sha256:string;readonly ast_sha256:string;readonly symbol_table_sha256:string;readonly coverage_sha256:string;
}
