import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { closeSync, constants, fstatSync, lstatSync, mkdtempSync, openSync, readFileSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { isAbsolute, join, relative } from "node:path";

import { canonicalJson, sha256 } from "./canonical-json.js";
import { fail, type ExactRef } from "./types.js";

const CEILING = "trusted-local-native-case-observation-only-no-isolation-oracle-formal-claim-evf-or-runtime-guarantee" as const;
const MAX_CASES = 64;
const MAX_INPUT_BYTES = 1024 * 1024;
const exactKeys = (value: object, keys: readonly string[]) =>
  canonicalJson(Object.keys(value).sort()) === canonicalJson([...keys].sort());

export type LocalNativeCaseSelection = Readonly<{
  schema_version: "tde.local-native-case-selection/v1-candidate";
  mode: "trusted-local-no-isolation";
  runtime_ref: ExactRef;
  adapter_ref: ExactRef;
  cases: readonly Readonly<{ case_id: string; input_ref: ExactRef }>[];
  policy: Readonly<{ timeout_ms: number; max_output_bytes: number }>;
}>;

export type LocalNativeCaseObservation = Readonly<{
  case_id: string;
  input_ref: ExactRef;
  exit_code: number | null;
  signal: NodeJS.Signals | null;
  timed_out: boolean;
  output_limit_exceeded: boolean;
  stdout_base64: string;
  stdout_sha256: string;
  stderr_base64: string;
  stderr_sha256: string;
}>;

export type LocalNativeCaseReceipt = Readonly<{
  schema_version: "tde.local-native-case-observation/v1-candidate";
  mode: "trusted-local-no-isolation";
  selection: LocalNativeCaseSelection;
  observations: readonly LocalNativeCaseObservation[];
  status: "observed" | "incomplete";
  isolation_verification: "unverified";
  oracle_verification: "not-performed";
  evf_join: "forbidden";
  can_satisfy_obligation: false;
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
  receipt_digest: string;
}>;

function regularBytes(path: string, maxBytes: number): Buffer {
  const stat = lstatSync(path);
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size < 1 || stat.size > maxBytes)
    fail("TARGET_BASELINE_DRIFT", "admission", `not a bounded regular file: ${path}`);
  const fd = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const before = fstatSync(fd);
    const bytes = readFileSync(fd);
    const after = fstatSync(fd);
    if (!before.isFile() || bytes.length !== before.size || before.ino !== after.ino || before.dev !== after.dev ||
        before.mtimeMs !== after.mtimeMs || before.ctimeMs !== after.ctimeMs || bytes.length > maxBytes)
      fail("TARGET_BASELINE_DRIFT", "admission", `file changed while reading: ${path}`);
    return bytes;
  } finally { closeSync(fd); }
}

function selectedFile(root: string, ref: ExactRef, maxBytes: number): { absolute: string; bytes: Buffer } {
  if (!ref || typeof ref !== "object" || !exactKeys(ref, ["path", "sha256", "size_bytes"]) ||
      typeof ref.path !== "string" || !ref.path || isAbsolute(ref.path) ||
      ref.path.includes("\\") || ref.path.split("/").some(part => part === "" || part === "." || part === "..") ||
      !/^[a-f0-9]{64}$/.test(ref.sha256) || !Number.isSafeInteger(ref.size_bytes) ||
      ref.size_bytes < 1 || ref.size_bytes > maxBytes)
    fail("TARGET_BASELINE_DRIFT", "admission", "invalid exact local file reference");
  const base = realpathSync(root);
  let absolute = base;
  for (const part of ref.path.split("/")) {
    absolute = join(absolute, part);
    if (lstatSync(absolute).isSymbolicLink())
      fail("TARGET_BASELINE_DRIFT", "admission", "symlink in selected local file path");
  }
  const rel = relative(base, absolute);
  if (rel === ".." || rel.startsWith("../") || isAbsolute(rel) || realpathSync(absolute) !== absolute)
    fail("TARGET_BASELINE_DRIFT", "admission", "selected local file escapes root");
  const bytes = regularBytes(absolute, maxBytes);
  if (bytes.length !== ref.size_bytes || sha256(bytes) !== ref.sha256)
    fail("TARGET_BASELINE_DRIFT", "admission", `selected local file drifted: ${ref.path}`);
  return { absolute, bytes };
}

function runtimeFile(ref: ExactRef): string {
  if (!ref || typeof ref !== "object" || !exactKeys(ref, ["path", "sha256", "size_bytes"]) ||
      typeof ref.path !== "string" || !isAbsolute(ref.path) ||
      !/^[a-f0-9]{64}$/.test(ref.sha256) || !Number.isSafeInteger(ref.size_bytes) || ref.size_bytes < 1)
    fail("PROVIDER_RUNTIME_UNAVAILABLE", "admission", "exact absolute runtime reference required");
  const absolute = realpathSync(ref.path);
  const bytes = regularBytes(absolute, 256 * 1024 * 1024);
  if (bytes.length !== ref.size_bytes || sha256(bytes) !== ref.sha256)
    fail("PROVIDER_RUNTIME_UNAVAILABLE", "admission", "selected runtime bytes drifted");
  return absolute;
}

function validateSelection(selection: LocalNativeCaseSelection): void {
  if (!selection || !exactKeys(selection, ["schema_version", "mode", "runtime_ref", "adapter_ref", "cases", "policy"]) ||
      selection.schema_version !== "tde.local-native-case-selection/v1-candidate" ||
      selection.mode !== "trusted-local-no-isolation" || !Array.isArray(selection.cases) ||
      selection.cases.length < 1 || selection.cases.length > MAX_CASES ||
      !selection.policy || typeof selection.policy !== "object" ||
      !exactKeys(selection.policy, ["timeout_ms", "max_output_bytes"]) ||
      !Number.isSafeInteger(selection.policy.timeout_ms) ||
      selection.policy.timeout_ms < 1 || selection.policy.timeout_ms > 30_000 ||
      !Number.isSafeInteger(selection.policy.max_output_bytes) ||
      selection.policy.max_output_bytes < 1 || selection.policy.max_output_bytes > 1024 * 1024)
    fail("PROVIDER_SCOPE_INVALID", "admission", "invalid trusted-local observation selection");
  if (selection.cases.some(item => !item || typeof item !== "object" || !exactKeys(item, ["case_id", "input_ref"])))
    fail("PROVIDER_SCOPE_INVALID", "admission", "case rows must have exact identity and input reference fields");
  const ids = selection.cases.map(item => item.case_id);
  if (ids.some(id => typeof id !== "string" || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(id)) ||
      new Set(ids).size !== ids.length ||
      new Set(selection.cases.map(item => item.input_ref?.path)).size !== ids.length ||
      canonicalJson(ids) !== canonicalJson([...ids].sort()))
    fail("PROVIDER_SCOPE_INVALID", "admission", "case IDs and input paths must be unique and sorted");
}

async function invoke(runtime: string, adapter: string, input: Buffer, cwd: string,
  policy: LocalNativeCaseSelection["policy"]): Promise<Omit<LocalNativeCaseObservation, "case_id" | "input_ref">> {
  return await new Promise((resolve, reject) => {
    const child = spawn(runtime, [adapter], {
      cwd, shell: false, detached: true, stdio: ["pipe", "pipe", "pipe"],
      env: { LANG: "C", LC_ALL: "C", TZ: "UTC" },
    });
    const stdout: Buffer[] = [], stderr: Buffer[] = [];
    let total = 0, timedOut = false, outputLimitExceeded = false, settled = false;
    const killGroup = () => {
      if (child.pid) {
        try { process.kill(-child.pid, "SIGKILL"); } catch (error) {
          if ((error as NodeJS.ErrnoException).code !== "ESRCH") child.kill("SIGKILL");
        }
      }
    };
    const timer = setTimeout(() => { timedOut = true; killGroup(); }, policy.timeout_ms);
    const collect = (target: Buffer[]) => (chunk: Buffer) => {
      total += chunk.length;
      if (total > policy.max_output_bytes) {
        outputLimitExceeded = true;
        killGroup();
      } else target.push(chunk);
    };
    child.stdout.on("data", collect(stdout));
    child.stderr.on("data", collect(stderr));
    child.once("error", error => {
      if (!settled) { settled = true; clearTimeout(timer); killGroup(); reject(error); }
    });
    child.once("close", (code, signal) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      killGroup();
      const out = Buffer.concat(stdout), err = Buffer.concat(stderr);
      resolve({ exit_code: code, signal, timed_out: timedOut, output_limit_exceeded: outputLimitExceeded,
        stdout_base64: out.toString("base64"), stdout_sha256: sha256(out),
        stderr_base64: err.toString("base64"), stderr_sha256: sha256(err) });
    });
    child.stdin.on("error", () => {});
    child.stdin.end(input);
  });
}

/** A separate trusted-local experiment, never an execution of a finalized F5 request.
 * Staging and rechecking bytes detect ordinary drift, but are not an isolation
 * boundary or proof of the exact instructions executed by a mutable process. */
export async function observeLocalNativeCases(repoRoot: string, selection: LocalNativeCaseSelection): Promise<LocalNativeCaseReceipt> {
  validateSelection(selection);
  if (process.platform !== "linux") fail("PROVIDER_SCOPE_INVALID", "admission", "trusted-local observation requires Linux process groups");
  const selectedShape = canonicalJson(selection);
  const runtime = runtimeFile(selection.runtime_ref);
  const adapterSource = selectedFile(repoRoot, selection.adapter_ref, MAX_INPUT_BYTES);
  const inputs = selection.cases.map(item => ({ item, bytes: selectedFile(repoRoot, item.input_ref, MAX_INPUT_BYTES).bytes }));
  const cwd = mkdtempSync(join(tmpdir(), "tde-local-native-case-"));
  try {
    const adapter = join(cwd, "selected-adapter.mjs");
    writeFileSync(adapter, adapterSource.bytes, { mode: 0o400, flag: "wx" });
    const observations: LocalNativeCaseObservation[] = [];
    for (const { item, bytes } of inputs) {
      const result = await invoke(runtime, adapter, bytes, cwd, selection.policy);
      observations.push({ case_id: item.case_id, input_ref: item.input_ref, ...result });
      if (result.timed_out || result.output_limit_exceeded || result.exit_code !== 0) break;
    }
    if (canonicalJson(selection) !== selectedShape || runtimeFile(selection.runtime_ref) !== runtime ||
        selectedFile(repoRoot, selection.adapter_ref, MAX_INPUT_BYTES).absolute !== adapterSource.absolute ||
        sha256(regularBytes(adapter, MAX_INPUT_BYTES)) !== selection.adapter_ref.sha256)
      fail("TARGET_BASELINE_DRIFT", "replay", "selected local invocation changed during observation");
    for (const { item } of inputs) selectedFile(repoRoot, item.input_ref, MAX_INPUT_BYTES);
    const unsigned = { schema_version: "tde.local-native-case-observation/v1-candidate" as const,
      mode: "trusted-local-no-isolation" as const, selection, observations,
      status: observations.length === selection.cases.length && observations.every(row =>
        !row.timed_out && !row.output_limit_exceeded && row.exit_code === 0) ? "observed" as const : "incomplete" as const,
      isolation_verification: "unverified" as const, oracle_verification: "not-performed" as const,
      evf_join: "forbidden" as const, can_satisfy_obligation: false as const,
      authority_effect: "none" as const, claim_ceiling: CEILING };
    return { ...unsigned, receipt_digest: sha256(canonicalJson(unsigned)) };
  } finally { rmSync(cwd, { recursive: true, force: true }); }
}

/** Re-execution binds a separately selected contract. It cannot authenticate
 * the historical receipt's origin; the caller must independently select the
 * expected contract before invoking this function. */
export async function replayLocalNativeCases(repoRoot: string, expectedSelection: LocalNativeCaseSelection,
  receipt: LocalNativeCaseReceipt): Promise<LocalNativeCaseReceipt> {
  if (!receipt || receipt.schema_version !== "tde.local-native-case-observation/v1-candidate" ||
      receipt.mode !== "trusted-local-no-isolation" ||
      receipt.status !== "observed" || receipt.can_satisfy_obligation !== false ||
      receipt.isolation_verification !== "unverified" || receipt.oracle_verification !== "not-performed" ||
      receipt.evf_join !== "forbidden" || receipt.authority_effect !== "none" || receipt.claim_ceiling !== CEILING ||
      !exactKeys(receipt, ["schema_version", "mode", "selection", "observations", "status", "isolation_verification",
        "oracle_verification", "evf_join", "can_satisfy_obligation", "authority_effect", "claim_ceiling", "receipt_digest"]) ||
      canonicalJson(receipt.selection) !== canonicalJson(expectedSelection))
    fail("PROVIDER_RECEIPT_TAMPERED", "replay", "local observation receipt has invalid scope");
  const { receipt_digest: _receiptDigest, ...unsigned } = receipt;
  if (receipt.receipt_digest !== sha256(canonicalJson(unsigned)))
    fail("PROVIDER_RECEIPT_TAMPERED", "replay", "local observation receipt digest differs");
  const current = await observeLocalNativeCases(repoRoot, expectedSelection);
  if (canonicalJson(current) !== canonicalJson(receipt))
    fail("PROVIDER_RECEIPT_TAMPERED", "replay", "local native case observations differ on re-execution");
  return current;
}
