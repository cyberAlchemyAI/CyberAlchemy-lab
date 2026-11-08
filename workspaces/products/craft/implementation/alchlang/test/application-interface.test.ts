import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { lowerApplicationDomain, assertApplicationDomainCurrent } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { testTypeScript } from "./toolchain.js";

const api = `interface OrderApi:
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
`;
const mappings = `mapping RequestToOrder:
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
function fixture(suffix = api, publicMappings = false) {
  const f = executableFixture(), source = f.source + suffix + (publicMappings ? mappings : "");
  const fields = (ontology: string) => ({ ontology, properties: {
    id: { ontology: ontology + "#id", meaning: "Public identifier value." },
    accepted: { ontology: ontology + "#accepted", meaning: "Explicit public Boolean value." },
  } });
  const bindings = { ...f.bindings, source_sha256: digest(source), formal: { ...f.bindings.formal, source_sha256: digest(source) },
    declarations: { ...f.bindings.declarations, ...(publicMappings ? {
      RequestToOrder: { ontology: "FIXTURE-REQUEST-MAPPING", meaning: "Project explicitly supplied request fields." },
      OrderToSummary: { ontology: "FIXTURE-RESPONSE-MAPPING", meaning: "Project explicitly supplied order fields." },
    } : {}), OrderApi: { ontology: "FIXTURE-ORDER-API", meaning: "Explicit public submission boundary.",
      contracts: { SubmitOrderRequest: fields("FIXTURE-SUBMIT-REQUEST"), OrderSummary: fields("FIXTURE-ORDER-SUMMARY") } } } };
  return { ...f, source, bindings };
}
const lower = (f: ReturnType<typeof fixture>) => lowerApplicationDomain(f.source, f.bindings, f.sources);

test("public request Mapping can target a declared Value Object without construction", () => {
  const f = fixture(api, true);
  f.source = f.source.replace("  target Order\n", "  target OrderNotice\n") + "value-object OrderNotice:\n  id UInt64\n  accepted Bool\n";
  f.bindings.source_sha256 = digest(f.source); f.bindings.formal.source_sha256 = digest(f.source);
  Object.assign(f.bindings.declarations, {OrderNotice: {ontology: "FIXTURE-ORDER-NOTICE", meaning: "Explicit projected fields.", invariants: ["IdentityValid"], properties: {
    id: {ontology: "FIXTURE-ORDER-NOTICE#id", meaning: "Projected identifier."},
    accepted: {ontology: "FIXTURE-ORDER-NOTICE#accepted", meaning: "Projected eligibility."},
  }}});
  const result = lower(f);
  const node = JSON.parse(result.projectFiles["specs/commerce/nodes/request-to-order.json"]!);
  assert.deepEqual(node.body.typed_contract.target, {kind: "named", selector: "commerce:order-notice"});
  assert.ok(result.projectFiles["specs/commerce/edges/request-to-order-maps-order-notice.json"]);
  assertApplicationDomainCurrent(f.source, f.bindings, f.sources, result);
});

test("public Mapping retains qualified payload identity and canonical target owners", () => {
  const f = fixture(api, true), result = lower(f);
  const read = (id: string) => JSON.parse(result.projectFiles[`specs/commerce/nodes/${id}.json`]!).body.typed_contract;
  const request = read("request-to-order"), response = read("order-to-summary");
  assert.equal(request.schema_version, "domainspec.typed-mapping/v3");
  assert.deepEqual(request.inputs[0], { name: "request", type: { kind: "contract", interface_selector: "commerce:order-api", contract_id: "submit-order-request" }, use: null });
  assert.deepEqual(request.fields[0].value.properties, ["FIXTURE-SUBMIT-REQUEST#id"]);
  assert.deepEqual(response.target, { kind: "contract", interface_selector: "commerce:order-api", contract_id: "order-summary" });
  assert.equal(response.target_use, null);
  assert.ok(result.projectFiles["specs/commerce/edges/order-to-summary-maps-order-api.json"]);
  assert.ok(result.projectFiles["specs/commerce/edges/request-to-order-maps-order.json"]);
  assertApplicationDomainCurrent(f.source, f.bindings, f.sources, result);
  for (const [before, after, code] of [
    ["input request OrderApi.SubmitOrderRequest", "input request OrderApi.Missing", "APPLICATION_PUBLIC_TYPE"],
    ["target OrderApi.OrderSummary", "target Missing.OrderSummary", "APPLICATION_MAPPING_TARGET"],
    ["request.id", "request.missing", "APPLICATION_MAPPING_PATH"],
    ["field accepted <- request.accepted", "field accepted <- request.id", "APPLICATION_MAPPING_TYPE"],
    ["  field accepted <- request.accepted\n", "", "APPLICATION_MAPPING_TOTAL"],
  ]) {
    const bad = fixture(api, true); bad.source = bad.source.replace(before!, after!);
    bad.bindings.source_sha256 = digest(bad.source); bad.bindings.formal.source_sha256 = digest(bad.source);
    assert.throws(() => lower(bad), new RegExp(code!));
  }
});

test("Interface lowers distinct named public contracts and exact exposed members without domain records", () => {
  const f = fixture(), result = lower(f), node = JSON.parse(result.projectFiles["specs/commerce/nodes/order-api.json"]!);
  const contract = node.body.typed_contract;
  assert.equal(node.kind, "Interface"); assert.equal(contract.schema_version, "domainspec.typed-interface/v1");
  assert.deepEqual(contract.version_policy, { schema_version: "domainspec.interface-version-policy/v1", mode: "exact", direction: "consumer-to-provider", provider_version: "1.0.0" });
  assert.deepEqual(contract.operations, [{ operation_id: "submit-order", operation_ref: "commerce:submit-order",
    request: { kind: "contract", contract_id: "submit-order-request" }, result: { kind: "contract", contract_id: "order-summary" } }]);
  assert.equal(contract.contracts[0].fields[0].ontology_field, "FIXTURE-SUBMIT-REQUEST#id");
  assert.ok(!Object.keys(result.projectFiles).some(p => /nodes\/(submit-order-request|order-summary)\.json$/.test(p)));
  assert.equal(JSON.parse(result.projectFiles["specs/commerce/edges/order-api-exposes-submit-order.json"]!).relationship, "exposes");
  assertApplicationDomainCurrent(f.source, f.bindings, f.sources, result);
  const changed = structuredClone(result); (changed.files as Record<string, string>)["project/specs/commerce/nodes/order-api.json"] = "{}";
  assert.throws(() => assertApplicationDomainCurrent(f.source, f.bindings, f.sources, changed), /APPLICATION_FORMATION_STALE/);
});

test("Interface rejects ambiguous, unbound, recursive or Entity-leaking public declarations", () => {
  for (const [before, after, code] of [
    ["kind external", "kind database", "APPLICATION_INTERFACE"],
    ["version 1.0.0", "version 1", "APPLICATION_INTERFACE"],
    ["compatibility exact", "compatibility exact\n  compatibility backward", "APPLICATION_INTERFACE"],
    ["request SubmitOrderRequest", "request Missing", "APPLICATION_INTERFACE_TYPE"],
    ["result OrderSummary", "result Order", "APPLICATION_INTERFACE_TYPE"],
    ["exposes SubmitOrder:", "exposes Order:", "APPLICATION_INTERFACE_MEMBER"],
    ["    id UInt64", "    id -> Order.id", "APPLICATION_INTERFACE_TYPE"],
    ["    id UInt64", "    id SubmitOrderRequest", "APPLICATION_INTERFACE_CYCLE"],
    ["    id UInt64", "    id UInt64\n    id UInt64", "APPLICATION_INTERFACE"],
    ["    accepted Bool", "      accepted Bool", "APPLICATION_INTERFACE"],
    ["contract SubmitOrderRequest:", "contract Order:", "APPLICATION_INTERFACE"],
    ["    result OrderSummary\n", "", "APPLICATION_INTERFACE"],
  ]) assert.throws(() => lower(fixture(api.replace(before!, after!))), new RegExp(code!));
  const f = fixture(); delete (f.bindings.declarations.OrderApi.contracts as any).OrderSummary;
  assert.throws(() => lower(f), /APPLICATION_BINDING_COVERAGE/);
  const g = fixture(); g.bindings.declarations.OrderApi.contracts.OrderSummary.ontology = "FIXTURE-SUBMIT-REQUEST";
  assert.throws(() => lower(g), /APPLICATION_ONTOLOGY/);
});

test("public compiler emits native Interface values with separate identity and explicit version eligibility", async t => {
  const f = fixture(api, true), compiler = await loadDomainSpecCompiler(), formation = lower(f);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, interpretation);
  const execution = { ...f.execution, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, interpretation, execution, compiler);
  const temp = mkdtempSync(path.join(tmpdir(), "alch-interface-")); t.after(() => rmSync(temp, { recursive: true, force: true }));
  const write = (dir: string, files: Record<string, string>) => { for (const [relative, bytes] of Object.entries(files)) {
    const target = path.join(dir, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  } };
  const sourceRoot = path.join(temp, "source"); write(sourceRoot, candidate.projectFiles);
  const result = compileApplicationExecutable(candidate, compiler.compileProject(sourceRoot).graph, compiler);
  const generated = path.join(temp, "generated"); write(generated, Object.fromEntries(result.view.artifacts.map(a => [a.relative_path, a.content])));
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
    "--rootDir", generated, "--outDir", path.join(temp, "js"), ...result.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const module = result.view.artifacts.find(a => a.relative_path.endsWith("/order-api.ts")); assert.ok(module);
  const boundary = createRequire(import.meta.url)(path.join(temp, "js", module.relative_path.replace(/\.ts$/, ".js")));
  const request = boundary.publicContracts["submit-order-request"], response = boundary.publicContracts["order-summary"];
  const input = { id: "18446744073709551615", accepted: true }, normalized = request.normalize(input);
  assert.deepEqual(normalized, { id: 18446744073709551615n, accepted: true });
  assert.ok(Object.isFrozen(normalized)); assert.equal(input.id, "18446744073709551615");
  assert.notEqual(request.key(normalized), response.key(response.normalize(input)));
  assert.equal(boundary.endpointValues["submit-order"].request, request); assert.equal(boundary.endpointValues["submit-order"].result, response);
  assert.equal(boundary.acceptsVersion("1.0.0"), true); assert.equal(boundary.acceptsVersion("1.0.1"), false);
  for (const invalid of [{ id: "-1", accepted: true }, { id: "1", accepted: "true" }, { ...input, extra: true }]) assert.throws(() => request.normalize(invalid));
  const mapping = (file: string, name: string) => {
    const artifact = result.view.artifacts.find(a => a.relative_path.endsWith(`/${file}.ts`)); assert.ok(artifact);
    return createRequire(import.meta.url)(path.join(temp, "js", artifact.relative_path.replace(/\.ts$/, ".js")))[name];
  };
  const toOrder = mapping("request-to-order", "mappingRequestToOrder"), toSummary = mapping("order-to-summary", "mappingOrderToSummary");
  const order = toOrder({ request: normalized }), summary = toSummary({ order });
  assert.deepEqual(order, normalized); assert.deepEqual(summary, normalized);
  assert.ok(Object.isFrozen(order)); assert.ok(Object.isFrozen(summary));
  assert.notEqual(order, normalized); assert.notEqual(summary, order);
  assert.deepEqual(input, { id: "18446744073709551615", accepted: true });
  assert.throws(() => toOrder({ request: { id: "-1", accepted: true } }));
  assert.throws(() => toOrder({ request: normalized, extra: true }));
  assert.throws(() => toSummary({ order: { id: 1n, accepted: "true" } }));
});
