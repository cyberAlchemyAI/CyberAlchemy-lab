import {mkdtemp, readFile, rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import {resolve} from "node:path";

import {afterAll, beforeAll, describe, expect, it} from "vitest";

import {decodeFactoryRunRequestV1} from
  "../codecs/decode-factory-run-request-v1.js";
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

const requestPath = resolve(repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-value-object.request.json");
const load = async (): Promise<FactoryRunRequestV1> =>
  decodeFactoryRunRequestV1(JSON.parse(await readFile(requestPath, "utf8")));
const clone = <T>(value: T): T => structuredClone(value);

let outputParent: string;
let plan: FactoryRunPlanV1;
let run: Awaited<ReturnType<typeof executeFactoryRun>>;

beforeAll(async () => {
  const request = await load();
  plan = await planFactoryRun({repositoryRoot, request});
  outputParent = await mkdtemp(resolve(tmpdir(),
    "domainspec-rmt-value-object-factory-"));
  run = await executeFactoryRun({repositoryRoot, outputParent, plan});
}, 70_000);

afterAll(async () => {
  if (outputParent !== undefined) {
    await rm(outputParent, {recursive: true, force: true});
  }
});

describe("RMT-VO-006 factory proof closure", () => {
  it("registers three direct providers, parity, then architecture relations", async () => {
    const providers = listFactoryNodeProvidersV1().map(({provider_id: id}) => id);
    expect(providers).toEqual(expect.arrayContaining([
      "typescript-value-object-v1",
      "python-value-object-v1",
      "rust-value-object-v1",
      "value-object-parity-v1",
      "value-object-relations-v1",
    ]));
    expect(new Set(providers).size).toBe(providers.length);
    const request = await load();
    expect(request.nodes.map(({node_id: id}) => id)).toEqual([
      "value-object.typescript.settlement-value",
      "value-object.python.settlement-value",
      "value-object.rust.settlement-value",
      "value-object.parity.settlement-value",
      "value-object.relations.settlement-value",
    ]);
    expect(request.nodes[3]!.depends_on).toEqual(request.nodes.slice(0, 3)
      .map(({node_id: id}) => id));
    expect(request.nodes[4]!.depends_on).toEqual(request.nodes.slice(0, 4)
      .map(({node_id: id}) => id));
    expect(plan.lock.ordered_node_ids).toEqual([
      "value-object.python.settlement-value",
      "value-object.rust.settlement-value",
      "value-object.typescript.settlement-value",
      "value-object.parity.settlement-value",
      "value-object.relations.settlement-value",
    ]);
    for (const providerId of ["value-object-parity-v1",
      "value-object-relations-v1"]) {
      const node = plan.lock.nodes.find(({provider_id: id}) => id === providerId)!;
      expect(node.components.map(({path}) => path)).toEqual(expect.arrayContaining([
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/value-object/evaluate-value-object-joins.ts",
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/value-object/evaluate-value-object-joins.test.ts",
      ]));
    }
  });

  it("executes exact direct, parity, and relation accounting", async () => {
    const verified = await verifyFactoryRun(run.run_path);
    expect(verified.semantic_receipt_sha256).toBe(run.semantic_receipt_sha256);
    const receipt = JSON.parse(await readFile(resolve(run.run_path,
      "semantic-receipt.json"), "utf8")) as FactorySemanticReceiptV1;
    expect(receipt.result).toBe("pass");
    expect(receipt.ordered_nodes.map(({provider_id: id}) => id)).toEqual([
      "python-value-object-v1",
      "rust-value-object-v1",
      "typescript-value-object-v1",
      "value-object-parity-v1",
      "value-object-relations-v1",
    ]);
    expect(receipt.ordered_nodes.map(({accounting}) => ({
      positives: [accounting.positives_declared, accounting.positives_passed],
      mutants: [accounting.mutants_declared, accounting.mutants_killed],
    }))).toEqual([
      {positives: [7, 7], mutants: [12, 12]},
      {positives: [7, 7], mutants: [12, 12]},
      {positives: [7, 7], mutants: [12, 12]},
      {positives: [17, 17], mutants: [18, 18]},
      {positives: [11, 11], mutants: [14, 14]},
    ]);
    const parity = JSON.parse(await readFile(resolve(run.run_path,
      "nodes/value-object.parity.settlement-value/semantic.json"), "utf8")) as any;
    const relations = JSON.parse(await readFile(resolve(run.run_path,
      "nodes/value-object.relations.settlement-value/semantic.json"), "utf8")) as any;
    expect(parity.semantic_output.proof.composed_from).toHaveLength(3);
    expect(parity.semantic_output.proof.portable_projection.equality.every(
      (row: {native_hash_bytes_compared_cross_language: boolean}) =>
        row.native_hash_bytes_compared_cross_language === false)).toBe(true);
    expect(relations.semantic_output.proof.relation_rows).toHaveLength(15);
  });

  it("replays all five nodes through the same locked oracle", async () => {
    const replayed = await replayFactoryRun(run.run_path);
    expect(replayed).toMatchObject({result: "pass", replayed_nodes: 5});
    expect(new Set(replayed.child_pids).size).toBe(5);
  }, 70_000);

  it("rejects graph drift, stale inputs, and totals-only join handles", async () => {
    const request = await load();
    const changedOrder = clone(request) as any;
    changedOrder.nodes[3].depends_on.reverse();
    const changedPlan = await planFactoryRun({repositoryRoot,
      request: changedOrder});
    expect(changedPlan.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const missingDependency = clone(request) as any;
    missingDependency.nodes[4].depends_on = [];
    const narrowed = await planFactoryRun({repositoryRoot,
      request: missingDependency});
    expect(narrowed.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const staleInput = clone(request) as any;
    staleInput.nodes[0].input_refs[0].ref.sha256 = "0".repeat(64);
    await expect(planFactoryRun({repositoryRoot, request: staleInput}))
      .rejects.toThrow("FACTORY_INPUT_TAMPERED");
    const parityProvider = getFactoryNodeProviderV1("value-object-parity-v1");
    const totalsOnly = Object.fromEntries(request.nodes.slice(0, 3)
      .map((node, index) => [node.node_id, {
        node_id: node.node_id,
        provider_id: node.provider_id,
        semantic_sha256: String(index + 1).repeat(64),
        semantic_output: {accounting: {positives_declared: 7,
          positives_passed: 7, mutants_declared: 12, mutants_killed: 12}},
      }]));
    const rawInputs = Object.fromEntries(await Promise.all(
      request.nodes[3]!.input_refs.map(async ({role, ref}) =>
        [role, await readFile(resolve(repositoryRoot, ref.path), "utf8")] as const),
    ));
    await expect(parityProvider.execute({raw_inputs: rawInputs,
      upstream: totalsOnly})).rejects.toThrow("VALUE_OBJECT_PARITY_PROOF_INVALID");
  }, 70_000);
});
