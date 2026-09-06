import { createHash, randomUUID } from "node:crypto";
import { lstat, mkdir, readdir, realpath, rename, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

export type ProofRunIndex = Readonly<{
  schema_version: "ProofRunIndex/v1";
  run_id: string;
  artifacts: readonly Readonly<{ path: string; sha256: string; byte_length: number }>[];
  authority_effect: "none";
}>;

type WriteProofRunOptions = Readonly<{
  root: string;
  runId: string;
  artifacts: Readonly<Record<string, string>>;
  validate?: (temporaryRunPath: string, index: ProofRunIndex) => Promise<void> | void;
}>;

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const safeSegmentedPath = (value: string): boolean => !value.startsWith("/")
  && !value.includes("\\")
  && !value.split("/").some((part) => part === "" || part === "." || part === "..");
const exists = async (path: string): Promise<boolean> => lstat(path).then(() => true, () => false);
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};

export const writeProofRun = async (options: WriteProofRunOptions): Promise<Readonly<{
  runPath: string;
  index: ProofRunIndex;
  indexSha256: string;
}>> => {
  if (!/^[a-z0-9][a-z0-9-]*$/u.test(options.runId)) return fail("ARCH_PROOF_RUN_ID_INVALID");
  await mkdir(options.root, { recursive: true });
  const ownedRoot = await realpath(options.root);
  const target = resolve(ownedRoot, options.runId);
  if (!target.startsWith(`${ownedRoot}/`)) return fail("ARCH_PROOF_PATH_ESCAPE");
  if (await exists(target)) return fail("ARCH_PROOF_OVERWRITE_FORBIDDEN");
  const partialPrefix = `.${options.runId}.tmp-`;
  if ((await readdir(ownedRoot)).some((name) => name.startsWith(partialPrefix))) {
    return fail("ARCH_PROOF_PARTIAL_TARGET_EXISTS");
  }
  const lock = resolve(ownedRoot, `.${options.runId}.lock`);
  try {
    await mkdir(lock);
  } catch {
    return fail("ARCH_PROOF_WRITER_CONFLICT");
  }
  const temporary = resolve(ownedRoot, `${partialPrefix}${randomUUID()}`);
  try {
    await mkdir(temporary);
    const entries = Object.entries(options.artifacts).sort(([left], [right]) =>
      Buffer.from(left).compare(Buffer.from(right)));
    if (entries.length === 0 || entries.some(([path]) => !safeSegmentedPath(path))) {
      return fail("ARCH_PROOF_ARTIFACT_PATH_INVALID");
    }
    const artifacts = entries.map(([path, value]) => Object.freeze({
      path,
      sha256: sha256(value),
      byte_length: Buffer.byteLength(value, "utf8"),
    }));
    const index = Object.freeze({
      schema_version: "ProofRunIndex/v1" as const,
      run_id: options.runId,
      artifacts: Object.freeze(artifacts),
      authority_effect: "none" as const,
    });
    for (const [path, value] of entries) {
      const destination = resolve(temporary, path);
      if (!destination.startsWith(`${temporary}/`)) return fail("ARCH_PROOF_PATH_ESCAPE");
      await mkdir(dirname(destination), { recursive: true });
      await writeFile(destination, value, { encoding: "utf8", flag: "wx" });
    }
    await options.validate?.(temporary, index);
    await rename(temporary, target);
    await rm(lock, { recursive: true, force: false });
    return Object.freeze({
      runPath: target,
      index,
      indexSha256: sha256(`${JSON.stringify(index, null, 2)}\n`),
    });
  } catch (error) {
    await rm(temporary, { recursive: true, force: true });
    await rm(lock, { recursive: true, force: true });
    throw error;
  }
};
