import {mkdtemp, readFile, rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import {resolve} from "node:path";

import {afterAll, beforeAll, describe, expect, it} from "vitest";

import {decodeFactoryRunRequestV1} from "../codecs/decode-factory-run-request-v1.js";
import type {FactoryRunPlanV1} from "../contracts/factory-run-plan-v1.js";
import type {FactoryRunRequestV1} from "../contracts/factory-run-request-v1.js";
import type {FactorySemanticReceiptV1} from
  "../contracts/factory-semantic-receipt-v1.js";
import {repositoryRoot} from "../cli/index.js";
import {executeFactoryRun} from "../pipeline/execute-factory-run.js";
import {planFactoryRun} from "../pipeline/plan-factory-run.js";
import {replayFactoryRun} from "../pipeline/replay-factory-run.js";
import {verifyFactoryRun} from "../pipeline/verify-factory-run.js";
import {getFactoryNodeProviderV1, listFactoryNodeProvidersV1} from
  "../registry/factory-node-registry-v1.js";

const requestPath = resolve(
  repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-query.request.json",
);
const load = async (): Promise<FactoryRunRequestV1> =>
  decodeFactoryRunRequestV1(JSON.parse(await readFile(requestPath, "utf8")));
const clone = <T>(value: T): T => structuredClone(value);

let outputParent: string;
let plan: FactoryRunPlanV1;
let run: Awaited<ReturnType<typeof executeFactoryRun>>;

beforeAll(async () => {
  const request = await load();
  plan = await planFactoryRun({repositoryRoot, request});
  outputParent = await mkdtemp(resolve(tmpdir(), "domainspec-rmt-query-factory-"));
  run = await executeFactoryRun({repositoryRoot, outputParent, plan});
}, 70_000);

afterAll(async () => {
  if (outputParent !== undefined) {
    await rm(outputParent, {recursive: true, force: true});
  }
});

describe("RMT-QUERY-006 factory proof closure", () => {
  it("registers the exact three direct providers and one parity join", async () => {
    const providers = listFactoryNodeProvidersV1()
      .map(({provider_id: providerId}) => providerId);
    expect(providers).toEqual(expect.arrayContaining([
      "typescript-query-v1",
      "python-query-v1",
      "rust-query-v1",
      "query-parity-v1",
    ]));
    expect(new Set(providers).size).toBe(providers.length);
    const request = await load();
    expect(request.nodes.map(({node_id: nodeId}) => nodeId)).toEqual([
      "query.typescript.complete-settlement",
      "query.python.complete-settlement",
      "query.rust.complete-settlement",
      "query.parity.complete-settlement",
    ]);
    expect(request.nodes[3]!.depends_on).toEqual(request.nodes.slice(0, 3)
      .map(({node_id: nodeId}) => nodeId));
    expect(plan.lock.ordered_node_ids).toEqual([
      "query.python.complete-settlement",
      "query.rust.complete-settlement",
      "query.typescript.complete-settlement",
      "query.parity.complete-settlement",
    ]);
    const parity = plan.lock.nodes.find(({provider_id: providerId}) =>
      providerId === "query-parity-v1")!;
    expect(parity.components.map(({path}) => path)).toEqual(expect.arrayContaining([
      "projects/domainspec-v2/impl/architecture-conformance/acceptance/query/evaluate-query-parity.ts",
      "projects/domainspec-v2/impl/architecture-conformance/acceptance/query/evaluate-query-parity.test.ts",
    ]));
  });

  it("executes and verifies exact direct and parity accounting", async () => {
    const verified = await verifyFactoryRun(run.run_path);
    expect(verified.semantic_receipt_sha256).toBe(run.semantic_receipt_sha256);
    const receipt = JSON.parse(await readFile(resolve(
      run.run_path,
      "semantic-receipt.json",
    ), "utf8")) as FactorySemanticReceiptV1;
    expect(receipt.result).toBe("pass");
    expect(receipt.ordered_nodes.map(({provider_id: providerId}) => providerId))
      .toEqual([
        "python-query-v1",
        "rust-query-v1",
        "typescript-query-v1",
        "query-parity-v1",
      ]);
    expect(receipt.ordered_nodes.map(({accounting}) => ({
      positives: [accounting.positives_declared, accounting.positives_passed],
      mutants: [accounting.mutants_declared, accounting.mutants_killed],
    }))).toEqual([
      {positives: [4, 4], mutants: [8, 8]},
      {positives: [4, 4], mutants: [8, 8]},
      {positives: [4, 4], mutants: [8, 8]},
      {positives: [16, 16], mutants: [20, 20]},
    ]);
    const parity = JSON.parse(await readFile(resolve(
      run.run_path,
      "nodes/query.parity.complete-settlement/semantic.json",
    ), "utf8")) as any;
    expect(parity.semantic_output.proof.composed_from).toHaveLength(3);
    expect(parity.semantic_output.proof.native_evidence_by_language).toHaveLength(3);
    expect(parity.semantic_output.proof.obligations).toHaveLength(16);
    expect(parity.semantic_output.proof.hostile_mutations).toHaveLength(20);
    expect(JSON.stringify(parity)).not.toContain('"pid"');
  });

  it("replays all four nodes through the same locked oracle", async () => {
    const replayed = await replayFactoryRun(run.run_path);
    expect(replayed).toMatchObject({result: "pass", replayed_nodes: 4});
    expect(new Set(replayed.child_pids).size).toBe(4);
  }, 70_000);

  it("rejects graph drift stale material components and totals-only handles", async () => {
    const request = await load();
    const changedOrder = clone(request) as any;
    changedOrder.nodes[3].depends_on.reverse();
    const changedPlan = await planFactoryRun({repositoryRoot, request: changedOrder});
    expect(changedPlan.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const missingDependency = clone(request) as any;
    missingDependency.nodes[3].depends_on.pop();
    const narrowed = await planFactoryRun({repositoryRoot, request: missingDependency});
    expect(narrowed.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const staleInput = clone(request) as any;
    staleInput.nodes[0].input_refs[0].ref.sha256 = "0".repeat(64);
    await expect(planFactoryRun({repositoryRoot, request: staleInput}))
      .rejects.toThrow("FACTORY_INPUT_TAMPERED");
    const staleComponent = clone(plan) as any;
    staleComponent.lock.nodes[3].components[0].sha256 = "0".repeat(64);
    const hostileParent = await mkdtemp(resolve(tmpdir(),
      "domainspec-rmt-query-hostile-"));
    try {
      await expect(executeFactoryRun({
        repositoryRoot,
        outputParent: hostileParent,
        plan: staleComponent,
      })).rejects.toThrow(/FACTORY_(?:SNAPSHOT|INPUT|REPLAY|RUN)/u);
    } finally {
      await rm(hostileParent, {recursive: true, force: true});
    }
    const parity = getFactoryNodeProviderV1("query-parity-v1");
    const totalsOnly = Object.fromEntries(request.nodes.slice(0, 3)
      .map((node, index) => [node.node_id, {
        node_id: node.node_id,
        provider_id: node.provider_id,
        semantic_sha256: String(index + 1).repeat(64),
        semantic_output: {
          accounting: {
            positives_declared: 100,
            positives_passed: 100,
            mutants_declared: 100,
            mutants_killed: 100,
          },
        },
      }]));
    const rawInputs = Object.fromEntries(await Promise.all(
      request.nodes[3]!.input_refs.map(async ({role, ref}) => [
        role,
        await readFile(resolve(repositoryRoot, ref.path), "utf8"),
      ]),
    ));
    await expect(parity.execute({raw_inputs: rawInputs, upstream: totalsOnly}))
      .rejects.toThrow("QUERY_PARITY_PROOF_INVALID");
  }, 70_000);
});
