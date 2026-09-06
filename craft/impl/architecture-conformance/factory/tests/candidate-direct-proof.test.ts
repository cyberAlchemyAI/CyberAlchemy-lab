import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { executeFactoryRun } from "../pipeline/execute-factory-run.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";
import { replayFactoryRun } from "../pipeline/replay-factory-run.js";
import { verifyFactoryRun } from "../pipeline/verify-factory-run.js";
import { canonicalJson, sha256 } from "../shared/canonical.js";

const fixturePath = resolve(
  repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/candidate-direct-proof.request.json",
);
const outputRoots: string[] = [];

afterEach(async () => Promise.all(outputRoots.splice(0).map((root) =>
  rm(root, { recursive: true, force: true }))));

describe("candidate direct factory proof", () => {
  it("executes and replays an explicit new-kit direct proof without granting init readiness", async () => {
    const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(fixturePath, "utf8")));
    expect(request).toMatchObject({
      schema_version: "FactoryRunRequest/v1",
      purpose: "new-kit-proof",
      authority_effect: "none",
      nodes: [{
        node_id: "candidate.rule.typescript.can-settle-payout",
        kind: "direct-proof",
        provider_id: "typescript-rule-v1",
        depends_on: [],
      }],
    });
    expect(request.nodes).toHaveLength(1);

    const plan = await planFactoryRun({ repositoryRoot, request });
    expect(plan.lock).toMatchObject({
      purpose: "new-kit-proof",
      ordered_node_ids: ["candidate.rule.typescript.can-settle-payout"],
      authority_effect: "none",
    });

    const outputRoot = await mkdtemp(resolve(tmpdir(), "domainspec-candidate-direct-proof-"));
    outputRoots.push(outputRoot);
    const run = await executeFactoryRun({ repositoryRoot, outputParent: outputRoot, plan });
    const verified = await verifyFactoryRun(run.run_path);
    const replayed = await replayFactoryRun(run.run_path);
    const semanticReceipt = JSON.parse(await readFile(
      resolve(run.run_path, "semantic-receipt.json"),
      "utf8",
    )) as Record<string, unknown>;
    const nodeSemantic = JSON.parse(await readFile(
      resolve(
        run.run_path,
        "nodes/candidate.rule.typescript.can-settle-payout/semantic.json",
      ),
      "utf8",
    )) as Record<string, unknown>;
    const orderedNodes = semanticReceipt.ordered_nodes as readonly Record<string, unknown>[];
    const nodeReceipt = orderedNodes[0]!;

    expect(run).toMatchObject({ result: "pass", authority_effect: "none" });
    expect(verified).toMatchObject({
      result: "pass",
      semantic_receipt_sha256: run.semantic_receipt_sha256,
      lock_sha256: run.lock_sha256,
      run_id: run.run_id,
      authority_effect: "none",
    });
    expect(replayed).toMatchObject({
      result: "pass",
      replayed_nodes: 1,
      authority_effect: "none",
    });
    expect(replayed.child_pids.every((pid) => pid !== process.pid)).toBe(true);
    expect(semanticReceipt).toMatchObject({
      schema_version: "FactorySemanticReceipt/v1",
      result: "pass",
      request_sha256: plan.lock.request_sha256,
      lock_sha256: plan.lock.lock_sha256,
      run_id: plan.run_id,
      claim_ceiling:
        "candidate-local direct proof for one bounded TypeScript Rule; no factory inspect or init readiness",
      authority_effect: "none",
    });
    expect(orderedNodes).toHaveLength(1);
    expect(nodeReceipt).toMatchObject({
      node_id: "candidate.rule.typescript.can-settle-payout",
      provider_id: "typescript-rule-v1",
      depends_on: [],
      accounting: {
        positives_declared: 3,
        positives_passed: 3,
        mutants_declared: 3,
        mutants_killed: 3,
      },
      claim_ceiling: "one candidate-local handwritten TypeScript Rule in the admitted bound-arrow subset",
    });
    expect(nodeReceipt.semantic_sha256).toBe(nodeReceipt.replay_sha256);
    expect(sha256(canonicalJson(nodeSemantic))).toBe(nodeReceipt.semantic_sha256);
  }, 70_000);
});
