import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import type { FactoryNodeSemanticResultV1 } from "../contracts/factory-node-provider-v1.js";
import type { FactoryRunLockV1 } from "../contracts/factory-run-lock-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";
import {
  decodeLockedChildOutput,
  lockedComponentSetSha256,
  runChildJsonProtocol,
  runLockedChild,
  verifyLockedComponentSet,
} from "../replay/run-locked-child.js";
import { canonicalJson, sha256 } from "../shared/canonical.js";

const roots: string[] = [];
afterEach(async () => Promise.all(roots.splice(0).map((root) =>
  rm(root, { recursive: true, force: true }))));

const temporaryRoot = async (prefix: string): Promise<string> => {
  const root = await mkdtemp(resolve(tmpdir(), prefix));
  roots.push(root);
  return root;
};

const semanticResult: FactoryNodeSemanticResultV1 = Object.freeze({
  schema_version: "FactoryNodeSemanticResult/v1",
  result: "pass",
  provider_id: "fixture-provider-v1",
  semantic_output: Object.freeze({ fixture: true }),
  accounting: Object.freeze({
    positives_declared: 1,
    positives_passed: 1,
    mutants_declared: 1,
    mutants_killed: 1,
  }),
  claim_ceiling: "fixture only",
  authority_effect: "none",
});

const envelope = (componentDigest: string): Record<string, unknown> => ({
  schema_version: "FactoryReplayChildResult/v1",
  result: "pass",
  replay_mode: "same-oracle-deterministic",
  node_id: "fixture-node",
  provider_id: "fixture-provider-v1",
  provider_version: "1.0.0",
  component_identity: {
    algorithm: "sha256",
    locked_set_sha256: componentDigest,
    pre_load_sha256: componentDigest,
    post_execute_sha256: componentDigest,
  },
  semantic_result: semanticResult,
  semantic_result_sha256: sha256(canonicalJson(semanticResult)),
  authority_effect: "none",
});

const decodeFixture = (rendered: string): FactoryNodeSemanticResultV1 =>
  decodeLockedChildOutput({
    rendered,
    nodeId: "fixture-node",
    providerId: "fixture-provider-v1",
    providerVersion: "1.0.0",
    lockedComponentSetSha256: lockedComponentSetSha256([]),
  });

const rulePlan = async () => {
  const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
    repositoryRoot,
    "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rule-only.request.json",
  ), "utf8")));
  return planFactoryRun({ repositoryRoot, request });
};

const rawInputsFor = async (lock: FactoryRunLockV1, nodeId: string) => {
  const node = lock.nodes.find(({ node_id: candidate }) => candidate === nodeId)!;
  return Object.fromEntries(await Promise.all(node.inputs.map(async ({ role, path }) => [
    role,
    await readFile(resolve(repositoryRoot, path), "utf8"),
  ])));
};

describe("RMT-FND-002 replay child contract", () => {
  it("accepts exactly one closed same-oracle envelope", () => {
    const digest = lockedComponentSetSha256([]);
    const valid = `${JSON.stringify(envelope(digest))}\n`;
    expect(decodeFixture(valid)).toEqual(semanticResult);
    expect(() => decodeFixture("")).toThrow("FACTORY_REPLAY_OUTPUT_INVALID");
    expect(() => decodeFixture("{}\n{}\n")).toThrow("FACTORY_REPLAY_OUTPUT_INVALID");
    expect(() => decodeFixture(`${JSON.stringify(envelope(digest))} trailing\n`))
      .toThrow("FACTORY_REPLAY_OUTPUT_INVALID");
    expect(() => decodeFixture(`${JSON.stringify({
      ...envelope(digest),
      replay_mode: "locked-snapshot-deterministic",
    })}\n`)).toThrow("FACTORY_REPLAY_OUTPUT_INVALID");
    expect(() => decodeFixture(`${JSON.stringify({
      ...envelope(digest),
      provider_version: "2.0.0",
    })}\n`)).toThrow("FACTORY_REPLAY_OUTPUT_INVALID");
  });

  it("checks every declared component and rejects drift and duplicates", async () => {
    const root = await temporaryRoot("domainspec-replay-components-");
    const componentPath = "components/provider.ts";
    await mkdir(resolve(root, "components"));
    await writeFile(resolve(root, componentPath), "export const value = 1;\n", {
      encoding: "utf8",
      flag: "wx",
    });
    const bytes = await readFile(resolve(root, componentPath));
    const ref = Object.freeze({
      role: "component",
      path: componentPath,
      sha256: sha256(bytes),
      byte_length: bytes.byteLength,
    });
    await expect(verifyLockedComponentSet({ repositoryRoot: root, refs: [ref] }))
      .resolves.toHaveLength(1);
    await expect(verifyLockedComponentSet({ repositoryRoot: root, refs: [ref, ref] }))
      .rejects.toThrow("FACTORY_REPLAY_COMPONENT_SET_INVALID");
    await writeFile(resolve(root, componentPath), "export const value = 2;\n");
    await expect(verifyLockedComponentSet({ repositoryRoot: root, refs: [ref] }))
      .rejects.toThrow("FACTORY_REPLAY_COMPONENT_TAMPERED");
  });

  it("times out, escalates, awaits close, and reaps the child", async () => {
    const root = await temporaryRoot("domainspec-replay-timeout-");
    const childPath = resolve(root, "timeout-child.mjs");
    const resultPath = resolve(root, "timeout-result.json");
    await writeFile(childPath,
      "process.on('SIGTERM', () => undefined); setInterval(() => undefined, 1000);\n",
      { encoding: "utf8", flag: "wx" });
    const error = await runChildJsonProtocol({
      executable: process.execPath,
      args: [childPath, resultPath],
      cwd: root,
      environment: { PATH: process.env.PATH ?? "" },
      policy: { timeout_ms: 50, output_limit_bytes: 1024, termination_grace_ms: 30 },
      nodeId: "timeout-node",
      resultPath,
    }).then(() => null, (reason: unknown) => reason as { code?: string; child_pid?: number });
    expect(error?.code).toBe("FACTORY_REPLAY_TIMEOUT");
    expect(error?.child_pid).toEqual(expect.any(Number));
    expect(() => process.kill(error!.child_pid!, 0)).toThrow();
  });

  it("caps combined output, kills, awaits close, and reaps the child", async () => {
    const root = await temporaryRoot("domainspec-replay-output-cap-");
    const childPath = resolve(root, "output-child.mjs");
    const resultPath = resolve(root, "output-result.json");
    await writeFile(childPath,
      "const {writeFile}=await import('node:fs/promises'); await writeFile(process.argv[2], 'x'.repeat(65536)); setInterval(() => undefined, 1000);\n",
      { encoding: "utf8", flag: "wx" });
    const error = await runChildJsonProtocol({
      executable: process.execPath,
      args: [childPath, resultPath],
      cwd: root,
      environment: { PATH: process.env.PATH ?? "" },
      policy: { timeout_ms: 2_000, output_limit_bytes: 128, termination_grace_ms: 30 },
      nodeId: "output-node",
      resultPath,
    }).then(() => null, (reason: unknown) => reason as { code?: string; child_pid?: number });
    expect(error?.code).toBe("FACTORY_REPLAY_OUTPUT_LIMIT");
    expect(error?.child_pid).toEqual(expect.any(Number));
    expect(() => process.kill(error!.child_pid!, 0)).toThrow();
  });

  it("executes the Rule child with declared component identity and removes scratch", async () => {
    const plan = await rulePlan();
    const nodeId = plan.lock.ordered_node_ids[0]!;
    const node = plan.lock.nodes.find(({ node_id: candidate }) => candidate === nodeId)!;
    const scratchRoot = await temporaryRoot("domainspec-replay-child-contract-");
    const replay = await runLockedChild({
      scratchRoot,
      nodeId,
      providerId: node.provider_id,
      rawInputs: await rawInputsFor(plan.lock, nodeId),
      upstream: {},
      lock: plan.lock,
    });
    expect(replay.result).toMatchObject({ result: "pass", provider_id: node.provider_id });
    expect(replay.replay_kind).toBe("same-oracle-deterministic");
    expect(replay.locked_component_set_sha256).toMatch(/^[a-f0-9]{64}$/u);
    expect(replay.protocol_bytes).toBeGreaterThan(0);
    expect(replay.stdout_bytes).toBe(0);
    expect(replay.child_pid).not.toBe(process.pid);
    expect(await readdir(scratchRoot)).toEqual([]);
  }, 90_000);

  it("removes scratch when a pre-load component check fails", async () => {
    const plan = await rulePlan();
    const nodeId = plan.lock.ordered_node_ids[0]!;
    const node = plan.lock.nodes.find(({ node_id: candidate }) => candidate === nodeId)!;
    const scratchRoot = await temporaryRoot("domainspec-replay-cleanup-");
    const tamperedLock = Object.freeze({
      ...plan.lock,
      nodes: Object.freeze(plan.lock.nodes.map((candidate) => candidate.node_id === nodeId
        ? Object.freeze({
          ...candidate,
          components: Object.freeze(candidate.components.map((component, index) => index === 0
            ? Object.freeze({ ...component, sha256: "0".repeat(64) })
            : component)),
        })
        : candidate)),
    }) as FactoryRunLockV1;
    await expect(runLockedChild({
      scratchRoot,
      nodeId,
      providerId: node.provider_id,
      rawInputs: await rawInputsFor(plan.lock, nodeId),
      upstream: {},
      lock: tamperedLock,
    })).rejects.toThrow("FACTORY_REPLAY_COMPONENT_TAMPERED");
    expect(await readdir(scratchRoot)).toEqual([]);
  });
});
