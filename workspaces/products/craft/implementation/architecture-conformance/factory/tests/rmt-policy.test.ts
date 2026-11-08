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
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-policy.request.json",
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
  outputParent = await mkdtemp(resolve(tmpdir(), "domainspec-rmt-policy-factory-"));
  run = await executeFactoryRun({repositoryRoot, outputParent, plan});
}, 70_000);

afterAll(async () => {
  if (outputParent !== undefined) await rm(outputParent, {recursive: true, force: true});
});

describe("RMT-POLICY-007 factory proof closure", () => {
  it("registers three direct providers, parity, then selects_strategy", async () => {
    const providers = listFactoryNodeProvidersV1()
      .map(({provider_id: providerId}) => providerId);
    expect(providers).toEqual(expect.arrayContaining([
      "typescript-policy-v1",
      "python-policy-v1",
      "rust-policy-v1",
      "policy-parity-v1",
      "policy-selects-strategy-v1",
    ]));
    expect(new Set(providers).size).toBe(providers.length);
    const request = await load();
    expect(request.nodes.map(({node_id: nodeId}) => nodeId)).toEqual([
      "policy.typescript.settlement-routing",
      "policy.python.settlement-routing",
      "policy.rust.settlement-routing",
      "policy.parity.settlement-routing",
      "policy.selects-strategy.settlement-routing",
    ]);
    expect(request.nodes[3]!.depends_on).toEqual(request.nodes.slice(0, 3)
      .map(({node_id: nodeId}) => nodeId));
    expect(request.nodes[4]!.depends_on).toEqual(request.nodes.slice(0, 4)
      .map(({node_id: nodeId}) => nodeId));
    expect(plan.lock.ordered_node_ids).toEqual([
      "policy.python.settlement-routing",
      "policy.rust.settlement-routing",
      "policy.typescript.settlement-routing",
      "policy.parity.settlement-routing",
      "policy.selects-strategy.settlement-routing",
    ]);
    for (const providerId of ["policy-parity-v1", "policy-selects-strategy-v1"]) {
      const node = plan.lock.nodes.find(({provider_id: id}) => id === providerId)!;
      expect(node.components.map(({path}) => path)).toEqual(expect.arrayContaining([
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/policy/evaluate-policy-joins.ts",
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/policy/evaluate-policy-joins.test.ts",
      ]));
    }
  });

  it("executes exact direct, parity, relation, and non-execution accounting", async () => {
    const verified = await verifyFactoryRun(run.run_path);
    expect(verified.semantic_receipt_sha256).toBe(run.semantic_receipt_sha256);
    const receipt = JSON.parse(await readFile(resolve(
      run.run_path,
      "semantic-receipt.json",
    ), "utf8")) as FactorySemanticReceiptV1;
    expect(receipt.result).toBe("pass");
    expect(receipt.ordered_nodes.map(({provider_id: providerId}) => providerId))
      .toEqual([
        "python-policy-v1",
        "rust-policy-v1",
        "typescript-policy-v1",
        "policy-parity-v1",
        "policy-selects-strategy-v1",
      ]);
    expect(receipt.ordered_nodes.map(({accounting}) => ({
      positives: [accounting.positives_declared, accounting.positives_passed],
      mutants: [accounting.mutants_declared, accounting.mutants_killed],
    }))).toEqual([
      {positives: [14, 14], mutants: [16, 16]},
      {positives: [14, 14], mutants: [16, 16]},
      {positives: [14, 14], mutants: [16, 16]},
      {positives: [14, 14], mutants: [13, 13]},
      {positives: [32, 32], mutants: [20, 20]},
    ]);
    const parity = JSON.parse(await readFile(resolve(
      run.run_path,
      "nodes/policy.parity.settlement-routing/semantic.json",
    ), "utf8")) as any;
    const relation = JSON.parse(await readFile(resolve(
      run.run_path,
      "nodes/policy.selects-strategy.settlement-routing/semantic.json",
    ), "utf8")) as any;
    expect(parity.semantic_output.proof.composed_from).toHaveLength(3);
    expect(parity.semantic_output.proof.non_execution_by_language.every(
      ({attempt_count: attempts}: {attempt_count: number}) => attempts === 0,
    )).toBe(true);
    expect(relation.semantic_output.proof.relation_rows).toHaveLength(5);
    expect(relation.semantic_output.proof.relation_rows.every(
      ({member_executable: executable}: {member_executable: boolean}) =>
        executable === false,
    )).toBe(true);
  });

  it("replays all five nodes through the same locked oracle", async () => {
    const replayed = await replayFactoryRun(run.run_path);
    expect(replayed).toMatchObject({result: "pass", replayed_nodes: 5});
    expect(new Set(replayed.child_pids).size).toBe(5);
  }, 70_000);

  it("rejects graph drift, stale inputs, and totals-only direct handles", async () => {
    const request = await load();
    const changedOrder = clone(request) as any;
    changedOrder.nodes[3].depends_on.reverse();
    const changedPlan = await planFactoryRun({repositoryRoot, request: changedOrder});
    expect(changedPlan.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const missingDependency = clone(request) as any;
    missingDependency.nodes[4].depends_on = [];
    const narrowed = await planFactoryRun({repositoryRoot, request: missingDependency});
    expect(narrowed.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const staleInput = clone(request) as any;
    staleInput.nodes[0].input_refs[0].ref.sha256 = "0".repeat(64);
    await expect(planFactoryRun({repositoryRoot, request: staleInput}))
      .rejects.toThrow("FACTORY_INPUT_TAMPERED");
    const parityProvider = getFactoryNodeProviderV1("policy-parity-v1");
    const totalsOnly = Object.fromEntries(request.nodes.slice(0, 3)
      .map((node, index) => [node.node_id, {
        node_id: node.node_id,
        provider_id: node.provider_id,
        semantic_sha256: String(index + 1).repeat(64),
        semantic_output: {accounting: {
          positives_declared: 14,
          positives_passed: 14,
          mutants_declared: 16,
          mutants_killed: 16,
        }},
      }]));
    const rawInputs = Object.fromEntries(await Promise.all(
      request.nodes[3]!.input_refs.map(async ({role, ref}) =>
        [role, await readFile(resolve(repositoryRoot, ref.path), "utf8")] as const),
    ));
    await expect(parityProvider.execute({raw_inputs: rawInputs, upstream: totalsOnly}))
      .rejects.toThrow("POLICY_PARITY_PROOF_INVALID");
  }, 70_000);
});
