import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import path from "node:path";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { parseDomainSource } from "../src/parser.js";
import { lowerApplicationRuntimeProfiles, assertApplicationRuntimeProfilesCurrent } from "../src/application-runtime-profile.js";
import { lowerApplicationDomain, assertApplicationDomainCurrent } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections, assertApplicationRuleProjectionCurrent } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable } from "../src/application-executable.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { digest, json } from "../src/domainspec-profile.js";

const base = 'domain commerce "Commerce"\nprofile application-v1\nowner fixture-owner\n';
const ts = `runtime-profile Production:
  target typescript
  selection provider-selection:reference-typescript
  provider-pack domainspec.reference-postgresql16-nats-http/v1-candidate
  runtime node "26.8.1"
  provider persistence postgresql:16
  provider messaging nats:jetstream
  provider outbound-http http:outbound
  provider inbound-http http:inbound
  environment DATABASE_URL secret-reference required
  environment INBOUND_BIND_ADDRESS endpoint-reference required
  environment NATS_URL endpoint-reference required
  environment PAYMENT_BASE_URL endpoint-reference required
  environment WEBHOOK_SECRET secret-reference required
  environment ORDER_EVENTS_TOPIC endpoint-reference required
  messaging-destination channel:order-events-topic ORDER_EVENTS_TOPIC
`;
const python = ts.replaceAll("typescript", "python").replace('node "26.8.1"', 'python ">=3.11"');
const rust = ts.replaceAll("typescript", "rust").replace('node "26.8.1"', 'rust-edition "2024"');

test("runtime profile lowering emits exact existing provider contracts for all three targets", async () => {
  const compiler = await loadDomainSpecCompiler();
  for (const [language, text] of [["typescript", ts], ["python", python], ["rust", rust]]) {
    const source = base + text;
    const lowered = lowerApplicationRuntimeProfiles(source, "Production", compiler);
    const expected = JSON.parse(readFileSync(path.join(compiler.binding.package_root, "examples/reconciled-commerce/providers", language + ".json"), "utf8"));
    assert.deepEqual(lowered.selected.selection, expected);
    assert.deepEqual(JSON.parse(lowered.files["runtime-profiles/production/providers.json"]!), expected);
    assert.equal(lowered.trace.runtime_guarantees_observed, false);
    assert.equal(lowered.trace.authority_effect, "none");
    assertApplicationRuntimeProfilesCurrent(source, "Production", compiler, lowered);
    assert.deepEqual(lowerApplicationRuntimeProfiles(source, "Production", compiler), lowered);
  }
});

test("runtime authoring rejects incomplete, duplicate, executable and credential-valued clauses without echoing credentials", async () => {
  const compiler = await loadDomainSpecCompiler();
  for (const bad of [
    ts.replace("  target typescript\n", ""), ts.replace("  provider messaging nats:jetstream\n", ""),
    ts.replace("  messaging-destination channel:order-events-topic ORDER_EVENTS_TOPIC\n", ""),
    ts + "  target typescript\n", ts + "  environment DATABASE_URL secret-reference required\n",
    ts + "  runtime node \"26.8.1\"\n", ts + "  provider persistence postgresql:16\n",
    ts + "  messaging-destination channel:order-events-topic ANOTHER_TOPIC\n",
    ts.replace("provider persistence postgresql:16", "provider persistence postgresql:16 library pg version 8.23.0"),
    ts + "  password \"never-echo-this\"\n", ts + "  environment DATABASE_URL = \"never-echo-this\"\n",
    ts + "  do ConnectDatabase\n", ts + "  provider-pack another/pack\n",
  ]) assert.throws(() => lowerApplicationRuntimeProfiles(base + bad, "Production", compiler), e => {
    assert.ok(e instanceof Error); assert.doesNotMatch(e.message, /never-echo-this/); return true;
  });
  assert.throws(() => parseDomainSource((base + ts).replace("profile application-v1\n", "")), /ALCH_PROFILE_REQUIRED/);
});

test("provider/runtime compatibility is owned by DomainSpec and cannot fall back", async () => {
  const compiler = await loadDomainSpecCompiler();
  for (const [bad, code] of [
    [ts.replace("target typescript", "target python"), "DS_PROVIDER_SELECTION_SCHEMA"],
    [ts.replace("26.8.1", "24.0.0"), "DS_PROVIDER_RUNTIME_REQUIREMENTS"],
    [ts.replace('node "26.8.1"', 'python ">=3.11"'), "DS_PROVIDER_SELECTION_SCHEMA"],
    [ts.replace("postgresql:16", "unknown:provider"), "DS_PROVIDER_SELECTION_REALIZATION"],
    [ts.replace("postgresql:16", "postgresql:17"), "DS_PROVIDER_SELECTION_REALIZATION"],
    [ts.replace("outbound-http http:outbound", "outbound-http http:inbound"), "DS_PROVIDER_SELECTION_REALIZATION"],
    [ts.replace("domainspec.reference-postgresql16-nats-http/v1-candidate", "unknown/pack"), "DS_PROVIDER_SELECTION_SCHEMA"],
    [ts.replace("WEBHOOK_SECRET secret-reference", "WEBHOOK_SECRET endpoint-reference"), "DS_PROVIDER_SELECTION_CONFIGURATION"],
    [ts.replace("  environment WEBHOOK_SECRET secret-reference required\n", ""), "DS_PROVIDER_SELECTION_CONFIGURATION"],
  ]) assert.throws(() => lowerApplicationRuntimeProfiles(base + bad, "Production", compiler), e => e instanceof Error && e.message.includes(code!));
});

test("multiple profiles require exact selection, reject collisions, and validate even unselected profiles", async () => {
  const compiler = await loadDomainSpecCompiler();
  const source = base + ts + python.replace("Production", "PythonRuntime");
  assert.throws(() => lowerApplicationRuntimeProfiles(source, "", compiler), /APPLICATION_RUNTIME_SELECTION/);
  assert.throws(() => lowerApplicationRuntimeProfiles(source, "production", compiler), /APPLICATION_RUNTIME_SELECTION/);
  assert.equal(lowerApplicationRuntimeProfiles(source, "PythonRuntime", compiler).selected.selection.language, "python");
  assert.throws(() => lowerApplicationRuntimeProfiles(source.replace("runtime python \">=3.11\"", "runtime python \">=3.12\""), "Production", compiler), /DS_PROVIDER_RUNTIME_REQUIREMENTS/);
  assert.throws(() => parseDomainSource(base + ts + ts.replace("Production", "Other")), /APPLICATION_RUNTIME_COLLISION/);
  assert.throws(() => parseDomainSource(base + ts + python.replace("Production", "production")), /APPLICATION_RUNTIME_COLLISION/);
});

test("runtime currentness binds source bytes, selected profile, requirements and every emitted file", async () => {
  const compiler = await loadDomainSpecCompiler();
  const source = base + ts + python.replace("Production", "PythonRuntime");
  const current = lowerApplicationRuntimeProfiles(source, "Production", compiler);
  assert.throws(() => assertApplicationRuntimeProfilesCurrent(source + "\n", "Production", compiler, current), /APPLICATION_RUNTIME_STALE/);
  assert.throws(() => assertApplicationRuntimeProfilesCurrent(source, "PythonRuntime", compiler, current), /APPLICATION_RUNTIME_STALE/);
  const forged = structuredClone(current);
  forged.files["runtime-profiles/production/providers.json"] = "{}\n";
  assert.throws(() => assertApplicationRuntimeProfilesCurrent(source, "Production", compiler, forged), /APPLICATION_RUNTIME_STALE/);
  const altered = structuredClone(current);
  altered.selected.requirements.node = "0.0.0";
  assert.throws(() => assertApplicationRuntimeProfilesCurrent(source, "Production", compiler, altered), /APPLICATION_RUNTIME_STALE/);
});

test("same-source runtime profiles preserve domain/formal meaning and bind executable target without executing providers", async () => {
  const compiler = await loadDomainSpecCompiler();
  const f = executableFixture();
  const before = lowerApplicationDomain(f.source, f.bindings, f.sources);
  const source = f.source + ts + python.replace("Production", "PythonRuntime");
  const bindings = structuredClone(f.bindings);
  bindings.source_sha256 = digest(source); bindings.formal.source_sha256 = digest(source);
  assert.throws(() => lowerApplicationDomain(source, bindings, f.sources), /APPLICATION_RUNTIME_LOWERING_REQUIRED/);
  const context = { profile: "Production", compiler };
  const formation = lowerApplicationDomain(source, bindings, f.sources, undefined, undefined, undefined, context);
  assert.deepEqual(formation.projectFiles, before.projectFiles);
  assert.deepEqual(formation.model.formal_claims, before.model.formal_claims);
  assert.deepEqual(formation.model.rules, before.model.rules);
  assert.deepEqual(formation.model.declarations, before.model.declarations);
  assert.deepEqual(formation.conditions, before.conditions);
  assert.deepEqual(formation.trace.declarations, before.trace.declarations);
  assertApplicationDomainCurrent(source, bindings, f.sources, formation, undefined, undefined, undefined, context);
  const interpretation = { ...f.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(source, bindings, f.sources, interpretation, undefined, undefined, undefined, context);
  assertApplicationRuleProjectionCurrent(source, bindings, f.sources, interpretation, projection, undefined, undefined, undefined, context);
  const execution = { ...f.execution, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(source, bindings, f.sources, interpretation, execution, compiler, undefined, undefined, undefined, context);
  assert.equal(candidate.projection.formation.runtime!.selected.selection.language, "typescript");
  assert.equal(candidate.projection.formation.runtime!.selected.runtime_guarantees_observed, false);
  const other = { profile: "PythonRuntime", compiler };
  const pyFormation = lowerApplicationDomain(source, bindings, f.sources, undefined, undefined, undefined, other);
  const pyInterpretation = { ...interpretation, formation_sha256: digest(json(pyFormation)) };
  const pyProjection = lowerApplicationRuleProjections(source, bindings, f.sources, pyInterpretation, undefined, undefined, undefined, other);
  assert.throws(() => prepareApplicationExecutable(source, bindings, f.sources, pyInterpretation,
    { ...execution, projection_sha256: digest(json(pyProjection)) }, compiler, undefined, undefined, undefined, other), /APPLICATION_RUNTIME_TARGET/);
});
