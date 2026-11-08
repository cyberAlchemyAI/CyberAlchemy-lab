import {mkdtemp, readFile, rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import {resolve} from "node:path";

import {afterAll, beforeAll, describe, expect, it} from "vitest";

import {decodeFactoryRunRequestV1} from
  "../codecs/decode-factory-run-request-v1.js";
import type {FactoryRunPlanV1} from "../contracts/factory-run-plan-v1.js";
import type {FactoryRunRequestV1} from
  "../contracts/factory-run-request-v1.js";
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
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-entity.request.json");
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
    "domainspec-rmt-entity-factory-"));
  run = await executeFactoryRun({repositoryRoot, outputParent, plan});
}, 90_000);

afterAll(async () => {
  if (outputParent !== undefined) {
    await rm(outputParent, {recursive: true, force: true});
  }
});

describe("RMT-ENTITY-006 factory proof closure", () => {
  it("registers three direct providers, parity, then architecture relations", async () => {
    const providers = listFactoryNodeProvidersV1().map(({provider_id: id}) => id);
    expect(providers).toEqual(expect.arrayContaining([
      "typescript-entity-v1",
      "python-entity-v1",
      "rust-entity-v1",
      "entity-parity-v1",
      "entity-relations-v1",
    ]));
    expect(new Set(providers).size).toBe(providers.length);
    const request = await load();
    expect(request.nodes.map(({node_id: id}) => id)).toEqual([
      "entity.typescript.settlement",
      "entity.python.settlement",
      "entity.rust.settlement",
      "entity.parity.settlement",
      "entity.relations.settlement",
    ]);
    expect(request.nodes[3]!.depends_on).toEqual(request.nodes.slice(0, 3)
      .map(({node_id: id}) => id));
    expect(request.nodes[4]!.depends_on).toEqual(request.nodes.slice(0, 4)
      .map(({node_id: id}) => id));
    expect(request.nodes.reduce((total, node) =>
      total + node.input_refs.length, 0)).toBe(60);
    expect(request.nodes[4]!.input_refs.slice(-6, -3).map(({role, ref}) =>
      ({role, path: ref.path}))).toEqual([
      {role: "typescript_receipt",
        path: "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-ENTITY-003.json"},
      {role: "python_receipt",
        path: "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-ENTITY-004.json"},
      {role: "rust_receipt",
        path: "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-ENTITY-005.json"},
    ]);
    expect(request.nodes[4]!.input_refs.slice(-3).map(({role, ref}) =>
      ({role, path: ref.path}))).toEqual([
      {role: "entity_decision",
        path: "projects/domainspec-v2/development/ontology-form-decisions/decisions/W1-ENTITY-001.json"},
      {role: "value_object_receipt",
        path: "projects/domainspec-v2/development/remaining-meta-types/receipts/RMT-VO-007.json"},
      {role: "value_object_candidate",
        path: "projects/domainspec-v2/development/remaining-meta-types/candidates/value-object.json"},
    ]);
    expect(plan.lock.ordered_node_ids).toEqual([
      "entity.python.settlement",
      "entity.rust.settlement",
      "entity.typescript.settlement",
      "entity.parity.settlement",
      "entity.relations.settlement",
    ]);
    for (const providerId of ["entity-parity-v1", "entity-relations-v1"]) {
      const node = plan.lock.nodes.find(({provider_id: id}) => id === providerId)!;
      expect(node.components.map(({path}) => path)).toEqual(expect.arrayContaining([
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/entity/evaluate-entity-joins.ts",
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/entity/evaluate-entity-joins.test.ts",
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
      "python-entity-v1",
      "rust-entity-v1",
      "typescript-entity-v1",
      "entity-parity-v1",
      "entity-relations-v1",
    ]);
    expect(receipt.ordered_nodes.map(({accounting}) => ({
      positives: [accounting.positives_declared, accounting.positives_passed],
      mutants: [accounting.mutants_declared, accounting.mutants_killed],
    }))).toEqual([
      {positives: [5, 5], mutants: [18, 18]},
      {positives: [5, 5], mutants: [12, 12]},
      {positives: [5, 5], mutants: [17, 17]},
      {positives: [20, 20], mutants: [26, 26]},
      {positives: [12, 12], mutants: [15, 15]},
    ]);
    const parity = JSON.parse(await readFile(resolve(run.run_path,
      "nodes/entity.parity.settlement/semantic.json"), "utf8")) as any;
    const relations = JSON.parse(await readFile(resolve(run.run_path,
      "nodes/entity.relations.settlement/semantic.json"), "utf8")) as any;
    expect(parity.semantic_output.proof.composed_from).toHaveLength(3);
    expect(parity.semantic_output.proof.native_evidence_by_language.map(
      ({evidence}: any) => evidence.target_source_control_count))
      .toEqual([10, 11, 12]);
    expect(parity.semantic_output.proof.portable_projection.equality.every(
      (row: {native_hash_bytes_compared_cross_language: boolean}) =>
        row.native_hash_bytes_compared_cross_language === false)).toBe(true);
    expect(relations.semantic_output.proof.relation_rows).toHaveLength(15);
  });

  it("replays all five nodes through the same locked oracle", async () => {
    const replayed = await replayFactoryRun(run.run_path);
    expect(replayed).toMatchObject({result: "pass", replayed_nodes: 5});
    expect(new Set(replayed.child_pids).size).toBe(5);
  }, 90_000);

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
    const parityProvider = getFactoryNodeProviderV1("entity-parity-v1");
    const totalsOnly = Object.fromEntries(request.nodes.slice(0, 3)
      .map((node, index) => [node.node_id, {
        node_id: node.node_id,
        provider_id: node.provider_id,
        semantic_sha256: String(index + 1).repeat(64),
        semantic_output: {accounting: {positives_declared: 5,
          positives_passed: 5}},
      }]));
    const rawInputs = Object.fromEntries(await Promise.all(
      request.nodes[3]!.input_refs.map(async ({role, ref}) =>
        [role, await readFile(resolve(repositoryRoot, ref.path), "utf8")] as const),
    ));
    await expect(parityProvider.execute({raw_inputs: rawInputs,
      upstream: totalsOnly})).rejects.toThrow("ENTITY_PARITY_PROOF_INVALID");
  }, 90_000);
});
