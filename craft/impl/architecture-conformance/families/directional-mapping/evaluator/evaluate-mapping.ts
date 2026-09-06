import type {DirectionalMappingDescriptor, DirectionalMappingObservation, MappingEvaluation, MappingFindingCode, MappingRelationAssertion} from "../contracts/mapping-contracts.js";

type Finding = MappingEvaluation["findings"][number];
const finding = (code: MappingFindingCode, expected: unknown, observed: unknown): Finding => ({code, expected, observed});
const canonical = (value: unknown): string => JSON.stringify(value);
const sameSet = (left: readonly unknown[], right: readonly unknown[]): boolean => {
  const a = left.map(canonical).sort(); const b = right.map(canonical).sort();
  return a.length === new Set(a).size && b.length === new Set(b).size && canonical(a) === canonical(b);
};
const finish = (descriptor_id: string, findings: Finding[]): MappingEvaluation => Object.freeze({
  schema_version:"domainspec.directional-mapping-evaluation/v1", descriptor_id,
  verdict:findings.length === 0 ? "pass" : "reject", findings:Object.freeze(findings), authority_effect:"none",
});

export const evaluateDirectionalMapping = (descriptor: DirectionalMappingDescriptor, observed: DirectionalMappingObservation): MappingEvaluation => {
  const findings: Finding[] = [];
  if (observed.source_contract_id !== descriptor.source_contract_id || observed.target_contract_id !== descriptor.target_contract_id)
    findings.push(finding("RMT_MAP_SOURCE_TARGET_SWAP", [descriptor.source_contract_id, descriptor.target_contract_id], [observed.source_contract_id, observed.target_contract_id]));
  if (observed.direction !== descriptor.direction) findings.push(finding("RMT_MAP_DIRECTION_FLIP", descriptor.direction, observed.direction));
  if (observed.missing_required_fields.length > 0) findings.push(finding("RMT_MAP_MISSING_REQUIRED_FIELD", [], observed.missing_required_fields));
  if (observed.undeclared_extra_fields.length > 0) findings.push(finding("RMT_MAP_UNDECLARED_EXTRA_FIELD", [], observed.undeclared_extra_fields));
  if (!sameSet(descriptor.correspondence, observed.observed_correspondence)) findings.push(finding("RMT_MAP_CORRESPONDENCE_DRIFT", descriptor.correspondence, observed.observed_correspondence));
  if (observed.totality !== descriptor.totality) findings.push(finding("RMT_MAP_TOTALITY_OVERCLAIM", descriptor.totality, observed.totality));
  if (observed.coercions.length > 0) findings.push(finding("RMT_MAP_SILENT_COERCION", [], observed.coercions));
  if (observed.effect_policy !== descriptor.effect_policy || observed.effects.length > 0)
    findings.push(finding("RMT_MAP_EFFECT_POLICY_VIOLATION", {policy:descriptor.effect_policy,effects:[]}, {policy:observed.effect_policy,effects:observed.effects}));
  if (observed.failure_outcome.status !== "failure") findings.push(finding("RMT_MAP_FAILURE_AS_SUCCESS", "failure", observed.failure_outcome.status));
  else if (!observed.failure_outcome.code || observed.failure_outcome.details.length === 0)
    findings.push(finding("RMT_MAP_FAILURE_DETAIL_LOSS", {code:"non-empty",details:"non-empty"}, observed.failure_outcome));
  return finish(descriptor.descriptor_id, findings);
};

const endpoints = (_contractId: MappingRelationAssertion["contract_id"]) => ({source:["architecture.MappingImplementation"],target:["architecture.DataShapeContract"]});
export const evaluateMappingRelation = (assertion: MappingRelationAssertion): MappingEvaluation => {
  const findings: Finding[] = []; const allowed=endpoints(assertion.contract_id);
  if(assertion.owner_evidence_sha256!==assertion.current_owner_evidence_sha256) findings.push(finding("RMT_RELATION_OWNER_EVIDENCE_STALE",assertion.current_owner_evidence_sha256,assertion.owner_evidence_sha256));
  if(!allowed.source.includes(assertion.source_type)) findings.push(finding("RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",allowed.source,assertion.source_type));
  if(!allowed.target.includes(assertion.target_type)) findings.push(finding("RMT_RELATION_TARGET_ENDPOINT_MISMATCH",allowed.target,assertion.target_type));
  if(assertion.mode==="materialized"&&!assertion.exact_assertion_id) findings.push(finding("RMT_RELATION_ASSERTION_REQUIRED","non-empty exact assertion id",assertion.exact_assertion_id));
  return finish(assertion.contract_id, findings);
};
