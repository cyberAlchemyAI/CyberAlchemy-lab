import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {beforeAll, describe, expect, it} from "vitest";

import {
  computeBindingSha256,
  evaluateRuleRelations,
  sha256Bytes,
} from "./evaluate-rule-relations.js";

type JsonObject = Record<string, any>;
const root = process.cwd();
const bindingPath = "projects/domainspec-v2/impl/architecture-conformance/" +
  "acceptance/rule/wp-rmt-002/relations/rule-relation-binding.json";
let bindingRaw = "";
let rawInputs: Record<string, string> = {};

beforeAll(async () => {
  bindingRaw = await readFile(resolve(root, bindingPath), "utf8");
  const binding = JSON.parse(bindingRaw) as JsonObject;
  rawInputs = Object.fromEntries(await Promise.all(binding.sources.map(
    async ({role, path}: JsonObject) => [
      role, await readFile(resolve(root, path), "utf8"),
    ])));
});

const rebound = (role: string, raw: string) => {
  const binding = JSON.parse(bindingRaw) as JsonObject;
  const source = binding.sources.find((entry: JsonObject) => entry.role === role);
  source.sha256 = sha256Bytes(raw);
  source.size_bytes = Buffer.byteLength(raw, "utf8");
  binding.binding_sha256 = computeBindingSha256(binding);
  return {binding_raw: `${JSON.stringify(binding, null, 2)}\n`,
    raw_inputs: {...rawInputs, [role]: raw}};
};

describe("RMT-RULE-008 exact Rule relation blueprints", () => {
  it("preserves Rule-to-guard and factory-to-Rule directions without materializing edges", () => {
    const proof = evaluateRuleRelations({binding_raw: bindingRaw, raw_inputs: rawInputs});
    expect(proof).toMatchObject({
      result: "pass",
      evidence_mode: "blueprint",
      relation_contract_count: 2,
      materialized_relation_count: 0,
      unmapped_domain_relations: ["mirrors"],
      rule_guard_direction_preserved: true,
      factory_validation_direction_preserved: true,
      no_self_authored_authority: true,
      authority_effect: "none",
    });
    expect(proof.relations).toEqual([
      expect.objectContaining({
        contract_id: "rule/enforces-to-guards",
        architecture_relation_id: "architecture.guards",
        source_types: ["architecture.RuleImplementation"],
        target_types: ["architecture.OperationImplementation",
          "architecture.StateMachineImplementation"],
        assertion_owner_mapping: "source Rule candidate",
        cycle_policy: "acyclic",
        materialized: false,
      }),
      expect.objectContaining({
        contract_id: "rule/factory-validation",
        architecture_relation_id: "architecture.validated_by",
        source_types: ["architecture.ValueObjectFactoryProvider",
          "architecture.EntityFactoryProvider"],
        target_types: ["architecture.RuleImplementation"],
        assertion_owner_mapping: "source factory candidate",
        materialized: false,
      }),
    ]);
  });

  it("kills all four REL-A controls with singleton diagnostics and non-noop proof", () => {
    const proof = evaluateRuleRelations({binding_raw: bindingRaw, raw_inputs: rawInputs});
    expect(proof.hostile_controls.map(({hostile_id, observed_codes,
      semantic_non_noop}) => ({hostile_id, observed_codes, semantic_non_noop})))
      .toEqual([
        {hostile_id: "rule/relation-owner-evidence-stale",
          observed_codes: ["RMT_RELATION_OWNER_EVIDENCE_STALE"],
          semantic_non_noop: true},
        {hostile_id: "rule/relation-source-endpoint-mismatch",
          observed_codes: ["RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"],
          semantic_non_noop: true},
        {hostile_id: "rule/relation-target-endpoint-mismatch",
          observed_codes: ["RMT_RELATION_TARGET_ENDPOINT_MISMATCH"],
          semantic_non_noop: true},
        {hostile_id: "rule/materialized-without-exact-assertion",
          observed_codes: ["RMT_RELATION_ASSERTION_REQUIRED"],
          semantic_non_noop: true},
      ]);
  });

  it("rejects a fully rehashed staged relation-direction drift", () => {
    const plan = JSON.parse(rawInputs.relation_contracts!) as JsonObject;
    const group = plan.type_contracts.find(
      ({owner_swu: owner}: JsonObject) => owner === "RMT-RULE-008");
    group.contracts[0].source_types = ["architecture.OperationImplementation"];
    const changed = rebound("relation_contracts", `${JSON.stringify(plan, null, 2)}\n`);
    expect(() => evaluateRuleRelations(changed)).toThrowError(
      "RMT_RULE_RELATION_CONTRACT_DRIFT");
  });
});
