import {mkdtemp, readFile, rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import {resolve} from "node:path";
import {afterEach, describe, expect, it} from "vitest";
import {decodeFactoryRunRequestV1} from "../codecs/decode-factory-run-request-v1.js";
import {repositoryRoot} from "../cli/index.js";
import {executeFactoryRun} from "../pipeline/execute-factory-run.js";
import {planFactoryRun} from "../pipeline/plan-factory-run.js";
import {replayFactoryRun} from "../pipeline/replay-factory-run.js";
import {verifyFactoryRun} from "../pipeline/verify-factory-run.js";

const roots: string[] = [];
afterEach(async () => Promise.all(roots.splice(0).map((root) => rm(root, {recursive: true, force: true}))));

describe("W4 factory reproduction", () => {
  it("locks, executes, verifies, and independently replays State Machine and Workflow", async () => {
    const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(repositoryRoot,
      "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/w4-orchestration-lifecycle.request.json"), "utf8")));
    const plan = await planFactoryRun({repositoryRoot, request});
    expect(plan.lock.nodes.map(({node_id}) => node_id)).toEqual(["w4.state-machine", "w4.workflow"]);
    expect(plan.lock.nodes.every(({provider_id}) => provider_id === "typescript-w4-orchestration-lifecycle-v1")).toBe(true);
    expect(plan.lock.nodes.every(({inputs}) => inputs.length === 3)).toBe(true);
    const outputParent = await mkdtemp(resolve(tmpdir(), "domainspec-w4-factory-"));
    roots.push(outputParent);
    const run = await executeFactoryRun({repositoryRoot, outputParent, plan});
    const semantic = JSON.parse(await readFile(resolve(run.run_path, "semantic-receipt.json"), "utf8")) as {ordered_nodes: {accounting: {mutants_declared: number; mutants_killed: number}}[]};
    expect(semantic.ordered_nodes.map(({accounting}) => accounting.mutants_declared)).toEqual([8, 9]);
    expect(semantic.ordered_nodes.every(({accounting}) => accounting.mutants_killed === accounting.mutants_declared)).toBe(true);
    const verified = await verifyFactoryRun(run.run_path);
    const replayed = await replayFactoryRun(run.run_path);
    expect(verified.semantic_receipt_sha256).toBe(run.semantic_receipt_sha256);
    expect(replayed).toMatchObject({result: "pass", replayed_nodes: 2});
  }, 70_000);
});
