import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { canonicalJson, compileBindingManifest, generatedRelativePath, LANGUAGES, loadProfilePackage, PACKAGE_ROOT, readBindingSetFile, renderLanguageContract, SystemIntegrationError, validateBindingSet, verifyLanguageContract } from "../compiler/system-integration-v1.mjs";

const fixture = readBindingSetFile(path.join(PACKAGE_ROOT, "fixtures/provider-neutral-v1/settlement-runtime.json"));

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function withMessaging(value = fixture) {
  const candidate = clone(value);
  candidate.message_channels = [
    { channel_id: "settlement-events", purpose: "delivery", allowed_event_refs: ["settlement:settlement-requested"], publisher_operation_refs: ["settlement:request-settlement"], consumer_operation_refs: ["audit:record-settlement"], evidence_boundary: "formation-only-no-delivery-claim" },
    { channel_id: "settlement-events-dead-letter", purpose: "dead-letter", allowed_event_refs: ["settlement:settlement-requested"], publisher_operation_refs: [], consumer_operation_refs: [], evidence_boundary: "terminal-route-configuration-only" },
  ];
  candidate.delivery_policies = [{ policy_id: "settlement-delivery", semantics: "at-least-once", acknowledgement_boundary: "provider-accepted", ordering_scope: "none", visibility_timeout_seconds: 60, retention_seconds: 345600, max_receive_count: 5, dead_letter_channel_ref: "settlement-events-dead-letter", deduplication_owner_ref: "consumer:inbox-message-id", evidence_boundary: "provider-acceptance-is-not-application-commit" }];
  candidate.transport_failure_policies = [{ policy_id: "settlement-transport-failure", retry_eligibility: "idempotent-message-id-only", max_attempts: 5, backoff: "exponential-bounded", unknown_outcome: "reconcile-by-message-id", terminal_action: "dead-letter", evidence_boundary: "bounded-attempt-observation-only" }];
  candidate.transport_bindings = [{ binding_id: "settlement-message-transport", mode: "message", direction: "publish-subscribe", operation_ref: "settlement:request-settlement", event_ref: "settlement:settlement-requested", channel_ref: "settlement-events", delivery_policy_ref: "settlement-delivery", failure_policy_ref: "settlement-transport-failure", envelope_profile_ref: "envelope:domainspec-event-json-v1", evidence_boundary: "intent-send-acceptance-delivery-and-commit-remain-distinct" }];
  return candidate;
}

test("canonical profile closes D45-D49 across exactly three languages", () => {
  const state = loadProfilePackage();
  assert.equal(state.profile.contract_kinds.length, 5);
  assert.deepEqual(Object.keys(state.language_profiles).sort(), [...LANGUAGES].sort());
  for (const language of LANGUAGES) assert.deepEqual(state.language_profiles[language].value.semantic_obligations, state.profile.definition_ids);
  assert.equal(state.profile.claim_ceiling.provider_selected_by_domainspec, false);
  assert.equal(state.profile.claim_ceiling.runtime_guarantees_observed, false);
});

test("binding compilation is canonical and deterministic in every language", () => {
  for (const language of LANGUAGES) {
    const left = compileBindingManifest(fixture, language);
    const right = compileBindingManifest(clone(fixture), language);
    assert.equal(canonicalJson(left), canonicalJson(right));
    assert.match(left.binding_digest, /^[a-f0-9]{64}$/);
    assert.equal(left.runtime_guarantees_observed, false);
    const source = renderLanguageContract(left);
    assert.equal(verifyLanguageContract(source, left), true);
    assert.equal(/\bPort\b/.test(source), false);
    assert.match(generatedRelativePath(fixture.binding_set_id, language), new RegExp(`/${language}/`));
    for (const key of ["message_channels", "transport_bindings", "delivery_policies", "transport_failure_policies"]) assert.deepEqual(left.canonical_bindings[key], []);
  }
});

test("generated Python parses and generated Rust compiles when their runtimes are available", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-system-integration-"));
  try {
    const pythonManifest = compileBindingManifest(fixture, "python");
    const pythonPath = path.join(root, "bindings.py");
    fs.writeFileSync(pythonPath, renderLanguageContract(pythonManifest));
    const python = spawnSync("python3", ["-m", "py_compile", pythonPath], { encoding: "utf8" });
    if (python.error?.code !== "ENOENT") assert.equal(python.status, 0, `${python.stdout}\n${python.stderr}`);
    const rustManifest = compileBindingManifest(fixture, "rust");
    const rustPath = path.join(root, "bindings.rs");
    fs.writeFileSync(rustPath, renderLanguageContract(rustManifest));
    const rust = spawnSync("rustc", ["--edition", "2024", "--crate-type", "lib", rustPath, "--out-dir", root], { encoding: "utf8" });
    if (rust.error?.code !== "ENOENT") assert.equal(rust.status, 0, `${rust.stdout}\n${rust.stderr}`);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test("closed records reject authored continuation, digest, and universal Port fields", () => {
  const cases = [];
  const digest = clone(fixture); digest.binding_digest = "f".repeat(64); cases.push([digest, "SIC_AUTHORED_DIGEST_FORBIDDEN"]);
  const continuation = clone(fixture); continuation.failure_outcome_bindings[0].retry_selection = "retry"; cases.push([continuation, "SIC_FAILURE_CONTINUATION_FORBIDDEN"]);
  const universal = clone(fixture); universal.dependency_contracts[0].concern = "Port"; cases.push([universal, "SIC_UNIVERSAL_PORT_FORBIDDEN"]);
  for (const [candidate, code] of cases) assert.throws(() => validateBindingSet(candidate), (error) => error instanceof SystemIntegrationError && error.code === code);
});

test("unresolved and wrong-kind durable references fail closed", () => {
  const missingDependency = clone(fixture);
  missingDependency.persistence_bindings[0].dependency_contract_ref = "missing-repository";
  assert.throws(() => validateBindingSet(missingDependency), (error) => error instanceof SystemIntegrationError && error.code === "SIC_REFERENCE_UNRESOLVED");
  const missingRuntime = clone(fixture);
  missingRuntime.durable_workflow_runtime_bindings[0].transaction_guarantee_binding_refs = ["missing-transaction"];
  assert.throws(() => validateBindingSet(missingRuntime), (error) => error instanceof SystemIntegrationError && error.code === "SIC_DURABLE_BINDING_INCOMPLETE");
});

test("DS-D1 Interface references are explicit and optional", () => {
  const absent = validateBindingSet(fixture);
  assert.equal(absent.dependency_contracts.every((entry) => entry.domain_interface_ref === null), true);
  const invalid = clone(fixture);
  invalid.dependency_contracts[0].domain_interface_ref = "Interface:repository";
  assert.throws(() => validateBindingSet(invalid), (error) => error instanceof SystemIntegrationError && error.code === "SIC_DOMAIN_INTERFACE_MISUSE");
  const valid = clone(fixture);
  valid.dependency_contracts[0].domain_interface_ref = "DS-D1.11:recovery-repository";
  assert.equal(validateBindingSet(valid).dependency_contracts.find((entry) => entry.contract_id === valid.dependency_contracts[0].contract_id).domain_interface_ref, "DS-D1.11:recovery-repository");
});

test("candidate message bindings are canonical without collapsing provider acceptance into delivery", () => {
  const value = withMessaging();
  const canonical = validateBindingSet(value);
  assert.equal(canonical.transport_bindings.length, 1);
  assert.equal(canonical.message_channels.length, 2);
  assert.equal(canonical.delivery_policies[0].acknowledgement_boundary, "provider-accepted");
  assert.equal(canonical.delivery_policies[0].semantics, "at-least-once");
  assert.equal(compileBindingManifest(value, "typescript").runtime_guarantees_observed, false);
});

test("candidate message bindings reject guarantee inflation and unresolved joins", () => {
  const exactlyOnce = withMessaging();
  exactlyOnce.delivery_policies[0].semantics = "exactly-once";
  assert.throws(() => validateBindingSet(exactlyOnce), (error) => error instanceof SystemIntegrationError && error.code === "SIC_DELIVERY_CLAIM");
  const missingChannel = withMessaging();
  missingChannel.transport_bindings[0].channel_ref = "missing-channel";
  assert.throws(() => validateBindingSet(missingChannel), (error) => error instanceof SystemIntegrationError && error.code === "SIC_MESSAGE_REFERENCE_UNRESOLVED");
  const collapsedDeadLetter = withMessaging();
  collapsedDeadLetter.message_channels[1].consumer_operation_refs = ["audit:record-settlement"];
  assert.throws(() => validateBindingSet(collapsedDeadLetter), (error) => error instanceof SystemIntegrationError && error.code === "SIC_MESSAGE_CHANNEL");
  const invalidSubject = withMessaging();
  invalidSubject.transport_bindings[0].operation_ref = "settlement/request-settlement";
  assert.throws(() => validateBindingSet(invalidSubject), (error) => error instanceof SystemIntegrationError && error.code === "SIC_SCHEMA");
  const invalidChannel = withMessaging();
  invalidChannel.message_channels[0].channel_id = "settlement:events";
  invalidChannel.transport_bindings[0].channel_ref = "settlement:events";
  assert.throws(() => validateBindingSet(invalidChannel), (error) => error instanceof SystemIntegrationError && error.code === "SIC_MESSAGE_CHANNEL");
  const unsupportedEnvelope = withMessaging();
  unsupportedEnvelope.transport_bindings[0].envelope_profile_ref = "envelope:arbitrary";
  assert.throws(() => validateBindingSet(unsupportedEnvelope), (error) => error instanceof SystemIntegrationError && error.code === "SIC_ENVELOPE_PROFILE");
  const unsupportedDeduplication = withMessaging();
  unsupportedDeduplication.delivery_policies[0].deduplication_owner_ref = "producer:memory";
  assert.throws(() => validateBindingSet(unsupportedDeduplication), (error) => error instanceof SystemIntegrationError && error.code === "SIC_DEDUPLICATION_OWNER");
  const mismatchedDeadLetter = withMessaging();
  mismatchedDeadLetter.message_channels[1].allowed_event_refs = ["audit:other-event"];
  assert.throws(() => validateBindingSet(mismatchedDeadLetter), (error) => error instanceof SystemIntegrationError && error.code === "SIC_MESSAGE_BINDING_INCOMPLETE");
});

test("candidate message binding schemas accept the compiler-valid extension", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-message-schema-"));
  try {
    const valuePath = path.join(root, "binding.json");
    fs.writeFileSync(valuePath, `${JSON.stringify(withMessaging(), null, 2)}\n`);
    const contractsPath = path.join(PACKAGE_ROOT, "contracts");
    const schemaPath = path.join(contractsPath, "binding-set-v1.schema.json");
    const result = spawnSync("python3", ["-c", "import json,jsonschema,sys,pathlib;d=pathlib.Path(sys.argv[1]);schemas=[json.load(open(p)) for p in d.glob('*schema.json')];store={s['$id']:s for s in schemas};root=next(s for s in schemas if s['$id'].endswith('/binding-set-v1.schema.json'));resolver=jsonschema.RefResolver.from_schema(root,store=store);jsonschema.Draft202012Validator(root,resolver=resolver).validate(json.load(open(sys.argv[2])))", contractsPath, valuePath], { encoding: "utf8" });
    if (result.error?.code !== "ENOENT") assert.equal(result.status, 0, result.stderr);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
