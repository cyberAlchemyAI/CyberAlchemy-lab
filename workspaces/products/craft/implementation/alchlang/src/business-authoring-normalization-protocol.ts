// Generated data-only mirror of Core business-authoring-normalization-protocol.ts; do not edit.
import type {BusinessCapability,BusinessField,BusinessParameter,BusinessRequirement,BusinessSourceCapture,BusinessSpecData,ReviewDefinition} from './business-authoring-protocol.js';

/** Additive B03/B05.2 data contract. No acceptance or handle registration.
 * Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md. Alch mirror is generated. */
export const BUSINESS_NORMALIZATION_CONTRACT='craft.business-normalization/1-candidate' as const;
export const BUSINESS_RECIPE_GUARANTEES=Object.freeze(['preserve-settlement-outcome','preflight-cancellation-only'] as const);
export interface BusinessEntityStructure {readonly kind:'entity';readonly entity_ref:string;readonly identity:string;readonly fields:readonly Readonly<{name:string;type:BusinessField['type']}>[]}
export interface BusinessBoolPrimitive {readonly kind:'entity-bool-field';readonly entity_ref:string;readonly parameter:string;readonly field:string;readonly field_type:'Bool';readonly comparison:'eq';readonly value:true}
export type BusinessGroundProposition=
 |Readonly<{kind:'predicate';name:string;arguments:readonly Readonly<{kind:'constant';name:string;sort:string}>[]}>
 |Readonly<{kind:'not';operand:BusinessGroundProposition}>
 |Readonly<{kind:'and'|'or'|'implies'|'iff';left:BusinessGroundProposition;right:BusinessGroundProposition}>;
export interface BusinessNormalizedDefinition {
 readonly definition_ref:string;readonly requirement_ref:string;readonly input:BusinessParameter;
 readonly entity:BusinessEntityStructure;readonly field:BusinessField;readonly primitive:BusinessBoolPrimitive;
 readonly formal:ReviewDefinition['formal'];
 readonly predicate_uses:readonly Readonly<{claim_ref:string;predicate_ref:string;sort_ref:string}>[];
}
export interface BusinessNormalizedClaim {
 readonly claim_ref:string;readonly version:string;readonly logic_profile:'fol-core/1-candidate';
 readonly signature:Readonly<{sorts:readonly Readonly<{name:string}>[];functions:readonly [];predicates:readonly Readonly<{name:string;parameter_sorts:readonly string[]}>[];constants:readonly Readonly<{name:string;sort:string}>[]}>;
 readonly proposition_source:string;readonly proposition:BusinessGroundProposition;readonly ceiling:string;
}
export interface BusinessRuleInterpretation {readonly sorts:Readonly<Record<string,string>>;readonly constants:Readonly<Record<string,string>>;readonly predicates:Readonly<Record<string,string>>}
export interface BusinessFormalData {
 readonly schema_version:'craft.business-formal-normalization/v1-candidate';readonly normalization_contract:typeof BUSINESS_NORMALIZATION_CONTRACT;
 readonly model_id:string;readonly business_sha256:string;
 readonly definitions:readonly BusinessNormalizedDefinition[];readonly claims:readonly BusinessNormalizedClaim[];
 readonly rule_meanings:Readonly<Record<string,BusinessRuleInterpretation>>;readonly authority_effect:'none';
}
export interface BusinessNormalizedOperation {
 readonly operation_ref:string;readonly meaning:string;
 readonly input:Readonly<{name:string;type:BusinessEntityStructure}>;readonly output:BusinessEntityStructure;
 readonly guards:readonly Readonly<{rule_ref:string;claim_ref:string;parameter:Readonly<{name:string;type:BusinessEntityStructure}>;argument:Readonly<{root:string;path:readonly []}>}>[];
 readonly result:Readonly<{root:string;path:readonly [];type:BusinessEntityStructure}>;
 readonly effects:readonly [];readonly failure:Readonly<{kind:'continuation-metadata';continuation:string;executable:false}>;
}
export interface BusinessBehaviorData {
 readonly schema_version:'craft.business-behavior-normalization/v1-candidate';readonly normalization_contract:typeof BUSINESS_NORMALIZATION_CONTRACT;
 readonly model_id:string;readonly business_sha256:string;readonly formal_sha256:string;
 readonly operations:readonly BusinessNormalizedOperation[];readonly exposures:readonly BusinessCapability[];
 readonly contexts:readonly BusinessRequirement[];readonly actor_semantics:'informational-only';readonly authority_effect:'none';
}
/** Inert transport data, never a serialized Alch handle or accepted carrier. */
export interface BusinessRecipeModelInput {
 readonly model_id:string;readonly source:Omit<BusinessSourceCapture,'text'>;
 readonly spec:BusinessSpecData;readonly formal:BusinessFormalData;readonly behavior:BusinessBehaviorData;
}
export interface BusinessRecipeRequirements {
 readonly recipe_ref:'ground-entity-bool-operation/v1-candidate';readonly logic_profile:'fol-core/1-candidate';readonly target:'node-typescript';readonly effects:'none';
 readonly required_guarantees:readonly string[];
}
