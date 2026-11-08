import {mkdirSync, mkdtempSync, rmSync} from "node:fs";
import {spawnSync} from "node:child_process";
import {isAbsolute, join} from "node:path";
import type {FactoryNodeProviderV1} from "../../contracts/factory-node-provider-v1.js";
import {fail} from "../../shared/canonical.js";
import type {EventCase, EventPortableResult, EventS1PortableResult} from "../../../targets/typescript/event-v1.js";
import {decodePastTenseEventObservation} from "../../../families/past-tense-event/decoder/decode-event-observation.js";
import {evaluatePastTenseEvent} from "../../../families/past-tense-event/evaluator/evaluate-event.js";
import {evaluateW3} from "../../../families/effects-connections/evaluator/evaluate-w3.js";

const manifest = "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.toml";
const targetDir = "projects/domainspec-v2/development/remaining-meta-types/runs/event/cargo-target";
const caseKeys = ["w3_descriptor", "w3_observation", "descriptor", "observation"];
const descriptorKeys = ["schema_version", "descriptor_id", "semantic_plan_epoch_id", "semantic_contract_digest", "event_name", "tense", "payload_contract_id", "payload_version", "payload_immutable", "occurrence_identity_contract_id", "persistence_checkpoint", "publication_policy_id", "consumer_contract_ids", "distributed_exactly_once_claim", "durable_handle", "admission_status", "authority_effect"];
const exactKeys = (value: unknown, expected: readonly string[]): boolean => value !== null && typeof value === "object" && !Array.isArray(value) && JSON.stringify(Object.keys(value).sort()) === JSON.stringify([...expected].sort());
let nativeProofComplete = false;

const runNativeProof = (): void => {
  if (nativeProofComplete) return;
  const pathEnv = process.env.PATH;
  const userHome = process.env.HOME;
  if (!pathEnv || !userHome || !isAbsolute(userHome)) fail("FACTORY_EVENT_RUST_FAILED", "runtime-home-or-path-invalid");
  const stableHome = userHome as string;
  const cargoHome = process.env.CARGO_HOME ?? join(stableHome, ".cargo");
  const rustupHome = process.env.RUSTUP_HOME ?? join(stableHome, ".rustup");
  if (!isAbsolute(cargoHome) || !isAbsolute(rustupHome)) fail("FACTORY_EVENT_RUST_FAILED", "runtime-tool-home-invalid");
  mkdirSync(targetDir, {recursive: true});
  const ownedTarget = mkdtempSync(join(targetDir, "run-"));
  let child: ReturnType<typeof spawnSync>;
  try {
    child = spawnSync("cargo", ["test", "--manifest-path", manifest, "--locked", "--offline", "--test", "event_v1"], {cwd: process.cwd(), encoding: "utf8", env: {PATH: pathEnv, CARGO_HOME: cargoHome, RUSTUP_HOME: rustupHome, CARGO_TARGET_DIR: ownedTarget}});
  } finally {
    rmSync(ownedTarget, {recursive: true, force: true});
  }
  if (child.status !== 0) fail("FACTORY_EVENT_RUST_FAILED", String(child.stderr).trim() || String(child.status));
  nativeProofComplete = true;
};

const normalize = (input: EventCase): EventPortableResult | EventS1PortableResult => {
  if (!exactKeys(input, caseKeys) || !exactKeys(input.descriptor, descriptorKeys)) fail("FACTORY_EVENT_RUST_FAILED", "closed-event-case");
  const descriptor = input.descriptor;
  if (descriptor.event_name !== "SettlementCreated" || descriptor.semantic_plan_epoch_id !== "WP-RMT-002/S1/2026-08-16" || descriptor.semantic_contract_digest !== "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7") fail("FACTORY_EVENT_RUST_FAILED", "stale-event-binding");
  const observed = decodePastTenseEventObservation(input.observation);
  const w3 = evaluateW3(input.w3_descriptor, input.w3_observation);
  if (w3.verdict !== "pass") fail("FACTORY_EVENT_RUST_FAILED", `w3:${w3.findings.map(({code}) => code).join(",")}`);
  const extension = evaluatePastTenseEvent(descriptor, observed);
  if (observed.s1_observation !== null) {
    if (extension.verdict !== "reject" || extension.findings.length !== 1) fail("FACTORY_EVENT_RUST_FAILED", "s1-classification-invalid");
    return Object.freeze({
      schema_version: "domainspec.event-s1-portable-result/v1", result: "reject", meta_type: "Event", diagnostic_code: extension.findings[0]!.code,
      scenario: observed.s1_observation.scenario, occurrence_id: observed.occurrence_id, durable_occurrence: Object.freeze({...observed.durable_occurrence}),
      required_residue: Object.freeze({...observed.s1_observation}), distributed_exactly_once_claim: false,
      semantic_plan_epoch_id: descriptor.semantic_plan_epoch_id, semantic_contract_digest: descriptor.semantic_contract_digest, authority_effect: "none",
    });
  }
  if (extension.verdict !== "pass") fail("FACTORY_EVENT_RUST_FAILED", `event:${extension.findings.map(({code}) => code).join(",")}`);
  return Object.freeze({
    schema_version: "domainspec.event-portable-result/v1", result: "pass", meta_type: "Event", event_name: descriptor.event_name, tense: "past",
    payload_contract_id: descriptor.payload_contract_id, payload_version: descriptor.payload_version, payload_immutable: true,
    occurrence_identity_contract_id: descriptor.occurrence_identity_contract_id, occurrence_id: observed.occurrence_id, retry_occurrence_id: observed.occurrence_id,
    persistence_checkpoint: descriptor.persistence_checkpoint, publication_is_separate_from_commit: true, publication_policy_id: descriptor.publication_policy_id,
    consumer_contract_ids: Object.freeze([...descriptor.consumer_contract_ids].sort()), durable_occurrence: Object.freeze({...observed.durable_occurrence}),
    distributed_exactly_once_claim: false, semantic_plan_epoch_id: descriptor.semantic_plan_epoch_id, semantic_contract_digest: descriptor.semantic_contract_digest, authority_effect: "none",
  });
};

export const eventRustV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "event-rust-v1",
  provider_version: "1.0.0-candidate",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(["event_case"]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/event-rust-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/event_v1.rs",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/tests/event_v1.rs",
    "projects/domainspec-v2/impl/architecture-conformance/families/past-tense-event/decoder/decode-event-observation.ts",
  ]),
  tool_ids: Object.freeze(["cargo", "rustc"]),
  execute: async ({raw_inputs: rawInputs}) => {
    let input: EventCase;
    try { input = JSON.parse(rawInputs.event_case ?? "") as EventCase; }
    catch { return fail("FACTORY_EVENT_RUST_FAILED", "invalid-json"); }
    let portable: EventPortableResult | EventS1PortableResult;
    try { portable = normalize(input); }
    catch (error) { return fail("FACTORY_EVENT_RUST_FAILED", error instanceof Error ? error.message : String(error)); }
    runNativeProof();
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1", result: "pass", provider_id: "event-rust-v1",
      semantic_output: Object.freeze({portable, native_evidence: Object.freeze({language: "rust", mechanism: "owned-event-enum-and-durable-observation-handle"})}),
      accounting: Object.freeze({positives_declared: 1, positives_passed: 1, mutants_declared: 19, mutants_killed: 19}),
      claim_ceiling: "candidate-local native Rust Event proof over 10 base and 9 S1 controls; provider remains unregistered; no distributed exactly-once claim",
      authority_effect: "none",
    });
  },
});
