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
