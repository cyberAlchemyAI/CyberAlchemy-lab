import { mkdir, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

import type {
  FactoryNodeSemanticResultV1,
  FactoryUpstreamResultV1,
} from "../contracts/factory-node-provider-v1.js";
import type { FactoryProcessObservationV1 } from "../contracts/factory-process-observation-v1.js";
import type { FactorySemanticNodeReceiptV1 } from "../contracts/factory-semantic-receipt-v1.js";
import type { FactoryRunPlanV1 } from "../contracts/factory-run-plan-v1.js";
import { normalizeFactorySemanticReceipt } from "../evidence/normalize-semantic-receipt.js";
import { publishFactoryRun } from "../evidence/publish-factory-run.js";
import { getFactoryNodeProviderV1 } from "../registry/factory-node-registry-v1.js";
import { runLockedChild } from "../replay/run-locked-child.js";
import { resolveLockedSnapshot } from "../resolution/resolve-locked-snapshot.js";
import {
  resolveProviderExecutionContextV1,
  verifyProviderExecutionContextV1,
} from "../resolution/resolve-provider-execution-context.js";
import { canonicalJson, fail, json, sha256 } from "../shared/canonical.js";

const deepFreeze = <T>(value: T): T => {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
};

export const bindReplayVerifiedSemanticResult = (input: Readonly<{
  node_id: string;
  locked_claim_ceiling: string;
  direct_sha256: string;
  replay_result: FactoryNodeSemanticResultV1;
  replay_result_sha256: string;
}>): FactoryNodeSemanticResultV1 => {
  if (input.replay_result_sha256 !== input.direct_sha256 ||
      sha256(canonicalJson(input.replay_result)) !== input.replay_result_sha256) {
    return fail("FACTORY_REPLAY_DRIFT", input.node_id);
  }
  if (input.replay_result.claim_ceiling !== input.locked_claim_ceiling) {
    return fail("FACTORY_CLAIM_CEILING_MISMATCH", input.node_id);
  }
  return deepFreeze(input.replay_result);
};

export const executeFactoryRun = async (input: Readonly<{
  repositoryRoot: string;
  outputParent: string;
  plan: FactoryRunPlanV1;
}>): Promise<Readonly<{
  result: "pass";
  run_path: string;
  run_id: string;
  semantic_receipt_sha256: string;
  lock_sha256: string;
  authority_effect: "none";
}>> => {
  let semanticReceiptSha256 = "";
  const startedAt = new Date().toISOString();
  const publication = await publishFactoryRun({
    outputParent: input.outputParent,
    plan: input.plan,
    build: async (stagingRoot, targetPath) => {
      await writeFile(resolve(stagingRoot, "request.json"), json(input.plan.request), { flag: "wx" });
      await writeFile(resolve(stagingRoot, "lock.json"), json(input.plan.lock), { flag: "wx" });
      await writeFile(resolve(stagingRoot, "plan.json"), json(input.plan), { flag: "wx" });
      const snapshot = await resolveLockedSnapshot({
        repositoryRoot: input.repositoryRoot,
        stagingRoot,
        lock: input.plan.lock,
      });
      const nodeResults: Record<string, FactoryNodeSemanticResultV1> = {};
      const upstreamHandles: Record<string, FactoryUpstreamResultV1> = {};
      const semanticNodes: FactorySemanticNodeReceiptV1[] = [];
      const childPids: number[] = [];
      const scratchRoot = resolve(stagingRoot, "scratch");
      await mkdir(scratchRoot);
      for (const nodeId of input.plan.lock.ordered_node_ids) {
        const locked = input.plan.lock.nodes.find(({ node_id: id }) => id === nodeId)!;
        const provider = getFactoryNodeProviderV1(locked.provider_id);
        const upstream = Object.fromEntries(locked.depends_on.map((dependency) => {
          const handle = upstreamHandles[dependency];
          if (handle === undefined) fail("FACTORY_DEPENDENCY_STALE", dependency);
          return [dependency, handle];
        }));
        const rawInputs = snapshot.raw_inputs_by_node[nodeId];
        if (rawInputs === undefined) fail("FACTORY_SNAPSHOT_INCOMPLETE", nodeId);
        const directScratch = resolve(scratchRoot, "direct", nodeId);
        await mkdir(directScratch, { recursive: true });
        const directExecution = await resolveProviderExecutionContextV1({
          repositoryRoot: input.repositoryRoot,
          provider,
          lockedNode: locked,
          scratchPath: directScratch,
          outputLimitBytes: input.plan.lock.replay_policy.output_limit_bytes,
          terminationGraceMs: input.plan.lock.replay_policy.termination_grace_ms,
        });
        const direct = await provider.execute({
          raw_inputs: rawInputs,
          upstream,
          execution_context: directExecution.context,
        });
        await verifyProviderExecutionContextV1({
          before: directExecution,
          repositoryRoot: input.repositoryRoot,
          provider,
          lockedNode: locked,
        });
        const directSha256 = sha256(canonicalJson(direct));
        const replay = await runLockedChild({
          scratchRoot,
          nodeId,
          providerId: locked.provider_id,
          rawInputs,
          upstream,
          lock: input.plan.lock,
        });
        childPids.push(replay.child_pid);
        const stable = bindReplayVerifiedSemanticResult({
          node_id: nodeId,
          locked_claim_ceiling: locked.claim_ceiling,
          direct_sha256: directSha256,
          replay_result: replay.result,
          replay_result_sha256: replay.result_sha256,
        });
        if (stable.accounting.positives_declared !== stable.accounting.positives_passed ||
            stable.accounting.mutants_declared !== stable.accounting.mutants_killed) {
          fail("FACTORY_ACCOUNTING_INCOMPLETE", nodeId);
        }
        nodeResults[nodeId] = stable;
        upstreamHandles[nodeId] = Object.freeze({
          node_id: nodeId,
          provider_id: locked.provider_id,
          semantic_sha256: replay.result_sha256,
          semantic_output: stable.semantic_output,
        });
        const nodeRoot = resolve(stagingRoot, "nodes", nodeId);
        await mkdir(nodeRoot, { recursive: true });
        await writeFile(resolve(nodeRoot, "semantic.json"), json(stable), { flag: "wx" });
        await writeFile(resolve(nodeRoot, "replay.json"), json(Object.freeze({
          schema_version: "FactoryNodeReplay/v1",
          result: "pass",
          semantic_sha256: replay.result_sha256,
          stdout_bytes: replay.stdout_bytes,
          stderr_bytes: replay.stderr_bytes,
          authority_effect: "none",
        })), { flag: "wx" });
        semanticNodes.push(Object.freeze({
          node_id: nodeId,
          provider_id: locked.provider_id,
          depends_on: locked.depends_on,
          semantic_sha256: replay.result_sha256,
          replay_sha256: replay.result_sha256,
          accounting: stable.accounting,
          claim_ceiling: stable.claim_ceiling,
        }));
      }
      await rm(scratchRoot, { recursive: true, force: false });
      const normalized = normalizeFactorySemanticReceipt({ plan: input.plan, nodes: semanticNodes });
      semanticReceiptSha256 = normalized.semantic_receipt_sha256;
      await writeFile(resolve(stagingRoot, "semantic-receipt.json"), json(normalized.receipt), { flag: "wx" });
      const processObservation: FactoryProcessObservationV1 = Object.freeze({
        schema_version: "FactoryProcessObservation/v1",
        run_id: input.plan.run_id,
        coordinator_pid: process.pid,
        staging_path: stagingRoot,
        output_path: targetPath,
        started_at: startedAt,
        finished_at: new Date().toISOString(),
        child_pids: Object.freeze(childPids),
        cleanup: "pass",
        authority_effect: "none",
      });
      await writeFile(resolve(stagingRoot, "process-observation.json"), json(processObservation), { flag: "wx" });
      await writeFile(resolve(stagingRoot, "terminal.json"), json(Object.freeze({
        schema_version: "FactoryTerminalReceipt/v1",
        result: "pass",
        semantic_receipt_sha256: normalized.semantic_receipt_sha256,
        snapshot_index_sha256: snapshot.snapshot_index_sha256,
        authority_effect: "none",
      })), { flag: "wx" });
    },
  });
  return Object.freeze({
    result: "pass",
    run_path: publication.run_path,
    run_id: input.plan.run_id,
    semantic_receipt_sha256: semanticReceiptSha256,
    lock_sha256: input.plan.lock.lock_sha256,
    authority_effect: "none",
  });
};
