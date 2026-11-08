import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import type {
  ToolEvidenceProfileReplayInputs,
  ToolEvidenceProfileReplayCaseBundle,
  ToolEvidenceProfileReplayHostileCase,
  ToolEvidenceProfileReplayTestContextBundle,
} from "../contracts/tool-evidence-profile-replay.js";
import type { ToolEvidenceProfile } from "../contracts/tool-evidence-profile.js";
import { evaluateToolProfileEvidenceEligibility } from "../src/evaluate-evidence-eligibility.js";
import { replayToolEvidenceProfile, validateToolEvidenceProfileNormalizerOutput } from "../src/replay-tool-evidence-profile.js";
import {
  runToolEvidenceProfileNormalizer,
  selectToolEvidenceProfileNormalizer,
  TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY,
  validateToolEvidenceProfileNormalizerRegistry,
} from "../src/tool-evidence-profile-normalizer-registry.js";
import { validateToolEvidenceProfile } from "../src/validate-tool-evidence-profile.js";

type JsonRecord = Record<string, unknown>;
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const casesPath = resolve(root, "fixtures/tool-evidence-profile-replay/golden/cases.json");
const contextsPath = resolve(root, "fixtures/tool-evidence-profile-replay/evaluation-context.json");
const hostilePath = resolve(root, "fixtures/tool-evidence-profile-replay/hostile/cases.json");
const expectedPath = resolve(root, "fixtures/tool-evidence-profile-replay/expected-results.json");
const inventoryPath = resolve(root, "contracts/tool-evidence-profile-family-inventory.json");
const policyPath = resolve(root, "contracts/tool-evidence-profile-attribute-policy.json");
const referentsPath = resolve(root, "fixtures/tool-evidence-profiles/referents.json");
const normalizationSchema = resolve(root, "contracts/tool-evidence-profile-normalization-result.schema.json");
const eligibilitySchema = resolve(root, "contracts/tool-profile-evidence-eligibility-result.schema.json");
const replaySchema = resolve(root, "contracts/tool-evidence-profile-replay-result.schema.json");

const text = (path: string): string => readFileSync(path, "utf8");
const json = <T>(path: string): T => JSON.parse(text(path)) as T;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const cases = json<ToolEvidenceProfileReplayCaseBundle>(casesPath);
const contexts = json<ToolEvidenceProfileReplayTestContextBundle>(contextsPath);
const hostile = json<{ cases: ToolEvidenceProfileReplayHostileCase[] }>(hostilePath);
const expected = json<{ results: { case_id: string; expected_code: string }[] }>(expectedPath);
const inventory = text(inventoryPath);
const policy = text(policyPath);
const referents = text(referentsPath);

const goldenInputs = (index = 0) => {
  const replayCase = cases.cases[index]!;
  const descriptor = text(resolve(root, replayCase.descriptor_ref));
  const context = contexts.contexts.find(({ context_id }) => context_id === replayCase.context_id)!;
  const wp5 = validateToolEvidenceProfile({
    descriptor, family_inventory: inventory, attribute_policy: policy,
    referent_inventory: referents, evaluated_at: cases.evaluated_at,
  });
  return {
    replay_id: `wp6-${replayCase.case_id}`,
    descriptor,
    family_inventory: inventory,
    attribute_policy: policy,
    referent_inventory: referents,
    wp5_validation_result: JSON.stringify(wp5),
    fixture: JSON.stringify(replayCase.fixture),
    evaluation_context: JSON.stringify(context.evaluation_context),
    evaluated_at: cases.evaluated_at,
  } as const;
};

const schemaCheck = (instance: unknown, schema: string, scratch: string, name: string): void => {
  const path = join(scratch, `${name}.json`);
  writeFileSync(path, `${JSON.stringify(instance, null, 2)}\n`);
  const check = spawnSync("python3", ["-m", "jsonschema", "-i", path, schema], { encoding: "utf8" });
  assert.equal(check.status, 0, check.stdout + check.stderr);
};

const schemaRejects = (instance: unknown, schema: string, scratch: string, name: string): void => {
  const path = join(scratch, `${name}.json`);
  writeFileSync(path, `${JSON.stringify(instance, null, 2)}\n`);
  const check = spawnSync("python3", ["-m", "jsonschema", "-i", path, schema], { encoding: "utf8" });
  assert.notEqual(check.status, 0, `${name} unexpectedly passed its closed schema`);
};

test("the registry is an exact seven-family static denominator", () => {
  assert.equal(TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY.length, 7);
  assert.deepEqual(validateToolEvidenceProfileNormalizerRegistry(TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY), []);
  assert.equal(new Set(TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY.map(({ family_id }) => family_id)).size, 7);
  assert.ok(TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY.every(({ normalizer }) =>
    normalizer.ref === "orodi://normalizer/pure-profile/v1" &&
    normalizer.version === "1.0.0" &&
    normalizer.sha256 === "d6a45d4e99806fca19e5d683d9fc0c7b216f9d57706a87ae5112b32dbabe92ca"));
});

test("all seven profile families replay deterministically without runtime authority", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-wp6-"));
  try {
    assert.equal(cases.cases.length, 7);
    assert.equal(contexts.contexts.length, 7);
    for (const [index, replayCase] of cases.cases.entries()) {
      const inputs = goldenInputs(index);
      const before = JSON.stringify(inputs);
      const first = replayToolEvidenceProfile(inputs);
      const second = replayToolEvidenceProfile(inputs);
      assert.equal(JSON.stringify(inputs), before, replayCase.case_id);
      assert.equal(JSON.stringify(first), JSON.stringify(second), replayCase.case_id);
      assert.equal(first.verdict, "replayed", `${replayCase.case_id}: ${JSON.stringify(first.findings)}`);
      assert.equal(first.normalization.verdict, "normalized");
      assert.equal(first.normalization.observations.length, 1);
      const observation = first.normalization.observations[0]!;
      assert.equal(observation.kind, replayCase.expected_observation_kind);
      assert.equal(observation.plane, "product");
      assert.equal(observation.mode, "simulation");
      assert.equal(observation.deployment_effect, false);
      assert.equal(observation.independently_observed, false);
      assert.deepEqual(observation.telemetry, {
        offered: 0, queued: 0, exported: 0, rejected: 0,
        dropped: 0, pending: 0, partial_success: 0,
      });
      assert.equal(first.runtime_admission, "denied");
      assert.equal(first.referent_trust, "unverified");
      assert.equal(first.authority_effect, "none");
      assert.equal(first.eligibility?.decision, "replay-only");
      assert.deepEqual(first.eligibility?.runtime_admitted_observations, []);
      assert.ok(first.eligibility?.eligibility_receipts.every(({ eligible_controls }) => eligible_controls.length === 0));
      schemaCheck(first.normalization, normalizationSchema, scratch, `${replayCase.case_id}-normalization`);
      schemaCheck(first.eligibility, eligibilitySchema, scratch, `${replayCase.case_id}-eligibility`);
      schemaCheck(first, replaySchema, scratch, `${replayCase.case_id}-replay`);
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("the hostile corpus has exact unique one-to-one parity", () => {
  assert.equal(hostile.cases.length, 34);
  assert.equal(expected.results.length, 34);
  assert.equal(new Set(hostile.cases.map(({ case_id }) => case_id)).size, 34);
  assert.deepEqual(
    hostile.cases.map(({ case_id, expected_code }) => ({ case_id, expected_code })).sort((a, b) => a.case_id.localeCompare(b.case_id)),
    [...expected.results].sort((a, b) => a.case_id.localeCompare(b.case_id)),
  );
});

test("all emitted-result schemas reject an open top-level object", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-wp6-schema-negative-"));
  try {
    const replay = replayToolEvidenceProfile(goldenInputs());
    assert.equal(replay.verdict, "replayed");
    schemaRejects({ ...replay.normalization, unexpected: true }, normalizationSchema, scratch, "normalization-open");
    schemaRejects({ ...replay.eligibility!, unexpected: true }, eligibilitySchema, scratch, "eligibility-open");
    schemaRejects({ ...replay, unexpected: true }, replaySchema, scratch, "replay-open");
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

const replayHostile = (caseId: string) => {
  const inputs = clone(goldenInputs()) as unknown as Record<keyof ToolEvidenceProfileReplayInputs, string>;
  const updateJson = (key: keyof ToolEvidenceProfileReplayInputs, mutate: (value: JsonRecord) => void): void => {
    const value = JSON.parse(inputs[key]) as JsonRecord;
    mutate(value);
    inputs[key] = JSON.stringify(value);
  };
  switch (caseId) {
    case "wp5-result-absent": inputs.wp5_validation_result = "null"; break;
    case "wp5-result-rejected":
      updateJson("wp5_validation_result", (value) => {
        value.verdict = "reject"; value.profile_state = "rejected";
        value.findings = [{ code: "TEST_REJECTED", path: "$", detail: "hostile fixture" }];
      });
      break;
    case "wp5-result-digest-drift": updateJson("wp5_validation_result", (value) => { value.profile_id = "drifted"; }); break;
    case "descriptor-digest-drift": inputs.descriptor += "\n"; break;
    case "family-inventory-drift": inputs.family_inventory += "\n"; break;
    case "attribute-policy-drift": inputs.attribute_policy += "\n"; break;
    case "referent-inventory-drift": inputs.referent_inventory += "\n"; break;
    case "fixture-source-digest-mismatch": updateJson("fixture", (value) => { value.source_sha256 = "0".repeat(64); }); break;
    case "fixture-producer-ref-mismatch": updateJson("fixture", (value) => {
      (value.producer as JsonRecord).ref = "orodi://producer/unknown/v1";
    }); break;
    case "fixture-profile-family-mismatch": updateJson("fixture", (value) => { value.family_id = "fault"; }); break;
    case "normalizer-role-collapse": updateJson("descriptor", (value) => {
      (value.normalizer as JsonRecord).role = "producer";
    }); break;
    case "selector-missing": updateJson("descriptor", (value) => {
      ((value.mapping as JsonRecord)).selector = "/sample/absent";
    }); break;
    case "selector-type-mismatch": updateJson("descriptor", (value) => {
      ((value.mapping as JsonRecord)).selector_value_type = "string";
    }); break;
    case "replay-from-future": updateJson("fixture", (value) => { value.replayed_at = "2026-08-26T13:37:54Z"; }); break;
    case "profile-expired-at-equality": inputs.evaluated_at = "2026-08-27T00:00:00Z"; break;
    case "invalidation-key-mismatch": updateJson("fixture", (value) => { value.invalidation_key_digest = "f".repeat(64); }); break;
    default: throw new Error(`not a replay hostile case: ${caseId}`);
  }
  return replayToolEvidenceProfile(inputs);
};

const registryHostile = (caseId: string) => {
  const registry = clone(TOOL_EVIDENCE_PROFILE_NORMALIZER_REGISTRY) as unknown as JsonRecord[];
  if (caseId === "normalizer-registry-tuple-duplicate") registry.push(clone(registry[0]!));
  else if (caseId === "normalizer-registry-tuple-unknown") {
    (registry[0]!.normalizer as JsonRecord).ref = "orodi://normalizer/unknown/v1";
  } else throw new Error(`not a registry hostile case: ${caseId}`);
  return validateToolEvidenceProfileNormalizerRegistry(registry);
};

const normalizerHostile = (caseId: string) => {
  const inputs = goldenInputs();
  const profile = JSON.parse(inputs.descriptor) as ToolEvidenceProfile;
  const fixture = JSON.parse(inputs.fixture) as ReturnType<typeof JSON.parse>;
  const registryEntry = selectToolEvidenceProfileNormalizer(profile)!;
  const golden = replayToolEvidenceProfile(inputs);
  assert.equal(golden.verdict, "replayed");
  const valid = runToolEvidenceProfileNormalizer({
    replay_id: inputs.replay_id,
    profile,
    fixture,
    selected_value: 42,
    selected_value_sha256: golden.normalization.selected_value_sha256!,
    registry_entry: registryEntry,
  });
  let candidate: unknown = clone(valid);
  const observation = (): JsonRecord => (candidate as JsonRecord).observation as JsonRecord;
  switch (caseId) {
    case "dynamic-loader-payload": candidate = "Function(payload)"; break;
    case "path-url-discovery-payload": candidate = "file:///tmp/normalizer.mjs"; break;
    case "normalizer-zero-observations": candidate = []; break;
    case "normalizer-multiple-observations": candidate = [clone(valid.observation), { ...clone(valid.observation), observation_id: "second" }]; break;
    case "duplicate-observation-id": candidate = [clone(valid.observation), clone(valid.observation)]; break;
    case "workflow-plane-observation": observation().plane = "workflow"; break;
    case "live-mode-observation": observation().mode = "live"; break;
    case "independent-observation-claim": observation().independently_observed = true; break;
    case "deployment-effect-claim": observation().deployment_effect = true; break;
    case "nonzero-telemetry-claim": ((observation().telemetry as JsonRecord)).offered = 1; break;
    case "unsafe-attribute-key": ((observation().attributes as JsonRecord))["secret.token"] = "forbidden"; break;
    case "attribute-cardinality-exceeded": ((observation().cardinality as JsonRecord)).observed = 999; break;
    default: throw new Error(`not a normalizer hostile case: ${caseId}`);
  }
  return validateToolEvidenceProfileNormalizerOutput(candidate, profile, fixture, inputs.replay_id);
};

const eligibilityHostile = (caseId: string) => {
  const inputs = goldenInputs();
  const golden = replayToolEvidenceProfile(inputs);
  assert.equal(golden.verdict, "replayed");
  const candidate = {
    normalization: clone(golden.normalization),
    evaluation_context: JSON.parse(inputs.evaluation_context) as JsonRecord,
    evaluated_at: inputs.evaluated_at,
  };
  switch (caseId) {
    case "forged-trust-or-runtime-admission": (candidate.normalization as unknown as JsonRecord).runtime_admission = "admitted"; break;
    case "eligible-control-or-observation-ref-laundering":
      ((candidate.evaluation_context.controls as JsonRecord[])[0]!).observation_refs = [golden.normalization.observations[0]!.observation_id];
      break;
    case "foundational-controls-incomplete": (candidate.evaluation_context.controls as unknown[]).pop(); break;
    case "legacy-v1-contract-impersonation": (candidate.normalization as unknown as JsonRecord).schema_version = "domainspec.orodi.legacy-v1-normalization-result/v1"; break;
    default: throw new Error(`not an eligibility hostile case: ${caseId}`);
  }
  return evaluateToolProfileEvidenceEligibility(candidate);
};

test("all 34 hostile cases execute through their bounded pure surface and fail closed", () => {
  for (const hostileCase of hostile.cases) {
    if (hostileCase.surface === "replay") {
      const result = replayHostile(hostileCase.case_id);
      assert.equal(result.verdict, "rejected", hostileCase.case_id);
      assert.ok(result.findings.some(({ code }) => code === hostileCase.expected_code), `${hostileCase.case_id}: ${JSON.stringify(result.findings)}`);
      assert.equal(result.normalization.verdict, "rejected");
      assert.deepEqual(result.normalization.observations, []);
      assert.equal(result.eligibility, null);
      assert.equal(result.runtime_admission, "denied");
      assert.equal(result.referent_trust, "unverified");
      assert.equal(result.authority_effect, "none");
      assert.deepEqual(result.findings, [...result.findings].sort((a, b) =>
        a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.detail.localeCompare(b.detail)));
    } else if (hostileCase.surface === "registry") {
      const findings = registryHostile(hostileCase.case_id);
      assert.ok(findings.some(({ code }) => code === hostileCase.expected_code), hostileCase.case_id);
      assert.deepEqual(findings, [...findings].sort((a, b) =>
        a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.detail.localeCompare(b.detail)));
    } else if (hostileCase.surface === "normalizer-output") {
      const result = normalizerHostile(hostileCase.case_id);
      assert.equal(result.observation, null, hostileCase.case_id);
      assert.ok(result.findings.some(({ code }) => code === hostileCase.expected_code), `${hostileCase.case_id}: ${JSON.stringify(result.findings)}`);
      assert.deepEqual(result.findings, [...result.findings].sort((a, b) =>
        a.path.localeCompare(b.path) || a.code.localeCompare(b.code) || a.detail.localeCompare(b.detail)));
    } else {
      const result = eligibilityHostile(hostileCase.case_id);
      assert.equal(result.decision, "rejected", hostileCase.case_id);
      assert.ok(result.findings.some(({ code }) => code === hostileCase.expected_code), `${hostileCase.case_id}: ${JSON.stringify(result.findings)}`);
      assert.deepEqual(result.replay_observations, []);
      assert.deepEqual(result.runtime_admitted_observations, []);
      assert.deepEqual(result.eligibility_receipts, []);
      assert.equal(result.derived_result, null);
      assert.equal(result.runtime_admission, "denied");
      assert.equal(result.referent_trust, "unverified");
      assert.equal(result.authority_effect, "none");
    }
  }
});
