import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { executeFactoryRun } from "../pipeline/execute-factory-run.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";
import { replayFactoryRun } from "../pipeline/replay-factory-run.js";
import { verifyFactoryRun } from "../pipeline/verify-factory-run.js";

const roots: string[] = [];
afterEach(async () => Promise.all(roots.splice(0).map((root) =>
  rm(root, { recursive: true, force: true }))));

const plan = async () => {
  const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
    repositoryRoot,
    "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rule-only.request.json",
  ), "utf8")));
  return planFactoryRun({ repositoryRoot, request });
};

describe("factory execution", () => {
  it("runs, replays and verifies the locked TypeScript Rule", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "domainspec-factory-execution-"));
    roots.push(root);
    const run = await executeFactoryRun({ repositoryRoot, outputParent: root, plan: await plan() });
    const verified = await verifyFactoryRun(run.run_path);
    const replayed = await replayFactoryRun(run.run_path);
    expect(verified.semantic_receipt_sha256).toBe(run.semantic_receipt_sha256);
    expect(replayed).toMatchObject({ result: "pass", replayed_nodes: 1 });
    expect(replayed.child_pids.every((pid) => pid !== process.pid)).toBe(true);
  }, 70_000);

  it("refuses an existing terminal run and detects tampering", async () => {
    const root = await mkdtemp(resolve(tmpdir(), "domainspec-factory-collision-"));
    roots.push(root);
    const locked = await plan();
    const run = await executeFactoryRun({ repositoryRoot, outputParent: root, plan: locked });
    await expect(executeFactoryRun({ repositoryRoot, outputParent: root, plan: locked }))
      .rejects.toThrow("FACTORY_OUTPUT_EXISTS");
    const target = resolve(run.run_path, "semantic-receipt.json");
    await writeFile(target, `${await readFile(target, "utf8")} `);
    await expect(verifyFactoryRun(run.run_path)).rejects.toThrow("FACTORY_RUN_BYTES_TAMPERED");
  }, 70_000);
});
