import { createHash, randomUUID } from "node:crypto";
import {
  lstat,
  mkdir,
  readFile,
  readdir,
  realpath,
  rename,
  rm,
  writeFile,
} from "node:fs/promises";
import { dirname, relative, resolve } from "node:path";

import type {
  RawIndexEntryV2,
  RawIndexV2,
} from "../contracts/raw-index-v2.js";

type EvidenceBytes = string | Uint8Array;
type WriteEvidenceBundleOptions = Readonly<{
  root: string;
  runId: string;
  rawInputs: Readonly<Record<string, EvidenceBytes>>;
  artifacts: Readonly<Record<string, EvidenceBytes>>;
  validate?: (
    temporaryRunPath: string,
    index: RawIndexV2,
  ) => Promise<void> | void;
}>;

const sha256 = (value: Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};
const exists = async (path: string): Promise<boolean> =>
  lstat(path).then(() => true, () => false);
const safePath = (value: string): boolean =>
  !value.startsWith("/") && !value.includes("\\") &&
  !value.split("/").some((part) => part === "" || part === "." || part === "..") &&
  value !== "raw-index.json";
const bytes = (value: EvidenceBytes): Uint8Array =>
  typeof value === "string" ? Buffer.from(value, "utf8") : Buffer.from(value);
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const indexBytes = (index: RawIndexV2): string =>
  `${JSON.stringify(index, null, 2)}\n`;

const walkFiles = async (root: string, current = root): Promise<string[]> => {
  const files: string[] = [];
  for (const name of await readdir(current)) {
    const path = resolve(current, name);
    const stat = await lstat(path);
    if (stat.isSymbolicLink()) return fail("FACTORY_EVIDENCE_SYMLINK_FORBIDDEN");
    if (stat.isDirectory()) files.push(...await walkFiles(root, path));
    else if (stat.isFile()) files.push(relative(root, path).replaceAll("\\", "/"));
    else return fail("FACTORY_EVIDENCE_FILE_TYPE_INVALID");
  }
  return files.sort(compareUtf8);
};

export const validateRawIndexV2 = async (
  runPath: string,
  index: RawIndexV2,
): Promise<void> => {
  const ownedRun = await realpath(runPath);
  const expectedPaths = new Set<string>(["raw-index.json"]);
  for (const entry of index.entries) {
    if (!safePath(entry.path) || expectedPaths.has(entry.path)) {
      return fail("FACTORY_EVIDENCE_INDEX_PATH_INVALID");
    }
    expectedPaths.add(entry.path);
    const path = resolve(ownedRun, entry.path);
    if (!path.startsWith(`${ownedRun}/`)) return fail("FACTORY_EVIDENCE_PATH_ESCAPE");
    let observed: Uint8Array;
    try {
      const stat = await lstat(path);
      if (!stat.isFile() || stat.isSymbolicLink()) {
        return fail("FACTORY_EVIDENCE_FILE_TYPE_INVALID");
      }
      observed = await readFile(path);
    } catch (error) {
      if ((error as { code?: string }).code?.startsWith("FACTORY_")) throw error;
      return fail("FACTORY_EVIDENCE_REFERENCED_BYTES_MISSING");
    }
    if (observed.byteLength !== entry.byte_length ||
        sha256(observed) !== entry.sha256) {
      return fail("FACTORY_EVIDENCE_REFERENCED_BYTES_TAMPERED");
    }
  }
  const rawIndexPath = resolve(ownedRun, "raw-index.json");
  let storedIndex: string;
  try {
    storedIndex = await readFile(rawIndexPath, "utf8");
  } catch {
    return fail("FACTORY_EVIDENCE_RAW_INDEX_MISSING");
  }
  if (storedIndex !== indexBytes(index)) {
    return fail("FACTORY_EVIDENCE_RAW_INDEX_TAMPERED");
  }
  const observedPaths = await walkFiles(ownedRun);
  const expected = [...expectedPaths].sort(compareUtf8);
  if (JSON.stringify(observedPaths) !== JSON.stringify(expected)) {
    return fail("FACTORY_EVIDENCE_UNINDEXED_FILE");
  }
};

export const writeEvidenceBundleV2 = async (
  options: WriteEvidenceBundleOptions,
): Promise<Readonly<{
  runPath: string;
  index: RawIndexV2;
  indexSha256: string;
}>> => {
  if (!/^[a-z0-9][a-z0-9-]*$/u.test(options.runId)) {
    return fail("FACTORY_EVIDENCE_RUN_ID_INVALID");
  }
  await mkdir(options.root, { recursive: true });
  const ownedRoot = await realpath(options.root);
  const target = resolve(ownedRoot, options.runId);
  if (!target.startsWith(`${ownedRoot}/`)) return fail("FACTORY_EVIDENCE_PATH_ESCAPE");
  if (await exists(target)) return fail("FACTORY_EVIDENCE_OVERWRITE_FORBIDDEN");
  const partialPrefix = `.${options.runId}.tmp-`;
  if ((await readdir(ownedRoot)).some((name) => name.startsWith(partialPrefix))) {
    return fail("FACTORY_EVIDENCE_PARTIAL_TARGET_EXISTS");
  }
  const lock = resolve(ownedRoot, `.${options.runId}.lock`);
  try {
    await mkdir(lock);
  } catch {
    return fail("FACTORY_EVIDENCE_WRITER_CONFLICT");
  }
  const temporary = resolve(ownedRoot, `${partialPrefix}${randomUUID()}`);
  try {
    await mkdir(temporary);
    const raw = Object.entries(options.rawInputs).map(([path, value]) => ({
      role: "raw-input" as const,
      path: `raw/${path}`,
      value,
    }));
    const artifacts = Object.entries(options.artifacts).map(([path, value]) => ({
      role: "artifact" as const,
      path: `artifacts/${path}`,
      value,
    }));
    const entries = [...raw, ...artifacts].sort((left, right) =>
      compareUtf8(left.path, right.path));
    if (raw.length === 0 || artifacts.length === 0 ||
        entries.some(({ path }) => !safePath(path))) {
      return fail("FACTORY_EVIDENCE_ARTIFACT_SET_INVALID");
    }
    const indexedEntries: RawIndexEntryV2[] = entries.map(({ role, path, value }) => {
      const content = bytes(value);
      return Object.freeze({
        role,
        path,
        sha256: sha256(content),
        byte_length: content.byteLength,
        encoding: typeof value === "string" ? "utf8" as const : "binary" as const,
      });
    });
    const index: RawIndexV2 = Object.freeze({
      schema_version: "RawIndex/v2" as const,
      run_id: options.runId,
      entries: Object.freeze(indexedEntries),
      authority_effect: "none" as const,
    });
    for (const entry of entries) {
      const destination = resolve(temporary, entry.path);
      if (!destination.startsWith(`${temporary}/`)) {
        return fail("FACTORY_EVIDENCE_PATH_ESCAPE");
      }
      await mkdir(dirname(destination), { recursive: true });
      await writeFile(destination, bytes(entry.value), { flag: "wx" });
    }
    await writeFile(resolve(temporary, "raw-index.json"), indexBytes(index), {
      encoding: "utf8",
      flag: "wx",
    });
    await validateRawIndexV2(temporary, index);
    await options.validate?.(temporary, index);
    await rename(temporary, target);
    await rm(lock, { recursive: true, force: false });
    return Object.freeze({
      runPath: target,
      index,
      indexSha256: sha256(Buffer.from(indexBytes(index), "utf8")),
    });
  } catch (error) {
    await rm(temporary, { recursive: true, force: true });
    await rm(lock, { recursive: true, force: true });
    throw error;
  }
};
