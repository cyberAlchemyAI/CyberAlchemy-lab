import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import { readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { ReplayRawIndex, ReplayResult } from "../contracts/replay-result.js";
import { validateReplayEnvironment } from "./replay-environment.js";

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};
const safePath = (value: string): boolean => !value.startsWith("/") && !value.includes("\\")
  && !value.split("/").some((part) => part === "" || part === "." || part === "..");

export const replayEnumProof = async (options: Readonly<{
  repositoryRoot: string;
  rawRoot: string;
  rawIndex: ReplayRawIndex;
}>): Promise<ReplayResult> => {
  if (options.rawIndex.schema_version !== "ReplayRawIndex/v2"
      || options.rawIndex.authority_effect !== "none") return fail("ARCH_REPLAY_INDEX_INVALID");
  const entries = Object.entries(options.rawIndex.inputs);
  if (entries.some(([name, ref]) => name.includes("evaluation") || name.includes("receipt")
      || !safePath(ref.path))) return fail("ARCH_REPLAY_RECEIPT_ONLY_FORBIDDEN");
  for (const [, ref] of entries) {
    const path = resolve(options.rawRoot, ref.path);
    if (!path.startsWith(`${resolve(options.rawRoot)}/`)) return fail("ARCH_REPLAY_PATH_ESCAPE");
    let bytes: string;
    try {
      bytes = await readFile(path, "utf8");
    } catch {
      return fail("ARCH_REPLAY_RAW_INPUT_MISSING");
    }
    if (sha256(bytes) !== ref.sha256) return fail("ARCH_REPLAY_RAW_INPUT_TAMPERED");
  }
  const environment = await validateReplayEnvironment(
    options.repositoryRoot,
    options.rawIndex.environment,
  );
  const here = dirname(fileURLToPath(import.meta.url));
  const childEntry = resolve(here, "child-entry.ts");
  const implementationRoot = resolve(options.repositoryRoot, "projects/domainspec-v2/impl");
  const requestPath = resolve(options.rawRoot, `.replay-request-${process.pid}.json`);
  await writeFile(requestPath, `${JSON.stringify({
    repositoryRoot: resolve(options.repositoryRoot),
    rawRoot: resolve(options.rawRoot),
    rawIndex: options.rawIndex,
    parentPid: process.pid,
  })}\n`, { encoding: "utf8", flag: "wx" });
  try {
    const output = await new Promise<string>((resolveOutput, reject) => {
      const child = spawn(environment.toolchain.node.path, [
        "--import",
        environment.toolchain.tsx_loader.path,
        childEntry,
        requestPath,
      ], {
        cwd: implementationRoot,
        env: { PATH: process.env.PATH ?? "" },
        stdio: ["ignore", "pipe", "pipe"],
      });
      let stdout = "";
      let stderr = "";
      child.stdout.setEncoding("utf8").on("data", (chunk: string) => { stdout += chunk; });
      child.stderr.setEncoding("utf8").on("data", (chunk: string) => { stderr += chunk; });
      child.on("error", reject);
      child.on("close", (code) => {
        if (code === 0) resolveOutput(stdout);
        else reject(Object.assign(new Error(stderr || stdout || `child exited ${code}`), {
          code: "ARCH_REPLAY_CHILD_FAILED",
        }));
      });
    });
    const result = JSON.parse(output) as ReplayResult;
    if (result.schema_version !== "ReplayResult/v2" || result.child_pid === process.pid
        || result.status !== "pass" || result.authority_effect !== "none"
        || result.claims.semantic_recomposition !== "pass"
        || result.claims.process_isolation !== "pass"
        || result.claims.byte_identity !== "not-claimed") {
      return fail("ARCH_REPLAY_RESULT_INVALID");
    }
    return Object.freeze(result);
  } finally {
    await import("node:fs/promises").then(({ rm }) => rm(requestPath, { force: true }));
  }
};
