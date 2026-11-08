import test from "node:test";
import assert from "node:assert/strict";
import { parseDomainSource } from "../src/parser.js";
import type { ApplicationFormalSource } from "../src/formal-claim.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { digest, json } from "../src/domainspec-profile.js";
import type { DomainSpecCompiler } from "../src/domainspec-cli.js";
import { checkApplicationRealizationTypes } from "../src/application-realization-types.js";
import { deriveApplicationRealizationActions, deriveApplicationRealizationCompositions } from "../src/application-realization-actions.js";
import { realizationFixture } from "./fixtures/application-realization-fixture.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { compileApplicationRealizationGraph } from "../src/application-realization-graph.js";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { testTypeScript } from "./toolchain.js";

const block = `realization SubmitOrderExecution:
  operation SubmitOrder
  input request
  read current <- Order key request.id
  guard EligibleOrder(order <- current)
  write Order replace <- request
  result <- request
  atomicity state-and-outbox
  continuation awaited-settlement
`;
const parse = (source: string) => parseDomainSource(source).carrier as unknown as ApplicationFormalSource;
function projectContext(realization: string, extra = "", metadata: Record<string, unknown> = {}) {
  const f = executableFixture(), source = f.source + extra + realization;
  const bindings = { ...f.bindings, declarations: { ...f.bindings.declarations, ...metadata }, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) } };
  const formation = lowerApplicationDomain(source, bindings, f.sources);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)) };
  return {source,bindings,sources:f.sources,interpretation,projection:lowerApplicationRuleProjections(source, bindings, f.sources, interpretation)};
}
function project(realization:string,extra='',metadata:Record<string,unknown>={}){return projectContext(realization,extra,metadata).projection;}

test("realization is separate from Operation and retains explicit stored/request connections", () => {
  const f = executableFixture(), original = parse(f.source), model = parse(f.source + block);
  assert.ok(!Object.hasOwn(original, "realizations"));
  assert.deepEqual(model.declarations, original.declarations);
  assert.deepEqual(model.formal_claims, original.formal_claims);
  const r = model.realizations![0]!;
  assert.equal(r.operation, "SubmitOrder");
  assert.deepEqual(r.reads[0]!.key, ["request", "id"]);
  assert.deepEqual(r.guards[0]!.arguments[0]!.path, ["current"]);
  assert.deepEqual(r.writes[0]!.path, ["request"]);
  assert.equal(r.writes[0]!.mode, "replace");
  assert.deepEqual(r.result, ["request"]);
  assert.ok(r.source_line > 0 && r.reads[0]!.source_line > r.source_line);
  const reversed = block.split("\n").filter(Boolean);
  const reordered = reversed[0] + "\n" + reversed.slice(1).reverse().join("\n") + "\n";
  const eraseLines = (value: unknown) => JSON.parse(JSON.stringify(value, (key, v) => key === "source_line" ? undefined : v));
  assert.deepEqual(eraseLines(parse(f.source + reordered).realizations), eraseLines(model.realizations));
});

test("realization rejects missing choices, invalid roles, coverage, unknown values, duplicates and imperative clauses", () => {
  const source = executableFixture().source;
  const invalid = [
    block.replace("  result <- request\n", ""),
    block.replace("operation SubmitOrder", "operation Order"),
    block.replace("guard EligibleOrder", "guard SubmitOrder"),
    block.replace("order <- current", "order <- missing"),
    block.replace("read current <- Order key request.id", "read request <- Order key request.id"),
    block.replace("request.id", "current.id"),
    block.replace("  write Order replace <- request\n", ""),
    block.replace("  guard EligibleOrder(order <- current)\n", ""),
    block.replace("order <- current", "order <- current, order <- request"),
    block.replace("result <- request", "result <- request.accepted == true"),
    block + "  input another\n",
    block + "  save Order\n",
    block + "  let other = request\n",
    block + "  event Order <- request\n",
    block + block.replace("SubmitOrderExecution", "OtherExecution"),
  ];
  for (const candidate of invalid) assert.throws(() => parse(source + candidate), /APPLICATION_REALIZATION/);
  assert.throws(() => parse((source + block).replace("profile application-v1", "profile legacy-sfol-v1")), /ALCH_PROFILE_REQUIRED/);
});

test("declared Queries and Mappings keep named inputs and identities, never implicit calls", () => {
  const source = executableFixture().source + `query FindOrder:
  input id UInt64
  source candidate Order
  output optional<Order>
  where EligibleOrder
  bind order <- candidate
mapping CopyOrder:
  input value Order
  target Order
  total true
  field id <- value.id
  field accepted <- value.accepted
`;
  const realization = block.replace("read current <- Order key request.id", "query current <- FindOrder(id <- request.id)")
    .replace("  result <- request", "  map copied <- CopyOrder(value <- request)\n  result <- copied");
  const result = parse(source + realization).realizations![0]!;
  assert.equal(result.queries[0]!.query, "FindOrder");
  assert.equal(result.mappings[0]!.mapping, "CopyOrder");
  assert.deepEqual(result.queries[0]!.arguments[0]!.path, ["request", "id"]);
  for (const changed of [
    realization.replace("FindOrder(id", "CopyOrder(id"),
    realization.replace("CopyOrder(value", "FindOrder(value"),
    realization.replace("value <- request", "wrong <- request"),
    realization.replace("value <- request", "value <- copied"),
    realization.replace("id <- request.id", "id <- calculate(request.id)"),
  ]) assert.throws(() => parse(source + changed), /APPLICATION_REALIZATION/);
  // Parsing does not unwrap optional Query results; type/cardinality lowering is still required.
  assert.equal(result.guards[0]!.arguments[0]!.path[0], "current");
});

test("authored realization cannot be overridden by a legacy execution selection", () => {
  const f = executableFixture(), source = f.source + block;
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) } };
  const formation = lowerApplicationDomain(source, bindings, f.sources);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(source, bindings, f.sources, interpretation);
  assert.throws(() => prepareApplicationExecutable(source, bindings, f.sources, interpretation,
    { ...f.execution, projection_sha256: digest(json(projection)) }, {} as DomainSpecCompiler), /APPLICATION_EXECUTION_SCHEMA/);
});

test("typed realization binds source fields to exact ontology paths and rejects wrong key, guard, write and result types", () => {
  const checked = checkApplicationRealizationTypes(project(block))[0]!;
  assert.deepEqual(checked.reads[0]!.key.value, { op: "path", root: "request", properties: ["FIXTURE-ORDER#id"] });
  assert.deepEqual(checked.reads[0]!.key.type, { kind: "scalar", name: "UInt64" });
  assert.equal(checked.guards[0]!.arguments[0]!.value.root, "current");
  assert.equal(checked.writes[0]!.value.root, "request");
  assert.equal(checked.execution, "not-performed");
  const node = (id: string) => checked.graph.nodes.find(n => n.id === id)!;
  assert.deepEqual(node("read:current").depends_on, ["input:request", "transaction"]);
  assert.ok(node("write:commerce:order").depends_on.includes("guard:commerce:eligible-order"));
  assert.ok(node("commit").depends_on.includes("result"));
  assert.equal(checked.graph.layers.flat().length, checked.graph.nodes.length);
  assert.ok(Object.isFrozen(checked.graph) && Object.isFrozen(checked.graph.nodes));
  const missing = structuredClone(checked);
  missing.reads[0]!.key.value.root = "missing";
  assert.throws(() => compileApplicationRealizationGraph(missing), /APPLICATION_REALIZATION_GRAPH/);
  const cyclic = structuredClone(checked);
  cyclic.reads[0]!.key.value.root = "current";
  assert.throws(() => compileApplicationRealizationGraph(cyclic), /APPLICATION_REALIZATION_GRAPH/);
  for (const changed of [
    block.replace("key request.id", "key request.accepted"),
    block.replace("key request.id", "key request.unknown"),
    block.replace("key request.id", "key request.id.nested"),
    block.replace("order <- current", "order <- current.id"),
    block.replace("order <- current", "wrong <- current"),
    block.replace("write Order replace <- request", "write Order replace <- request.id"),
    block.replace("result <- request", "result <- request.accepted"),
  ]) assert.throws(() => checkApplicationRealizationTypes(project(changed)), /APPLICATION_REALIZATION_TYPE/);
});

test("typed Query results retain cardinality and Mapping inputs cannot coerce them", () => {
  const extra = `query FindOrder:
  input id UInt64
  source candidate Order
  output optional<Order>
  where EligibleOrder
  bind order <- candidate
mapping CopyOrder:
  input value Order
  target Order
  total true
  field id <- value.id
  field accepted <- value.accepted
`;
  const metadata = {
    FindOrder: { ontology: "FIXTURE-FIND-ORDER", meaning: "Explicit optional order projection." },
    CopyOrder: { ontology: "FIXTURE-COPY-ORDER", meaning: "Explicit field projection without construction." },
  };
  const text = block.replace("read current <- Order key request.id", "query current <- FindOrder(id <- request.id)")
    .replace("order <- current", "order <- request")
    .replace("result <- request", "map copied <- CopyOrder(value <- request)\n  result <- copied");
  const checked = checkApplicationRealizationTypes(project(text, extra, metadata))[0]!;
  const lowered = deriveApplicationRealizationCompositions(project(text, extra, metadata))[0]!;
  assert.deepEqual(lowered.composition.bindings, [
    { kind: "mapping", name: "copied", selector: "commerce:copy-order", arguments: [{ parameter: "value", value: { op: "path", root: "request", properties: [] } }] },
    { kind: "query", name: "current", selector: "commerce:find-order", source_slot: "commerce:order", arguments: [{ parameter: "id", value: { op: "path", root: "request", properties: ["FIXTURE-ORDER#id"] } }], absence: "preserve" },
  ]);
  assert.deepEqual(lowered.action.reads, [], "Query remains a named call, not a keyed Entity read");
  assert.deepEqual(lowered.action.result.value, { op: "path", root: "copied", properties: [] });
  assert.deepEqual(lowered.absence_failures, [], "no absence failure policy is invented");
  const required = text.replace("value <- request", "value <- current") + "  on-absence current fail ORDER_NOT_FOUND\n";
  const requiredProjection = project(required, extra, metadata);
  const requiredChecked = checkApplicationRealizationTypes(requiredProjection)[0]!;
  const requiredLowered = deriveApplicationRealizationCompositions(requiredProjection)[0]!;
  assert.deepEqual(requiredChecked.queries[0]!.output, { kind: "named", selector: "commerce:order" });
  assert.equal(requiredLowered.composition.bindings.find(b => b.kind === "query")!.absence, "require-present");
  assert.deepEqual(requiredLowered.absence_failures, [{ binding: "current", code: "ORDER_NOT_FOUND" }]);
  assert.notEqual(requiredChecked.graph.graph_sha256, checked.graph.graph_sha256);
  assert.notEqual(checkApplicationRealizationTypes(project(required.replace("ORDER_NOT_FOUND", "ORDER_UNAVAILABLE"), extra, metadata))[0]!.graph.graph_sha256,
    requiredChecked.graph.graph_sha256, "failure codes participate in graph identity");
  const requiredLines = required.trimEnd().split("\n");
  assert.deepEqual(deriveApplicationRealizationCompositions(project(requiredLines[0] + "\n" + requiredLines.slice(1).reverse().join("\n") + "\n", extra, metadata)), [requiredLowered]);
  for (const invalid of [
    required + "  on-absence current fail OTHER\n",
    required.replace("on-absence current", "on-absence request"),
    required.replace("on-absence current", "on-absence copied"),
    required.replace("on-absence current", "on-absence missing"),
    required.replace(" fail ORDER_NOT_FOUND", " fail"),
    required.replace("ORDER_NOT_FOUND", "lowercase"),
    required.replace("ORDER_NOT_FOUND", '"ORDER_NOT_FOUND"'),
    required.replace("ORDER_NOT_FOUND", "X".repeat(129)),
  ]) assert.throws(() => project(invalid, extra, metadata), /APPLICATION_REALIZATION/);
  assert.throws(() => project(required, extra.replace("optional<Order>", "list<Order>"), metadata), /optional Query result/);
  const partialRequired = project(required, extra, metadata);
  const partialRequiredPath = "specs/commerce/nodes/find-order.json";
  const partialRequiredNode = JSON.parse(partialRequired.projectFiles[partialRequiredPath]!);
  partialRequiredNode.body.typed_contract.projection = ["id"];
  partialRequired.projectFiles[partialRequiredPath] = json(partialRequiredNode);
  assert.throws(() => checkApplicationRealizationTypes(partialRequired), /connection types differ/,
    "presence does not turn a partial Query projection into a whole Entity");
  const secondQuery = text.replace("  result <- copied", "  query second <- FindOrder(id <- current.id)\n  result <- copied") + "  on-absence current fail ORDER_NOT_FOUND\n";
  const projectedPath = project(secondQuery, extra, metadata);
  projectedPath.projectFiles[partialRequiredPath] = json(partialRequiredNode);
  assert.deepEqual(checkApplicationRealizationTypes(projectedPath)[0]!.queries[1]!.arguments[0]!.value.properties, ["FIXTURE-ORDER#id"]);
  assert.throws(() => checkApplicationRealizationTypes(project(secondQuery.replace("id <- current.id", "id <- current.accepted"), extra, metadata)), /connection types differ/);
  const omittedField = project(secondQuery.replace("id <- current.id", "id <- current.accepted"), extra, metadata);
  omittedField.projectFiles[partialRequiredPath] = json(partialRequiredNode);
  assert.throws(() => checkApplicationRealizationTypes(omittedField), /projection does not contain/);
  assert.throws(() => deriveApplicationRealizationActions(project(text, extra, metadata)), /APPLICATION_REALIZATION_UNSUPPORTED/);
  assert.deepEqual(checked.queries[0]!.output, { kind: "optional", element: { kind: "named", selector: "commerce:order" } });
  assert.equal(checked.mappings[0]!.mapping, "commerce:copy-order");
  const queryNode = checked.graph.nodes.find(n => n.id === "query:current")!;
  const mappingNode = checked.graph.nodes.find(n => n.id === "mapping:copied")!;
  assert.equal(queryNode.kind, "query"); assert.equal(mappingNode.kind, "mapping");
  assert.equal((queryNode.binding as any).query, "commerce:find-order");
  assert.equal((queryNode.binding as any).output.kind, "optional");
  assert.equal((mappingNode.binding as any).mapping, "commerce:copy-order");
  assert.match((mappingNode.binding as any).contract_sha256, /^[a-f0-9]{64}$/);
  const lines = text.trimEnd().split("\n");
  const reordered = lines[0] + "\n" + lines.slice(1).reverse().join("\n") + "\n";
  assert.deepEqual(checkApplicationRealizationTypes(project(reordered, extra, metadata))[0]!.graph, checked.graph);
  assert.deepEqual(deriveApplicationRealizationCompositions(project(reordered, extra, metadata)), [lowered]);
  for (const changed of [
    text.replace("id <- request.id", "id <- request.accepted"),
    text.replace("order <- request", "order <- current"),
    text.replace("value <- request", "value <- current"),
    text.replace("value <- request", "value <- current.id"),
    text.replace("result <- copied", "result <- current"),
  ]) assert.throws(() => checkApplicationRealizationTypes(project(changed, extra, metadata)), /APPLICATION_REALIZATION_TYPE/);
  const list = checkApplicationRealizationTypes(project(text, extra.replace("optional<Order>", "list<Order>"), metadata))[0]!;
  assert.equal(list.queries[0]!.output.kind, "list");
  assert.notEqual(list.graph.graph_sha256, checked.graph.graph_sha256, "cardinality changes cannot collapse in graph identity");
  const partial = project(text, extra, metadata);
  const queryPath = "specs/commerce/nodes/find-order.json";
  const partialNode = JSON.parse(partial.projectFiles[queryPath]!);
  partialNode.body.typed_contract.projection = ["id"];
  partial.projectFiles[queryPath] = json(partialNode);
  assert.deepEqual(checkApplicationRealizationTypes(partial)[0]!.queries[0]!.output, {
    kind: "optional", element: { kind: "projection", owner: { kind: "named", selector: "commerce:order" }, fields: ["id"] },
  }, "partial query fields cannot become a full Entity just because the authored output names it");
  partialNode.body.typed_contract.result_cardinality = "list";
  partial.projectFiles[queryPath] = json(partialNode);
  assert.throws(() => checkApplicationRealizationTypes(partial), /Query cardinality differs/);
  const mixed = text.replace("  query current", "  read direct <- Order key request.id\n  query current");
  assert.throws(() => deriveApplicationRealizationCompositions(project(mixed, extra, metadata)), /both a keyed read and a Query collection/);
  const changedProjection = project(text, extra, metadata);
  const rulePath = "specs/commerce/nodes/eligible-order.json";
  const changedRule = JSON.parse(changedProjection.projectFiles[rulePath]!);
  changedRule.body.typed_contract.expression.right.value = false;
  changedProjection.projectFiles[rulePath] = json(changedRule);
  assert.notEqual(checkApplicationRealizationTypes(changedProjection)[0]!.graph.graph_sha256, checked.graph.graph_sha256,
    "even a same-name same-type projected Rule mutation changes dependency identity; this does not admit the mutated projection");
});

for (const requirePresent of [false, true]) test(`authored named calls compile through the Alch project adapter and execute native artifacts (${requirePresent ? "require-present" : "preserve"})`, async t => {
  const extra = `query FindOrder:
  input id UInt64
  source candidate Order
  output optional<Order>
  where EligibleOrder
  bind order <- candidate
mapping CopyOrder:
  input value Order
  target Order
  total true
  field id <- value.id
  field accepted <- value.accepted
`;
  let text = block.replace("read current <- Order key request.id", "query current <- FindOrder(id <- request.id)")
    .replace("order <- current", "order <- request")
    .replace("write Order replace <- request", "map copied <- CopyOrder(value <- request)\n  write Order replace <- copied")
    .replace("result <- request", "result <- copied");
  if (requirePresent) text = text.replace("value <- request", "value <- current") + "  on-absence current fail ORDER_NOT_FOUND\n";
  const context = projectContext(text, extra, {
    FindOrder: { ontology: "FIXTURE-FIND-ORDER", meaning: "Optional order query." },
    CopyOrder: { ontology: "FIXTURE-COPY-ORDER", meaning: "Explicit order projection." },
  });
  const projection=context.projection;
  const derived = deriveApplicationRealizationCompositions(projection)[0]!;
  const compiler = await loadDomainSpecCompiler();
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "alch-composed-native-")); t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const write = (relative: string, content: string) => { const file = path.join(root, relative); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, content); };
  const {operations,...base}=executableFixture().execution.selection;
  const execution={schema_version:'alchlang.application-execution/v2-candidate',projection_sha256:digest(json(projection)),
    selection:{...base,schema_version:'domainspec.reconciled-compilation/v2-candidate',profile_id:'domainspec.reconciled-typescript/v2-candidate'}};
  const prepare=(value:unknown=execution)=>prepareApplicationExecutable(context.source,context.bindings,context.sources,context.interpretation,value,compiler);
  const candidate=prepare();
  assert.deepEqual(candidate.selection.operations,[derived.action]);
  assert.deepEqual(candidate.selection.value_compositions,[{composition:derived.composition,absence_failures:derived.absence_failures}]);
  for(const name of ['operations','value_compositions'])assert.throws(()=>prepare({...execution,selection:{...execution.selection,[name]:undefined}}),/APPLICATION_REALIZATION_OVERRIDE/);
  assert.throws(()=>prepare({...execution,projection_sha256:'0'.repeat(64)}),/APPLICATION_EXECUTION_STALE/);
  let getters=0;const bad={...execution.selection};Object.defineProperty(bad,'schema_version',{enumerable:true,get(){getters++;return execution.selection.schema_version;}});
  assert.throws(()=>prepare({...execution,selection:bad}),/APPLICATION_EXECUTION_SCHEMA/);assert.equal(getters,0);
  assert.throws(()=>prepare({...execution,selection:base}),/APPLICATION_REALIZATION_UNSUPPORTED/,'named calls cannot silently switch the selected legacy profile');
  for (const [relative, content] of Object.entries(candidate.projectFiles)) write(`source/${relative}`, content);
  const graph = compiler.compileProject(path.join(root, "source")).graph;
  const generatedProject=compileApplicationExecutable(candidate,graph,compiler),plan=generatedProject.view;
  assert.deepEqual(compileApplicationExecutable(candidate,graph,compiler).view,plan);
  assert.throws(()=>compileApplicationExecutable(structuredClone(candidate),graph,compiler),/APPLICATION_EXECUTION_UNVALIDATED/);
  for(const node of graph.nodes)assert.ok((plan.modules as any[]).some(m=>m.qualified_selectors.includes(node.selector)),node.selector);
  for (const artifact of plan.artifacts) write(`generated/${artifact.relative_path}`, artifact.content);
  const generated = path.join(root, "generated");
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs", "--rootDir", generated, "--outDir", path.join(root, "js"), ...plan.artifacts.map((a: any) => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const module = plan.artifacts.find(a=>a.relative_path.endsWith('/operations/submit-order.ts'))!;
  const run = createRequire(import.meta.url)(path.join(root, "js", module.relative_path.replace(/\.ts$/, ".js"))).operationSubmitOrder;
  for (const rows of [[], [{ id: "7", accepted: true }], [{ id: "7", accepted: true }, { id: "8", accepted: true }]]) {
    const calls: string[] = [], batches: any[] = [];
    const result = await run({ request: { id: "1", accepted: true } }, { store: { begin: async () => ({
      read: async () => { throw Error("Query must not become keyed lookup"); },
      querySource: async (request: any) => { calls.push("query"); assert.deepEqual(request, { slot: "commerce:order", target: "commerce:order" }); return rows; },
      commit: async (batch: any) => { calls.push("commit"); batches.push(batch); return { status: "committed" }; },
      rollback: async () => { calls.push("rollback"); },
    }) } });
    if (rows.length < 2 && (!requirePresent || rows.length === 1)) {
      assert.equal(result.status, "committed"); assert.deepEqual(result.value, { id: requirePresent ? 7n : 1n, accepted: true });
      assert.deepEqual(calls, ["query", "commit"]); assert.deepEqual(batches[0].writes[0].value, result.value);
    } else {
      assert.equal(result.status, "failed");
      assert.equal(result.code, rows.length === 0 ? "ORDER_NOT_FOUND" : "QUERY_CARDINALITY"); assert.deepEqual(calls, ["query", "rollback"]); assert.equal(batches.length, 0);
    }
  }
});

test("public payload field paths stay qualified and cannot substitute for a domain Entity", () => {
  const extra = `interface OrderApi:
  kind external
  version 1.0.0
  compatibility exact
  contract Request:
    id UInt64
    accepted Bool
  exposes SubmitOrder:
    request Request
    result Request
mapping OrderToRequest:
  input value Order
  target OrderApi.Request
  total true
  field id <- value.id
  field accepted <- value.accepted
mapping RequestToOrder:
  input payload OrderApi.Request
  target Order
  total true
  field id <- payload.id
  field accepted <- payload.accepted
`;
  const metadata = {
    OrderApi: { ontology: "FIXTURE-ORDER-API", meaning: "Explicit public interface.", contracts: {
      Request: { ontology: "FIXTURE-REQUEST", properties: {
        id: { ontology: "FIXTURE-REQUEST#id", meaning: "Public identity." },
        accepted: { ontology: "FIXTURE-REQUEST#accepted", meaning: "Public flag." },
      } },
    } },
    OrderToRequest: { ontology: "FIXTURE-ORDER-TO-REQUEST", meaning: "Explicit public projection." },
    RequestToOrder: { ontology: "FIXTURE-REQUEST-TO-ORDER", meaning: "Field projection only." },
  };
  const text = block.replace("  read current <- Order key request.id", "  map public <- OrderToRequest(value <- request)\n  read current <- Order key public.id")
    .replace("  write Order replace <- request", "  map mapped <- RequestToOrder(payload <- public)\n  write Order replace <- mapped")
    .replace("result <- request", "result <- mapped");
  const checked = checkApplicationRealizationTypes(project(text, extra, metadata))[0]!;
  assert.deepEqual(checked.reads[0]!.key.value.properties, ["FIXTURE-REQUEST#id"]);
  assert.deepEqual(checked.mappings[0]!.output, { kind: "contract", interface_selector: "commerce:order-api", contract_id: "request" });
  assert.throws(() => checkApplicationRealizationTypes(project(text.replace("write Order replace <- mapped", "write Order replace <- public"), extra, metadata)), /APPLICATION_REALIZATION_TYPE/);
  assert.throws(() => deriveApplicationRealizationActions(project(text, extra, metadata)), /APPLICATION_REALIZATION_UNSUPPORTED/);
});

test("source-derived actions omit operation JSON and reject overrides and stale input", async () => {
  const f = realizationFixture(), compiler = await loadDomainSpecCompiler();
  assert.deepEqual(deriveApplicationRealizationActions(f.projection), f.expectedOperations);
  const prepare = (execution: unknown) => prepareApplicationExecutable(f.source, f.bindings, f.sources, f.interpretation, execution, compiler);
  const candidate = prepare(f.execution);
  assert.deepEqual(candidate.selection.operations, f.expectedOperations);
  assert.deepEqual(candidate, prepare(f.execution));
  assert.ok(Object.isFrozen(candidate.selection));
  for (const operations of [[], f.expectedOperations, undefined]) {
    assert.throws(() => prepare({ ...f.execution, selection: { ...f.execution.selection, operations } }), /APPLICATION_REALIZATION_OVERRIDE/);
  }
  assert.throws(() => prepare({ ...f.execution, projection_sha256: "0".repeat(64) }), /APPLICATION_EXECUTION_STALE/);
  assert.throws(() => prepare({ ...f.execution, schema_version: "alchlang.application-execution/v1-candidate" }), /APPLICATION_EXECUTION_SCHEMA/);
});

test("Event input identity remains distinct from Entity values and opaque until Event construction", () => {
  const f = executableFixture();
  const declarations = `event OrderSubmitted:
  event-type order-submitted
  version 1
  occurrence-id eventId String
  occurred-at generated
  orderId -> Order.id
event OtherEvent:
  event-type other-event
  version 1
  occurrence-id eventId String
  occurred-at generated
  orderId -> Order.id
`;
  const realization = block.replace("  input request", "  input request\n  event-input submitted OrderSubmitted")
    .replace("  result <- request", "  event OrderSubmitted <- submitted\n  result <- request");
  const projectEvent = (text: string) => {
    const source = f.source.replace("  requires EligibleOrder", "  requires EligibleOrder\n  produces OrderSubmitted") + declarations + text;
    const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) }, declarations: {
      ...f.bindings.declarations,
      OrderSubmitted: { ontology: "FIXTURE-SUBMITTED", meaning: "Explicit event occurrence intent." },
      OtherEvent: { ontology: "FIXTURE-OTHER-EVENT", meaning: "Distinct event occurrence intent." },
    } };
    const formation = lowerApplicationDomain(source, bindings, f.sources);
    return lowerApplicationRuleProjections(source, bindings, f.sources, { ...f.interpretation, formation_sha256: digest(json(formation)) });
  };
  const projection = projectEvent(realization);
  const checked = checkApplicationRealizationTypes(projection)[0]!;
  assert.deepEqual(checked.events[0]!.type, { kind: "event-input", selector: "commerce:order-submitted" });
  assert.ok(checked.graph.nodes.find(n => n.id === "event:commerce:order-submitted")!.depends_on.includes("write:commerce:order"));
  assert.ok(checked.graph.nodes.find(n => n.id === "commit")!.depends_on.includes("event:commerce:order-submitted"));
  assert.deepEqual(deriveApplicationRealizationActions(projection)[0]!.events, [{ slot: "commerce:order-submitted", target: "commerce:order-submitted", parameter: "submitted" }]);
  for (const wrong of [
    realization.replace("event-input submitted OrderSubmitted", "event-input submitted OtherEvent"),
    realization.replace("event OrderSubmitted <- submitted", "event OrderSubmitted <- submitted.payload"),
    realization.replace("order <- current", "order <- submitted"),
    realization.replace("result <- request", "result <- submitted"),
  ]) assert.throws(() => checkApplicationRealizationTypes(projectEvent(wrong)), /APPLICATION_REALIZATION_TYPE/);
  for (const wrong of [
    realization.replace("event-input submitted OrderSubmitted", "event-input submitted Order"),
    realization + "  event-input unused OrderSubmitted\n",
    realization + "  event-input submitted OrderSubmitted\n",
    realization.replace("event OrderSubmitted <- submitted", "event OrderSubmitted <- request"),
  ]) assert.throws(() => projectEvent(wrong), /APPLICATION_REALIZATION/);
});
