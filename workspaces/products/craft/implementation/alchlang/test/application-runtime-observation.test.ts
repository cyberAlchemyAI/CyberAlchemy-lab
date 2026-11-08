import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { assertApplicationRuntimeObservationsCurrent, joinApplicationRuntimeObservations, type ApplicationRuntimeStageKey } from "../src/application-runtime-observation.js";

const sha = (bytes: string | Buffer) => createHash("sha256").update(bytes).digest("hex");
const canonical = (value: any): string => Array.isArray(value) ? `[${value.map(canonical).join(",")}]` : value && typeof value === "object" ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}` : JSON.stringify(value);
const stageMap = { application_commit: "application-committed", provider_acceptance: "provider-accepted",
  transport_delivery: "transport-delivered", business_completion: "business-completed" } as const;
const stageKeys = Object.keys(stageMap) as ApplicationRuntimeStageKey[];

function fixture(observed = new Set<ApplicationRuntimeStageKey>(stageKeys)) {
  const sources = new Map<string, Buffer>();
  const put = (path: string, value: unknown) => { const bytes = Buffer.from(JSON.stringify(value)); sources.set(path, bytes);
    return { path, sha256: sha(bytes), size_bytes: bytes.length, current: true as boolean }; };
  const sourceRef = put("fixture/application.alch", "synthetic application source");
  const graphRef = put("fixture/compiled-graph.json", { graph_id: "fixture-graph" });
  const providerRef = put("fixture/provider-selection.json", { provider_id: "fixture-provider" });
  const generatedRefs = [put("fixture/generated/domain.ts", "export const fixture = true;"), put("fixture/generated/manifest.json", { files: ["domain.ts"] })];
  const environmentRef = put("fixture/runtime-environment.json", { environment_id: "fixture-loopback" });
  const orodi = { binding_id: "orodi-binding:fixture", observation_selector: "domainspec:integration-observation",
    projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator",
    disclosure_policy_ref: "disclosure:fixture", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"],
    return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false,
      deploy: false, enact_business_effects: false }, evidence_boundary: "synthetic observation only", authority_effect: "none" };
  const orodiRef = put("fixture/orodi-binding.json", orodi);
  const cleanup = { schema_version: "alchlang.runtime-cleanup-report/v1-candidate", run_id: "fixture-run", cleanup_observed: true,
    temporary_resources_removed: true, owned_residue: [], authority_effect: "none", claim_ceiling: "Synthetic owned resources only." };
  const cleanupRef = put("fixture/cleanup.json", cleanup);
  const stages: any = {}; const receipts: any[] = []; const observations: any[] = [];
  for (const key of stageKeys) {
    if (!observed.has(key)) { stages[key] = { runtime_receipt_ref: null, observation_ref: null }; continue; }
    const stage = stageMap[key];
    const receipt = { receipt_id: `receipt:${key}`, binding_ref: "binding:fixture", operation_ref: "operation:fixture",
      observed_at: "2026-09-20T12:00:00.000Z", observed_stage: stage, outcome: "accepted", provider_evidence_ref: `evidence:${key}`,
      correlation_ref: cleanup.run_id, claim_ceiling: stage, authority_effect: "none" };
    const receiptRef = put(`fixture/receipts/${key}.json`, receipt);
    const observation = { schema_version: "domainspec.integration-observation/v1-candidate", observation_id: `observation:${key}`,
      source_receipt_digest: sha(canonical(receipt)), binding_ref: receipt.binding_ref, operation_ref: receipt.operation_ref, stage,
      outcome: receipt.outcome, observed_at: receipt.observed_at, duration_ms: 1, correlation_ref: receipt.correlation_ref,
      sanitized_attributes: { fixture: true }, evidence_refs: [receipt.provider_evidence_ref], claim_ceiling: stage,
      orodi_binding_ref: orodi.binding_id, immutable: true, authority_effect: "none" };
    const observationRef = put(`fixture/observations/${key}.json`, observation);
    stages[key] = { runtime_receipt_ref: receiptRef, observation_ref: observationRef }; receipts.push(receipt); observations.push(observation);
  }
  const input: any = { schema_version: "alchlang.runtime-observation-bindings/v1", join_id: "fixture-runtime-join",
    source_ref: sourceRef, compiled_graph_ref: graphRef, provider_selection_ref: providerRef, generated_artifact_refs: generatedRefs,
    runtime_environment_ref: environmentRef, orodi_binding_ref: orodiRef, cleanup_report_ref: cleanupRef, stages,
    claim_ceiling: "Synthetic loopback runtime evidence only." };
  return { input, sources, put, orodi, cleanup, receipts, observations };
}

test("joins four exact runtime stages without inferring any stage from another", () => {
  const item = fixture(); const result = joinApplicationRuntimeObservations(item.input, item.sources);
  assert.deepEqual(result, joinApplicationRuntimeObservations(structuredClone(item.input), item.sources));
  assert.equal((result.join as any).observed_stage_count, 4); assert.equal((result.join as any).all_stages_independently_observed, true);
  assert.equal((result.join as any).stage_inference_used, false); assert.equal((result.trace as any).runtime_executed_by_join, false);
  for (const key of stageKeys) {
    assert.equal((result.join as any).stages[key].domain_stage, stageMap[key]);
    assert.equal((result.join as any).stages[key].status, "observed");
  }
  assertApplicationRuntimeObservationsCurrent(item.input, item.sources, result);
});

test("each runtime stage remains independently observable and all missing stages stay explicit", () => {
  for (const selected of stageKeys) {
    const item = fixture(new Set([selected])); const result = joinApplicationRuntimeObservations(item.input, item.sources);
    assert.equal((result.join as any).observed_stage_count, 1); assert.equal((result.join as any).all_stages_independently_observed, false);
    for (const key of stageKeys) assert.equal((result.join as any).stages[key].status, key === selected ? "observed" : "not-observed");
  }
});

test("join, cleanup and every consumed observation satisfy their closed schemas", () => {
  const item = fixture(); const result = joinApplicationRuntimeObservations(item.input, item.sources);
  const root = "../../../../../../../craft/projects/domainspec-v2/";
  const schemas = [
    fileURLToPath(new URL(`${root}development/authoring-to-runtime-v1/runtime-observation-join.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}development/authoring-to-runtime-v1/runtime-cleanup-report.schema.json`, import.meta.url)),
    fileURLToPath(new URL(`${root}impl/cli/contracts/integration-observation-v1.schema.json`, import.meta.url)),
  ];
  const script = `import json,sys,jsonschema
p=json.load(sys.stdin); s=[json.load(open(x)) for x in sys.argv[1:]]
jsonschema.Draft202012Validator(s[0]).validate(p['join'])
jsonschema.Draft202012Validator(s[1]).validate(p['cleanup'])
for x in p['observations']: jsonschema.Draft202012Validator(s[2]).validate(x)`;
  const validation = spawnSync("python3", ["-c", script, ...schemas], { input: JSON.stringify({ join: result.join, cleanup: item.cleanup, observations: item.observations }), encoding: "utf8", timeout: 20000 });
  assert.equal(validation.status, 0, validation.stderr || String(validation.error));
});

test("a receipt cannot be swapped into another stage or inflated past its own ceiling", () => {
  const swapped = fixture(); swapped.input.stages.provider_acceptance = swapped.input.stages.application_commit;
  assert.throws(() => joinApplicationRuntimeObservations(swapped.input, swapped.sources), /APPLICATION_RUNTIME_OBSERVATION_STAGE/);
  const inflated = fixture(); const ref = inflated.input.stages.application_commit.runtime_receipt_ref;
  const receipt = JSON.parse((inflated.sources.get(ref.path) as Buffer).toString()); receipt.claim_ceiling = "business-completed";
  const bytes = Buffer.from(JSON.stringify(receipt)); inflated.sources.set(ref.path, bytes); ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
  assert.throws(() => joinApplicationRuntimeObservations(inflated.input, inflated.sources), /APPLICATION_RUNTIME_OBSERVATION_STAGE/);
});

test("receipt/observation identity and digest mismatches reject", () => {
  const item = fixture(); const ref = item.input.stages.transport_delivery.observation_ref;
  const observation = JSON.parse((item.sources.get(ref.path) as Buffer).toString()); observation.source_receipt_digest = "0".repeat(64);
  const bytes = Buffer.from(JSON.stringify(observation)); item.sources.set(ref.path, bytes); ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
  assert.throws(() => joinApplicationRuntimeObservations(item.input, item.sources), /APPLICATION_RUNTIME_OBSERVATION_DIGEST/);
});

test("missing, stale and half-present evidence pairs fail closed", () => {
  const missing = fixture(); missing.sources.delete(missing.input.generated_artifact_refs[0].path);
  assert.throws(() => joinApplicationRuntimeObservations(missing.input, missing.sources), /APPLICATION_RUNTIME_OBSERVATION_MISSING/);
  const stale = fixture(); stale.input.runtime_environment_ref.current = false;
  assert.throws(() => joinApplicationRuntimeObservations(stale.input, stale.sources), /APPLICATION_RUNTIME_OBSERVATION_CURRENTNESS/);
  const half = fixture(); half.input.stages.business_completion.observation_ref = null;
  assert.throws(() => joinApplicationRuntimeObservations(half.input, half.sources), /APPLICATION_RUNTIME_OBSERVATION_PAIR/);
});

test("ORODI return edges and runtime control capabilities are structurally impossible", () => {
  for (const mutate of [
    (value: any) => { value.return_edge = "allowed"; },
    (value: any) => { value.runtime_control_capabilities.select_retries = true; },
    (value: any) => { value.evaluator_ref = null; },
  ]) {
    const item = fixture(); const ref = item.input.orodi_binding_ref; const value = structuredClone(item.orodi); mutate(value);
    const bytes = Buffer.from(JSON.stringify(value)); item.sources.set(ref.path, bytes); ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
    assert.throws(() => joinApplicationRuntimeObservations(item.input, item.sources), /APPLICATION_RUNTIME_OBSERVATION_(ORODI_|INPUT)/);
  }
});

test("cleanup and every observed stage must refer to one causal run", () => {
  const wrongCleanup = fixture();
  const cleanupRef = wrongCleanup.input.cleanup_report_ref;
  const cleanupBytes = Buffer.from(JSON.stringify({ ...wrongCleanup.cleanup, run_id: "unrelated-run" }));
  wrongCleanup.sources.set(cleanupRef.path, cleanupBytes);
  cleanupRef.sha256 = sha(cleanupBytes); cleanupRef.size_bytes = cleanupBytes.length;
  assert.throws(() => joinApplicationRuntimeObservations(wrongCleanup.input, wrongCleanup.sources), /APPLICATION_RUNTIME_OBSERVATION_RUN/);

  const wrongStage = fixture();
  const ref = wrongStage.input.stages.provider_acceptance.runtime_receipt_ref;
  const receipt = JSON.parse((wrongStage.sources.get(ref.path) as Buffer).toString("utf8"));
  receipt.correlation_ref = "unrelated-run";
  const bytes = Buffer.from(JSON.stringify(receipt));
  wrongStage.sources.set(ref.path, bytes); ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
  const observationRef = wrongStage.input.stages.provider_acceptance.observation_ref;
  const observation = JSON.parse((wrongStage.sources.get(observationRef.path) as Buffer).toString("utf8"));
  observation.correlation_ref = "unrelated-run"; observation.source_receipt_digest = sha(canonical(receipt));
  const observationBytes = Buffer.from(JSON.stringify(observation));
  wrongStage.sources.set(observationRef.path, observationBytes);
  observationRef.sha256 = sha(observationBytes); observationRef.size_bytes = observationBytes.length;
  assert.throws(() => joinApplicationRuntimeObservations(wrongStage.input, wrongStage.sources), /APPLICATION_RUNTIME_OBSERVATION_RUN/);

  const noParticipants = fixture(new Set());
  const empty = joinApplicationRuntimeObservations(noParticipants.input, noParticipants.sources);
  assert.equal((empty.join as any).observed_stage_count, 0);
  assert.equal((empty.join as any).all_stages_independently_observed, false);
});

test("cleanup residue and output mutation reject currentness", () => {
  const dirty = fixture(); const ref = dirty.input.cleanup_report_ref; const cleanup = { ...dirty.cleanup, temporary_resources_removed: false, owned_residue: ["fixture-process"] };
  const bytes = Buffer.from(JSON.stringify(cleanup)); dirty.sources.set(ref.path, bytes); ref.sha256 = sha(bytes); ref.size_bytes = bytes.length;
  assert.throws(() => joinApplicationRuntimeObservations(dirty.input, dirty.sources), /APPLICATION_RUNTIME_OBSERVATION_CLEANUP/);
  const item = fixture(); const result = joinApplicationRuntimeObservations(item.input, item.sources);
  for (const mutate of [
    (value: any) => { value.join.stages.transport_delivery.status = "not-observed"; },
    (value: any) => { value.join.stage_inference_used = true; },
    (value: any) => { value.join.orodi_projection.return_edge = "allowed"; },
  ]) {
    const changed = structuredClone(result); mutate(changed);
    assert.throws(() => assertApplicationRuntimeObservationsCurrent(item.input, item.sources, changed), /APPLICATION_RUNTIME_OBSERVATION_STALE/);
  }
});
