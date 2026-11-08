// GENERATED from Core business-authoring-protocol-v2.ts; canonical owner is Core.
/** Core-owned additive U0 authoring contract. Captured data is not custody.
 * Open Questions: docs/BUSINESS-AUTHORING-V2.md. Alch mirror is generated. */
import type {BusinessClaim, BusinessDefinition, BusinessEntity, BusinessModelIdentity, BusinessObligation, BusinessOperation, BusinessParameter, BusinessRequirement, BusinessSourceCapture, BusinessSourceSpan, BusinessValuePath} from './business-authoring-protocol.js';
export const BUSINESS_AUTHORING_CONTRACT_V2 = 'craft.business-authoring-contracts/2-candidate' as const;
export const BUSINESS_SPEC_V2 = 'alchlang.business-spec/v2-candidate' as const;
export const BUSINESS_AUTHORING_RECIPE_V2 = 'direct-entity-bool-operation/v2-candidate' as const;
export const BUSINESS_SOURCE_V2_MARKER = 'source-contract alchlang.business-spec/v2-candidate' as const;
export const BUSINESS_AUTHORING_V2_LIMITS = Object.freeze({source_bytes:1048576,lines:10000,requirements:16,entities:1,fields:2,rules:1,operations:1,entries:1,claims:256,definitions:256});
export interface DirectBooleanConditionV2 {readonly kind:'boolean-field';readonly value:Readonly<{root:string;path:readonly [string]}>}
export interface DirectBusinessRuleV2 {readonly id:string;readonly requirement_ref:string;readonly meaning:string;readonly input:BusinessParameter;readonly condition:DirectBooleanConditionV2}
/** Assurance-only references. A claim never supplies a Rule condition or execution permission. */
export interface BusinessClaimV2 extends BusinessClaim {readonly subject_refs:readonly string[]}
/** Frontend composition over existing Operation/Interface/Mapping roles, not a new meta-type. */
export interface BusinessLogicalEntryV2 {readonly id:string;readonly operation_ref:string;readonly public_name:string;readonly permission:Readonly<{kind:'public'}>}
export interface BusinessSpecDataV2 {
 readonly schema_version:typeof BUSINESS_SPEC_V2;readonly identity:BusinessModelIdentity;
 readonly requirements:readonly BusinessRequirement[];readonly entities:readonly BusinessEntity[];
 readonly definitions:readonly BusinessDefinition[];readonly claims:readonly BusinessClaimV2[];
 readonly rules:readonly DirectBusinessRuleV2[];readonly operations:readonly BusinessOperation[];
 readonly entries:readonly BusinessLogicalEntryV2[];readonly source_spans:readonly BusinessSourceSpan[];
 readonly obligations:readonly BusinessObligation[];readonly authority_effect:'none';
}
/** Parser/resolver implementations must register these handles privately; interfaces grant no custody. */
export interface ParsedBusinessSourceV2 {readonly kind:'parsed-business-source-v2';readonly data:BusinessSpecDataV2;readonly source:BusinessSourceCapture}
export interface ResolvedBusinessSpecV2 {readonly kind:'resolved-business-spec-v2';readonly data:BusinessSpecDataV2;readonly source:BusinessSourceCapture;readonly executable_sha256:string;readonly assurance_sha256:string}
export interface DirectExecutableRuleV2 {readonly id:string;readonly requirement_ref:string;readonly input:BusinessParameter;readonly condition:DirectBooleanConditionV2}
export interface DirectExecutableProjectionV2 {
 readonly schema_version:'craft.business-executable/v2-candidate';readonly normalization_contract:typeof BUSINESS_AUTHORING_CONTRACT_V2;
 readonly identity:BusinessModelIdentity;readonly requirements:readonly BusinessRequirement[];
 readonly entities:readonly BusinessEntity[];readonly rules:readonly DirectExecutableRuleV2[];
 readonly operations:readonly BusinessOperation[];readonly entries:readonly BusinessLogicalEntryV2[];readonly authority_effect:'none';
}
export interface OptionalAssuranceProjectionV2 {readonly schema_version:'craft.business-assurance/v2-candidate';readonly definitions:readonly BusinessDefinition[];readonly claims:readonly BusinessClaimV2[];readonly authority_effect:'none'}
export type DirectOperationGuardV2 = Readonly<{rule_ref:string;arguments:readonly Readonly<{parameter:string;value:BusinessValuePath}>[]}>;
