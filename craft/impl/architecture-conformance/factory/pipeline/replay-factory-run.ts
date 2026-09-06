import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import type {
  FactoryNodeSemanticResultV1,
  FactoryUpstreamResultV1,
} from "../contracts/factory-node-provider-v1.js";
import type { FactoryRunPlanV1 } from "../contracts/factory-run-plan-v1.js";
import { verifyFactoryRunRoot } from "../evidence/verify-run-root.js";
import { runLockedChild } from "../replay/run-locked-child.js";
import { canonicalJson, fail, sha256 } from "../shared/canonical.js";

export const replayFactoryRun = async (runPath: string): Promise<Readonly<{
  result: "pass";
  replayed_nodes: number;
  child_pids: readonly number[];
  authority_effect: "none";
}>> => {
  await verifyFactoryRunRoot(runPath);
  const plan = JSON.parse(await readFile(resolve(runPath, "plan.json"), "utf8")) as FactoryRunPlanV1;
  const scratchRoot = await mkdtemp(resolve(tmpdir(), "domainspec-factory-replay-"));
  const handles: Record<string, FactoryUpstreamResultV1> = {};
  const childPids: number[] = [];
  try {
    for (const nodeId of plan.lock.ordered_node_ids) {
      const node = plan.lock.nodes.find(({ node_id: id }) => id === nodeId)!;
      const rawInputs = Object.fromEntries(await Promise.all(node.inputs.map(async ({ role }) => [
        role,
        await readFile(resolve(runPath, `snapshot/nodes/${nodeId}/inputs/${role}.raw`), "utf8"),
      ])));
      const upstream = Object.fromEntries(node.depends_on.map((dependency) => {
        const handle = handles[dependency];
        if (handle === undefined) fail("FACTORY_DEPENDENCY_STALE", dependency);
        return [dependency, handle];
      }));
      const stored = JSON.parse(await readFile(
        resolve(runPath, `nodes/${nodeId}/semantic.json`),
        "utf8",
      )) as FactoryNodeSemanticResultV1;
      const replay = await runLockedChild({
        scratchRoot,
        nodeId,
        providerId: node.provider_id,
        rawInputs,
        upstream,
        lock: plan.lock,
      });
      childPids.push(replay.child_pid);
      const storedSha256 = sha256(canonicalJson(stored));
      if (replay.result_sha256 !== storedSha256) fail("FACTORY_REPLAY_DRIFT", nodeId);
      handles[nodeId] = Object.freeze({
        node_id: nodeId,
        provider_id: node.provider_id,
        semantic_sha256: storedSha256,
        semantic_output: stored.semantic_output,
      });
    }
    return Object.freeze({
      result: "pass",
      replayed_nodes: plan.lock.ordered_node_ids.length,
      child_pids: Object.freeze(childPids),
      authority_effect: "none",
    });
  } finally {
    await rm(scratchRoot, { recursive: true, force: true });
  }
};
