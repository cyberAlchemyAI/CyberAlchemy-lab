import assert from "node:assert/strict";
import test from "node:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { digest, json } from "../src/domainspec-profile.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { parseDomainSource } from "../src/parser.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";

function fixture(mutate = (source: string) => source) {
  const base = executableFixture();
  const suffix = `event OrderPlaced:
  event-type order-placed
  version 1
  occurrence-id id String
  occurred-at generated
event ReviewRequested:
  event-type review-requested
  version 1
  occurrence-id id String
  occurred-at generated
operation ReviewOrder:
  input Order
  output Order
  reads Order
  writes Order
query EligibleOrders:
  source candidate Order
  output list<Order>
  where EligibleOrder
  bind order <- candidate
policy DispatchOrder:
  input order Order
  case EligibleOrder -> SubmitOrder
  bind EligibleOrder.order <- order
  default ReviewOrder
  applies SubmitOrder, ReviewOrder
workflow SubmissionFlow:
  scope intra-feature
  input order Order
  requires EligibleOrder
  bind EligibleOrder.order <- order
  steps SubmitOrder, ReviewOrder
state-machine OrderLifecycle:
  subject Order
  input order Order
  initial Draft
  state Draft
  state Submitted
  transition Submit:
    from Draft
    to Submitted
    on OrderPlaced
    guard EligibleOrder
    bind order <- order
    emits ReviewRequested
invariant SubmissionEligibility:
  claim EligibleClaim
EligibleOrder --enforces--> ReviewOrder
`;
  const source = mutate(base.source + suffix);
  const bindings = { ...base.bindings, source_sha256: digest(source), formal: { ...base.bindings.formal, source_sha256: digest(source) }, declarations: {
    ...base.bindings.declarations,
    OrderPlaced: { ontology: "FIXTURE-ORDER-PLACED", meaning: "Synthetic trigger Event." },
    ReviewRequested: { ontology: "FIXTURE-REVIEW-REQUESTED", meaning: "Synthetic result Event." },
    ReviewOrder: { ontology: "FIXTURE-REVIEW-ORDER", meaning: "Request review.", failure_continuation: "return-review-error" },
    EligibleOrders: { ontology: "FIXTURE-ELIGIBLE-ORDERS", meaning: "Find eligible orders." },
    DispatchOrder: { ontology: "FIXTURE-DISPATCH-ORDER", meaning: "Select submission or review." },
    SubmissionFlow: { ontology: "FIXTURE-SUBMISSION-FLOW", meaning: "Coordinate guarded submission." },
    OrderLifecycle: { ontology: "FIXTURE-ORDER-LIFECYCLE", meaning: "Track submission state." },
  } };
  const formation = lowerApplicationDomain(source, bindings, base.sources);
  const interpretation = { ...base.interpretation, formation_sha256: digest(json(formation)) };
  return { source, bindings, sources: base.sources, interpretation };
}

test("all formal consumers preserve declared Rule or claim identity without proposition duplication", async t => {
  const f = fixture(); const projected = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, f.interpretation);
  const consumers = projected.trace.formal_consumers as any[];
  assert.deepEqual([...new Set(consumers.map(item => item.consumer_kind))].sort(), ["Invariant", "Operation", "Policy", "Query", "State Machine", "Workflow"]);
  assert.equal(consumers.find(item => item.consumer_kind === "Invariant").claim_ref, "EligibleClaim");
  assert.equal(consumers.find(item => item.consumer_kind === "Workflow").binding, "typed-exact-arguments-plus-guarded-steps");
  assert.deepEqual(consumers.find(item => item.consumer_kind === "Workflow").step_rules, ["commerce:eligible-order"]);

  const policy = JSON.parse(projected.projectFiles["specs/commerce/nodes/dispatch-order.json"]!).body.typed_contract;
  assert.equal(policy.schema_version, "domainspec.typed-policy/v2");
  assert.deepEqual(policy.cases[0].rule.arguments, [{ parameter: "order", value: { op: "path", root: "order", properties: [] } }]);
  const machine = JSON.parse(projected.projectFiles["specs/commerce/nodes/order-lifecycle.json"]!).body.typed_contract;
  assert.equal(machine.schema_version, "domainspec.typed-state-machine/v1");
  assert.equal(machine.transitions[0].trigger_event_ref, "commerce:order-placed");
  assert.equal(machine.transitions[0].output_intents[0].event_ref, "commerce:review-requested");
  assert.equal(machine.transitions[0].guard.selector, "commerce:eligible-order");
  const feature = JSON.parse(projected.projectFiles["specs/commerce/feature.json"]!);
  assert.ok(feature.edges.includes("order-placed-transitions-order-lifecycle"));
  assert.ok(!feature.edges.includes("review-requested-transitions-order-lifecycle"));

  const compiler = await loadDomainSpecCompiler(); const root = mkdtempSync(path.join(tmpdir(), "alch-c03-consumers-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const [relative, bytes] of Object.entries(projected.projectFiles)) {
    const target = path.join(root, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  }
  assert.doesNotThrow(() => compiler.compileProject(root));
});

test("formal consumers reject missing, mistyped and inline condition bindings", () => {
  for (const [before, after, code] of [
    ["bind EligibleOrder.order <- order", "bind EligibleOrder.missing <- order", "FORMAL_CONSUMER_ARGUMENTS"],
    ["input order Order\n  case EligibleOrder", "input order UInt64\n  case EligibleOrder", "FORMAL_CONSUMER_ARGUMENT_TYPE"],
    ["bind order <- order\n    emits ReviewRequested", "bind missing <- order\n    emits ReviewRequested", "FORMAL_CONSUMER_ARGUMENTS"],
  ]) {
    const f = fixture(source => source.replace(before!, after!));
    assert.throws(() => lowerApplicationRuleProjections(f.source, f.bindings, f.sources, f.interpretation), new RegExp(code!));
  }
  const prefix = 'domain contract "Contract"\nprofile application-v1\nowner fixture-owner\n';
  assert.throws(() => parseDomainSource(prefix + "guard order.total > 0\n"), /GUARD_RULE_REFERENCE/);
  assert.throws(() => parseDomainSource(prefix + "policy P:\n  case order.total > 0 -> SubmitOrder\n  default RejectOrder\n"), /POLICY_RULE_REFERENCE/);
  assert.throws(() => parseDomainSource(prefix + "workflow W:\n  scope intra-feature\n  guard order.total > 0\n  steps A, B\n"), /GUARD_RULE_REFERENCE/);
});
