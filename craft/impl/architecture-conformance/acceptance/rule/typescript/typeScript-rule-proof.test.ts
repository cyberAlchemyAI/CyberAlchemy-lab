import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { replayFromRawInputsV2 } from "../../../kernel/evidence/generic-replay-v2.js";
import { publishTypeScriptRuleProof, repositoryRoot } from "./run-rule-proof.js";

describe("joined TypeScript Rule proof", () => {
  it("accounts for all positives/mutants and replays from pinned raw inputs", async () => {
    const root = await mkdtemp(join(tmpdir(), "domainspec-rule-proof-"));
    try {
      const joined = await publishTypeScriptRuleProof({ evidenceRoot: root, runId: "proof" });
      expect(joined.proof.summary.accounting).toMatchObject({
        result: "pass",
        positive: { declared: 3, passed: 3, failed: 0, unaccounted: 0 },
        mutations: { declared: 3, killed: 3, survived: 0, unaccounted: 0 },
      });
      const replay = await replayFromRawInputsV2({
        repositoryRoot,
        runPath: joined.publication.runPath,
        rawIndex: joined.publication.index,
        rawIndexSha256: joined.publication.indexSha256,
        manifest: joined.manifest,
      });
      expect(replay.status).toBe("pass");
      expect(replay.child_pid).not.toBe(process.pid);
      expect(replay.claims).toEqual({
        semantic_recomposition: "pass",
        process_isolation: "pass",
        byte_identity: "not-claimed",
      });
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  }, 60_000);
});
