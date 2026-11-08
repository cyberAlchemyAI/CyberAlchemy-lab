import { randomUUID } from "node:crypto";
import { lstat, mkdir, readFile, readdir, rename, rm, writeFile } from "node:fs/promises";
import { relative, resolve } from "node:path";

import type { FactoryRunPlanV1 } from "../contracts/factory-run-plan-v1.js";
import { fail, json, sha256 } from "../shared/canonical.js";
import { verifyFactoryRunRoot } from "./verify-run-root.js";

const exists = async (path: string): Promise<boolean> =>
  lstat(path).then(() => true, () => false);

const walk = async (root: string, current = root): Promise<string[]> => {
  const paths: string[] = [];
  for (const name of await readdir(current)) {
    const path = resolve(current, name);
    const stat = await lstat(path);
    if (stat.isSymbolicLink()) fail("FACTORY_RUN_SYMLINK_FORBIDDEN");
    if (stat.isDirectory()) paths.push(...await walk(root, path));
    else if (stat.isFile()) paths.push(relative(root, path).replaceAll("\\", "/"));
  }
  return paths.sort((left, right) => Buffer.from(left).compare(Buffer.from(right)));
};

export const publishFactoryRun = async (input: Readonly<{
  outputParent: string;
  plan: FactoryRunPlanV1;
  build: (stagingRoot: string, targetPath: string) => Promise<void>;
}>): Promise<Readonly<{ run_path: string; cleanup: "pass" }>> => {
  await mkdir(input.outputParent, { recursive: true });
  const target = resolve(input.outputParent, input.plan.run_id);
  if (await exists(target)) fail("FACTORY_OUTPUT_EXISTS", target);
  const lock = resolve(input.outputParent, `.${input.plan.run_id}.lock`);
  try {
    await mkdir(lock);
  } catch {
    return fail("FACTORY_OUTPUT_COLLISION", target);
  }
  const staging = resolve(input.outputParent, `.${input.plan.run_id}.tmp-${randomUUID()}`);
  try {
    await mkdir(staging);
    await input.build(staging, target);
    const indexedPaths = (await walk(staging)).filter((path) => path !== "run-index.json");
    const entries = await Promise.all(indexedPaths.map(async (path) => {
      const bytes = await readFile(resolve(staging, path));
      return Object.freeze({ path, sha256: sha256(bytes), byte_length: bytes.byteLength });
    }));
    await writeFile(resolve(staging, "run-index.json"), json(Object.freeze({
      schema_version: "FactoryRunIndex/v1",
      entries: Object.freeze(entries),
      authority_effect: "none",
    })), { encoding: "utf8", flag: "wx" });
    await verifyFactoryRunRoot(staging);
    await rename(staging, target);
    await rm(lock, { recursive: true, force: false });
    await verifyFactoryRunRoot(target);
    return Object.freeze({ run_path: target, cleanup: "pass" });
  } catch (error) {
    await rm(staging, { recursive: true, force: true });
    await rm(lock, { recursive: true, force: true });
    throw error;
  }
};
