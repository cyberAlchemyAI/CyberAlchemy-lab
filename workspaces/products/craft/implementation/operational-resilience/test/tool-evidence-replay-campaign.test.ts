import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import type {
  ToolEvidenceReplayCampaignExpectedResultBundle,
  ToolEvidenceReplayCampaignFixtureBundle,
  ToolEvidenceReplayCampaignHostileCaseBundle,
  ToolEvidenceReplayCampaignInputs,
  ToolEvidenceReplayCampaignResult,
} from "../contracts/tool-evidence-replay-campaign.js";
import type {
  ToolEvidenceProfileReplayCaseBundle,
  ToolEvidenceProfileReplayInputs,
  ToolEvidenceProfileReplayTestContextBundle,
} from "../contracts/tool-evidence-profile-replay.js";
import { composeToolEvidenceReplayCampaign } from "../src/compose-tool-evidence-replay-campaign.js";
import { replayToolEvidenceProfile } from "../src/replay-tool-evidence-profile.js";
import { validateToolEvidenceProfile } from "../src/validate-tool-evidence-profile.js";

type JsonRecord = Record<string, unknown>;
type MutableReplayInputs = Record<keyof ToolEvidenceProfileReplayInputs, string>;
type MutableCampaignItem = {
  item_id: string;
  replay_inputs: MutableReplayInputs;
  supplied_result_bytes?: string;
  supplied_result_sha256: string;
};
type MutableCampaign = {
  campaign_id: string;
  evaluated_at: string;
  items: MutableCampaignItem[];
  authority_effect: string;
};

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const campaignFixturePath = resolve(root, "fixtures/tool-evidence-replay-campaign/golden/cases.json");
const hostilePath = resolve(root, "fixtures/tool-evidence-replay-campaign/hostile/cases.json");
const expectedPath = resolve(root, "fixtures/tool-evidence-replay-campaign/expected-results.json");
const wp6CasesPath = resolve(root, "fixtures/tool-evidence-profile-replay/golden/cases.json");
const contextsPath = resolve(root, "fixtures/tool-evidence-profile-replay/evaluation-context.json");
const inventoryPath = resolve(root, "contracts/tool-evidence-profile-family-inventory.json");
const policyPath = resolve(root, "contracts/tool-evidence-profile-attribute-policy.json");
const referentsPath = resolve(root, "fixtures/tool-evidence-profiles/referents.json");
const fixtureSchema = resolve(root, "contracts/tool-evidence-replay-campaign-fixture.schema.json");
const resultSchema = resolve(root, "contracts/tool-evidence-replay-campaign-result.schema.json");
const composerSource = resolve(root, "src/compose-tool-evidence-replay-campaign.ts");

const text = (path: string): string => readFileSync(path, "utf8");
const json = <T>(path: string): T => JSON.parse(text(path)) as T;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const sha256 = (value: string): string => createHash("sha256").update(value).digest("hex");

const campaigns = json<ToolEvidenceReplayCampaignFixtureBundle>(campaignFixturePath);
const hostile = json<ToolEvidenceReplayCampaignHostileCaseBundle>(hostilePath);
const expected = json<ToolEvidenceReplayCampaignExpectedResultBundle>(expectedPath);
const wp6Cases = json<ToolEvidenceProfileReplayCaseBundle>(wp6CasesPath);
const contexts = json<ToolEvidenceProfileReplayTestContextBundle>(contextsPath);
const inventory = text(inventoryPath);
const policy = text(policyPath);
const referents = text(referentsPath);

const schemaCheck = (instance: unknown, schema: string, scratch: string, name: string): void => {
  const instancePath = join(scratch, `${name}.json`);
  writeFileSync(instancePath, `${JSON.stringify(instance, null, 2)}\n`);
  const check = spawnSync("python3", ["-m", "jsonschema", "-i", instancePath, schema], { encoding: "utf8" });
  assert.equal(check.status, 0, check.stdout + check.stderr);
};

const replayInputsFor = (caseId: string): ToolEvidenceProfileReplayInputs => {
  const replayCase = wp6Cases.cases.find(({ case_id }) => case_id === caseId);
  assert.ok(replayCase, `unknown WP6 case ${caseId}`);
  const descriptor = text(resolve(root, replayCase.descriptor_ref));
  const context = contexts.contexts.find(({ context_id }) => context_id === replayCase.context_id);
  assert.ok(context, `unknown WP6 context ${replayCase.context_id}`);
  const wp5 = validateToolEvidenceProfile({
    descriptor,
    family_inventory: inventory,
    attribute_policy: policy,
    referent_inventory: referents,
    evaluated_at: campaigns.evaluated_at,
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
    evaluated_at: campaigns.evaluated_at,
  };
};

const campaignItemFor = (caseId: string) => {
  const replayInputs = replayInputsFor(caseId);
  const suppliedResultBytes = JSON.stringify(replayToolEvidenceProfile(replayInputs));
  return {
    item_id: `item-${caseId}`,
    replay_inputs: replayInputs,
    supplied_result_bytes: suppliedResultBytes,
    supplied_result_sha256: sha256(suppliedResultBytes),
  } as const;
};

const campaignInput = (
  campaignId: string,
  itemCaseIds: readonly string[],
): ToolEvidenceReplayCampaignInputs => ({
  campaign_id: campaignId,
  evaluated_at: campaigns.evaluated_at,
  items: itemCaseIds.map(campaignItemFor),
  authority_effect: "none",
});

const assertAuthorityCeiling = (result: ToolEvidenceReplayCampaignResult): void => {
  assert.equal(result.runtime_admission, "denied");
  assert.equal(result.referent_trust, "unverified");
  assert.equal(result.authority_effect, "none");
  assert.deepEqual(result.runtime_admitted_observations, []);
  assert.deepEqual(result.eligible_controls, []);
  assert.equal("aggregate_derived_result" in result, false);
};

const isDeepFrozen = (value: unknown): boolean =>
  value === null || typeof value !== "object" ||
  (Object.isFrozen(value) && Object.values(value as JsonRecord).every(isDeepFrozen));

const sortedFindings = (result: ToolEvidenceReplayCampaignResult) =>
  [...result.findings].sort((left, right) =>
    (left.path < right.path ? -1 : left.path > right.path ? 1 : 0) ||
    (left.code < right.code ? -1 : left.code > right.code ? 1 : 0) ||
    (left.detail < right.detail ? -1 : left.detail > right.detail ? 1 : 0));

const mutableBase = (): MutableCampaign => clone(campaignInput(
  "campaign-hostile",
  ["golden-telemetry", "golden-health-failure"],
)) as unknown as MutableCampaign;

const updateSuppliedResult = (
  item: MutableCampaignItem,
  mutate: (result: JsonRecord) => void,
): void => {
  if (typeof item.supplied_result_bytes !== "string") {
    throw new Error("supplied result bytes are absent");
  }
  const result = JSON.parse(item.supplied_result_bytes) as JsonRecord;
  mutate(result);
  item.supplied_result_bytes = JSON.stringify(result);
  item.supplied_result_sha256 = sha256(item.supplied_result_bytes);
};

const refreshSuppliedResult = (item: MutableCampaignItem): void => {
  const result = replayToolEvidenceProfile(item.replay_inputs as unknown as ToolEvidenceProfileReplayInputs);
  item.supplied_result_bytes = JSON.stringify(result);
  item.supplied_result_sha256 = sha256(item.supplied_result_bytes);
};

const replaceSecondWithFirstFamily = (campaign: MutableCampaign, caseId: string): void => {
  const duplicate = clone(campaign.items[0]!);
  duplicate.item_id = `item-${caseId}`;
  duplicate.replay_inputs.replay_id = `wp6-${caseId}`;
  refreshSuppliedResult(duplicate);
  campaign.items[1] = duplicate;
};

const hostileInput = (caseId: string): ToolEvidenceReplayCampaignInputs => {
  let campaign = mutableBase();
  switch (caseId) {
    case "zero-items": campaign.items = []; break;
    case "one-item": campaign.items = [campaign.items[0]!]; break;
    case "eight-items": {
      campaign = clone(campaignInput(
        "campaign-hostile",
        campaigns.campaigns.find(({ case_id }) => case_id === "golden-full-seven")!.item_case_ids,
      )) as unknown as MutableCampaign;
      const eighth = clone(campaign.items[0]!);
      eighth.item_id = "item-eighth";
      campaign.items.push(eighth);
      break;
    }
    case "duplicate-item-id": campaign.items[1]!.item_id = campaign.items[0]!.item_id; break;
    case "duplicate-replay-id":
      campaign.items[1]!.replay_inputs.replay_id = campaign.items[0]!.replay_inputs.replay_id;
      refreshSuppliedResult(campaign.items[1]!);
      break;
    case "duplicate-family": replaceSecondWithFirstFamily(campaign, caseId); break;
    case "duplicate-profile-identity": replaceSecondWithFirstFamily(campaign, caseId); break;
    case "duplicate-binding-id": replaceSecondWithFirstFamily(campaign, caseId); break;
    case "duplicate-observation-id": {
      const duplicate = clone(campaign.items[0]!);
      duplicate.item_id = `item-${caseId}`;
      campaign.items[1] = duplicate;
      break;
    }
    case "evaluated-at-mismatch": campaign.evaluated_at = "2026-08-26T12:38:54Z"; break;
    case "supplied-result-absent": delete campaign.items[0]!.supplied_result_bytes; break;
    case "supplied-result-malformed":
      campaign.items[0]!.supplied_result_bytes = "{";
      campaign.items[0]!.supplied_result_sha256 = sha256("{");
      break;
    case "supplied-result-digest-drift": campaign.items[0]!.supplied_result_sha256 = "0".repeat(64); break;
    case "recomputed-replay-rejected": {
      const fixture = JSON.parse(campaign.items[0]!.replay_inputs.fixture) as JsonRecord;
      fixture.source_sha256 = "0".repeat(64);
      campaign.items[0]!.replay_inputs.fixture = JSON.stringify(fixture);
      break;
    }
    case "supplied-result-semantic-drift":
      updateSuppliedResult(campaign.items[0]!, (result) => { result.replay_id = "semantic-drift"; });
      break;
    case "eligibility-absent":
      updateSuppliedResult(campaign.items[0]!, (result) => { result.eligibility = null; });
      break;
    case "eligibility-rejected":
      updateSuppliedResult(campaign.items[0]!, (result) => {
        (result.eligibility as JsonRecord).decision = "rejected";
      });
      break;
    case "runtime-admission-forged":
      updateSuppliedResult(campaign.items[0]!, (result) => { result.runtime_admission = "allowed"; });
      break;
    case "referent-trust-forged":
      updateSuppliedResult(campaign.items[0]!, (result) => { result.referent_trust = "verified"; });
      break;
    case "authority-effect-forged":
      updateSuppliedResult(campaign.items[0]!, (result) => { result.authority_effect = "deployment"; });
      break;
    case "runtime-observation-forged":
      updateSuppliedResult(campaign.items[0]!, (result) => {
        const eligibility = result.eligibility as JsonRecord;
        eligibility.runtime_admitted_observations = clone(eligibility.replay_observations);
      });
      break;
    case "eligible-controls-forged":
      updateSuppliedResult(campaign.items[0]!, (result) => {
        const eligibility = result.eligibility as JsonRecord;
        const receipt = (eligibility.eligibility_receipts as JsonRecord[])[0]!;
        receipt.eligible_controls = ["C01"];
      });
      break;
    case "live-mode-observation":
      updateSuppliedResult(campaign.items[0]!, (result) => {
        const eligibility = result.eligibility as JsonRecord;
        (eligibility.replay_observations as JsonRecord[])[0]!.mode = "live";
      });
      break;
    case "deployment-effect-forged":
      updateSuppliedResult(campaign.items[0]!, (result) => {
        const eligibility = result.eligibility as JsonRecord;
        (eligibility.replay_observations as JsonRecord[])[0]!.deployment_effect = true;
      });
      break;
    case "independent-observation-forged":
      updateSuppliedResult(campaign.items[0]!, (result) => {
        const eligibility = result.eligibility as JsonRecord;
        (eligibility.replay_observations as JsonRecord[])[0]!.independently_observed = true;
      });
      break;
    default: throw new Error(`unknown hostile campaign case ${caseId}`);
  }
  return campaign as unknown as ToolEvidenceReplayCampaignInputs;
};

test("the persisted campaign corpus is the exact finite denominator", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-wp7-fixture-"));
  try {
    assert.equal(campaigns.campaigns.length, 3);
    assert.equal(new Set(campaigns.campaigns.map(({ case_id }) => case_id)).size, 3);
    assert.equal(hostile.cases.length, 25);
    assert.equal(expected.results.length, 25);
    assert.equal(new Set(hostile.cases.map(({ case_id }) => case_id)).size, 25);
    assert.deepEqual(
      [...hostile.cases].sort((left, right) => left.case_id.localeCompare(right.case_id)),
      [...expected.results].sort((left, right) => left.case_id.localeCompare(right.case_id)),
    );
    const full = campaigns.campaigns.find(({ case_id }) => case_id === "golden-full-seven")!;
    const families = full.item_case_ids.map((caseId) =>
      wp6Cases.cases.find(({ case_id }) => case_id === caseId)!.family_id);
    assert.equal(new Set(families).size, 7);
    assert.equal(campaigns.campaigns.every(({ item_case_ids }) =>
      item_case_ids.length >= 2 && item_case_ids.length <= 7 &&
      new Set(item_case_ids).size === item_case_ids.length), true);
    schemaCheck(campaigns, fixtureSchema, scratch, "campaign-fixtures");
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("all three golden campaigns compose as independent replay-only partitions", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-wp7-golden-"));
  try {
    for (const campaign of campaigns.campaigns) {
      const inputs = campaignInput(campaign.campaign_id, campaign.item_case_ids);
      const before = JSON.stringify(inputs);
      const first = composeToolEvidenceReplayCampaign(inputs);
      const second = composeToolEvidenceReplayCampaign(inputs);
      assert.equal(first.verdict, "composed", `${campaign.case_id}: ${JSON.stringify(first.findings)}`);
      assert.equal(JSON.stringify(first), JSON.stringify(second), campaign.case_id);
      assert.equal(JSON.stringify(inputs), before, campaign.case_id);
      assert.equal(first.item_receipts.length, campaign.item_case_ids.length);
      assert.equal(first.replay_observations.length, campaign.item_case_ids.length);
      assert.equal(first.eligibility_receipts.length, campaign.item_case_ids.length);
      assert.equal(first.per_binding_derived_results.length, campaign.item_case_ids.length);
      assert.equal(new Set(first.item_receipts.map(({ family_id }) => family_id)).size, campaign.item_case_ids.length);
      assert.equal(new Set(first.item_receipts.map(({ binding_id }) => binding_id)).size, campaign.item_case_ids.length);
      assert.equal(first.eligibility_receipts.every(({ decision, eligible_controls }) =>
        decision === "replay-only" && eligible_controls.length === 0), true);
      assert.equal(first.replay_observations.every((observation) =>
        observation.plane === "product" && observation.mode === "simulation" &&
        observation.deployment_effect === false && observation.independently_observed === false &&
        Object.values(observation.telemetry).every((count) => count === 0)), true);
      first.per_binding_derived_results.forEach((partition) => {
        assert.equal(partition.binding_id, partition.derived_result.binding_id);
        assert.equal(partition.authority_effect, "none");
      });
      assertAuthorityCeiling(first);
      assert.equal(isDeepFrozen(first), true);
      schemaCheck(first, resultSchema, scratch, campaign.case_id);
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("the full-seven campaign is byte-identical under fixed input permutations", () => {
  const full = campaigns.campaigns.find(({ case_id }) => case_id === "golden-full-seven")!;
  const base = campaignInput(full.campaign_id, full.item_case_ids);
  const reversed = { ...base, items: [...base.items].reverse() };
  const shuffleOrder = [3, 0, 6, 2, 5, 1, 4] as const;
  const shuffled = { ...base, items: shuffleOrder.map((index) => base.items[index]!) };
  const originalResult = composeToolEvidenceReplayCampaign(base);
  assert.equal(originalResult.verdict, "composed", JSON.stringify(originalResult.findings));
  assert.equal(JSON.stringify(composeToolEvidenceReplayCampaign(reversed)), JSON.stringify(originalResult));
  assert.equal(JSON.stringify(composeToolEvidenceReplayCampaign(shuffled)), JSON.stringify(originalResult));
});

test("all 25 hostile campaigns reject atomically with their required discriminator", () => {
  const scratch = mkdtempSync(join(tmpdir(), "orodi-wp7-hostile-"));
  try {
    for (const hostileCase of hostile.cases) {
      const inputs = hostileInput(hostileCase.case_id);
      const first = composeToolEvidenceReplayCampaign(inputs);
      const second = composeToolEvidenceReplayCampaign(inputs);
      assert.equal(first.verdict, "rejected", hostileCase.case_id);
      assert.equal(JSON.stringify(first), JSON.stringify(second), hostileCase.case_id);
      assert.ok(first.findings.some(({ code }) => code === hostileCase.required_code),
        `${hostileCase.case_id}: ${JSON.stringify(first.findings)}`);
      assert.deepEqual(first.findings, sortedFindings(first), hostileCase.case_id);
      assert.deepEqual(first.item_receipts, [], hostileCase.case_id);
      assert.deepEqual(first.replay_observations, [], hostileCase.case_id);
      assert.deepEqual(first.eligibility_receipts, [], hostileCase.case_id);
      assert.deepEqual(first.per_binding_derived_results, [], hostileCase.case_id);
      assertAuthorityCeiling(first);
      assert.equal(isDeepFrozen(first), true, hostileCase.case_id);
      schemaCheck(first, resultSchema, scratch, hostileCase.case_id);
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

test("the campaign product source exposes no I/O, dynamic-code, clock, or live-tool surface", () => {
  const source = text(composerSource);
  const forbidden = /import\(|require\(|eval\(|new Function|Function\(|node:(?:fs|child_process|net|http|https|os|vm|module)|process\.|fetch\(|Date\.now|new Date\(|readdir\(|glob\(|exec(?:File)?\(|spawn\(/;
  assert.equal(forbidden.test(source), false);
  assert.equal(source.includes("replayToolEvidenceProfile"), true);
  assert.equal(source.includes("aggregate_derived_result"), false);
});
