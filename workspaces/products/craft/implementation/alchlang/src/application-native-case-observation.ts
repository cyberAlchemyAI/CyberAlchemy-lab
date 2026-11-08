import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { chmod, copyFile, lstat, mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { isAbsolute, join } from "node:path";
import { CompilationRejected } from "./model.js";
import { finalizeApplicationExecutionRequest, type ExactExecutionSourceRef, type ExecutionRequestSelection } from "./application-execution-request.js";

type JsonObject = Record<string, unknown>;
type ExactRef = ExactExecutionSourceRef;

/** The caller must deliberately opt in to executing these trusted local bytes.
 * This is not a sandbox, a provider authentication mechanism, or an EVF join. */
export interface NativeCaseObservationInput {
  opt_in: "trusted-local-native-case-observation";
  selection: ExecutionRequestSelection;
  finalized_request_ref: ExactRef;
  local_adapter_ref: ExactRef;
  local_executable_ref: ExactRef;
}

const residue = [
  "TDE producer authenticity and executable oracle truth unverified",
  "local adapter equivalence to the selected provider unverified",
  "network and memory ceilings not enforced by this trusted-local runner",
  "host environment isolation unverified",
  "EVF satisfaction and runtime_guarantees_observed forbidden",
] as const;
// These are limits of this opt-in diagnostic, not a strengthening of the
// finalized request's provider policy.
const LOCAL_MAX_TIMEOUT_MS = 30_000;
const LOCAL_MAX_OUTPUT_BYTES = 1_048_576;
const LOCAL_MAX_CASES = 256;
const LOCAL_MAX_ADAPTER_BYTES = 1_048_576;

const fail = (code: string, path: string, message: string): never => {
  throw new CompilationRejected([{ code, path, message }]);
};
const sha = (bytes: Buffer | string): string => createHash("sha256").update(bytes).digest("hex");
const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const item = value as JsonObject;
    return `{${Object.keys(item).sort().map(key => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
};
const object = (value: unknown, path: string): JsonObject => {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("APPLICATION_NATIVE_INPUT", path, "expected object");
  return value as JsonObject;
};
const exactKeys = (value: unknown, keys: readonly string[], path: string): JsonObject => {
  const item = object(value, path);
  if (canonical(Object.keys(item).sort()) !== canonical([...keys].sort())) {
    fail("APPLICATION_NATIVE_INPUT", path, "unexpected or missing property");
  }
  return item;
};
const same = (left: unknown, right: unknown): boolean => canonical(left) === canonical(right);
const snapshot = (sources: ReadonlyMap<string, Buffer>): Map<string, Buffer> =>
  new Map([...sources].map(([key, bytes]) => [key, Buffer.from(bytes)]));
const assertUnchanged = (sources: ReadonlyMap<string, Buffer>, before: ReadonlyMap<string, Buffer>): void => {
  if (sources.size !== before.size || [...before].some(([key, bytes]) => {
    const current = sources.get(key);
    return !current || !current.equals(bytes);
  })) fail("APPLICATION_NATIVE_SOURCE_MUTATED", "$sources", "source map or Buffer changed during local execution");
};

function exactBytes(value: unknown, sources: ReadonlyMap<string, Buffer>, path: string): { ref: ExactRef; bytes: Buffer } {
  const ref = exactKeys(value, ["path", "sha256", "size_bytes", "current"], path);
  if (typeof ref.path !== "string" || !ref.path || typeof ref.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/.test(ref.sha256) || !Number.isSafeInteger(ref.size_bytes) ||
      (ref.size_bytes as number) < 1 || ref.current !== true) {
    fail("APPLICATION_NATIVE_REF", path, "expected a current exact nonempty byte reference");
  }
  const bytes = sources.get(ref.path as string);
  if (!bytes) fail("APPLICATION_NATIVE_MISSING", path, "referenced bytes are missing");
  const present = bytes as Buffer;
  if (present.length !== ref.size_bytes || sha(present) !== ref.sha256) {
    fail("APPLICATION_NATIVE_STALE", path, "referenced bytes differ");
  }
  return { ref: { path: ref.path as string, sha256: ref.sha256 as string,
    size_bytes: ref.size_bytes as number, current: true }, bytes: Buffer.from(present) };
}

async function assertFileHash(path: string, expected: ExactRef): Promise<void> {
  let stat;
  try { stat = await lstat(path); }
  catch { return fail("APPLICATION_NATIVE_EXECUTABLE", "$input/local_executable_ref", "selected executable is missing"); }
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size !== expected.size_bytes || (stat.mode & 0o111) === 0) {
    fail("APPLICATION_NATIVE_EXECUTABLE", "$input/local_executable_ref", "selected executable must be a regular executable file of exact size");
  }
  const hash = createHash("sha256");
  for await (const chunk of createReadStream(path)) hash.update(chunk);
  if (hash.digest("hex") !== expected.sha256) {
    fail("APPLICATION_NATIVE_EXECUTABLE", "$input/local_executable_ref", "selected executable bytes differ");
  }
}

async function assertExecutableCurrent(value: unknown): Promise<ExactRef> {
  const ref = exactKeys(value, ["path", "sha256", "size_bytes", "current"], "$input/local_executable_ref");
  if (typeof ref.path !== "string" || !isAbsolute(ref.path) || typeof ref.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/.test(ref.sha256) || !Number.isSafeInteger(ref.size_bytes) ||
      (ref.size_bytes as number) < 1 || ref.current !== true) {
    fail("APPLICATION_NATIVE_EXECUTABLE", "$input/local_executable_ref", "expected exact current absolute executable ref");
  }
  const current: ExactRef = { path: ref.path as string, sha256: ref.sha256 as string,
    size_bytes: ref.size_bytes as number, current: true };
  await assertFileHash(current.path, current);
  return current;
}

function parseJson(bytes: Buffer, path: string): JsonObject {
  try { return object(JSON.parse(bytes.toString("utf8")), path); }
  catch { return fail("APPLICATION_NATIVE_JSON", path, "referenced bytes are not a JSON object"); }
}

function boundedRelativePath(path: string): boolean {
  return /^(?!\/)(?!.*(?:^|\/)\.\.?(?:\/|$))[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*$/.test(path);
}

type FailureKind = "timeout" | "output-limit" | "nonzero-exit" | "spawn-error" | "malformed-output";
class NativeExecutionFailure extends Error {
  constructor(readonly kind: FailureKind) { super(kind); }
}
async function runOne(executablePath: string, adapterPath: string, cwd: string, input: Buffer, timeoutMs: number, maxOutputBytes: number): Promise<Buffer> {
  return await new Promise<Buffer>((resolve, reject) => {
    const child = spawn(executablePath, [adapterPath], {
      cwd, detached: true, stdio: ["pipe", "pipe", "pipe"], shell: false,
      env: {},
    });
    const output: Buffer[] = [];
    let outputSize = 0;
    let failed: Error | null = null;
    let timedOut = false;
    const killGroup = () => {
      if (child.pid) {
        try { process.kill(-child.pid, "SIGKILL"); }
        catch { try { child.kill("SIGKILL"); } catch { /* process already gone */ } }
      }
    };
    const timer = setTimeout(() => { timedOut = true; killGroup(); }, timeoutMs);
    const collect = (chunk: Buffer, stdout: boolean) => {
      outputSize += chunk.length;
      if (outputSize > maxOutputBytes) { failed = new Error("output ceiling exceeded"); killGroup(); return; }
      if (stdout) output.push(chunk);
    };
    child.stdout.on("data", chunk => collect(chunk as Buffer, true));
    child.stderr.on("data", chunk => collect(chunk as Buffer, false));
    child.stdin.on("error", () => { /* close status is authoritative */ });
    child.once("error", error => { failed = error; });
    child.once("close", (code, signal) => {
      clearTimeout(timer);
      // A successful parent can leave same-group descendants alive. The
      // observation owns that group even after the direct child exits.
      killGroup();
      if (timedOut) reject(new NativeExecutionFailure("timeout"));
      else if (failed) reject(new NativeExecutionFailure(failed.message === "output ceiling exceeded" ? "output-limit" : "spawn-error"));
      else if (code !== 0 || signal !== null) reject(new NativeExecutionFailure("nonzero-exit"));
      else resolve(Buffer.concat(output));
    });
    child.stdin.end(input);
  });
}

function selectedCases(obligations: JsonObject, finalized: JsonObject) {
  if (!Array.isArray(obligations.obligations)) fail("APPLICATION_NATIVE_CASES", "$obligation_set", "missing selected cases");
  const cases = (obligations.obligations as unknown[]).map((raw: unknown, index: number) => {
    const row = object(raw, `$obligation_set/obligations/${index}`);
    if (typeof row.obligation_id !== "string" || typeof row.case_id !== "string") {
      fail("APPLICATION_NATIVE_CASES", `$obligation_set/obligations/${index}`, "case identity is missing");
    }
    const normalizedInputs = object(row.normalized_inputs, `$obligation_set/obligations/${index}/normalized_inputs`);
    return { obligation_id: row.obligation_id as string, case_id: row.case_id as string, normalized_inputs: normalizedInputs,
      kind: row.kind, case_class: row.case_class, expected_relation_or_oracle: row.expected_relation_or_oracle };
  }).sort((left, right) => left.case_id.localeCompare(right.case_id));
  const caseDomain = cases.map(({ obligation_id, case_id, kind, case_class }) => ({ obligation_id, case_id, kind, case_class }));
  const witnesses = cases.map(({ obligation_id, case_id, normalized_inputs, expected_relation_or_oracle }) =>
    ({ obligation_id, case_id, normalized_inputs, expected_relation_or_oracle }));
  if (!same(cases.map(item => item.case_id), finalized.selected_case_ids) ||
      cases.length !== finalized.selected_case_count || sha(canonical(caseDomain)) !== finalized.case_domain_sha256 ||
      sha(canonical(witnesses)) !== finalized.witness_input_set_sha256) {
    fail("APPLICATION_NATIVE_CASES", "$obligation_set", "selected cases or witness digest differ from the finalized request");
  }
  return cases;
}

async function prepare(input: NativeCaseObservationInput, sources: ReadonlyMap<string, Buffer>) {
  const root = exactKeys(input, ["opt_in", "selection", "finalized_request_ref", "local_adapter_ref", "local_executable_ref"], "$input");
  if (root.opt_in !== "trusted-local-native-case-observation") {
    fail("APPLICATION_NATIVE_OPT_IN", "$input/opt_in", "trusted local execution requires exact opt-in");
  }
  const before = snapshot(sources);
  const inputBefore = canonical(input);
  const finalized = finalizeApplicationExecutionRequest(root.selection, sources);
  const request = exactBytes(root.finalized_request_ref, sources, "$input/finalized_request_ref");
  if (!same(parseJson(request.bytes, "$request"), finalized)) {
    fail("APPLICATION_NATIVE_REQUEST", "$request", "request bytes differ from current post-TDE finalization");
  }
  const adapter = exactBytes(root.local_adapter_ref, sources, "$input/local_adapter_ref");
  const executable = await assertExecutableCurrent(root.local_executable_ref);
  const obligationSet = exactBytes(finalized.obligation_set_ref, sources, "$request/obligation_set_ref");
  const cases = selectedCases(parseJson(obligationSet.bytes, "$obligation_set"), finalized);
  if (cases.length > LOCAL_MAX_CASES || adapter.bytes.length > LOCAL_MAX_ADAPTER_BYTES) {
    fail("APPLICATION_NATIVE_LOCAL_BOUND", "$input", "case count or local adapter exceeds this diagnostic's bound");
  }
  const policy = exactKeys(finalized.execution_policy, ["timeout_ms", "memory_ceiling_bytes", "max_output_bytes", "network", "working_directory", "environment_allowlist"], "$request/execution_policy");
  if (!Number.isSafeInteger(policy.timeout_ms) || (policy.timeout_ms as number) < 1 ||
      (policy.timeout_ms as number) > LOCAL_MAX_TIMEOUT_MS ||
      !Number.isSafeInteger(policy.max_output_bytes) || (policy.max_output_bytes as number) < 1 ||
      (policy.max_output_bytes as number) > LOCAL_MAX_OUTPUT_BYTES ||
      typeof policy.working_directory !== "string" || !boundedRelativePath(policy.working_directory)) {
    fail("APPLICATION_NATIVE_POLICY", "$request/execution_policy", "invalid bounded local execution policy");
  }
  return { before, inputBefore, finalized, request, adapter, executable, cases, timeoutMs: policy.timeout_ms as number,
    maxOutputBytes: policy.max_output_bytes as number, workingDirectory: policy.working_directory as string };
}

const assertInputUnchanged = (input: NativeCaseObservationInput, before: string): void => {
  if (canonical(input) !== before) fail("APPLICATION_NATIVE_INPUT_MUTATED", "$input", "input or reference object changed during local execution");
};

/** Executes each exact case through a trusted local stdin/JSON adapter.
 * Its deterministic receipt is deliberately ineligible for EVF satisfaction. */
export async function observeApplicationNativeCases(input: NativeCaseObservationInput, sources: ReadonlyMap<string, Buffer>) {
  const prepared = await prepare(input, sources);
  const directory = await mkdtemp(join(tmpdir(), "alch-native-case-"));
  try {
    const cwd = join(directory, prepared.workingDirectory);
    await mkdir(cwd, { recursive: true, mode: 0o700 });
    const adapterPath = join(directory, "adapter");
    await writeFile(adapterPath, prepared.adapter.bytes, { mode: 0o700, flag: "wx" });
    if (!(await readFile(adapterPath)).equals(prepared.adapter.bytes)) {
      fail("APPLICATION_NATIVE_ADAPTER", "$input/local_adapter_ref", "staged adapter bytes differ");
    }
    const executablePath = join(directory, "executable");
    await copyFile(prepared.executable.path, executablePath);
    await chmod(executablePath, 0o700);
    await assertFileHash(executablePath, prepared.executable);
    const observations = [];
    let failure: { case_id: string; kind: FailureKind } | null = null;
    for (const row of prepared.cases) {
      assertUnchanged(sources, prepared.before);
      assertInputUnchanged(input, prepared.inputBefore);
      const inputBytes = Buffer.from(canonical({ obligation_id: row.obligation_id, case_id: row.case_id,
        normalized_inputs: row.normalized_inputs }));
      let stdout: Buffer;
      try { stdout = await runOne(executablePath, adapterPath, cwd, inputBytes, prepared.timeoutMs, prepared.maxOutputBytes); }
      catch (error) {
        if (!(error instanceof NativeExecutionFailure)) throw error;
        failure = { case_id: row.case_id, kind: error.kind };
        break;
      }
      assertUnchanged(sources, prepared.before);
      assertInputUnchanged(input, prepared.inputBefore);
      let result: JsonObject;
      try {
        result = exactKeys(parseJson(stdout, `$cases/${row.case_id}/stdout`), ["case_id", "native_output"], `$cases/${row.case_id}/stdout`);
        if (result.case_id !== row.case_id) throw new Error("case ID differs");
      } catch {
        failure = { case_id: row.case_id, kind: "malformed-output" };
        break;
      }
      observations.push({ obligation_id: row.obligation_id, case_id: row.case_id,
        witness_input_digest: sha(canonical({ obligation_id: row.obligation_id, case_id: row.case_id,
          normalized_inputs: row.normalized_inputs, expected_relation_or_oracle: row.expected_relation_or_oracle })),
        input_sha256: sha(inputBytes), native_output_sha256: sha(stdout), native_output: result.native_output,
        process_exit_code: 0, normalized_outcome: "unverified" as const });
    }
    assertUnchanged(sources, prepared.before);
    assertInputUnchanged(input, prepared.inputBefore);
    await assertFileHash(executablePath, prepared.executable);
    if (!(await readFile(adapterPath)).equals(prepared.adapter.bytes)) {
      fail("APPLICATION_NATIVE_ADAPTER", "$input/local_adapter_ref", "staged adapter bytes changed");
    }
    await assertExecutableCurrent(prepared.executable);
    const body = { schema_version: "alchlang.native-case-observation/v1-candidate" as const,
      finalized_request_ref: prepared.request.ref, finalized_request_id: prepared.finalized.request_id,
      obligation_set_ref: prepared.finalized.obligation_set_ref, runtime_ref: prepared.finalized.runtime_ref,
      local_adapter_ref: prepared.adapter.ref, local_executable_ref: prepared.executable,
      case_domain_sha256: prepared.finalized.case_domain_sha256,
      witness_input_set_sha256: prepared.finalized.witness_input_set_sha256, observations,
      selected_case_count: prepared.cases.length, observed_case_count: observations.length,
      execution_status: failure === null ? "complete" as const : "incomplete" as const,
      incomplete_case: failure, local_execution_observed: failure === null,
      replay_status: "requires-reexecution" as const, provider_equivalence: "unverified" as const,
      network_enforcement: "unverified" as const, memory_enforcement: "unverified" as const,
      executable_oracle: "unverified" as const, evf_join: "forbidden" as const,
      can_satisfy_obligation: false as const, runtime_guarantees_observed: false as const,
      authority_effect: "none" as const, release_admission: "not-granted" as const,
      residue: [...residue], claim_ceiling: "Trusted-local case output only; no provider, oracle, isolation, EVF or runtime-guarantee claim" };
    return { ...body, receipt_sha256: sha(canonical(body)) };
  } finally {
    await rm(directory, { recursive: true, force: true });
    assertUnchanged(sources, prepared.before);
    assertInputUnchanged(input, prepared.inputBefore);
    await assertExecutableCurrent(prepared.executable);
  }
}

/** Re-execution, not a caller-computed digest, is the receipt's currentness test. */
export async function assertApplicationNativeCasesCurrent(
  input: NativeCaseObservationInput, sources: ReadonlyMap<string, Buffer>, candidate: unknown,
): Promise<void> {
  const replayed = await observeApplicationNativeCases(input, sources);
  if (!same(candidate, replayed)) {
    fail("APPLICATION_NATIVE_REPLAY", "$candidate", "receipt differs from exact re-execution");
  }
}
