import {lstat} from "node:fs/promises";

import {describe, expect, it} from "vitest";

import {runRuleReplay} from "./run-rule-replay.js";

const expectAbsent = async (path: string): Promise<void> => {
  await expect(lstat(path)).rejects.toMatchObject({code: "ENOENT"});
};

describe("RMT-RULE-007 deterministic replay", () => {
  it("repeats the exact semantic receipt in two fresh processes", async () => {
    const result = await runRuleReplay();
    expect(result).toMatchObject({
      result: "pass",
      exit_code: 0,
      semantic_receipts_deterministic: true,
      fresh_process_count_declared: 2,
      child_process_ids_excluded_from_semantic_identity: true,
      failure_exit_preserved: true,
      workspace_cleaned: true,
      cleanup_did_not_replace_primary_failure: true,
      authority_effect: "none",
    });
    expect(new Set(result.child_pids)).toHaveLength(2);
    expect(result.semantic_receipt).toMatchObject({
      result: "pass",
      semantic_controls: {declared: 10, killed: 10},
    });
    await expectAbsent(result.workspace_path);
  }, 120_000);

  it("preserves a nonzero exit even with valid-looking output", async () => {
    const result = await runRuleReplay({probe: "nonzero-with-valid-output"});
    expect(result).toMatchObject({
      result: "block",
      primary_failure: "RMT_RULE_REPLAY_CHILD_NONZERO",
      exit_code: 17,
      failure_exit_preserved: true,
      valid_output_did_not_mask_failure: true,
      workspace_cleaned: true,
      cleanup_did_not_replace_primary_failure: true,
      authority_effect: "none",
    });
    await expectAbsent(result.workspace_path);
  }, 120_000);

  it("rejects malformed child output before successful cleanup", async () => {
    const result = await runRuleReplay({probe: "malformed-output"});
    expect(result).toMatchObject({
      result: "block",
      primary_failure: "RMT_RULE_REPLAY_CHILD_OUTPUT_INVALID",
      exit_code: 0,
      failure_exit_preserved: true,
      workspace_cleaned: true,
      cleanup_did_not_replace_primary_failure: true,
      authority_effect: "none",
    });
    await expectAbsent(result.workspace_path);
  }, 30_000);
});
