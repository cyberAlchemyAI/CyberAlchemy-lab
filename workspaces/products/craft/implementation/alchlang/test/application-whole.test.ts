import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync, mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { compileApplicationWhole, assertApplicationWholeCurrent } from "../src/application-whole.js";
import { wholeApplicationFixture } from "./fixtures/application-whole-fixture.js";
import { prepareApplicationExecutable } from "../src/application-executable.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { digest, json } from "../src/domainspec-profile.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";

test("one Alch source joins domain, optional Query, messaging, named API and runtime partitions", async t => {
  const f = await wholeApplicationFixture();
  const root = mkdtempSync(path.join(tmpdir(), "alch-whole-source-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const [relative, bytes] of Object.entries(f.candidate.projectFiles)) {
    const file = path.join(root, relative); mkdirSync(path.dirname(file), { recursive: true }); writeFileSync(file, bytes);
  }
  const graph = f.compiler.compileProject(root).graph;
  const result = compileApplicationWhole(f.candidate, graph, f.observation, f.compiler);
  assert.equal(result.runtimeBinding.providers.length, 5);
  assert.equal(result.runtimeBinding.binding.domain_source_manifest_sha256, graph.source_manifest.manifest_sha256);
  const query = graph.nodes.find(n => n.selector === "commerce:find-order")!.body as any;
  assert.equal(query.typed_contract.schema_version, "domainspec.typed-query/v2");
  assert.equal(query.typed_contract.result_cardinality, "optional");
  assert.equal(result.executable.persistence!.trace.references[0]!.queries[0]!.result_cardinality, "optional");
  assert.deepEqual(result.runtimeBinding.binding.application_graph.operation_requests.map((r: any) => r.operation_ref).sort(), ["commerce:receive-notice", "commerce:submit-order"]);
  assert.equal(result.trace.runtime_guarantees_observed, false);
  assert.equal(result.application.runtime_guarantees_observed, false);
  assert.equal(result.trace.whole_application_plan_sha256, result.wholeApplication.plan_sha256);
  assert.equal(result.trace.provider_application_plan_sha256, result.application.plan_sha256);
  assert.equal(result.application.whole_application_plan_sha256, result.wholeApplication.plan_sha256);
  assert.ok(result.application.artifacts.some(a=>a.relative_path==="src/integrations/application-request-handlers.ts"));
  assert.ok(result.application.artifacts.some(a=>a.relative_path==="src/providers/reference/bootstrap.ts"));
  assert.ok(result.application.artifacts.some(a=>a.relative_path===".domainspec/providers/manifest.json"));
  assert.throws(()=>f.compiler.composeApplicationArtifacts(structuredClone(result.executable.plan),result.integrationSource,result.runtimeBinding.binding), /registered reconciled/);
  assert.throws(()=>f.compiler.composeProviderApplicationArtifacts(structuredClone(result.wholeApplication),f.candidate.projection.formation.runtime!.selected.selection,result.integrationSource), /WHOLE_APPLICATION/);
  const outbound = result.runtimeBinding.providers.find((p: any) => p.role === "outbound_http");
  assert.equal(outbound.logical_boundary_ref, "commerce:order-api");
  assert.equal(result.integrationSource.external_api.external_api_contracts[0].contract_id, "contract:payment-gateway");
  const publicMapping = result.runtimeBinding.binding.application_graph.runtime_bindings.find((r: any) => r.mapping_ref === "commerce:request-to-order");
  assert.deepEqual(publicMapping.inputs[0].value_type, { kind: "contract", interface_selector: "commerce:order-api", contract_id: "submit-request" });
  assert.deepEqual(result.runtimeBinding.binding.application_graph.runtime_bindings.find((r: any) => r.mapping_ref === "commerce:order-to-message").inputs[0].source,
    { kind: "event-identity-reference", reference: "commerce:order-submitted", path: ["order-id"] });
  assertApplicationWholeCurrent(f.candidate, graph, f.observation, f.compiler, result);
  for (const mode of ["changed", "missing", "extra"]) {
    const changed = structuredClone(result);
    const files = changed.files as Record<string, string>;
    if (mode === "changed") files["application-integration-source.json"] = "{}";
    if (mode === "missing") delete files["application-runtime-binding.json"];
    if (mode === "extra") files["hidden.json"] = "{}";
    assert.throws(() => assertApplicationWholeCurrent(f.candidate, graph, f.observation, f.compiler, changed), /APPLICATION_WHOLE_STALE/);
  }
  const other = await wholeApplicationFixture("provider-selection:commerce-other");
  assert.deepEqual(other.candidate.projectFiles, f.candidate.projectFiles, "runtime identity does not rewrite domain meaning");
  assert.throws(() => assertApplicationWholeCurrent(other.candidate, graph, other.observation, other.compiler, result), /APPLICATION_WHOLE_STALE/);
  assert.throws(() => compileApplicationWhole(f.candidate, structuredClone(graph), f.observation, f.compiler));
  // A well-formed integration reference can still be unresolved in the domain.
  f.contexts[0].binding.composition.integration_kernel.failure_mappings[0].cases[0].failure_outcome_ref = "commerce:missing-operation";
  const changedFormation = lowerApplicationDomain(f.source, f.bindings, f.sources, ...f.contexts);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(changedFormation)) };
  const projection = lowerApplicationRuleProjections(f.source, f.bindings, f.sources, interpretation, ...f.contexts);
  const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, interpretation,
    { ...f.execution, projection_sha256: digest(json(projection)) }, f.compiler, ...f.contexts);
  assert.throws(() => compileApplicationWhole(candidate, graph, f.observation, f.compiler), /selector.*unresolved|unresolved.*selector/i);
});

test("public DomainSpec adapter joins the existing application graph, runtime and Operation request contracts", async () => {
  const compiler = await loadDomainSpecCompiler();
  const root = path.join(compiler.binding.package_root, "examples/reconciled-commerce");
  const read = (relative: string) => JSON.parse(readFileSync(path.join(root, relative), "utf8"));
  const graph = compiler.compileProject(path.join(root, "source")).graph;
  const source = read("integrations/application.json"), providers = read("providers/typescript.json"), selection = read("selections/typescript.json");
  const result = compiler.compileApplicationRuntimeBinding(graph, source, providers, selection);
  assert.equal(result.providers.length, 5);
  assert.ok(result.binding.application_graph.operation_requests.length);
  assert.equal(result.binding.domain_source_manifest_sha256, graph.source_manifest.manifest_sha256);
  assert.deepEqual(compiler.compileApplicationRuntimeBinding(graph, source, providers, selection), result);
  assert.throws(() => compiler.compileApplicationRuntimeBinding(graph, source, read("providers/python.json"), selection), /DOMAINSPEC_APPLICATION_RUNTIME_TARGET/);
  const invalid = structuredClone(selection);
  invalid.operations[0].inputs[0].name = "incorrect";
  assert.throws(() => compiler.compileApplicationRuntimeBinding(graph, source, providers, invalid), /REQUEST|request/);
});

test("combined formation rejects stale partitions and normalized declaration collisions", async () => {
  const f = await wholeApplicationFixture();
  const original = f.contexts[0].binding.source_sha256;
  f.contexts[0].binding.source_sha256 = "0".repeat(64);
  assert.throws(() => lowerApplicationDomain(f.source, f.bindings, f.sources, ...f.contexts), /APPLICATION_PERSISTENCE_SOURCE/);
  f.contexts[0].binding.source_sha256 = original;
  const source = f.source + "entity order:\n  id UInt64\n  identity id\n";
  const bindings = structuredClone(f.bindings);
  bindings.source_sha256 = digest(source); bindings.formal.source_sha256 = digest(source);
  (bindings.declarations as any).order = structuredClone(bindings.declarations.Order);
  for (const context of f.contexts.slice(0, 3)) if ("binding" in context) context.binding.source_sha256 = digest(source);
  assert.throws(() => lowerApplicationDomain(source, bindings, f.sources, ...f.contexts), /APPLICATION_SYMBOL_COLLISION/);
});

test("whole application does not invent missing partitions, trust forged preparation, or ignore observation source drift", async t => {
  const compiler = await loadDomainSpecCompiler();
  const f = executableFixture();
  const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, f.interpretation, f.execution, compiler);
  const root = mkdtempSync(path.join(tmpdir(), "alch-whole-boundary-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const [relative, bytes] of Object.entries(candidate.projectFiles)) {
    const file = path.join(root, relative); mkdirSync(path.dirname(file), { recursive: true }); writeFileSync(file, bytes);
  }
  const graph = compiler.compileProject(root).graph;
  const observation = { schema_version: "alchlang.application-observation/v1-candidate", source_sha256: digest(f.source),
    source_id: "integration-source:commerce", disclosure_policy: {}, orodi_binding: {} };
  assert.throws(() => compileApplicationWhole(candidate, graph, {}, compiler), /APPLICATION_WHOLE_OBSERVATION/);
  assert.throws(() => compileApplicationWhole(candidate, graph, { ...observation, source_sha256: "0".repeat(64) }, compiler), /APPLICATION_WHOLE_STALE/);
  assert.throws(() => compileApplicationWhole(candidate, graph, observation, compiler), /APPLICATION_WHOLE_PARTITIONS/);
  assert.throws(() => compileApplicationWhole(structuredClone(candidate), graph, observation, compiler), /APPLICATION_EXECUTION_UNVALIDATED/);
});
