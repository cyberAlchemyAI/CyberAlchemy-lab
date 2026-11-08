import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { replayFromRawInputsV2 } from "../../../kernel/evidence/generic-replay-v2.js";
import { buildDirectOperationProof } from "../../operation/typescript/run-direct-operation-proof.js";
import { buildTypeScriptRuleProof, loadTypeScriptRuleRawInputs } from "../../rule/typescript/run-rule-proof.js";
import {
  loadCompositionRawInputs,
  publishCompositionProof,
  repositoryRoot,
} from "./run-composition-proof.js";

describe("Rule enforces Operation composition proof", () => {
  it("joins direct proofs, call-before-write trace, two mutants, and raw replay", async () => {
    const root = await mkdtemp(join(tmpdir(), "domainspec-relation-proof-"));
    try {
      const [rule, operation] = await Promise.all([
        loadTypeScriptRuleRawInputs().then(buildTypeScriptRuleProof),
        buildDirectOperationProof(),
      ]);
      const rawInputs = await loadCompositionRawInputs({
        ruleDirectProof: JSON.stringify(rule.summary),
        operationDirectProof: JSON.stringify(operation),
      });
      const joined = await publishCompositionProof({
        evidenceRoot: root,
        runId: "proof",
        rawInputs,
      });
      expect(joined.proof.summary.positive).toEqual({
        outcome: true,
        trace: ["rule-call", "operation-call", "payout-write", "payout-created-event"],
        verdict: "pass",
      });
      expect(joined.proof.summary.denied_guard).toEqual({
        outcome: false, trace: ["rule-call"], payout_count: 0,
      });
      expect(joined.proof.summary.mutations.map(({ status }) => status)).toEqual([
        "killed", "killed",
      ]);
      const replay = await replayFromRawInputsV2({
        repositoryRoot, runPath: joined.publication.runPath,
        rawIndex: joined.publication.index,
        rawIndexSha256: joined.publication.indexSha256,
        manifest: joined.manifest,
      });
      expect(replay.status).toBe("pass");
      expect(replay.child_pid).not.toBe(process.pid);
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  }, 60_000);
});
