import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { lowerApplicationPersistence, assertApplicationPersistenceCurrent } from "../src/application-persistence.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { digest, json } from "../src/domainspec-profile.js";
import { lowerApplicationDomain, assertApplicationDomainCurrent } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections, assertApplicationRuleProjectionCurrent } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";

import { persistenceFixture as fixture } from "./fixtures/application-integration-fixtures.js";

test("persistence binds authored Entity, Query and writes to the current backend contract", async () => {
  const f = await fixture(), before = json(f.binding), result = lowerApplicationPersistence(f.source, f.binding, f.compiler);
  assert.equal(json(f.binding), before);
  assert.equal(result.composition.schema_version, "domainspec.persistence-composition/v2-candidate");
  assert.deepEqual(f.compiler.compilePersistenceComposition(JSON.parse(result.files["persistence-composition.json"])), result.composition);
  assert.deepEqual(result.sourceComposition, f.binding.composition);
  assert.equal(result.trace.compiled_composition_sha256, digest(result.files["persistence-compiled.json"]));
  assert.equal(result.trace.references[0]!.entity, "commerce:order");
  assert.deepEqual(result.trace.references[0]!.queries.map(q => [q.selector, q.result_cardinality]), [["commerce:find-order", "optional"]]);
  assert.deepEqual(result.trace.references[0]!.operations.map(o => o.selector), ["commerce:submit-order"]);
  assert.equal(result.composition.runtime_guarantees_observed, false);
  assert.equal(result.trace.authority_effect, "none");
  assert.deepEqual(result, lowerApplicationPersistence(f.source, f.binding, f.compiler));
  assertApplicationPersistenceCurrent(f.source, f.binding, f.compiler, result);
  const changed = structuredClone(result); changed.trace.references[0]!.queries[0]!.result_cardinality = "list";
  assert.throws(() => assertApplicationPersistenceCurrent(f.source, f.binding, f.compiler, changed), /APPLICATION_PERSISTENCE_STALE/);
  const stale = structuredClone(f.binding); stale.source_sha256 = "0".repeat(64);
  assert.throws(() => lowerApplicationPersistence(f.source, stale, f.compiler), /APPLICATION_PERSISTENCE_SOURCE/);
});

test("persistence rejects wrong source roles and mismatched physical coverage", async () => {
  const f = await fixture();
  for (const [before, after, code] of [
    ["stores Order", "stores SubmitOrder", "APPLICATION_PERSISTENCE_ENTITY"],
    ["serves FindOrder", "serves SubmitOrder", "APPLICATION_PERSISTENCE_QUERY"],
    ["accepts-writes-from SubmitOrder", "accepts-writes-from FindOrder", "APPLICATION_PERSISTENCE_OPERATION"],
    ["  writes Order\n", "", "APPLICATION_PERSISTENCE_OPERATION"],
  ]) {
    const source = f.source.replace(before!, after!); assert.notEqual(source, f.source);
    assert.throws(() => lowerApplicationPersistence(source, { ...f.binding, source_sha256: digest(source) }, f.compiler), new RegExp(code!));
  }
  const missing = structuredClone(f.binding); missing.composition.persistence_mappings[0].field_mappings.pop();
  assert.throws(() => lowerApplicationPersistence(f.source, missing, f.compiler), /APPLICATION_PERSISTENCE_COVERAGE/);
  const wrong = structuredClone(f.binding); wrong.composition.persistence_mappings[0].field_mappings[1].logical_shape = "enum";
  assert.throws(() => lowerApplicationPersistence(f.source, wrong, f.compiler), /APPLICATION_PERSISTENCE_SHAPE/);
  const hidden = structuredClone(f.binding); (hidden.declarations as any).Hidden = hidden.declarations.Orders;
  assert.throws(() => lowerApplicationPersistence(f.source, hidden, f.compiler), /APPLICATION_PERSISTENCE_BINDING/);
  const cross = structuredClone(f.binding), c = cross.composition;
  const persistence = { ...c.persistence_bindings[0], binding_id: "persistence-binding:other", integration_binding_ref: "binding:other", resource_ref: "resource:other" };
  c.persistence_bindings.push(persistence);
  c.integration_kernel.integration_bindings.push({ ...c.integration_kernel.integration_bindings[0], binding_id: "binding:other", provider_realization_ref: "provider-realization:other" });
  c.integration_kernel.provider_realizations.push({ ...c.integration_kernel.provider_realizations[0], realization_id: "provider-realization:other", resource_ref: "resource:other" });
  c.transaction_guarantees[0].persistence_binding_refs.push(persistence.binding_id);
  assert.throws(() => lowerApplicationPersistence(f.source, cross, f.compiler), /APPLICATION_PERSISTENCE_TRANSACTION/);
});

test("read-only and write-only persistence do not acquire hidden consumers", async () => {
  const f = await fixture();
  for (const clause of ["  serves FindOrder\n", "  accepts-writes-from SubmitOrder\n"]) {
    const source = f.source.replace(clause, "");
    const result = lowerApplicationPersistence(source, { ...f.binding, source_sha256: digest(source) }, f.compiler);
    assert.equal(clause.includes("serves") ? result.trace.references[0]!.queries.length : result.trace.references[0]!.operations.length, 0);
  }
});

test("one source joins persistence artifacts to exact domain, Query and executable write bindings", async t => {
  const f = await fixture(), base = executableFixture();
  const bindings = { ...base.bindings, source_sha256: digest(f.source), formal: { ...base.bindings.formal, source_sha256: digest(f.source) },
    declarations: { ...base.bindings.declarations, FindOrder: { ontology: "FIXTURE-FIND-ORDER", meaning: "Select at most one explicitly eligible order." } } };
  const context = { binding: f.binding, compiler: f.compiler };
  assert.throws(() => lowerApplicationDomain(f.source, bindings, base.sources), /APPLICATION_INTEGRATION_LOWERING_REQUIRED/);
  const formation = lowerApplicationDomain(f.source, bindings, base.sources, context);
  assert.ok(formation.persistence);
  for (const [name, bytes] of Object.entries(formation.persistence.files)) {
    assert.equal(formation.trace.formed_files[name]!.sha256, digest(bytes));
    assert.equal((formation.files as Record<string, string>)[name], bytes);
  }
  assertApplicationDomainCurrent(f.source, bindings, base.sources, formation, context);
  const altered = structuredClone(formation); altered.persistence!.trace.references[0]!.entity = "commerce:other";
  assert.throws(() => assertApplicationDomainCurrent(f.source, bindings, base.sources, altered, context), /APPLICATION_FORMATION_STALE/);
  const interpretation = { ...base.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(f.source, bindings, base.sources, interpretation, context);
  assertApplicationRuleProjectionCurrent(f.source, bindings, base.sources, interpretation, projection, context);
  const execution = { ...base.execution, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(f.source, bindings, base.sources, interpretation, execution, f.compiler, context);
  const root = mkdtempSync(path.join(tmpdir(), "alch-persistence-join-")); t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const [relative, bytes] of Object.entries(candidate.projectFiles)) {
    const target = path.join(root, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  }
  const graph = f.compiler.compileProject(root).graph;
  const compiled = compileApplicationExecutable(candidate, graph, f.compiler);
  assert.deepEqual(compiled.persistence, formation.persistence);
  assert.equal(compiled.trace.persistence_composition_sha256, formation.persistence.trace.composition_sha256);
  assert.ok(compiled.view.artifacts.some(a => a.relative_path.endsWith("/find-order.ts")));
  assert.ok(compiled.view.artifacts.some(a => a.relative_path.endsWith("/submit-order.ts")));
  assert.equal(graph.relationships.some(e => e.relationship === "serves" || e.relationship === "accepts-writes-from"), false);
  const drift = structuredClone(f.binding); drift.composition.persistence_mappings[0].physical_models[0].physical_name = "changed_orders";
  assert.throws(() => lowerApplicationRuleProjections(f.source, bindings, base.sources, interpretation, { ...context, binding: drift }), /RULE_PROJECTION_STALE/);
  const extra = f.source + `publication PublishOrder:
  event MissingEvent
    -> map MissingMap
    -> message MissingMessage
    -> topic MissingTopic
`;
  const extraBindings = { ...bindings, source_sha256: digest(extra), formal: { ...bindings.formal, source_sha256: digest(extra) } };
  assert.throws(() => lowerApplicationDomain(extra, extraBindings, base.sources, { ...context, binding: { ...f.binding, source_sha256: digest(extra) } }), /APPLICATION_INTEGRATION_LOWERING_REQUIRED/);
});
