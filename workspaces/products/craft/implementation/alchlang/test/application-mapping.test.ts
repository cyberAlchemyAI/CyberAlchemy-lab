import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { testTypeScript } from "./toolchain.js";

const mapping = `mapping SelectOrder:
  input order Order
  input accepted Bool
  target Order
  total true
  field id <- order.id
  field accepted <- accepted
`;
function fixture(suffix = mapping) {
  const f = executableFixture(); const source = f.source + suffix;
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) },
    declarations: { ...f.bindings.declarations, SelectOrder: { ontology: "FIXTURE-SELECT-ORDER", meaning: "Project identity and explicitly supplied acceptance." } } };
  return { ...f, source, bindings };
}
const lower = (f: ReturnType<typeof fixture>) => lowerApplicationDomain(f.source, f.bindings, f.sources);

test("Mapping retains multiple explicit inputs and exact typed paths without inferred calculations", () => {
  const f = fixture(); const result = lower(f);
  const body = JSON.parse(result.projectFiles["specs/commerce/nodes/select-order.json"]!).body;
  assert.deepEqual(body.typed_contract.inputs, [{ name: "order", type: { kind: "named", selector: "commerce:order" } }, { name: "accepted", type: { kind: "scalar", name: "Bool" } }]);
  assert.deepEqual(body.typed_contract.fields, [
    { target: "id", value: { op: "path", root: "order", properties: ["FIXTURE-ORDER#id"] }, default: null },
    { target: "accepted", value: { op: "path", root: "accepted", properties: [] }, default: null },
  ]);
  const edge = JSON.parse(result.projectFiles["specs/commerce/edges/select-order-maps-order.json"]!);
  assert.equal(edge.relationship, "maps"); assert.equal(edge.target_node_id, "order");
  assert.equal(result.trace.declarations.find(d => d.source_id === "SelectOrder")!.return_semantics, "field-projection-not-construction");
});

test("Mapping rejects wrong types, missing fields, hidden calls and ambiguous input names", () => {
  for (const [before, after, code] of [
    ["input accepted Bool", "input accepted String", "APPLICATION_MAPPING_TYPE"],
    ["order.id", "order.missing", "APPLICATION_MAPPING_PATH"],
    ["order.id", "missing.id", "APPLICATION_MAPPING_INPUT"],
    ["order.id", "calculateOrderId(order)", "APPLICATION_MAPPING"],
    ["field id <- order.id", "field other <- order.id", "APPLICATION_MAPPING_TARGET"],
    ["  field accepted <- accepted\n", "", "APPLICATION_MAPPING_TOTAL"],
    ["target Order", "target SubmitOrder", "APPLICATION_MAPPING_TARGET"],
    ["total true", "total true\n  total false", "APPLICATION_MAPPING"],
    ["input order Order", "input order Order\n  input order Bool", "APPLICATION_MAPPING"],
    ["input accepted Bool", "input accepted Bool\n  input orderValue Bool\n  input order_value Bool", "APPLICATION_SYMBOL_COLLISION"],
  ]) assert.throws(() => lower(fixture(mapping.replace(before!, after!))), new RegExp(code!));
  const partial = lower(fixture(mapping.replace("total true", "total false").replace("  field accepted <- accepted\n", "")));
  assert.equal(JSON.parse(partial.projectFiles["specs/commerce/nodes/select-order.json"]!).body.typed_contract.total, false);
});

test("identity-reference Mapping exposes only the identity, never the Entity snapshot", () => {
  const reference = mapping.replace("input order Order", "input order -> Order.id");
  const result = lower(fixture(reference));
  const contract = JSON.parse(result.projectFiles["specs/commerce/nodes/select-order.json"]!).body.typed_contract;
  assert.deepEqual(contract.inputs[0].type, { kind: "reference", selector: "commerce:order", projection: ["id"] });
  assert.deepEqual(contract.fields[0].value.properties, ["FIXTURE-ORDER#id"]);
  assert.throws(() => lower(fixture(reference.replace("field accepted <- accepted", "field accepted <- order.accepted"))), /APPLICATION_MAPPING_PATH/);
  assert.throws(() => lower(fixture(reference.replace("field id <- order.id", "field id <- order.id.id"))), /APPLICATION_MAPPING_PATH/);
  assert.throws(() => lower(fixture(reference.replace("field id <- order.id", "field id <- order"))), /APPLICATION_MAPPING_TYPE/);
});

for (const identityOnly of [false, true]) test(`public compiler emits a pure native multi-input Mapping (${identityOnly ? "identity reference" : "Entity value"})`, async t => {
  const compiler = await loadDomainSpecCompiler(); const f = fixture(identityOnly ? mapping.replace("input order Order", "input order -> Order.id") : mapping);
  if (identityOnly) {
    f.source += `event OrderSubmitted:
  event-type order-submitted
  version 1
  occurrence-id eventId String
  occurred-at required
  orderId -> Order.id
`;
    f.bindings.source_sha256 = digest(f.source); f.bindings.formal.source_sha256 = digest(f.source);
    Object.assign(f.bindings.declarations, { OrderSubmitted: { ontology: "FIXTURE-ORDER-SUBMITTED", meaning: "An occurrence carrying only Order identity." } });
  }
  const formation = lower(f);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, interpretation);
  const execution = { ...f.execution, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, interpretation, execution, compiler);
  const temp = mkdtempSync(path.join(tmpdir(), "alch-mapping-")); t.after(() => rmSync(temp, { recursive: true, force: true }));
  const write = (dir: string, files: Record<string, string>) => { for (const [relative, bytes] of Object.entries(files)) {
    const target = path.join(dir, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  } };
  const sourceRoot = path.join(temp, "source"); write(sourceRoot, candidate.projectFiles);
  const result = compileApplicationExecutable(candidate, compiler.compileProject(sourceRoot).graph, compiler);
  const generated = path.join(temp, "generated"); write(generated, Object.fromEntries(result.view.artifacts.map(a => [a.relative_path, a.content])));
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
    "--rootDir", generated, "--outDir", path.join(temp, "js"), ...result.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const module = result.view.artifacts.find(a => a.relative_path.endsWith("/mappings/select-order.ts")); assert.ok(module);
  const map = createRequire(import.meta.url)(path.join(temp, "js", module.relative_path.replace(/\.ts$/, ".js"))).mappingSelectOrder;
  const input = { order: identityOnly ? "18446744073709551615" : { id: "18446744073709551615", accepted: false }, accepted: true };
  const before = structuredClone(input);
  assert.deepEqual(map(input), { id: 18446744073709551615n, accepted: true });
  assert.deepEqual(input, before);
  if (identityOnly) {
    const eventModule = result.view.artifacts.find(a => a.relative_path.endsWith("/events/order-submitted.ts")); assert.ok(eventModule);
    const make = createRequire(import.meta.url)(path.join(temp, "js", eventModule.relative_path.replace(/\.ts$/, ".js"))).eventOrderSubmitted;
    const event = make({ occurrence: { "event-id": "event-1" }, occurredAt: "fixture-time", payload: { "order-id": "18446744073709551615" } });
    assert.deepEqual(map({ order: event.payload["order-id"], accepted: true }), { id: 18446744073709551615n, accepted: true });
    assert.equal(typeof event.payload["order-id"], "bigint");
    assert.throws(() => map({ ...input, order: { id: "1", accepted: true } }));
    assert.throws(() => map({ ...input, order: "-1" }));
    assert.throws(() => map({ ...input, order: "18446744073709551616" }));
  }
  assert.ok(Object.isFrozen(map(input)));
  assert.throws(() => map({ ...input, accepted: "true" }));
  assert.throws(() => map({ order: input.order }));
  assert.throws(() => map({ ...input, hidden: true }));
  assert.equal(map.descriptor.effect_contract, "pure-explicit-values");
  assert.equal(map.descriptor.return_semantics, "field-projection-not-construction");
});
