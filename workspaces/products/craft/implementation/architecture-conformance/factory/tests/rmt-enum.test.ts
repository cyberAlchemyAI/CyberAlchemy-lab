import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterAll, beforeAll, describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import type { FactoryRunPlanV1 } from "../contracts/factory-run-plan-v1.js";
import type { FactoryRunRequestV1 } from "../contracts/factory-run-request-v1.js";
import type { FactorySemanticReceiptV1 } from
  "../contracts/factory-semantic-receipt-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { executeFactoryRun } from "../pipeline/execute-factory-run.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";
import { replayFactoryRun } from "../pipeline/replay-factory-run.js";
import { verifyFactoryRun } from "../pipeline/verify-factory-run.js";
import { getFactoryNodeProviderV1, listFactoryNodeProvidersV1 } from
  "../registry/factory-node-registry-v1.js";

const requestPath = resolve(repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-enum-semantic-slice.request.json");
const load = async (): Promise<FactoryRunRequestV1> =>
  decodeFactoryRunRequestV1(JSON.parse(await readFile(requestPath, "utf8")));
const clone = <T>(value: T): T => structuredClone(value);

let outputParent: string;
let plan: FactoryRunPlanV1;
let run: Awaited<ReturnType<typeof executeFactoryRun>>;

beforeAll(async () => {
  const request = await load();
  plan = await planFactoryRun({ repositoryRoot, request });
  outputParent = await mkdtemp(resolve(tmpdir(), "domainspec-rmt-enum-factory-"));
  run = await executeFactoryRun({ repositoryRoot, outputParent, plan });
}, 70_000);

afterAll(async () => {
  if (outputParent !== undefined) await rm(outputParent, { recursive: true, force: true });
});

describe("RMT-ENUM-005 factory proof closure", () => {
  it("registers only the exact three direct and two join providers", async () => {
    const providers = listFactoryNodeProvidersV1().map(({ provider_id }) => provider_id);
    expect(providers).toEqual(expect.arrayContaining([
      "typescript-enum-shipment-priority-semantic-slice-v1",
      "python-enum-v1",
      "rust-enum-v1",
      "enum-composition-v1",
      "enum-parity-v1",
    ]));
    expect(new Set(providers).size).toBe(providers.length);
    const request = await load();
    expect(request.nodes.map(({ node_id }) => node_id)).toEqual([
      "enum.typescript.shipment-priority",
      "enum.python.shipment-priority",
      "enum.rust.shipment-priority",
      "enum.composition.shipment-priority",
      "enum.parity.shipment-priority",
    ]);
    expect(request.nodes[3]?.depends_on).toEqual(request.nodes.slice(0, 3)
      .map(({ node_id }) => node_id));
    expect(request.nodes[4]?.depends_on).toEqual(request.nodes.slice(0, 4)
      .map(({ node_id }) => node_id));
    expect(plan.lock.ordered_node_ids).toEqual([
      "enum.python.shipment-priority",
      "enum.rust.shipment-priority",
      "enum.typescript.shipment-priority",
      "enum.composition.shipment-priority",
      "enum.parity.shipment-priority",
    ]);
    for (const id of ["enum-composition-v1", "enum-parity-v1"]) {
      const locked = plan.lock.nodes.find(({ provider_id }) => provider_id === id)!;
      expect(locked.components.map(({ path }) => path)).toEqual(expect.arrayContaining([
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/evaluate-enum-joins.ts",
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/evaluate-enum-joins.test.ts",
        "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-parity/typescript-wire-probe.ts",
      ]));
    }
  });

  it("executes and verifies exact direct/composition/parity accounting", async () => {
    const verified = await verifyFactoryRun(run.run_path);
    expect(verified.semantic_receipt_sha256).toBe(run.semantic_receipt_sha256);
    const receipt = JSON.parse(await readFile(resolve(
      run.run_path, "semantic-receipt.json"), "utf8")) as FactorySemanticReceiptV1;
    expect(receipt.result).toBe("pass");
    expect(receipt.ordered_nodes.map(({ provider_id }) => provider_id)).toEqual([
      "python-enum-v1",
      "rust-enum-v1",
      "typescript-enum-shipment-priority-semantic-slice-v1",
      "enum-composition-v1",
      "enum-parity-v1",
    ]);
    expect(receipt.ordered_nodes.map(({ accounting }) => ({
      positives: [accounting.positives_declared, accounting.positives_passed],
      mutants: [accounting.mutants_declared, accounting.mutants_killed],
    }))).toEqual([
      { positives: [14, 14], mutants: [4, 4] },
      { positives: [14, 14], mutants: [4, 4] },
      { positives: [1, 1], mutants: [1, 1] },
      { positives: [8, 8], mutants: [0, 0] },
      { positives: [9, 9], mutants: [9, 9] },
    ]);
    const parity = JSON.parse(await readFile(resolve(
      run.run_path, "nodes/enum.parity.shipment-priority/semantic.json"), "utf8")) as any;
    expect(parity.semantic_output.parity.excluded_native_diagnostics).toEqual(
      expect.arrayContaining([expect.stringContaining("Rust"), expect.stringContaining("Python")]),
    );
    expect(parity.semantic_output.mutants).toHaveLength(9);
  });

  it("replays all five nodes through the same locked oracle", async () => {
    const replayed = await replayFactoryRun(run.run_path);
    expect(replayed).toMatchObject({ result: "pass", replayed_nodes: 5 });
    expect(new Set(replayed.child_pids).size).toBe(5);
  }, 70_000);

  it("rejects graph drift, stale input/component, totals-only handles, and relation bypass", async () => {
    const request = await load();
    const changedOrder = clone(request) as any;
    changedOrder.nodes[3].depends_on.reverse();
    const changedPlan = await planFactoryRun({ repositoryRoot, request: changedOrder });
    expect(changedPlan.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const missingDependency = clone(request) as any;
    missingDependency.nodes[4].depends_on.pop();
    const narrowed = await planFactoryRun({ repositoryRoot, request: missingDependency });
    expect(narrowed.lock.lock_sha256).not.toBe(plan.lock.lock_sha256);
    const staleInput = clone(request) as any;
    staleInput.nodes[1].input_refs[0].ref.sha256 = "0".repeat(64);
    await expect(planFactoryRun({ repositoryRoot, request: staleInput }))
      .rejects.toThrow("FACTORY_INPUT_TAMPERED");
    const staleComponent = clone(plan) as any;
    staleComponent.lock.nodes[3].components[0].sha256 = "0".repeat(64);
    const hostileParent = await mkdtemp(resolve(tmpdir(), "domainspec-rmt-enum-hostile-"));
    try {
      await expect(executeFactoryRun({ repositoryRoot, outputParent: hostileParent,
        plan: staleComponent })).rejects.toThrow(/FACTORY_(?:SNAPSHOT|INPUT|REPLAY|RUN)/u);
    } finally {
      await rm(hostileParent, { recursive: true, force: true });
    }
    const composition = getFactoryNodeProviderV1("enum-composition-v1");
    const totalsOnly = Object.fromEntries(request.nodes.slice(0, 3).map((node, index) =>
      [node.node_id, {
        node_id: node.node_id,
        provider_id: node.provider_id,
        semantic_sha256: String(index + 1).repeat(64),
        semantic_output: { accounting: { positives_declared: 100,
          positives_passed: 100, mutants_declared: 100, mutants_killed: 100 } },
      }]));
    const rawInputs = Object.fromEntries(await Promise.all(request.nodes[3]!.input_refs.map(
      async ({ role, ref }) => [role, await readFile(resolve(repositoryRoot, ref.path), "utf8")],
    )));
    await expect(composition.execute({ raw_inputs: rawInputs, upstream: totalsOnly }))
      .rejects.toThrow("ENUM_TS_DIRECT_OUTPUT_INVALID");
    const parity = getFactoryNodeProviderV1("enum-parity-v1");
    await expect(parity.execute({ raw_inputs: {}, upstream: totalsOnly }))
      .rejects.toThrow("ENUM_JOIN_DEPENDENCY_ORDER_MISMATCH");
  }, 70_000);
});
