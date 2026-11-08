import { createHash, randomUUID } from "node:crypto";
import { spawn } from "node:child_process";
import {
  copyFile,
  mkdir,
  mkdtemp,
  readFile,
  rm,
  writeFile,
} from "node:fs/promises";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { dirname, isAbsolute, join, resolve } from "node:path";

import type {
  GenericReplayChildRequestV2,
  GenericReplayChildResultV2,
  GenericReplayInputV2,
  GenericReplayManifestV2,
  GenericReplayResultV2,
  ReplayFilePinV2,
} from "../contracts/generic-replay-v2.js";
import type { RawIndexEntryV2 } from "../contracts/raw-index-v2.js";
import { validateRawIndexV2 } from "./write-evidence-bundle-v2.js";

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};
const safeRelativePath = (value: string): boolean =>
  !isAbsolute(value) && !value.includes("\\") &&
  !value.split("/").some((part) => part === "" || part === "." || part === "..");
const SHA256 = /^[a-f0-9]{64}$/u;
const rawIndexBytes = (value: GenericReplayInputV2["rawIndex"]): string =>
  `${JSON.stringify(value, null, 2)}\n`;

const packageVersion = async (path: string): Promise<string> => {
  const value = JSON.parse(await readFile(path, "utf8")) as { version?: unknown };
  return typeof value.version === "string" && value.version.length > 0
    ? value.version
    : fail("FACTORY_REPLAY_TOOLCHAIN_INVALID");
};

const pinRepositoryFile = async (
  repositoryRoot: string,
  path: string,
): Promise<ReplayFilePinV2> => {
  if (!safeRelativePath(path)) return fail("FACTORY_REPLAY_PIN_PATH_INVALID");
  const root = resolve(repositoryRoot);
  const absolute = resolve(root, path);
  if (!absolute.startsWith(`${root}/`)) return fail("FACTORY_REPLAY_PIN_PATH_INVALID");
  return Object.freeze({ path, sha256: sha256(await readFile(absolute)) });
};

export const createGenericReplayManifestV2 = async (options: Readonly<{
  repositoryRoot: string;
  childEntryPath: string;
  componentPaths: Readonly<Record<string, string>>;
  configPaths: Readonly<Record<string, string>>;
  expectedOutputSha256: string;
}>): Promise<GenericReplayManifestV2> => {
  if (!SHA256.test(options.expectedOutputSha256) ||
      Object.keys(options.componentPaths).length === 0 ||
      Object.keys(options.configPaths).length === 0) {
    return fail("FACTORY_REPLAY_MANIFEST_INVALID");
  }
  const implementationRoot = resolve(
    options.repositoryRoot,
    "projects/domainspec-v2/impl",
  );
  const require = createRequire(resolve(implementationRoot, "package.json"));
  const tsxPath = require.resolve("tsx");
  const [childEntry, components, configs, nodeBytes, tsxBytes, tsxVersion] =
    await Promise.all([
      pinRepositoryFile(options.repositoryRoot, options.childEntryPath),
      Promise.all(Object.entries(options.componentPaths).map(async ([name, path]) =>
        [name, await pinRepositoryFile(options.repositoryRoot, path)] as const)),
      Promise.all(Object.entries(options.configPaths).map(async ([name, path]) =>
        [name, await pinRepositoryFile(options.repositoryRoot, path)] as const)),
      readFile(process.execPath),
      readFile(tsxPath),
      packageVersion(require.resolve("tsx/package.json")),
    ]);
  return Object.freeze({
    schema_version: "GenericReplayManifest/v2" as const,
    child_entry: childEntry,
    components: Object.freeze(Object.fromEntries(components)),
    configs: Object.freeze(Object.fromEntries(configs)),
    toolchain: Object.freeze({
      node: Object.freeze({
        path: process.execPath,
        version: process.version,
        sha256: sha256(nodeBytes),
      }),
      tsx_loader: Object.freeze({
        path: tsxPath,
        version: tsxVersion,
        sha256: sha256(tsxBytes),
      }),
    }),
    expected_output_sha256: options.expectedOutputSha256,
    authority_effect: "none" as const,
  });
};

const validatePin = async (
  repositoryRoot: string,
  admitted: ReplayFilePinV2,
): Promise<void> => {
  const current = await pinRepositoryFile(repositoryRoot, admitted.path);
  if (current.sha256 !== admitted.sha256) {
    return fail("FACTORY_REPLAY_COMPONENT_TAMPERED");
  }
};

const validateManifest = async (
  repositoryRoot: string,
  admitted: GenericReplayManifestV2,
): Promise<void> => {
  if (admitted.schema_version !== "GenericReplayManifest/v2" ||
      admitted.authority_effect !== "none" ||
      !SHA256.test(admitted.expected_output_sha256) ||
      Object.keys(admitted.components).length === 0 ||
      Object.keys(admitted.configs).length === 0) {
    return fail("FACTORY_REPLAY_MANIFEST_INVALID");
  }
  await validatePin(repositoryRoot, admitted.child_entry);
  for (const pin of Object.values(admitted.components)) {
    await validatePin(repositoryRoot, pin);
  }
  for (const pin of Object.values(admitted.configs)) {
    try {
      await validatePin(repositoryRoot, pin);
    } catch (error) {
      if ((error as { code?: string }).code === "FACTORY_REPLAY_COMPONENT_TAMPERED") {
        return fail("FACTORY_REPLAY_CONFIG_TAMPERED");
      }
      throw error;
    }
  }
  const require = createRequire(resolve(
    repositoryRoot,
    "projects/domainspec-v2/impl/package.json",
  ));
  const currentTsxPath = require.resolve("tsx");
  const currentTsxVersion = await packageVersion(require.resolve("tsx/package.json"));
  if (admitted.toolchain.node.path !== process.execPath ||
      admitted.toolchain.node.version !== process.version ||
      sha256(await readFile(process.execPath)) !== admitted.toolchain.node.sha256 ||
      !isAbsolute(admitted.toolchain.tsx_loader.path) ||
      admitted.toolchain.tsx_loader.path !== currentTsxPath ||
      admitted.toolchain.tsx_loader.version !== currentTsxVersion ||
      sha256(await readFile(admitted.toolchain.tsx_loader.path)) !==
        admitted.toolchain.tsx_loader.sha256) {
    return fail("FACTORY_REPLAY_TOOLCHAIN_TAMPERED");
  }
};

const verifyRawInputs = async (
  runPath: string,
  entries: readonly RawIndexEntryV2[],
): Promise<void> => {
  for (const entry of entries) {
    if (entry.role !== "raw-input" || !entry.path.startsWith("raw/") ||
        !safeRelativePath(entry.path)) {
      return fail("FACTORY_REPLAY_RAW_INPUT_INVALID");
    }
    let observed: Uint8Array;
    try {
      observed = await readFile(resolve(runPath, entry.path));
    } catch {
      return fail("FACTORY_REPLAY_RAW_INPUT_MISSING");
    }
    if (observed.byteLength !== entry.byte_length ||
        sha256(observed) !== entry.sha256) {
      return fail("FACTORY_REPLAY_RAW_INPUT_TAMPERED");
    }
  }
};

const runChild = async (
  manifest: GenericReplayManifestV2,
  childPath: string,
  requestPath: string,
  cwd: string,
): Promise<string> => new Promise((resolveOutput, reject) => {
  const child = spawn(manifest.toolchain.node.path, [
    "--import",
    manifest.toolchain.tsx_loader.path,
    childPath,
    requestPath,
  ], {
    cwd,
    env: { PATH: process.env.PATH ?? "" },
    stdio: ["ignore", "pipe", "pipe"],
  });
  let stdout = "";
  let stderr = "";
  child.stdout.setEncoding("utf8").on("data", (chunk: string) => {
    stdout += chunk;
  });
  child.stderr.setEncoding("utf8").on("data", (chunk: string) => {
    stderr += chunk;
  });
  child.on("error", reject);
  child.on("close", (code) => {
    if (code === 0) resolveOutput(stdout);
    else reject(Object.assign(new Error(stderr || stdout || `child exited ${code}`), {
      code: "FACTORY_REPLAY_CHILD_FAILED",
    }));
  });
});

export const replayFromRawInputsV2 = async (
  input: GenericReplayInputV2,
): Promise<GenericReplayResultV2> => {
  const rawInputs = input.rawIndex.entries.filter(({ role }) => role === "raw-input");
  if (rawInputs.length === 0) return fail("FACTORY_REPLAY_RECEIPT_ONLY_FORBIDDEN");
  if (sha256(rawIndexBytes(input.rawIndex)) !== input.rawIndexSha256) {
    return fail("FACTORY_REPLAY_RAW_INDEX_DIGEST_STALE");
  }
  await verifyRawInputs(input.runPath, rawInputs);
  await validateRawIndexV2(input.runPath, input.rawIndex);
  await validateManifest(input.repositoryRoot, input.manifest);
  const workspace = await mkdtemp(join(tmpdir(), "domainspec-generic-replay-"));
  try {
    const stagedRaw = resolve(workspace, "raw");
    await mkdir(stagedRaw);
    for (const entry of rawInputs) {
      const destination = resolve(workspace, entry.path);
      await mkdir(dirname(destination), { recursive: true });
      await copyFile(resolve(input.runPath, entry.path), destination);
    }
    const request: GenericReplayChildRequestV2 = Object.freeze({
      schema_version: "GenericReplayChildRequest/v2",
      parent_pid: process.pid,
      raw_root: workspace,
      raw_inputs: Object.freeze(rawInputs.map((entry) => Object.freeze({ ...entry }))),
      expected_output_sha256: input.manifest.expected_output_sha256,
      authority_effect: "none",
    });
    const requestPath = resolve(workspace, `.request-${randomUUID()}.json`);
    await writeFile(requestPath, `${JSON.stringify(request)}\n`, {
      encoding: "utf8",
      flag: "wx",
    });
    const childPath = resolve(input.repositoryRoot, input.manifest.child_entry.path);
    const output = await runChild(
      input.manifest,
      childPath,
      requestPath,
      resolve(input.repositoryRoot, "projects/domainspec-v2/impl"),
    );
    const result = JSON.parse(output) as GenericReplayChildResultV2;
    const { result_sha256: resultSha256, ...body } = result;
    if (result.schema_version !== "GenericReplayChildResult/v2" ||
        result.status !== "pass" || result.child_pid === process.pid ||
        result.semantic_recomposition !== "pass" ||
        result.output_sha256 !== input.manifest.expected_output_sha256 ||
        result.observed_raw_count !== rawInputs.length ||
        result.diagnostics.length !== 0 || result.authority_effect !== "none" ||
        sha256(JSON.stringify(body)) !== resultSha256) {
      return fail("FACTORY_REPLAY_RESULT_INVALID");
    }
    return Object.freeze({
      schema_version: "GenericReplayResult/v2" as const,
      status: "pass" as const,
      child_pid: result.child_pid,
      raw_index_sha256: input.rawIndexSha256,
      result_sha256: resultSha256,
      claims: Object.freeze({
        semantic_recomposition: "pass" as const,
        process_isolation: "pass" as const,
        byte_identity: "not-claimed" as const,
      }),
      authority_effect: "none" as const,
    });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
};
