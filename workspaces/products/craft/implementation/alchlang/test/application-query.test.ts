import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { lowerApplicationDomain, assertApplicationDomainCurrent } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections, assertApplicationRuleProjectionCurrent } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { testTypeScript } from "./toolchain.js";

const query = `query FindEligibleOrder:
  source candidate Order
  output optional<Order>
  where EligibleOrder
  bind order <- candidate
`;
function fixture(suffix = query) {
  const f = executableFixture(); const source = f.source + suffix;
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) },
    declarations: { ...f.bindings.declarations, FindEligibleOrder: { ontology: "FIXTURE-FIND-ELIGIBLE", meaning: "Find at most one order satisfying the explicit eligibility Rule." } } };
  return { ...f, source, bindings };
}
const lower = (f: ReturnType<typeof fixture>) => lowerApplicationDomain(f.source, f.bindings, f.sources);
function interpret(f: ReturnType<typeof fixture>) {
  return { ...f.interpretation, formation_sha256: digest(json(lower(f))) };
}
function project(f: ReturnType<typeof fixture>) {
  return lowerApplicationRuleProjections(f.source, f.bindings, f.sources, interpret(f));
}

test("Query preserves Rule identity, explicit argument binding and optional versus list result shape", () => {
  const f = fixture(); const result = lower(f); const shape = result.queryShapes.queries[0]!;
  assert.equal(shape.rule_ref, "commerce:eligible-order");
  assert.deepEqual(shape.source, { parameter: "candidate", selector: "commerce:order" });
  assert.deepEqual(shape.output, { kind: "optional", element: { kind: "named", selector: "commerce:order" } });
  assert.deepEqual((shape.bindings as any[])[0].value, { op: "path", root: "candidate", properties: [] });
  assert.equal(result.queryShapes.executable, false);
  assert.equal(JSON.parse(result.projectFiles["specs/commerce/edges/find-eligible-order-reads-order.json"]!).relationship, "reads");
  assert.equal(Object.hasOwn(JSON.parse(result.projectFiles["specs/commerce/nodes/find-eligible-order.json"]!).body, "typed_contract"), false);
  const many = lower(fixture(query.replace("optional<Order>", "list<Order>")));
  assert.deepEqual(many.queryShapes.queries[0]!.output, { kind: "list", element: { kind: "named", selector: "commerce:order" } });
  assert.notEqual(result.files["query-shapes.json"], many.files["query-shapes.json"]);
  assert.ok(Object.hasOwn(result.trace.formed_files, "query-shapes.json"));
  const changed = structuredClone(result); changed.files["query-shapes.json"] += " ";
  assert.throws(() => assertApplicationDomainCurrent(f.source, f.bindings, f.sources, changed), /APPLICATION_FORMATION_STALE/);
});

test("Query rejects inline predicates, unresolved roots, wrong result roles and ambiguous binding identities", () => {
  for (const [before, after, code] of [
    ["where EligibleOrder", "where candidate.accepted == true", "APPLICATION_QUERY"],
    ["where EligibleOrder", "where EligibleClaim", "APPLICATION_QUERY_RULE"],
    ["source candidate Order", "source candidate SubmitOrder", "APPLICATION_QUERY_SOURCE"],
    ["output optional<Order>", "output Order", "APPLICATION_QUERY_OUTPUT"],
    ["bind order <- candidate", "bind order <- unknown", "APPLICATION_QUERY_BINDING"],
    ["bind order <- candidate", "bind order <- candidate.missing", "APPLICATION_QUERY_BINDING"],
    ["bind order <- candidate", "bind order <- candidate.id.field", "APPLICATION_QUERY_BINDING"],
    ["bind order <- candidate", "bind order <- loadOrder()", "APPLICATION_QUERY"],
    ["source candidate Order", "source candidate Order\n  input candidate Order", "APPLICATION_QUERY"],
    ["bind order <- candidate", "bind order <- candidate\n  bind order <- candidate", "APPLICATION_QUERY"],
    ["bind order <- candidate", "bind orderValue <- candidate\n  bind order_value <- candidate", "APPLICATION_SYMBOL_COLLISION"],
  ]) assert.throws(() => lower(fixture(query.replace(before!, after!))), new RegExp(code!));
});

test("Query projection checks Rule arguments before result realization", () => {
  const f = fixture(query.replace("bind order <- candidate", "bind identity <- candidate.id"));
  const result = lower(f);
  assert.deepEqual((result.queryShapes.queries[0]!.bindings as any[])[0].value, { op: "path", root: "candidate", properties: ["FIXTURE-ORDER#id"] });
  assert.throws(() => project(f), /APPLICATION_QUERY_ARGUMENTS/);
  assert.throws(() => project(fixture(query.replace("bind order <- candidate", "bind order <- candidate.id"))), /APPLICATION_QUERY_ARGUMENT_TYPE/);
  const optional = project(fixture());
  assert.equal(JSON.parse(optional.projectFiles["specs/commerce/nodes/find-eligible-order.json"]!).body.typed_contract.result_cardinality, "optional");
});

test("list Query derives its filter from the exact declared Rule and binds its trace", () => {
  const f = fixture(query.replace("optional<Order>", "list<Order>"));
  const result = project(f);
  const target = "specs/commerce/nodes/find-eligible-order.json";
  const contract = JSON.parse(result.projectFiles[target]!).body.typed_contract;
  assert.deepEqual(contract.filter, { op: "eq", left: { kind: "field", name: "accepted" }, right: { kind: "literal", type: "Bool", value: true } });
  assert.deepEqual(contract.projection, ["id", "accepted"]);
  assert.equal(contract.limit, null);
  assert.equal(contract.order_by, null);
  assert.equal(result.trace.query_projections[0]!.rule_sha256, digest(result.projectFiles["specs/commerce/nodes/eligible-order.json"]!));
  assertApplicationRuleProjectionCurrent(f.source, f.bindings, f.sources, interpret(f), result);
  const changed = structuredClone(result);
  const node = JSON.parse(changed.projectFiles[target]!); node.body.typed_contract.filter = null;
  changed.projectFiles[target] = json(node);
  changed.trace.project_files[target] = digest(changed.projectFiles[target]!);
  changed.trace.query_projections[0]!.target_sha256 = digest(changed.projectFiles[target]!);
  assert.throws(() => assertApplicationRuleProjectionCurrent(f.source, f.bindings, f.sources, interpret(f), changed), /RULE_PROJECTION_STALE/);
});

test("scalar Rule bindings project source fields and explicit inputs without inventing paths", () => {
  const base = query.replace("optional<Order>", "list<Order>").replace("where EligibleOrder", "where IdentityValid").replace("bind order <- candidate", "bind identity <- candidate.id");
  const result = project(fixture(base));
  const filter = JSON.parse(result.projectFiles["specs/commerce/nodes/find-eligible-order.json"]!).body.typed_contract.filter;
  assert.deepEqual(filter, { op: "eq", left: { kind: "field", name: "id" }, right: { kind: "field", name: "id" } });
  const input = project(fixture(base.replace("bind identity <- candidate.id", "input requested UInt64\n  bind identity <- requested")));
  assert.deepEqual(JSON.parse(input.projectFiles["specs/commerce/nodes/find-eligible-order.json"]!).body.typed_contract.filter.left, { kind: "parameter", name: "requested" });
  const nested = fixture(base.replace("bind identity <- candidate.id", "input requested Order\n  bind identity <- requested.id"));
  assert.throws(() => project(nested), /APPLICATION_QUERY_FILTER_UNSUPPORTED/);
});

for (const cardinality of ["list", "optional"] as const) test(`public compiler executes Rule-filtered ${cardinality} Query for zero, one and multiple matches`, async t => {
  const compiler = await loadDomainSpecCompiler(); const f = fixture(query.replace("optional<Order>", `${cardinality}<Order>`));
  const interpretation = interpret(f); const projection = project(f);
  const execution = { ...f.execution, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, interpretation, execution, compiler);
  const temp = mkdtempSync(path.join(tmpdir(), "alch-query-")); t.after(() => rmSync(temp, { recursive: true, force: true }));
  const write = (dir: string, files: Record<string, string>) => { for (const [relative, bytes] of Object.entries(files)) {
    const target = path.join(dir, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  } };
  const sourceRoot = path.join(temp, "source"); write(sourceRoot, candidate.projectFiles);
  const result = compileApplicationExecutable(candidate, compiler.compileProject(sourceRoot).graph, compiler);
  const generated = path.join(temp, "generated"); write(generated, Object.fromEntries(result.view.artifacts.map(a => [a.relative_path, a.content])));
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
    "--rootDir", generated, "--outDir", path.join(temp, "js"), ...result.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const module = result.view.artifacts.find(a => a.relative_path.endsWith("/queries/find-eligible-order.ts")); assert.ok(module);
  const find = createRequire(import.meta.url)(path.join(temp, "js", module.relative_path.replace(/\.ts$/, ".js"))).queryFindEligibleOrder;
  const rows = [{ id: "18446744073709551615", accepted: true }, { id: "2", accepted: false }, { id: "3", accepted: true }];
  assert.deepEqual(find([], {}), cardinality === "list" ? [] : null);
  assert.deepEqual(find([rows[1]], {}), cardinality === "list" ? [] : null);
  const one = { id: 18446744073709551615n, accepted: true };
  assert.deepEqual(find([rows[0]], {}), cardinality === "list" ? [one] : one);
  assert.ok(Object.isFrozen(find([rows[0]], {})));
  if (cardinality === "list") {
    const found = find(rows, {});
    assert.deepEqual(found, [one, { id: 3n, accepted: true }]);
    assert.ok(Object.isFrozen(found)); assert.ok(Object.isFrozen(found[0]));
  } else {
    assert.throws(() => find(rows, {}), /QUERY_CARDINALITY/);
    assert.throws(() => find([rows[0], rows[0]], {}), /QUERY_CARDINALITY/);
    assert.equal(find.descriptor.protocol_id, "typescript.bound-query/v2-candidate");
    assert.equal(find.descriptor.cardinality_extension.contract.optional_many, "QUERY_CARDINALITY");
    assert.deepEqual(find.descriptor.failures, ["QUERY_INPUT", "QUERY_CARDINALITY"]);
  }
  assert.equal(rows[0]!.id, "18446744073709551615");
  assert.throws(() => find([{ id: "-1", accepted: true }], {}));
  assert.throws(() => find([{ id: "1", accepted: "true" }], {}));
  assert.throws(() => find(rows, { hidden: true }));
});
