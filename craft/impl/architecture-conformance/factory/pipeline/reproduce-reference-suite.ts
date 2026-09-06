import { randomUUID } from "node:crypto";
import { lstat, mkdir, readFile, readdir, rename, rm, writeFile } from "node:fs/promises";
import { basename, dirname, relative, resolve } from "node:path";

import type { FactoryRunRequestV1 } from "../contracts/factory-run-request-v1.js";
import { executeFactoryRun } from "./execute-factory-run.js";
import { planFactoryRun } from "./plan-factory-run.js";
import { verifyFactoryRun } from "./verify-factory-run.js";
import { fail, json, sha256 } from "../shared/canonical.js";

const inventory = async (root: string, current = root): Promise<readonly string[]> => {
  const entries: string[] = [];
  for (const name of await readdir(current)) {
    if (name === "target" || name === "__pycache__") continue;
    const path = resolve(current, name);
    const stat = await lstat(path);
    if (stat.isDirectory()) entries.push(...await inventory(root, path));
    else if (stat.isFile()) {
      const bytes = await readFile(path);
      entries.push(`${relative(root, path).replaceAll("\\", "/")}:${bytes.byteLength}:${sha256(bytes)}`);
    }
  }
  return Object.freeze(entries.sort((left, right) => Buffer.from(left).compare(Buffer.from(right))));
};

export const reproduceReferenceSuite = async (input: Readonly<{
  repositoryRoot: string;
  request: FactoryRunRequestV1;
  outputRoot: string;
}>): Promise<Readonly<{
  result: "pass";
  reproduction_receipt: string;
  semantic_receipt_sha256: string;
  run_a: string;
  run_b: string;
  authority_effect: "none";
}>> => {
  if (input.request.purpose !== "reference-reproduction") {
    fail("FACTORY_PURPOSE_INFLATION", input.request.purpose);
  }
  const outputRoot = resolve(input.outputRoot);
  if (await lstat(outputRoot).then(() => true, () => false)) {
    fail("FACTORY_OUTPUT_EXISTS", outputRoot);
  }
  await mkdir(dirname(outputRoot), { recursive: true });
  const lock = resolve(dirname(outputRoot), `.${basename(outputRoot)}.lock`);
  await mkdir(lock).catch(() => fail("FACTORY_OUTPUT_COLLISION", outputRoot));
  const workingRoot = resolve(
    dirname(outputRoot),
    `.${basename(outputRoot)}.tmp-${randomUUID()}`,
  );
  await mkdir(workingRoot);
  try {
  const productRoot = resolve(
    input.repositoryRoot,
    "projects/domainspec-v2/impl/architecture-conformance",
  );
  const before = await inventory(productRoot);
  const plan = await planFactoryRun({ repositoryRoot: input.repositoryRoot, request: input.request });
  const runA = await executeFactoryRun({
    repositoryRoot: input.repositoryRoot,
    outputParent: resolve(workingRoot, "run-a"),
    plan,
  });
  const runB = await executeFactoryRun({
    repositoryRoot: input.repositoryRoot,
    outputParent: resolve(workingRoot, "run-b"),
    plan,
  });
  const [verificationA, verificationB] = await Promise.all([
    verifyFactoryRun(runA.run_path),
    verifyFactoryRun(runB.run_path),
  ]);
  if (verificationA.semantic_receipt_sha256 !== verificationB.semantic_receipt_sha256 ||
      verificationA.lock_sha256 !== verificationB.lock_sha256) {
    fail("FACTORY_SEMANTIC_DIGEST_MISMATCH");
  }
  const [processA, processB] = await Promise.all([
    readFile(resolve(runA.run_path, "process-observation.json")),
    readFile(resolve(runB.run_path, "process-observation.json")),
  ]);
  if (sha256(processA) === sha256(processB)) fail("FACTORY_PROCESS_ISOLATION_MISSING");
  const after = await inventory(productRoot);
  if (JSON.stringify(before) !== JSON.stringify(after)) fail("FACTORY_PRODUCT_TREE_MUTATED");
  const receiptPath = resolve(workingRoot, "reproduction-receipt.json");
  await writeFile(receiptPath, json(Object.freeze({
    schema_version: "FactoryReproductionReceipt/v1",
    result: "pass",
    request_sha256: plan.lock.request_sha256,
    lock_sha256: plan.lock.lock_sha256,
    semantic_receipt_sha256: verificationA.semantic_receipt_sha256,
    runs: Object.freeze([
      Object.freeze({ id: "a", path: `run-a/${plan.run_id}`,
        replayed_nodes: plan.lock.ordered_node_ids.length }),
      Object.freeze({ id: "b", path: `run-b/${plan.run_id}`,
        replayed_nodes: plan.lock.ordered_node_ids.length }),
    ]),
    process_observation_sha256: Object.freeze([sha256(processA), sha256(processB)]),
    product_tree_inventory_sha256: sha256(JSON.stringify(after)),
    claim_ceiling: input.request.claim_ceiling,
    authority_effect: "none",
  })), { encoding: "utf8", flag: "wx" });
  await rename(workingRoot, outputRoot);
  await rm(lock, { recursive: true, force: false });
  return Object.freeze({
    result: "pass",
    reproduction_receipt: resolve(outputRoot, "reproduction-receipt.json"),
    semantic_receipt_sha256: verificationA.semantic_receipt_sha256,
    run_a: resolve(outputRoot, "run-a", plan.run_id),
    run_b: resolve(outputRoot, "run-b", plan.run_id),
    authority_effect: "none",
  });
  } catch (error) {
    await rm(workingRoot, { recursive: true, force: true });
    await rm(lock, { recursive: true, force: true });
    throw error;
  }
};
