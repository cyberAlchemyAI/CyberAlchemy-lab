import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync, mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { lowerApplicationMessaging, assertApplicationMessagingCurrent } from "../src/application-messaging.js";
import { executableFixture } from "./fixtures/application-executable-fixture.js";
import { digest, json } from "../src/domainspec-profile.js";
import { lowerApplicationDomain, assertApplicationDomainCurrent } from "../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../src/application-executable.js";
import { testTypeScript } from "./toolchain.js";

import { messagingFixture as fixture } from "./fixtures/application-integration-fixtures.js";

test("messaging paths retain distinct Event, Message, Mapping, Operation and acknowledgement identities", async () => {
  const f = await fixture(), before = json(f.binding), result = lowerApplicationMessaging(f.source, f.binding, f.compiler);
  assert.equal(json(f.binding), before);
  assert.equal(result.trace.references[0]!.event_ref, "commerce:order-submitted");
  assert.equal(result.trace.references[0]!.message_ref, "message-type:order-submitted-v1");
  assert.equal(result.trace.references[1]!.operation_ref, "commerce:submit-order");
  assert.equal(result.trace.references[1]!.acknowledgement, "application-committed");
  assert.equal(result.trace.references[1]!.deduplication, "message.messageId");
  assert.equal(result.trace.payload_type_join, "required");
  assert.equal(result.trace.runtime_delivery_observed, false);
  assert.deepEqual(f.compiler.compileMessagingComposition(JSON.parse(result.files["messaging-composition.json"])), result.composition);
  assertApplicationMessagingCurrent(f.source, f.binding, f.compiler, result);
  const changed = structuredClone(result); changed.trace.references[1]!.acknowledgement = "consumer-handler-returned";
  assert.throws(() => assertApplicationMessagingCurrent(f.source, f.binding, f.compiler, changed), /APPLICATION_MESSAGING_STALE/);
});

test("messaging rejects wrong roles, changed path policies, missing consumers and stale inputs", async () => {
  const f = await fixture();
  for (const [before, after, code] of [
    ["  event OrderSubmitted", "  event Order", "APPLICATION_MESSAGING_EVENT"],
    ["-> map OrderToMessage", "-> map Order", "APPLICATION_MESSAGING_MAPPING"],
    ["-> operation SubmitOrder", "-> operation Order", "APPLICATION_MESSAGING_OPERATION"],
    ["    -> topic OrderEvents", "    -> queue OrderEvents", "APPLICATION_MESSAGING_PATH"],
    ["acknowledge after application-commit", "acknowledge after handler-return", "APPLICATION_MESSAGING_ACK"],
    ["deduplicate by messageId", "deduplicate by payload.id", "APPLICATION_MESSAGING_DEDUP"],
  ]) {
    const source = f.source.replace(before!, after!); assert.notEqual(source, f.source);
    assert.throws(() => lowerApplicationMessaging(source, { ...f.binding, source_sha256: digest(source) }, f.compiler), new RegExp(code!));
  }
  const stale = { ...f.binding, source_sha256: "0".repeat(64) };
  assert.throws(() => lowerApplicationMessaging(f.source, stale, f.compiler), /APPLICATION_MESSAGING_SOURCE/);
  const totality = structuredClone(f.binding); totality.composition.message_mappings[0].total = false;
  assert.throws(() => lowerApplicationMessaging(f.source, totality, f.compiler), /APPLICATION_MESSAGING_MAPPING/);
  const coverage = structuredClone(f.binding); coverage.composition.message_mappings[1].input_paths[0].parameter = "hidden";
  assert.throws(() => lowerApplicationMessaging(f.source, coverage, f.compiler), /APPLICATION_MESSAGING_COVERAGE/);
  const failure = structuredClone(f.binding); failure.composition.delivery_policies[0].terminal_disposition = "retain"; failure.composition.delivery_policies[0].dead_letter_channel_ref = null;
  assert.throws(() => lowerApplicationMessaging(f.source, failure, f.compiler), /APPLICATION_MESSAGING_FAILURE/);
});

test("handler-return acknowledgement remains distinct when explicitly selected on both sides", async () => {
  const f = await fixture(); f.source = f.source.replace("acknowledge after application-commit", "acknowledge after handler-return");
  f.binding.source_sha256 = digest(f.source); f.binding.composition.acknowledgement_boundaries[0].condition = "consumer-handler-returned";
  const result = lowerApplicationMessaging(f.source, f.binding, f.compiler);
  assert.equal(result.trace.references[1]!.acknowledgement, "consumer-handler-returned");
  assert.equal(result.composition.runtime_delivery_observed, false);
});

test("public compiler adapter enforces existing typed messaging and operation request joins", async () => {
  const compiler = await loadDomainSpecCompiler();
  const example = path.join(compiler.binding.package_root, "examples/reconciled-commerce");
  const graph = compiler.compileProject(path.join(example, "source")).graph;
  const source = JSON.parse(readFileSync(path.join(example, "integrations/application.json"), "utf8"));
  const selection = JSON.parse(readFileSync(path.join(example, "selections/typescript.json"), "utf8"));
  const result = compiler.compileMessagingRuntimeBindings(graph, source.messaging, selection);
  assert.equal(result.domain_source_manifest_sha256, graph.source_manifest.manifest_sha256);
  assert.equal(result.runtime_bindings.find((b: any) => b.direction === "logical-to-message").inputs[0].source.kind, "event-identity-reference");
  assert.equal(result.runtime_delivery_observed, false);
  const bad = structuredClone(source.messaging);
  bad.message_mappings.find((m: any) => m.direction === "message-to-application").request_parameters[0].parameter = "unknown";
  assert.throws(() => compiler.compileMessagingRuntimeBindings(graph, bad, selection), /request parameters must exactly cover/);
});

test("one authored source joins identity payload, message Mapping and exact Operation request", async t => {
  const f = await fixture(), base = executableFixture();
  const source = f.source.replace(/mapping OrderToMessage:[\s\S]*?publication PublishOrder:/, `value-object OrderNotice:
  id UInt64
mapping OrderToMessage:
  input order -> Order.id
  target OrderNotice
  total true
  field id <- order.id
mapping MessageToOrder:
  input payload OrderNotice
  target OrderNotice
  total true
  field id <- payload.id
operation ReceiveNotice:
  input OrderNotice
  output OrderNotice
  requires IdentityValid
publication PublishOrder:`).replace("-> operation SubmitOrder", "-> operation ReceiveNotice");
  const binding = structuredClone(f.binding); binding.source_sha256 = digest(source);
  binding.composition.subscription_bindings[0].operation_ref = "commerce:receive-notice";
  binding.composition.integration_kernel.integration_bindings[1].logical_boundary_ref = "commerce:receive-notice";
  binding.composition.message_mappings[1].target_ref = "commerce:receive-notice#request";
  const bindings = { ...base.bindings, source_sha256: digest(source), formal: { ...base.bindings.formal, source_sha256: digest(source) }, declarations: {
    ...base.bindings.declarations,
    OrderSubmitted: { ontology: "FIXTURE-ORDER-SUBMITTED", meaning: "An occurrence carrying the Order identity." },
    OrderNotice: { ontology: "FIXTURE-ORDER-NOTICE", meaning: "An explicitly projected order identity.", invariants: ["IdentityValid"], properties: { id: { ontology: "FIXTURE-ORDER-NOTICE#id", meaning: "The projected identity." } } },
    OrderToMessage: { ontology: "FIXTURE-ORDER-TO-MESSAGE", meaning: "Project the Event identity into a notice." },
    MessageToOrder: { ontology: "FIXTURE-MESSAGE-TO-ORDER", meaning: "Project the explicit message payload into a notice." },
    ReceiveNotice: { ontology: "FIXTURE-RECEIVE-NOTICE", meaning: "Return the supplied notice without inventing persistence.", failure_continuation: "return-notice-error" },
  } };
  const context = { binding, compiler: f.compiler };
  assert.throws(() => lowerApplicationDomain(source, bindings, base.sources), /APPLICATION_INTEGRATION_LOWERING_REQUIRED/);
  const formation = lowerApplicationDomain(source, bindings, base.sources, undefined, context);
  assert.ok(formation.messaging);
  for (const [name, bytes] of Object.entries(formation.messaging.files)) assert.equal(formation.trace.formed_files[name]!.sha256, digest(bytes));
  assertApplicationDomainCurrent(source, bindings, base.sources, formation, undefined, context);
  for (const kind of ["changed", "missing", "extra"] as const) {
    const changed = structuredClone(formation);
    if (kind === "changed") changed.messaging!.trace.references[0]!.event_ref = "commerce:other";
    if (kind === "missing") delete (changed.files as Record<string, string>)["messaging-trace.json"];
    if (kind === "extra") (changed.files as Record<string, string>)["extra.json"] = "{}";
    assert.throws(() => assertApplicationDomainCurrent(source, bindings, base.sources, changed, undefined, context), /APPLICATION_FORMATION_STALE/);
  }
  const interpretation = { ...base.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(source, bindings, base.sources, interpretation, undefined, context);
  const selection: any = structuredClone(base.execution.selection);
  selection.factories.push({ selector: "commerce:order-notice", base_validators: [{ rule: "commerce:identity-valid", arguments: [{ parameter: "identity", field: "id" }] }], extensions: [] });
  selection.operations.push({ schema_version: "domainspec.operation-action-bindings/v1-candidate", selector: "commerce:receive-notice",
    inputs: [{ name: "request", type: { kind: "named", selector: "commerce:order-notice" } }], reads: [],
    guards: [{ selector: "commerce:identity-valid", arguments: [{ parameter: "identity", value: { op: "path", root: "request", properties: ["FIXTURE-ORDER-NOTICE#id"] } }] }], writes: [], events: [],
    result: { type: { kind: "named", selector: "commerce:order-notice" }, value: { op: "path", root: "request", properties: [] } }, atomicity: "state-and-outbox", continuation: "awaited-settlement" });
  const execution = { ...base.execution, selection, projection_sha256: digest(json(projection)) };
  const candidate = prepareApplicationExecutable(source, bindings, base.sources, interpretation, execution, f.compiler, undefined, context);
  const root = mkdtempSync(path.join(tmpdir(), "alch-messaging-join-")); t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const [relative, bytes] of Object.entries(candidate.projectFiles)) {
    const target = path.join(root, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes);
  }
  const graph = f.compiler.compileProject(root).graph;
  const compiled = compileApplicationExecutable(candidate, graph, f.compiler);
  assert.deepEqual(compiled.messaging, formation.messaging);
  assert.equal(compiled.trace.messaging_join_sha256, digest(json(compiled.messagingJoin)));
  assert.equal(compiled.messagingJoin.domain_source_manifest_sha256, graph.source_manifest.manifest_sha256);
  const outbound = compiled.messagingJoin.runtime_bindings.find((b: any) => b.direction === "logical-to-message");
  assert.deepEqual(outbound.inputs[0].source, { kind: "event-identity-reference", reference: "commerce:order-submitted", path: ["order-id"] });
  assert.deepEqual(outbound.result_type, { kind: "named", selector: "commerce:order-notice" });
  assert.equal(compiled.messagingJoin.operation_requests[0].operation_ref, "commerce:receive-notice");
  assert.equal(compiled.messagingJoin.runtime_delivery_observed, false);
  assert.deepEqual(compiled, compileApplicationExecutable(candidate, graph, f.compiler));
  const generated = path.join(root, "generated"), js = path.join(root, "js");
  for (const artifact of compiled.view.artifacts) {
    const target = path.join(generated, artifact.relative_path); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, artifact.content);
  }
  execFileSync(process.execPath, [testTypeScript(), "--ignoreConfig", "--strict", "--skipLibCheck", "--target", "ES2022", "--module", "commonjs",
    "--rootDir", generated, "--outDir", js, ...compiled.view.artifacts.map(a => path.join(generated, a.relative_path))], { encoding: "utf8" });
  const load = (suffix: string, name: string) => {
    const artifact = compiled.view.artifacts.find(a => a.relative_path.endsWith(suffix)); assert.ok(artifact);
    return createRequire(import.meta.url)(path.join(js, artifact.relative_path.replace(/\.ts$/, ".js")))[name];
  };
  const event = load("/events/order-submitted.ts", "eventOrderSubmitted")({ occurrence: { "event-id": "notice-1" }, occurredAt: "fixture-time", payload: { "order-id": "18446744073709551615" } });
  const project = load("/mappings/order-to-message.ts", "mappingOrderToMessage");
  const receiveMap = load("/mappings/message-to-order.ts", "mappingMessageToOrder");
  // Explicit test adapter follows the compiled paths; no transport execution is claimed.
  const payload = project({ order: event.payload[outbound.inputs[0].source.path[0]] });
  const inbound = compiled.messagingJoin.runtime_bindings.find((b: any) => b.direction === "message-to-application");
  assert.deepEqual(inbound.inputs[0].source.path, ["payload"]);
  const message = { payload }, request = receiveMap({ payload: message[inbound.inputs[0].source.path[0] as "payload"] });
  assert.deepEqual(request, { id: 18446744073709551615n });
  assert.throws(() => project({ order: -1n }));
  assert.throws(() => project({ order: { id: 1n, accepted: true } }));
  assert.throws(() => receiveMap({ payload: { id: "18446744073709551616" } }));
  let committed = 0;
  const outcome = await load("/operations/receive-notice.ts", "operationReceiveNotice")({ request }, { store: { begin: async () => ({
    read: async () => { throw Error("unexpected read"); }, rollback: async () => {},
    commit: async (batch: any) => { assert.deepEqual(batch.writes, []); assert.deepEqual(batch.events, []); committed++; return { status: "committed" }; },
  }) } });
  assert.equal(outcome.status, "committed"); assert.equal(committed, 1);
  const changed = structuredClone(binding); changed.composition.message_mappings[1].request_parameters[0].parameter = "wrong";
  const badContext = { ...context, binding: changed };
  assert.throws(() => lowerApplicationRuleProjections(source, bindings, base.sources, interpretation, undefined, badContext), /RULE_PROJECTION_STALE/);
  const badFormation = lowerApplicationDomain(source, bindings, base.sources, undefined, badContext);
  const badInterpretation = { ...interpretation, formation_sha256: digest(json(badFormation)) };
  const badProjection = lowerApplicationRuleProjections(source, bindings, base.sources, badInterpretation, undefined, badContext);
  const badCandidate = prepareApplicationExecutable(source, bindings, base.sources, badInterpretation, { ...execution, projection_sha256: digest(json(badProjection)) }, f.compiler, undefined, badContext);
  assert.throws(() => compileApplicationExecutable(badCandidate, graph, f.compiler), /request parameters must exactly cover/);
});
