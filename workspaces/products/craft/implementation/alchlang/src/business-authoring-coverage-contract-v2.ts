// GENERATED from Core business-authoring-coverage-contract-v2.ts; canonical owner is Core.
import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import type {BusinessSpecDataV2} from './business-authoring-protocol-v2.js';
/** Finite coverage/output contracts. Plain inventories/plans are not original owner handles.
 * Open Questions: docs/BUSINESS-COVERAGE-V2.md. */
export const BUSINESS_OUTPUT_KINDS_V2=Object.freeze(['code','api-contracts','business-graph','system-graph','business-system-bridge','base-model','conjecture-problems'] as const);
export type BusinessOutputKindV2=typeof BUSINESS_OUTPUT_KINDS_V2[number];
export type BusinessCoverageOwnerV2='source'|'direct-condition'|'pure-operation'|'entry-intent'|'native-realization'|'checked-views';
export interface BusinessCoverageOriginV2 {readonly source:string;readonly selector:string;readonly sha256:string}
export interface BusinessCoverageObligationV2 {
 readonly id:string;readonly kind:'authored-fact'|'entity-shape'|'condition'|'guard'|'result'|'rejection'|'effects'|'entry'|'permission';
 readonly owner_required:BusinessCoverageOwnerV2;readonly origins:readonly BusinessCoverageOriginV2[];
 readonly state:'producer-required';
}
export interface BusinessCoverageInventoryV2 {
 readonly schema_version:'craft.business-coverage/v2-candidate';readonly model_id:string;readonly source_sha256:string;
 readonly executable_sha256:string;readonly obligations:readonly BusinessCoverageObligationV2[];
 readonly inventory_sha256:string;readonly authority_effect:'none';
}
export interface BusinessOutputRequestV2 {readonly kind:BusinessOutputKindV2;readonly requiredness:'required'|'optional'}
export interface BusinessOutputPlanV2 {
 readonly schema_version:'craft.business-output/v2-candidate';readonly mode:'code-only';
 readonly outputs:readonly Readonly<BusinessOutputRequestV2&{state:'pending-producer'|'unsupported-optional'}>[];readonly authority_effect:'none';
}
export type BusinessOutputStateV2='not-requested'|'pending-producer'|'produced'|'unsupported-required'|'unsupported-optional'|'failed-required'|'failed-optional'|'stale';
export interface BusinessProducedArtifactV2 {readonly path:string;readonly sha256:string;readonly bytes:number;readonly checked_owner_sha256:string;readonly producer_sha256:string}
export type BusinessOutputResultRowV2=
 |Readonly<BusinessOutputRequestV2&{state:'produced';artifact:BusinessProducedArtifactV2}>
 |Readonly<{kind:BusinessOutputKindV2;requiredness:'required';state:'pending-producer'|'unsupported-required'|'failed-required'|'stale';artifact:null}>
 |Readonly<{kind:BusinessOutputKindV2;requiredness:'optional';state:'not-requested'|'pending-producer'|'unsupported-optional'|'failed-optional'|'stale';artifact:null}>;
export interface BusinessOutputResultV2 {readonly schema_version:'craft.business-output-result/v2-candidate';readonly rows:readonly BusinessOutputResultRowV2[];readonly authority_effect:'none'}
export type BusinessSupportEvidenceV2=
 |Readonly<{stage:'declared';contract_ref:string}>
 |Readonly<{stage:'generated';artifact_sha256:string;producer_sha256:string}>
 |Readonly<{stage:'native-observed';subject_sha256:string;producer_sha256:string;receipt_sha256:string}>
 |Readonly<{stage:'installed-tested';candidate_sha256:string;runner_sha256:string;receipt_sha256:string}>;
export interface BusinessSupportCellV2 {
 readonly schema_version:'craft.business-support-cell/v2-candidate';readonly cell_id:string;
 readonly source_contract:'alchlang.business-spec/v2-candidate';readonly recipe:'direct-entity-bool-operation/v2-candidate';
 readonly descriptor:'node-http-entry-u0-v4';readonly abi:'craft.u0.pure-submission/v1-candidate';
 readonly entry_access:'public';readonly effects:'none';readonly evidence:readonly BusinessSupportEvidenceV2[];readonly authority_effect:'none';
}
