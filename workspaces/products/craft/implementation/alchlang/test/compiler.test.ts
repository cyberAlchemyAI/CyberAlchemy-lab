import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { compileCarrier } from "../src/index.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const verticalRoot = path.resolve(here, "../../../three-vertical-compilation-campaign/execution/verticals");
const carrierNames = ["customer-credit-release", "inventory-reservation", "production-rollback"];

for (const name of carrierNames) {
  test(`accepted reference carrier compiles generically: ${name}`, async () => {
    const carrier = JSON.parse(await readFile(path.join(verticalRoot, name, "alchlang.domain.json"), "utf8"));
    const first = compileCarrier(carrier);
    const second = compileCarrier(JSON.parse(JSON.stringify(carrier)));
    assert.equal(first.plan_digest, second.plan_digest);
    assert.equal(first.authority_effect, "none");
    assert.match(first.files["domain.tools.ts"], /interface .*Port/);
    assert.doesNotMatch(first.files["domain.tools.ts"], /fetch\(|process\.|child_process|writeFile/);
    assert.ok(first.plan.unsupported_residue.every((item) => item.code === "LEGACY_OPAQUE_PREDICATE"));
  });
}

export function unseenCarrier(): Record<string, unknown> {
  return {
    schema_version: "cav2.alchlang.carrier/v2-candidate",
    identity: { domain_id: "library-loan", title: "Library loan" },
    owners: [{ owner_route: "library-domain-owner" }],
    terms: [
      { term_id: "loan", kind: "entity", meaning: "A bounded book loan." },
      { term_id: "librarian", kind: "actor", meaning: "A loan operator." },
      { term_id: "available", kind: "state", meaning: "Available for loan." },
      { term_id: "borrowed", kind: "state", meaning: "Currently borrowed." }
    ],
    edges: [{ edge_id: "loan-state", type: "occupies", source_ref: "loan", target_ref: "available" }],
    facts: [{ fact_id: "loan-days", type: "integer", required: true, owner_route: "library-domain-owner" }],
    rules: [{ rule_id: "bounded-duration", scope_refs: ["loan"], fact_refs: ["loan-days"], condition: { operator: "lte", operands: [{ node: "fact_ref", ref: "loan-days" }, { node: "literal", value_type: "integer", value: 21 }] }, consequence: "eligible", exception_refs: [], owner_route: "library-domain-owner", source_refs: ["policy:loan-duration"] }],
    events: [{ event_id: "loan-started", subject_refs: ["loan"], payload_facts: ["loan-days"], trigger_refs: ["start-loan"], authority_boundary_ref: "loan-operation", source_refs: [] }],
    states: [{ state_id: "available", subject_ref: "loan" }, { state_id: "borrowed", subject_ref: "loan" }],
    transitions: [{ transition_id: "begin-loan", subject_ref: "loan", from_state_ref: "available", to_state_ref: "borrowed", trigger_ref: "start-loan", guard_rule_refs: ["bounded-duration"], authority_boundary_ref: "loan-operation", resulting_event_refs: ["loan-started"] }],
    actions: [{ action_id: "start-loan", actor_refs: ["librarian"], subject_refs: ["loan"], input_facts: ["loan-days"], precondition_rule_refs: ["bounded-duration"], permission_refs: ["operate-loan"], confirmation_policy_ref: null, outcome_refs: ["loan-started"], authority_boundary_ref: "loan-operation" }],
    permissions: [{ permission_id: "operate-loan", actor_refs: ["librarian"], action_refs: ["start-loan"], target_refs: ["loan"], scope_refs: [], condition: { node: "literal", value_type: "boolean", value: true }, exception_refs: [], confirmation_policy_ref: null, authority_boundary_ref: "loan-operation" }],
    examples: [{ example_id: "standard-loan", kind: "positive", facts: { "loan-days": 14 }, expected_interpretation: "eligible", affected_rule_refs: ["bounded-duration"], boundary_witness_refs: [], source_refs: [] }],
    authority: { authority_effect: "none", boundaries: [{ boundary_id: "loan-operation", owner_route: "library-domain-owner" }] },
    residue: []
  };
}

test("an unseen composition compiles without core changes", () => {
  const result = compileCarrier(unseenCarrier());
  assert.equal(result.plan.model.domain_id, "library-loan");
  assert.equal(result.plan.action_ports[0].id, "start-loan");
  assert.deepEqual(result.plan.unsupported_residue, []);
  assert.match(result.files["domain.tools.ts"], /StartLoanPort/);
  assert.equal(result.plan.type_model[0].fields[0].subject_ref, "loan");
});
