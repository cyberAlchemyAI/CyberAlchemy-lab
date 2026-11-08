import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import test from "node:test";

import {createModulePort} from "../../agent-reasoning-engine/packages/module-port/index.mjs";
import {
  createOntologyStagePort,
  ontologyStageOutputValidators,
  runOntologyStage,
  validateStageDescriptor,
} from "../packages/ontology-stage-port/index.mjs";
import {
  createSyntheticOntologyStageAdapter,
  SYNTHETIC_STAGE_ID,
} from "../packages/ontology-stage-port/synthetic-adapter.mjs";

function configured() {
  const fixture = createSyntheticOntologyStageAdapter();
  const modulePort = createModulePort({adapters: [fixture.adapter], output_validators: ontologyStageOutputValidators});
  return {fixture, port: createOntologyStagePort({module_port: modulePort, descriptors: [fixture.descriptor]})};
}

function response(overrides = {}) {
  return {
    response_kind: "answer",
    response: "Help teams agree on one bounded product promise.",
    evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true},
    ...overrides,
  };
}

test("empty registry is valid and an unknown stage is unavailable", () => {
  const modulePort = createModulePort({output_validators: ontologyStageOutputValidators});
  const port = createOntologyStagePort({module_port: modulePort, descriptors: []});
  assert.deepEqual(port.stage_ids, []);
  assert.equal(port.inspect().discovery, "disabled");
  assert.equal(port.inspect().fallback, "forbidden");
  const result = runOntologyStage({stage_port: port, stage_id: "unknown-stage"});
  assert.equal(result.schema_version, "cav2.define-stage-run/v1");
  assert.equal(result.phase, "resolve");
  assert.equal(result.disposition, "unavailable");
  assert.deepEqual(result.reason_codes, ["define.stage-unavailable"]);
  assert.equal(result.authority_effect, "none");
});

test("synthetic stage requires exact confirmation then emits deterministic handoff", () => {
  const {port} = configured();
  const first = runOntologyStage({stage_port: port, stage_id: SYNTHETIC_STAGE_ID, responses: [response()]});
  assert.equal(first.ok, false);
  assert.equal(first.phase, "handoff");
  assert.deepEqual(first.reason_codes, ["define.stage-user-confirmation"]);
  assert.match(first.candidate_digest, /^[a-f0-9]{64}$/u);

  const confirmed = runOntologyStage({
    stage_port: port,
    stage_id: SYNTHETIC_STAGE_ID,
    responses: [response()],
    confirmation_candidate_digest: first.candidate_digest,
  });
  const replay = runOntologyStage({
    stage_port: port,
    stage_id: SYNTHETIC_STAGE_ID,
    responses: [response()],
    confirmation_candidate_digest: first.candidate_digest,
  });
  assert.equal(confirmed.ok, true);
  assert.equal(confirmed.disposition, "handoff-ready");
  assert.equal(confirmed.candidate.product_purpose, response().response);
  assert.equal(confirmed.handoff_receipt.authority_effect, "none");
  assert.match(confirmed.handoff_receipt.handoff_receipt_digest, /^[a-f0-9]{64}$/u);
  assert.deepEqual(replay, confirmed);
});

test("semantic, non-collapse, and orthogonality defects remain independent", () => {
  for (const [field, repair] of [
    ["semantic_grounding", "semantic-grounding"],
    ["non_collapse", "non-collapse"],
    ["orthogonality", "orthogonality"],
  ]) {
    const {port} = configured();
    const evidence = {...response().evidence, [field]: false};
    const result = runOntologyStage({stage_port: port, stage_id: SYNTHETIC_STAGE_ID, responses: [response({evidence})]});
    assert.equal(result.phase, "readiness");
    assert.match(result.reason_codes.join("\n"), new RegExp(`define\\.stage-${repair}`));
  }
});

test("deferral remains open and never materializes a candidate", () => {
  const {port} = configured();
  const result = runOntologyStage({
    stage_port: port,
    stage_id: SYNTHETIC_STAGE_ID,
    responses: [{response_kind: "defer", response: "", evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true}}],
  });
  assert.equal(result.phase, "response");
  assert.equal(result.candidate, null);
  assert.deepEqual(result.reason_codes, ["define.stage-response-deferred"]);
});

test("descriptors are closed, unique, deterministic, and cycle-safe", () => {
  const {adapter, descriptor} = createSyntheticOntologyStageAdapter();
  const derived = (stageId, prerequisites = []) => ({
    ...descriptor,
    stage_id: stageId,
    ontology_type: stageId,
    prerequisite_stage_ids: prerequisites,
    capabilities: Object.fromEntries(Object.entries(descriptor.capabilities).map(([operation, capability]) => [operation, capability.replace("fixture-product", stageId)])),
  });
  assert.equal(validateStageDescriptor(descriptor), true);
  assert.equal(validateStageDescriptor({...descriptor, extra: true}), false);
  const modulePort = createModulePort({adapters: [adapter], output_validators: ontologyStageOutputValidators});
  assert.throws(() => createOntologyStagePort({module_port: modulePort, descriptors: [descriptor, descriptor]}), /duplicated/u);
  const other = derived("fixture-business-ontology", [descriptor.stage_id]);
  const left = createOntologyStagePort({module_port: modulePort, descriptors: [descriptor, other]});
  const right = createOntologyStagePort({module_port: modulePort, descriptors: [other, descriptor]});
  assert.equal(left.stage_graph_digest, right.stage_graph_digest);
  const cycleA = derived("cycle-a", ["cycle-b"]);
  const cycleB = derived("cycle-b", ["cycle-a"]);
  assert.throws(() => createOntologyStagePort({module_port: modulePort, descriptors: [cycleA, cycleB]}), /cycle/u);
});

test("missing and drifted providers block only the configured stage", () => {
  const fixture = createSyntheticOntologyStageAdapter();
  const absent = createOntologyStagePort({
    module_port: createModulePort({output_validators: ontologyStageOutputValidators}),
    descriptors: [fixture.descriptor],
  });
  const missing = runOntologyStage({stage_port: absent, stage_id: SYNTHETIC_STAGE_ID, responses: [response()]});
  assert.equal(missing.phase, "describe");
  assert.equal(missing.disposition, "unavailable");

  const driftedDescriptor = {...fixture.descriptor, manifest_digest: "0".repeat(64)};
  const drifted = createOntologyStagePort({
    module_port: createModulePort({adapters: [fixture.adapter], output_validators: ontologyStageOutputValidators}),
    descriptors: [driftedDescriptor],
  });
  const result = runOntologyStage({stage_port: drifted, stage_id: SYNTHETIC_STAGE_ID, responses: [response()]});
  assert.equal(result.phase, "describe");
  assert.equal(result.disposition, "blocked");
  assert.deepEqual(result.reason_codes, ["define.stage-provider-identity-drift"]);
});

test("authority-bearing adapter output is blocked before stage judgment", () => {
  const fixture = createSyntheticOntologyStageAdapter();
  const effectful = {
    manifest: fixture.adapter.manifest,
    invoke(invocation) {
      const value = fixture.adapter.invoke(invocation);
      if (invocation.capability_id === fixture.descriptor.capabilities.evaluate) {
        return {...value, authority_effect: "local-effect"};
      }
      return value;
    },
  };
  const port = createOntologyStagePort({
    module_port: createModulePort({adapters: [effectful], output_validators: ontologyStageOutputValidators}),
    descriptors: [fixture.descriptor],
  });
  const result = runOntologyStage({stage_port: port, stage_id: SYNTHETIC_STAGE_ID, responses: [response()]});
  assert.equal(result.phase, "evaluate");
  assert.equal(result.disposition, "blocked");
  assert.deepEqual(result.reason_codes, ["module.output-invalid"]);
});

test("published JSON schemas retain closed authority-none contracts", () => {
  for (const filename of ["stage-registry.schema.json", "stage-run.schema.json"]) {
    const schema = JSON.parse(readFileSync(resolve(import.meta.dirname, "../schemas/integration", filename), "utf8"));
    assert.equal(schema.additionalProperties, false);
    assert.equal(schema.properties.authority_effect.const, "none");
    assert.ok(schema.required.includes("authority_effect"));
  }
});
