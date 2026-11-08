import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { FOUNDATIONAL_CONTROL_IDS } from "../contracts/operational-evidence.js";
import type { LegacyV1EligibilityReplayRequest } from "../contracts/evidence-eligibility.js";
import type { LegacyV1SourceInventory } from "../contracts/legacy-v1-adapter.js";
import type {
  ToolEvidenceProfileReplayCaseBundle,
  ToolEvidenceProfileReplayTestContextBundle,
} from "../contracts/tool-evidence-profile-replay.js";
import {
  evaluateLegacyV1EvidenceEligibility,
  evaluateToolProfileEvidenceEligibility,
} from "../src/evaluate-evidence-eligibility.js";
import { replayToolEvidenceProfile } from "../src/replay-tool-evidence-profile.js";
import { validateToolEvidenceProfile } from "../src/validate-tool-evidence-profile.js";

type JsonRecord = Record<string, unknown>;
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const read = (path: string): string => readFileSync(path, "utf8");
const parse = <T>(path: string): T => JSON.parse(read(path)) as T;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

const cases = parse<ToolEvidenceProfileReplayCaseBundle>(resolve(root, "fixtures/tool-evidence-profile-replay/golden/cases.json"));
const contexts = parse<ToolEvidenceProfileReplayTestContextBundle>(resolve(root, "fixtures/tool-evidence-profile-replay/evaluation-context.json"));
const inventory = read(resolve(root, "contracts/tool-evidence-profile-family-inventory.json"));
const policy = read(resolve(root, "contracts/tool-evidence-profile-attribute-policy.json"));
const referents = read(resolve(root, "fixtures/tool-evidence-profiles/referents.json"));

const goldenCandidate = () => {
  const replayCase = cases.cases[0]!;
  const descriptor = read(resolve(root, replayCase.descriptor_ref));
  const context = contexts.contexts.find(({ context_id }) => context_id === replayCase.context_id)!;
  const wp5 = validateToolEvidenceProfile({
    descriptor, family_inventory: inventory, attribute_policy: policy,
    referent_inventory: referents, evaluated_at: cases.evaluated_at,
  });
  const replay = replayToolEvidenceProfile({
    replay_id: "wp6-profile-eligibility-golden",
    descriptor, family_inventory: inventory, attribute_policy: policy,
    referent_inventory: referents, wp5_validation_result: JSON.stringify(wp5),
    fixture: JSON.stringify(replayCase.fixture),
    evaluation_context: JSON.stringify(context.evaluation_context),
    evaluated_at: cases.evaluated_at,
  });
  assert.equal(replay.verdict, "replayed", JSON.stringify(replay.findings));
  return {
    normalization: replay.normalization,
    evaluation_context: context.evaluation_context,
    evaluated_at: cases.evaluated_at,
  };
};

test("the profile sibling gate retains one replay observation and admits none", () => {
  const candidate = goldenCandidate();
  const before = JSON.stringify(candidate);
  const first = evaluateToolProfileEvidenceEligibility(candidate);
  const second = evaluateToolProfileEvidenceEligibility(candidate);
  assert.equal(JSON.stringify(candidate), before);
  assert.equal(JSON.stringify(first), JSON.stringify(second));
  assert.equal(first.gate_id, "domainspec.orodi.tool-profile-replay-evidence-eligibility");
  assert.equal(first.decision, "replay-only");
  assert.equal(first.runtime_admission, "denied");
  assert.equal(first.referent_trust, "unverified");
  assert.equal(first.replay_observations.length, 1);
  assert.deepEqual(first.runtime_admitted_observations, []);
  assert.equal(first.eligibility_receipts.length, 1);
  assert.deepEqual(first.eligibility_receipts[0]!.eligible_controls, []);
  assert.deepEqual(first.eligibility_receipts[0]!.ineligible_controls, FOUNDATIONAL_CONTROL_IDS);
  assert.equal(first.authority_effect, "none");
});

test("foundational controls are derived only from the empty admitted set", () => {
  const result = evaluateToolProfileEvidenceEligibility(goldenCandidate());
  assert.ok(result.derived_result);
  assert.equal(result.derived_result.comparison, "match");
  assert.deepEqual(
    result.derived_result.derived_controls.map(({ control_id, state, observation_refs }) =>
      ({ control_id, state, observation_refs })),
    [
      { control_id: "C01", state: "passed", observation_refs: [] },
      { control_id: "C05", state: "missing", observation_refs: [] },
      { control_id: "C11", state: "not-run", observation_refs: [] },
      { control_id: "C12", state: "not-run", observation_refs: [] },
      { control_id: "C14", state: "passed", observation_refs: [] },
      { control_id: "C15", state: "missing", observation_refs: [] },
    ],
  );
});

test("profile rejection exposes no partial observation, receipt, or derived result", () => {
  const candidate = clone(goldenCandidate()) as unknown as JsonRecord;
  const context = candidate.evaluation_context as JsonRecord;
  (context.controls as unknown[]).pop();
  const result = evaluateToolProfileEvidenceEligibility(candidate);
  assert.equal(result.decision, "rejected");
  assert.deepEqual(result.replay_observations, []);
  assert.deepEqual(result.runtime_admitted_observations, []);
  assert.deepEqual(result.eligibility_receipts, []);
  assert.equal(result.derived_result, null);
  assert.ok(result.findings.some(({ code }) => code === "FOUNDATIONAL_CONTROLS_INCOMPLETE"));
});

test("the legacy-v1 gate remains a distinct compatible sibling", () => {
  const request = parse<LegacyV1EligibilityReplayRequest>(resolve(root, "fixtures/eligibility/golden/replay-request.json"));
  const legacyInventory = parse<LegacyV1SourceInventory>(resolve(root, "contracts/legacy-v1-source-inventory.json"));
  const result = evaluateLegacyV1EvidenceEligibility(request, legacyInventory);
  assert.equal(result.gate_id, "domainspec.orodi.legacy-v1-evidence-eligibility");
  assert.equal(result.schema_version, "domainspec.orodi.evidence-eligibility-result/v1");
  assert.equal(result.decision, "replay-only");
  assert.equal(result.runtime_admission, "denied");
  assert.notEqual(result.gate_id, evaluateToolProfileEvidenceEligibility(goldenCandidate()).gate_id);
});
