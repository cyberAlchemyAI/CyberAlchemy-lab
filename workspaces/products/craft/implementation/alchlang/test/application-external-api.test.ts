import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import path from "node:path";
import { lowerApplicationExternalApi, assertApplicationExternalApiCurrent } from "../src/application-external-api.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { digest, json } from "../src/domainspec-profile.js";
import { lowerApplicationDomain, assertApplicationDomainCurrent } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { testTypeScript } from "./toolchain.js";

import { externalApiFixture as fixture } from "./fixtures/application-integration-fixtures.js";

test("API formation preserves named public payloads, explicit mappers and HTTP route intent", async () => {
  const f = await fixture(), before = json(f.binding), result = lowerApplicationExternalApi(f.source, f.binding, f.compiler);
  assert.equal(json(f.binding), before);
  assert.deepEqual(result.composition, f.compiler.compileExternalApiComposition(JSON.parse(result.files["external-api-composition.json"])));
  assert.deepEqual(result.trace.references[0]!.request, { kind: "public-contract", interface: "OrderApi", contract: "SubmitRequest" });
  assert.deepEqual(JSON.parse(result.files["external-api-routes.json"]).routes, [{ source_id: "SubmitHttp", binding_ref: "inbound-endpoint:payment-webhook", protocol_operation_ref: "protocol-operation:payments-webhook", method: "POST", path: "/orders" }]);
  assert.equal(result.trace.routes_sha256, digest(result.files["external-api-routes.json"]));
  assert.equal(result.trace.runtime_calls_observed, false);
  assert.equal(result.trace.payload_type_join, "required");
  assert.equal(result.composition.runtime_calls_observed, false);
  assertApplicationExternalApiCurrent(f.source, f.binding, f.compiler, result);
  assert.deepEqual(result, lowerApplicationExternalApi(f.source, f.binding, f.compiler));
  const changed = structuredClone(result); changed.files["external-api-routes.json"] = "{}";
  assert.throws(() => assertApplicationExternalApiCurrent(f.source, f.binding, f.compiler, changed), /APPLICATION_API_STALE/);
  assert.throws(() => lowerApplicationExternalApi(f.source + "\n", f.binding, f.compiler), /APPLICATION_API_SOURCE/);
});

test("API formation rejects role, payload, mapper and exact coverage mismatches", async () => {
  const f = await fixture();
  for (const [before, after, code] of [
    ["-> operation SubmitOrder", "-> operation Order", "APPLICATION_API_OPERATION"],
    ["-> request OrderApi.SubmitRequest", "-> request OrderApi.Summary", "APPLICATION_API_PAYLOAD"],
    ["-> response OrderApi.Summary", "-> response OrderApi.Missing", "APPLICATION_API_TYPE"],
    ["external-api PaymentGateway", "external-api Order", "APPLICATION_API_BINDING"],
  ]) {
    const source = f.source.replace(before!, after!); assert.notEqual(source, f.source);
    assert.throws(() => lowerApplicationExternalApi(source, { ...f.binding, source_sha256: digest(source) }, f.compiler), new RegExp(code!));
  }
  const hidden = structuredClone(f.binding); (hidden.declarations as any).Hidden = hidden.declarations.SubmitHttp;
  assert.throws(() => lowerApplicationExternalApi(f.source, hidden, f.compiler), /APPLICATION_API_BINDING/);
  const missing = structuredClone(f.binding);
  missing.composition.inbound_endpoint_bindings[0].response_mapper_ref = "commerce:missing";
  missing.composition.api_mappings[3].mapper_ref = "commerce:missing";
  assert.throws(() => lowerApplicationExternalApi(f.source, missing, f.compiler), /APPLICATION_API_MAPPING/);
  const consumer = structuredClone(f.binding); consumer.composition.external_api_contracts[0].consumer_role_refs = ["commerce:other"];
  assert.throws(() => lowerApplicationExternalApi(f.source, consumer, f.compiler), /APPLICATION_API_OPERATION/);
  const collapsed = structuredClone(f.binding); collapsed.contract_refs["OrderApi.Summary"] = collapsed.contract_refs["OrderApi.SubmitRequest"];
  assert.throws(() => lowerApplicationExternalApi(f.source, collapsed, f.compiler), /APPLICATION_API_IDENTITY/);
  const wrongBoundary = structuredClone(f.binding); wrongBoundary.external_apis.PaymentGateway.interface_ref = "Order";
  assert.throws(() => lowerApplicationExternalApi(f.source, wrongBoundary, f.compiler), /APPLICATION_API_INTERFACE/);
  const conflated = structuredClone(f.binding);
  conflated.composition.integration_kernel.integration_bindings[0].logical_boundary_ref = conflated.external_apis.PaymentGateway.contract_ref;
  assert.throws(() => lowerApplicationExternalApi(f.source, conflated, f.compiler), /APPLICATION_API_KERNEL/);
  const implicit = structuredClone(f.binding); (implicit.external_apis as any).PaymentGateway = implicit.external_apis.PaymentGateway.contract_ref;
  assert.throws(() => lowerApplicationExternalApi(f.source, implicit, f.compiler), /APPLICATION_API_BINDING/);
});

test("API formation retains provider, failure, retry and observation boundaries", async () => {
  const f = await fixture();
  const badProvider = structuredClone(f.binding);
  badProvider.composition.integration_kernel.integration_bindings[1].provider_realization_ref = "provider-realization:payment-http-client";
  assert.throws(() => lowerApplicationExternalApi(f.source, badProvider, f.compiler), /APPLICATION_API_KERNEL/);
  const unsafe = structuredClone(f.binding); unsafe.composition.resilience_policies[0].retry_safety = "safe-operation";
  unsafe.composition.resilience_policies[0].idempotency_key_expression = null;
  assert.throws(() => lowerApplicationExternalApi(f.source, unsafe, f.compiler), (error: any) => error.code === "API_RETRY_SAFETY");
  const observed = structuredClone(f.binding); observed.composition.runtime_calls_observed = true;
  assert.throws(() => lowerApplicationExternalApi(f.source, observed, f.compiler), (error: any) => error.code === "API_RUNTIME_CLAIM");
  const paths = structuredClone(f.binding); paths.composition.api_mappings[2].input_paths[0].parameter = "wrong";
  assert.throws(() => lowerApplicationExternalApi(f.source, paths, f.compiler), /APPLICATION_API_COVERAGE/);
  const auth = structuredClone(f.binding); auth.composition.inbound_endpoint_bindings[0].authentication_binding_ref = "authentication:missing";
  assert.throws(() => lowerApplicationExternalApi(f.source, auth, f.compiler), (error: any) => error.code === "API_AUTH_BINDING");
});

test("API paths do not hide duplicate routes or invent inbound consumers for outbound-only sources", async () => {
  const f = await fixture();
  const source = f.source + `inbound-endpoint DuplicateRoute:
  HTTP POST "/orders"
    -> request OrderApi.SubmitRequest
    -> operation SubmitOrder
    -> response OrderApi.Summary
`;
  const duplicate = structuredClone(f.binding); duplicate.source_sha256 = digest(source);
  duplicate.composition.inbound_endpoint_bindings.push({ ...duplicate.composition.inbound_endpoint_bindings[0], binding_id: "inbound-endpoint:duplicate", authentication_binding_ref: null });
  (duplicate.declarations as any).DuplicateRoute = { binding_ref: "inbound-endpoint:duplicate" };
  assert.throws(() => lowerApplicationExternalApi(source, duplicate, f.compiler), /APPLICATION_API_COVERAGE/);
  const outboundSource = f.source.replace(/inbound-endpoint SubmitHttp:[\s\S]*?(?=outbound-call ProviderCall:)/, "");
  const only = structuredClone(f.binding); only.source_sha256 = digest(outboundSource);
  delete (only.declarations as any).SubmitHttp;
  only.composition.inbound_endpoint_bindings = []; only.composition.webhook_bindings = [];
  only.composition.api_mappings = only.composition.api_mappings.slice(0, 2);
  only.composition.authentication_bindings = only.composition.authentication_bindings.slice(0, 1);
  const result = lowerApplicationExternalApi(outboundSource, only, f.compiler);
  assert.equal(result.trace.references.length, 1);
  assert.deepEqual(JSON.parse(result.files["external-api-routes.json"]).routes, []);
  assert.equal(result.trace.references[0]!.kind, "outbound-call");
});

test("inbound-only authored endpoints compile without invented external APIs", async () => {
  const f = await fixture();
  const source = f.source.replace(/outbound-call ProviderCall:[\s\S]*$/, "");
  const binding: any = structuredClone(f.binding); binding.source_sha256 = digest(source);
  delete binding.declarations.ProviderCall; binding.external_apis = {}; binding.contract_refs = {};
  binding.composition.external_api_contracts = []; binding.composition.external_api_bindings = [];
  binding.composition.api_failure_mappings = []; binding.composition.resilience_policies = [];
  binding.composition.api_mappings = binding.composition.api_mappings.slice(2);
  binding.composition.authentication_bindings = binding.composition.authentication_bindings.slice(1);
  binding.composition.integration_kernel.integration_bindings = binding.composition.integration_kernel.integration_bindings.filter((b: any) => b.direction === "inbound");
  const result = lowerApplicationExternalApi(source, binding, f.compiler);
  assert.equal(result.trace.references.length, 1);
  assert.equal(result.trace.references[0]!.kind, "inbound-endpoint");
  assert.deepEqual(result.composition.external_api_contracts, []);
  assert.deepEqual(result.composition.external_api_bindings, []);
  assert.equal(JSON.parse(result.files["external-api-routes.json"]).routes.length, 1);
});

for (const valueObject of [false, true]) test(`one source joins public API Mapping to ${valueObject ? "Value Object" : "Entity"} Operation and back natively`, async t => {
  const f = await fixture(), base = executableFixture();
  if (valueObject) {
    f.source = f.source.replace("  target Order\n", "  target OrderNotice\n").replace("  input result Order\n", "  input result OrderNotice\n")
      .replace("  input Order\n  output Order\n  reads Order\n  writes Order\n  requires EligibleOrder", "  input OrderNotice\n  output OrderNotice\n  requires IdentityValid")
      + "value-object OrderNotice:\n  id UInt64\n  accepted Bool\n";
    f.binding.source_sha256 = digest(f.source);
  }
  const fields = (ontology: string) => ({ ontology, properties: {
    id: { ontology: ontology + "#id", meaning: "Public identity value." },
    accepted: { ontology: ontology + "#accepted", meaning: "Explicit acceptance flag." },
  } });
  const bindings = { ...base.bindings, source_sha256: digest(f.source), formal: { ...base.bindings.formal, source_sha256: digest(f.source) },
    declarations: { ...base.bindings.declarations,
      OrderApi: { ontology: "FIXTURE-ORDER-API", meaning: "Named API boundary.", contracts: { SubmitRequest: fields("FIXTURE-SUBMIT-REQUEST"), Summary: fields("FIXTURE-SUMMARY") } },
      RequestToOrder: { ontology: "FIXTURE-REQUEST-TO-ORDER", meaning: "Project request fields, without construction." },
      OrderToSummary: { ontology: "FIXTURE-ORDER-TO-SUMMARY", meaning: "Project public response fields." },
      ProviderRequest: { ontology: "FIXTURE-PROVIDER-REQUEST", meaning: "Explicit provider request projection." },
      ProviderResponse: { ontology: "FIXTURE-PROVIDER-RESPONSE", meaning: "Explicit provider response projection." },
    } };
  if (valueObject) Object.assign(bindings.declarations, {OrderNotice: {...fields("FIXTURE-ORDER-NOTICE"), meaning: "Explicit request value.", invariants: ["IdentityValid"]}});
  const context = { binding: f.binding, compiler: f.compiler };
  assert.throws(() => lowerApplicationDomain(f.source, bindings, base.sources), /APPLICATION_INTEGRATION_LOWERING_REQUIRED/);
  const formation = lowerApplicationDomain(f.source, bindings, base.sources, undefined, undefined, context);
  assert.ok(formation.externalApi);
  for (const [name, bytes] of Object.entries(formation.externalApi.files)) assert.equal(formation.trace.formed_files[name]!.sha256, digest(bytes));
  assertApplicationDomainCurrent(f.source, bindings, base.sources, formation, undefined, undefined, context);
  for (const change of ["missing", "extra", "changed"]) {
    const altered: any = structuredClone(formation);
    if (change === "missing") delete altered.files["external-api-routes.json"];
    else if (change === "extra") altered.files["hidden-api.json"] = "{}";
    else altered.externalApi.trace.references[0].operation_ref = "commerce:other";
    assert.throws(() => assertApplicationDomainCurrent(f.source, bindings, base.sources, altered, undefined, undefined, context), /APPLICATION_FORMATION_STALE/);
  }
  const interpretation = { ...base.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(f.source, bindings, base.sources, interpretation, undefined, undefined, context);
  const selection: any = structuredClone(base.execution.selection);
  if (valueObject) {
    const named = {kind: "named", selector: "commerce:order-notice"};
    selection.factories.push({selector: named.selector, base_validators: [{rule: "commerce:identity-valid", arguments: [{parameter: "identity", field: "id"}]}], extensions: []});
    selection.operations = [{schema_version: "domainspec.operation-action-bindings/v1-candidate", selector: "commerce:submit-order",
      inputs: [{name: "request", type: named}], reads: [],
      guards: [{selector: "commerce:identity-valid", arguments: [{parameter: "identity", value: {op: "path", root: "request", properties: ["FIXTURE-ORDER-NOTICE#id"]}}]}],
      writes: [], events: [], result: {type: named, value: {op: "path", root: "request", properties: []}}, atomicity: "state-and-outbox", continuation: "awaited-settlement"}];
  }
  const execution = { ...base.execution, selection, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(f.source, bindings, base.sources, interpretation, execution, f.compiler, undefined, undefined, context);
  const temp = mkdtempSync(path.join(tmpdir(), "alch-api-join-")); t.after(() => rmSync(temp, { recursive: true, force: true }));
  const write = (root: string, files: Record<string, string>) => { for (const [relative, bytes] of Object.entries(files)) {
    const target = path.join(root, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  } };
  const sourceRoot = path.join(temp, "source"); write(sourceRoot, candidate.projectFiles);
  const graph = f.compiler.compileProject(sourceRoot).graph;
  const compiled = compileApplicationExecutable(candidate, graph, f.compiler);
  const joined = compiled.externalApiJoin;
  assert.equal(joined.domain_source_manifest_sha256, graph.source_manifest.manifest_sha256);
  assert.equal(compiled.trace.external_api_join_sha256, digest(json(joined)));
  assert.equal(joined.runtime_calls_observed, false);
  const publicType = (contract_id: string) => ({ kind: "contract", interface_selector: "commerce:order-api", contract_id });
  const inbound = joined.runtime_bindings.find((b: any) => b.mapping_ref === "commerce:request-to-order");
  const response = joined.runtime_bindings.find((b: any) => b.mapping_ref === "commerce:order-to-summary");
  const outbound = joined.runtime_bindings.find((b: any) => b.mapping_ref === "commerce:provider-request");
  assert.deepEqual(inbound.inputs[0].value_type, publicType("submit-request"));
  assert.deepEqual(inbound.inputs[0].source, { kind: "protocol-body", reference: "protocol-operation:payments-webhook#request", path: ["payload"] });
  assert.deepEqual(inbound.result_type, { kind: "named", selector: valueObject ? "commerce:order-notice" : "commerce:order" });
  assert.deepEqual(response.result_type, publicType("summary"));
  assert.deepEqual(outbound.inputs[0].source, { kind: "direct-value", reference: "commerce:order-api#submit-request", path: [] });
  assert.equal(joined.operation_requests[0].operation_ref, "commerce:submit-order");
  if (valueObject) {
    assert.equal(graph.nodes.find(n => n.selector === "commerce:order-notice")!.kind, "Value Object");
    assert.ok(!graph.nodes.some(n => n.selector === "commerce:submit-request" || n.selector === "commerce:summary"));
    const wrongOwner = structuredClone(selection);
    wrongOwner.operations[0].inputs[0].type = {kind: "named", selector: "commerce:order"};
    assert.throws(() => f.compiler.compileExternalApiRuntimeBindings(graph, f.binding.composition, wrongOwner), /type|contract/i);
  }
  assert.deepEqual(compiled, compileApplicationExecutable(candidate, graph, f.compiler));
  assert.throws(() => f.compiler.compileExternalApiRuntimeBindings(structuredClone(graph), f.binding.composition, execution.selection));
  const changed = structuredClone(f.binding); changed.composition.api_mappings[2].request_parameters[0].parameter = "wrong";
  assert.throws(() => f.compiler.compileExternalApiRuntimeBindings(graph, changed.composition, execution.selection), /request parameters must exactly cover/);
  assert.throws(() => lowerApplicationRuleProjections(f.source, bindings, base.sources, interpretation, undefined, undefined, { ...context, binding: changed }), /RULE_PROJECTION_STALE/);
  const generated = path.join(temp, "generated"), js = path.join(temp, "js");
  write(generated, Object.fromEntries(compiled.view.artifacts.map(a => [a.relative_path, a.content])));
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs", "--rootDir", generated, "--outDir", js,
    ...compiled.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const load = (suffix: string, name: string) => {
    const a = compiled.view.artifacts.find(a => a.relative_path.endsWith(suffix)); assert.ok(a);
    return createRequire(import.meta.url)(path.join(js, a.relative_path.replace(/\.ts$/, ".js")))[name];
  };
  const toOrder = load("/mappings/request-to-order.ts", "mappingRequestToOrder"), toSummary = load("/mappings/order-to-summary.ts", "mappingOrderToSummary");
  const toProvider = load("/mappings/provider-request.ts", "mappingProviderRequest"), fromProvider = load("/mappings/provider-response.ts", "mappingProviderResponse");
  const submit = load("/operations/submit-order.ts", "operationSubmitOrder");
  const payload = { id: "18446744073709551615", accepted: true };
  // Explicit test adapter follows the bound ingress path; no HTTP transport is executed.
  const protocolBody = { payload }, request = toOrder({ payload: protocolBody[inbound.inputs[0].source.path[0] as "payload"] });
  let commits = 0;
  const outcome = await submit({ request }, { store: { begin: async () => ({ read: async () => request, rollback: async () => {},
    commit: async (batch: any) => { assert.equal(batch.writes.length, valueObject ? 0 : 1); assert.equal(batch.events.length, 0); commits++; return { status: "committed" }; },
  }) } });
  assert.equal(outcome.status, "committed"); assert.equal(commits, 1);
  const summary = toSummary({ result: outcome.value });
  assert.deepEqual(summary, { id: 18446744073709551615n, accepted: true });
  assert.deepEqual(toProvider({ request: payload }), request);
  assert.deepEqual(fromProvider({ result: summary }), summary);
  assert.deepEqual(payload, { id: "18446744073709551615", accepted: true });
  for (const bad of [{ id: "-1", accepted: true }, { id: "18446744073709551616", accepted: true }, { ...payload, extra: true }]) {
    assert.throws(() => toOrder({ payload: bad })); assert.throws(() => toProvider({ request: bad })); assert.throws(() => fromProvider({ result: bad }));
  }
});
