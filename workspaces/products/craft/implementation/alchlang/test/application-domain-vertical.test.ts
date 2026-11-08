import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections, assertApplicationRuleProjectionCurrent } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { testTypeScript } from "./toolchain.js";

/** Synthetic explicit interpretation and adapter choices, not a generated workflow. */
function fixture() {
  const f = executableFixture();
  const source = f.source
    .replace("  proposition identity = identity", "  constant expected: Identity\n  proposition identity = expected")
    .replace('  ceiling "Synthetic typed identity reflexivity only."', '  ceiling "Synthetic exact identity equality only."')
    .replace("  requires EligibleOrder", "  requires EligibleOrder\n  produces OrderSubmitted") + `query FindOrder:
  input requested UInt64
  source candidate Order
  output optional<Order>
  where IdentityValid
  bind identity <- candidate.id
  bind expected <- requested
mapping PrepareOrder:
  input order Order
  input accepted Bool
  target Order
  total true
  field id <- order.id
  field accepted <- accepted
event OrderSubmitted:
  event-type order-submitted
  version 1
  occurrence-id eventId String
  occurred-at generated
  orderId -> Order.id
interface OrderApi:
  kind external
  version 1.0.0
  compatibility exact
  contract SubmitOrderRequest:
    id UInt64
    accepted Bool
  contract OrderSummary:
    id UInt64
    accepted Bool
  exposes SubmitOrder:
    request SubmitOrderRequest
    result OrderSummary
mapping RequestToOrder:
  input request OrderApi.SubmitOrderRequest
  target Order
  total true
  field id <- request.id
  field accepted <- request.accepted
mapping OrderToSummary:
  input order Order
  target OrderApi.OrderSummary
  total true
  field id <- order.id
  field accepted <- order.accepted
`;
  const publicFields = (ontology: string) => ({ ontology, properties: {
    id: { ontology: ontology + "#id", meaning: "Explicit public identity value." },
    accepted: { ontology: ontology + "#accepted", meaning: "Explicit public acceptance value." },
  } });
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) },
    declarations: { ...f.bindings.declarations,
      IdentityValid: { ontology: "FIXTURE-IDENTITY", meaning: "Compare explicitly supplied identities; factory binds both to the same field." },
      FindOrder: { ontology: "FIXTURE-FIND-ORDER", meaning: "Find at most one order matching the explicit identity." },
      PrepareOrder: { ontology: "FIXTURE-PREPARE-ORDER", meaning: "Project existing identity and explicitly supplied acceptance." },
      OrderSubmitted: { ontology: "FIXTURE-SUBMITTED", meaning: "Synthetic submission occurrence, not transport delivery." },
      RequestToOrder: { ontology: "FIXTURE-REQUEST-MAPPING", meaning: "Explicit public request projection, not construction." },
      OrderToSummary: { ontology: "FIXTURE-RESPONSE-MAPPING", meaning: "Explicit public response projection." },
      OrderApi: { ontology: "FIXTURE-ORDER-API", meaning: "Public contract identity, not endpoint execution.", contracts: {
        SubmitOrderRequest: publicFields("FIXTURE-SUBMIT-REQUEST"), OrderSummary: publicFields("FIXTURE-ORDER-SUMMARY"),
      } },
    } };
  const formation = lowerApplicationDomain(source, bindings, f.sources);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)), rules: { ...f.interpretation.rules,
    IdentityValid: { ...f.interpretation.rules.IdentityValid,
      claim_identity_inputs_digest: formation.trace.declarations.find(d => d.source_id === "IdentityClaim")!.identity_inputs_digest,
      ceiling: "Exact equality of two explicitly supplied UInt64 identities.", constants: { identity: "identity", expected: "expected" } },
  } };
  const projection = lowerApplicationRuleProjections(source, bindings, f.sources, interpretation);
  const execution = { ...f.execution, projection_sha256: digest(json(projection)), selection: { ...f.execution.selection,
    factories: f.execution.selection.factories.map(factory => ({ ...factory, base_validators: [{ rule: "commerce:identity-valid",
      arguments: [{ parameter: "identity", field: "id" }, { parameter: "expected", field: "id" }] }] })),
    operations: f.execution.selection.operations.map(op => ({ ...op,
      events: [{ slot: "commerce:order-submitted", target: "commerce:order-submitted", parameter: "submitted" }] })),
  } };
  return { source, bindings, sources: f.sources, formation, interpretation, projection, execution };
}

test("combined domain projection binds keyed Query, Mapping, Operation and Event without invented graph edges", () => {
  const f = fixture();
  const query = JSON.parse(f.projection.projectFiles["specs/commerce/nodes/find-order.json"]!).body.typed_contract;
  assert.deepEqual(query.filter, { op: "eq", left: { kind: "field", name: "id" }, right: { kind: "parameter", name: "requested" } });
  assert.equal(query.result_cardinality, "optional");
  assertApplicationRuleProjectionCurrent(f.source, f.bindings, f.sources, f.interpretation, f.projection);
  assert.deepEqual(f.projection, lowerApplicationRuleProjections(f.source, f.bindings, f.sources, f.interpretation));
  const edges = Object.entries(f.projection.projectFiles).filter(([p]) => p.includes("/edges/")).map(([,b]) => JSON.parse(b));
  for (const [from, relationship, to] of [["find-order", "reads", "order"], ["prepare-order", "maps", "order"], ["submit-order", "produces", "order-submitted"]]) {
    assert.ok(edges.some(e => e.source_node_id === from && e.relationship === relationship && e.target_node_id === to));
  }
  assert.ok(!edges.some(e => e.source_node_id === "submit-order" && e.target_node_id === "find-order"));
  for (const target of ["find-order", "prepare-order", "order-submitted", "order-api", "request-to-order", "order-to-summary"]) {
    assert.ok(f.projection.trace.project_files[`specs/commerce/nodes/${target}.json`]);
  }
});

test("one compiled project executes keyed reads, explicit mapping and atomic write/Event intents", async t => {
  const f = fixture(), compiler = await loadDomainSpecCompiler();
  const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, f.interpretation, f.execution, compiler);
  const temp = mkdtempSync(path.join(tmpdir(), "alch-domain-vertical-")); t.after(() => rmSync(temp, { recursive: true, force: true }));
  const write = (dir: string, files: Record<string, string>) => { for (const [relative, bytes] of Object.entries(files)) {
    const target = path.join(dir, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  } };
  const root = path.join(temp, "source"); write(root, candidate.projectFiles);
  const built = compileApplicationExecutable(candidate, compiler.compileProject(root).graph, compiler);
  const generated = path.join(temp, "generated"); write(generated, Object.fromEntries(built.view.artifacts.map(a => [a.relative_path, a.content])));
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
    "--rootDir", generated, "--outDir", path.join(temp, "js"), ...built.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const load = (suffix: string, name: string) => {
    const artifact = built.view.artifacts.find(a => a.relative_path.endsWith(suffix)); assert.ok(artifact);
    assert.equal(built.trace.generated_files[artifact.relative_path]!.sha256, digest(artifact.content));
    return createRequire(import.meta.url)(path.join(temp, "js", artifact.relative_path.replace(/\.ts$/, ".js")))[name];
  };
  const find = load("/queries/find-order.ts", "queryFindOrder");
  const map = load("/mappings/prepare-order.ts", "mappingPrepareOrder");
  const submit = load("/operations/submit-order.ts", "operationSubmitOrder");
  const toOrder = load("/mappings/request-to-order.ts", "mappingRequestToOrder");
  const toSummary = load("/mappings/order-to-summary.ts", "mappingOrderToSummary");
  const publicContracts = load("/order-api.ts", "publicContracts");
  const id = "18446744073709551615";
  for (const scenario of ["success", "missing", "duplicate", "guard-rejection", "invalid-event", "commit-rejection", "commit-uncertain"]) {
    const calls: string[] = []; let batch: any;
    const order = { id, accepted: scenario !== "guard-rejection" };
    const rows = scenario === "missing" ? [] : scenario === "duplicate" ? [order, order] : [{ id: "2", accepted: false }, order];
    const before = structuredClone(rows);
    // The caller explicitly supplies the mapping input; this is not generated orchestration.
    const publicInput = { id, accepted: false };
    const mappedInput = toOrder({ request: publicContracts["submit-order-request"].normalize(publicInput) });
    const request = map({ order: mappedInput, accepted: mappedInput.accepted });
    assert.deepEqual(request, { id: BigInt(id), accepted: false });
    const outcome = await submit({ request, submitted: { occurrence: { "event-id": "submission-1" }, payload: { "order-id": scenario === "invalid-event" ? -1n : id } } }, {
      clocks: { "commerce:order-submitted": () => { calls.push("clock"); return "fixture-time"; } },
      store: { begin: async () => { calls.push("begin"); return {
        read: async (read: any) => { calls.push("read"); assert.equal(read.slot, "commerce:order"); assert.equal(read.key, BigInt(id)); return find(rows, { requested: read.key }); },
        commit: async (value: unknown) => { calls.push("commit"); batch = value;
          if (scenario === "commit-uncertain") throw Error("settlement unknown");
          return { status: scenario === "commit-rejection" ? "rejected" : "committed" }; },
        rollback: async () => { calls.push("rollback"); },
      }; } },
    });
    assert.deepEqual(rows, before);
    if (["missing", "duplicate", "guard-rejection", "invalid-event"].includes(scenario)) {
      assert.equal(batch, undefined); assert.deepEqual(calls, ["begin", "read", "rollback"]);
      assert.notEqual(outcome.status, "committed");
      assert.equal(outcome.stage, scenario === "guard-rejection" ? "guard" : scenario === "invalid-event" ? "event" : "read");
    } else {
      assert.deepEqual(calls, ["begin", "read", "clock", "commit"]);
      assert.equal(batch.writes.length, 1); assert.equal(batch.events.length, 1);
      assert.deepEqual(batch.writes[0].value, request);
      assert.equal(batch.events[0].value.payload["order-id"], BigInt(id));
      assert.equal(batch.events[0].value.occurredAt, "fixture-time");
      assert.ok(Object.isFrozen(batch)); assert.ok(Object.isFrozen(batch.events));
      assert.equal(outcome.status, scenario === "success" ? "committed" : scenario === "commit-rejection" ? "rejected" : "indeterminate");
      if (scenario === "success") {
        assert.deepEqual(outcome.value, request);
        const summary = toSummary({ order: outcome.value });
        assert.deepEqual(publicContracts["order-summary"].normalize(summary), request);
        assert.ok(Object.isFrozen(summary)); assert.notEqual(summary, request);
        assert.notEqual(publicContracts["order-summary"].key(summary), publicContracts["submit-order-request"].key(summary));
      }
    }
    assert.deepEqual(publicInput, { id, accepted: false });
    assert.equal(Object.hasOwn(outcome, "published"), false); assert.equal(Object.hasOwn(outcome, "delivered"), false);
  }
  assert.equal(find([{ id, accepted: true }], { requested: "2" }), null);
  assert.throws(() => find([{ id, accepted: true }], { requested: "18446744073709551616" }));
});
