import {createHash} from "node:crypto";

import type {RuleHostileFixtureV1} from
  "../../../../families/pure-boolean-rule/contracts/pure-boolean-rule-contracts.js";
import {
  evaluatePureBooleanRuleProfile,
  PURE_BOOLEAN_RULE_BASELINE,
} from
  "../../../../families/pure-boolean-rule/evaluator/evaluate-pure-boolean-rule.js";
import {applyRuleHostile} from
  "../../../../families/pure-boolean-rule/mutations/apply-rule-hostile.js";

type JsonObject = Record<string, any>;

const expectedRelations = Object.freeze([
  Object.freeze({
    contract_id: "rule/enforces-to-guards",
    domain_surface: "source_of:enforces",
    architecture_relation_id: "architecture.guards",
    translation: "same direction; Rule guards Operation or State Machine",
    source_types: Object.freeze(["architecture.RuleImplementation"]),
    target_types: Object.freeze([
      "architecture.OperationImplementation",
      "architecture.StateMachineImplementation",
    ]),
    assertion_owner_mapping: "source Rule candidate",
    cycle_policy: "acyclic",
  }),
  Object.freeze({
    contract_id: "rule/factory-validation",
    domain_surface: "validated factory guard",
    architecture_relation_id: "architecture.validated_by",
    translation: "factory provider points to Rule; relation is owned by the exact factory assertion candidate",
    source_types: Object.freeze([
      "architecture.ValueObjectFactoryProvider",
      "architecture.EntityFactoryProvider",
    ]),
    target_types: Object.freeze(["architecture.RuleImplementation"]),
    assertion_owner_mapping: "source factory candidate",
    cycle_policy: "not-applicable",
  }),
]);

const hostileCases = Object.freeze([
  Object.freeze({role: "hostile_owner", id: "rule/relation-owner-evidence-stale",
    code: "RMT_RELATION_OWNER_EVIDENCE_STALE"}),
  Object.freeze({role: "hostile_source", id: "rule/relation-source-endpoint-mismatch",
    code: "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"}),
  Object.freeze({role: "hostile_target", id: "rule/relation-target-endpoint-mismatch",
    code: "RMT_RELATION_TARGET_ENDPOINT_MISMATCH"}),
  Object.freeze({role: "hostile_assertion", id: "rule/materialized-without-exact-assertion",
    code: "RMT_RELATION_ASSERTION_REQUIRED"}),
]);

const canonicalValue = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalValue)
  : value !== null && typeof value === "object"
    ? Object.fromEntries(Object.entries(value as JsonObject)
      .sort(([left], [right]) => Buffer.from(left).compare(Buffer.from(right)))
      .map(([key, child]) => [key, canonicalValue(child)]))
    : value;
export const canonicalJson = (value: unknown): string =>
  JSON.stringify(canonicalValue(value));
export const sha256Bytes = (value: string): string =>
  createHash("sha256").update(value).digest("hex");
export const computeBindingSha256 = (binding: JsonObject): string => {
  const {binding_sha256: _ignored, ...body} = binding;
  return sha256Bytes(canonicalJson(body));
};
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};

export const evaluateRuleRelations = (input: Readonly<{
  binding_raw: string;
  raw_inputs: Readonly<Record<string, string>>;
}>) => {
  const binding = JSON.parse(input.binding_raw) as JsonObject;
  if (binding.schema_version !== "RuleWpRmt002RelationBinding/v1" ||
      binding.binding_sha256 !== computeBindingSha256(binding) ||
      binding.evidence_mode !== "blueprint" ||
      binding.authority_effect !== "none") {
    return fail("RMT_RULE_RELATION_BINDING_INVALID");
  }
  if (!Array.isArray(binding.sources) || binding.sources.length !== 6 ||
      Object.keys(input.raw_inputs).length !== 6) {
    return fail("RMT_RULE_RELATION_SOURCE_SET_INVALID");
  }
  for (const source of binding.sources as JsonObject[]) {
    const raw = input.raw_inputs[String(source.role)];
    if (raw === undefined || sha256Bytes(raw) !== source.sha256 ||
        Buffer.byteLength(raw, "utf8") !== source.size_bytes) {
      return fail("RMT_RULE_RELATION_SOURCE_DRIFT");
    }
  }
  const boundRelations = (binding.relations as JsonObject[]).map(
    ({materialized: _ignored, ...relation}) => relation);
  if (canonicalJson(boundRelations) !== canonicalJson(expectedRelations) ||
      canonicalJson(binding.unmapped_domain_relations) !==
      canonicalJson(["mirrors"]) ||
      !(binding.relations as JsonObject[]).every(
        ({materialized}) => materialized === false)) {
    return fail("RMT_RULE_RELATION_BLUEPRINT_DRIFT");
  }
  const relationPlan = JSON.parse(input.raw_inputs.relation_contracts!) as JsonObject;
  const group = (relationPlan.type_contracts as JsonObject[]).find(
    ({owner_swu: owner}) => owner === "RMT-RULE-008");
  if (group === undefined || group.prefix !== "RULE" || group.type !== "Rule" ||
      canonicalJson(group.contracts) !== canonicalJson(expectedRelations) ||
      canonicalJson(group.unmapped_domain_relations) !== canonicalJson(["mirrors"])) {
    return fail("RMT_RULE_RELATION_CONTRACT_DRIFT");
  }
  const dependency = JSON.parse(
    input.raw_inputs.rmt_rule_007_candidate_proof!) as JsonObject;
  if (dependency.swu_id !== "RMT-RULE-007" || dependency.result !== "pass" ||
      dependency.execution_mode !== "candidate-local-fast-lane" ||
      dependency.authority_effect !== "none" ||
      dependency.lifecycle?.task_session_admitted !== false ||
      dependency.lifecycle?.promoted !== false) {
    return fail("RMT_RULE_RELATION_DEPENDENCY_INVALID");
  }
  const controls = hostileCases.map(({role, id, code}) => {
    const fixture = JSON.parse(input.raw_inputs[role]!) as RuleHostileFixtureV1;
    if (fixture.hostile_id !== id || fixture.hostile_class !== "rel-a-evidence") {
      return fail("RMT_RULE_RELATION_HOSTILE_CATALOGUE_DRIFT");
    }
    const baseline = evaluatePureBooleanRuleProfile(PURE_BOOLEAN_RULE_BASELINE);
    const evaluation = evaluatePureBooleanRuleProfile(
      applyRuleHostile(PURE_BOOLEAN_RULE_BASELINE, fixture));
    if (baseline.findings.length !== 0 || evaluation.findings.length !== 1 ||
        evaluation.findings[0]?.code !== code) {
      return fail("RMT_RULE_RELATION_HOSTILE_NOT_KILLED");
    }
    return Object.freeze({
      hostile_id: id,
      observed_codes: Object.freeze([code]),
      status: "killed" as const,
      semantic_non_noop: true,
    });
  });
  const projection = Object.freeze({
    schema_version: "RuleWpRmt002RelationProof/v1" as const,
    result: "pass" as const,
    evidence_mode: "blueprint" as const,
    relation_contract_count: 2,
    materialized_relation_count: 0,
    relations: Object.freeze((binding.relations as JsonObject[]).map(
      (relation) => Object.freeze({...relation}))),
    unmapped_domain_relations: Object.freeze(["mirrors"]),
    hostile_controls: Object.freeze(controls),
    rule_guard_direction_preserved: true,
    factory_validation_direction_preserved: true,
    no_self_authored_authority: true,
    authority_effect: "none" as const,
  });
  return Object.freeze({
    ...projection,
    proof_sha256: sha256Bytes(canonicalJson(projection)),
  });
};
