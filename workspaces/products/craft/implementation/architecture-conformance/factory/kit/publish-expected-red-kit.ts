import { randomUUID } from "node:crypto";
import { lstat, mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import { scaffoldExpectedRedKit } from "../../kernel/scaffolding/scaffold-realization-kit.js";
import { fail, safeRelativePath, sha256 } from "../shared/canonical.js";
import type { inspectFactoryKitPackage } from "./inspect-kit-package.js";

const exists = async (path: string): Promise<boolean> =>
  lstat(path).then(() => true, () => false);

export const publishExpectedRedKit = async (input: Readonly<{
  inspection: Awaited<ReturnType<typeof inspectFactoryKitPackage>>;
  outputPath: string;
}>): Promise<Readonly<{
  result: "pass";
  output_path: string;
  file_count: number;
  kit_sha256: string;
  authority_effect: "none";
}>> => {
  if (input.inspection.readiness.result !== "ready") {
    fail(input.inspection.readiness.code);
  }
  const kit = scaffoldExpectedRedKit({
    readiness: input.inspection.readiness,
    descriptor: input.inspection.descriptor,
  });
  if (kit.files.length !== 6 || kit.files.some(({ path }) => !safeRelativePath(path))) {
    fail("FACTORY_KIT_ARTIFACT_SET_INVALID");
  }
  const output = resolve(input.outputPath);
  if (await exists(output)) fail("FACTORY_OUTPUT_EXISTS", output);
  await mkdir(dirname(output), { recursive: true });
  const lock = `${output}.lock`;
  try {
    await mkdir(lock);
  } catch {
    return fail("FACTORY_OUTPUT_COLLISION", output);
  }
  const staging = `${output}.tmp-${randomUUID()}`;
  try {
    await mkdir(staging);
    for (const file of kit.files) {
      const target = resolve(staging, file.path);
      if (!target.startsWith(`${staging}/`)) fail("FACTORY_KIT_PATH_ESCAPE", file.path);
      await mkdir(dirname(target), { recursive: true });
      await writeFile(target, file.content, { encoding: "utf8", flag: "wx" });
      const observed = await readFile(target, "utf8");
      if (sha256(observed) !== file.sha256) fail("FACTORY_KIT_WRITE_DRIFT", file.path);
    }
    await rename(staging, output);
    await rm(lock, { recursive: true, force: false });
    return Object.freeze({
      result: "pass",
      output_path: output,
      file_count: kit.files.length,
      kit_sha256: kit.kit_sha256,
      authority_effect: "none",
    });
  } catch (error) {
    await rm(staging, { recursive: true, force: true });
    await rm(lock, { recursive: true, force: true });
    throw error;
  }
};
