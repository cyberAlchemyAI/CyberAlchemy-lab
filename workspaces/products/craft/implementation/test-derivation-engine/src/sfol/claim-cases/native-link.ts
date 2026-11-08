import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { lstatSync, readFileSync, realpathSync, statSync } from "node:fs";
import { isAbsolute } from "node:path";

import { canonicalSfolJson, digestSfolValue } from "../cases/index.js";
import { deriveSelectedSfolClaimCases, type SelectedSfolClaimSources } from "./index.js";

const CLAIM_ID = "AF-ADMIT-AUTHORIZATION-COMMAND-001-SFOL";
const INPUT_ORDER = ["unique_trusted_authentication_evidence", "unique_complete_route_binding",
  "candidate_command_provenance"] as const;
const CEILING = "replayed trusted-local exact-selected Auth SFOL-to-Rust Boolean observations only; no historical admission authentication, binary-build provenance, isolation, DomainSpec v4 neutral set, EVF satisfaction or runtime guarantee" as const;
const PINNED_AUTH_SOURCES = {
  decision: ["formalization/decisions/AF-ADMIT-AUTHORIZATION-COMMAND-001/sfol-formal-claim-admission-001.json", "c321f051840f56a8cacd5e1b3a29efddc4708f1d438d356a0927237d33199fa5"],
  claim: ["formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/FORMAL-CLAIM-SFOL.v1.json", "50ce8c6d7aa49050345cac5ef192b8485dfc3cfb5541c153e382cd4c4d2bd37e"],
  module: ["formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/SFOL-MODULE.v1.json", "e9ba011a399d61e5310d1863306681c0c9907bcfb95ce85f53107dd18ee28742"],
  clause_manifest: ["formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/SFOL-CLAUSE-ADMISSION-MANIFEST.v1.json", "f3a8c7ca8598d3eccaef749df376537c7c902c5f42bc8101694dcffdf06a5431"],
} as const;

export type ExactNativeExecutable = Readonly<{ path: string; sha256: string; size_bytes: number }>;
export type SelectedSfolNativeExecution = Readonly<{
  executable: ExactNativeExecutable;
  timeout_ms: number;
  max_output_bytes: number;
}>;
export type SelectedSfolNativeObservation = Readonly<{
  case_id: string;
  witness_input_digest: string;
  argv: readonly string[];
  exit_code: number | null;
  signal: NodeJS.Signals | null;
  timed_out: boolean;
  output_limit_exceeded: boolean;
  stdout_base64: string;
  stderr_base64: string;
  observed_value: boolean | null;
  expected_value: boolean;
  comparison: "match" | "incomplete" | "mismatch";
}>;
export type SelectedSfolNativeLink = Readonly<{
  schema_version: "tde.selected-sfol-native-link/v1-candidate";
  case_set_digest: string;
  execution: SelectedSfolNativeExecution;
  observations: readonly SelectedSfolNativeObservation[];
  status: "matched" | "not-matched";
  mode: "trusted-local-no-isolation";
  admission_origin_verification: "not-performed";
  proof_context_verification: "not-performed";
  binary_build_provenance: "not-verified";
  f5_eligibility: "blocked-missing-domainspec-v4-chain";
  evf_join: "forbidden";
  can_satisfy_obligation: false;
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
  link_digest: string;
}>;

function selectedExecutable(ref: ExactNativeExecutable): string {
  if (!ref || Object.keys(ref).sort().join(",") !== "path,sha256,size_bytes" ||
      typeof ref.path !== "string" || !isAbsolute(ref.path) ||
      !/^[a-f0-9]{64}$/.test(ref.sha256) || !Number.isSafeInteger(ref.size_bytes) ||
      ref.size_bytes < 1 || ref.size_bytes > 64 * 1024 * 1024)
    throw new Error("SFOL_NATIVE_EXECUTABLE_REF_INVALID");
  const stat = lstatSync(ref.path);
  if (!stat.isFile() || stat.isSymbolicLink() || realpathSync(ref.path) !== ref.path)
    throw new Error("SFOL_NATIVE_EXECUTABLE_NOT_REGULAR");
  const before = statSync(ref.path);
  const bytes = readFileSync(ref.path);
  const after = statSync(ref.path);
  const digest = createHash("sha256").update(bytes).digest("hex");
  if (bytes.length !== ref.size_bytes || before.ino !== after.ino || before.dev !== after.dev ||
      before.mtimeMs !== after.mtimeMs || digest !== ref.sha256)
    throw new Error("SFOL_NATIVE_EXECUTABLE_DRIFT");
  return ref.path;
}

function validateExecution(execution: SelectedSfolNativeExecution): string {
  if (!execution || Object.keys(execution).sort().join(",") !== "executable,max_output_bytes,timeout_ms" ||
      !Number.isSafeInteger(execution.timeout_ms) || execution.timeout_ms < 1 || execution.timeout_ms > 30_000 ||
      !Number.isSafeInteger(execution.max_output_bytes) || execution.max_output_bytes < 1 ||
      execution.max_output_bytes > 64 * 1024)
    throw new Error("SFOL_NATIVE_EXECUTION_POLICY_INVALID");
  if (process.platform !== "linux") throw new Error("SFOL_NATIVE_LINUX_PROCESS_GROUP_REQUIRED");
  return selectedExecutable(execution.executable);
}

function requirePinnedAuthSelection(selection: SelectedSfolClaimSources): void {
  for (const name of Object.keys(PINNED_AUTH_SOURCES) as (keyof typeof PINNED_AUTH_SOURCES)[]) {
    const expected = PINNED_AUTH_SOURCES[name];
    const actual = selection?.[name];
    if (actual?.path !== expected[0] || actual.sha256 !== expected[1])
      throw new Error(`SFOL_NATIVE_AUTH_SOURCE_NOT_PINNED:${name}`);
  }
}

async function invoke(executable: string, argv: readonly string[], root: string,
  policy: SelectedSfolNativeExecution): Promise<Omit<SelectedSfolNativeObservation,
    "case_id" | "witness_input_digest" | "argv" | "observed_value" | "expected_value" | "comparison">> {
  return await new Promise((resolve, reject) => {
    const child = spawn(executable, [...argv], { cwd: root, shell: false, detached: true,
      stdio: ["ignore", "pipe", "pipe"], env: { LANG: "C", LC_ALL: "C", TZ: "UTC" } });
    const stdout: Buffer[] = [], stderr: Buffer[] = [];
    let bytes = 0, timedOut = false, outputLimitExceeded = false, settled = false;
    const killGroup = () => {
      if (child.pid) {
        try { process.kill(-child.pid, "SIGKILL"); }
        catch (error) { if ((error as NodeJS.ErrnoException).code !== "ESRCH") child.kill("SIGKILL"); }
      }
    };
    const timer = setTimeout(() => { timedOut = true; killGroup(); }, policy.timeout_ms);
    const collect = (target: Buffer[]) => (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > policy.max_output_bytes) { outputLimitExceeded = true; killGroup(); }
      else target.push(chunk);
    };
    child.stdout.on("data", collect(stdout));
    child.stderr.on("data", collect(stderr));
    child.once("error", error => {
      if (!settled) { settled = true; clearTimeout(timer); killGroup(); reject(error); }
    });
    child.once("close", (exit_code, signal) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      killGroup();
      resolve({ exit_code, signal, timed_out: timedOut, output_limit_exceeded: outputLimitExceeded,
        stdout_base64: Buffer.concat(stdout).toString("base64"),
        stderr_base64: Buffer.concat(stderr).toString("base64") });
    });
  });
}

/** Recompute cases first, then invoke one selected native executable per case.
 * The executable is independently selected, but its build provenance is not proved. */
export async function observeSelectedSfolNative(root: string, selection: SelectedSfolClaimSources,
  execution: SelectedSfolNativeExecution): Promise<SelectedSfolNativeLink> {
  requirePinnedAuthSelection(selection);
  const source = deriveSelectedSfolClaimCases(root, selection);
  if (source.claim_id !== CLAIM_ID || source.cases.length !== 8 || source.oracles.length !== 8)
    throw new Error("SFOL_NATIVE_CLAIM_SCOPE_INVALID");
  const selectedExecution = canonicalSfolJson(execution);
  const executable = validateExecution(execution);
  const observations: SelectedSfolNativeObservation[] = [];
  for (const derived of source.cases) {
    const oracle = source.oracles.find(item => item.case_id === derived.case_id);
    if (!oracle || oracle.expected_value.tag !== "boolean") throw new Error("SFOL_NATIVE_ORACLE_MISSING");
    const argv = INPUT_ORDER.map(name => {
      const value = derived.inputs[name];
      if (value?.tag !== "boolean") throw new Error("SFOL_NATIVE_INPUT_NOT_BOOLEAN");
      return String(value.value);
    });
    const raw = await invoke(executable, argv, root, execution);
    const stdout = Buffer.from(raw.stdout_base64, "base64").toString("utf8");
    const observed = !raw.timed_out && !raw.output_limit_exceeded && raw.exit_code === 0 &&
      raw.stderr_base64 === "" && (stdout === "true\n" || stdout === "false\n")
      ? stdout === "true\n" : null;
    const comparison = observed === null ? "incomplete" as const :
      observed === oracle.expected_value.value ? "match" as const : "mismatch" as const;
    observations.push({ case_id: derived.case_id, witness_input_digest: oracle.witness_input_digest,
      argv, ...raw, observed_value: observed, expected_value: oracle.expected_value.value, comparison });
    if (comparison === "incomplete") break;
  }
  if (canonicalSfolJson(execution) !== selectedExecution || selectedExecutable(execution.executable) !== executable ||
      deriveSelectedSfolClaimCases(root, selection).case_set_digest !== source.case_set_digest)
    throw new Error("SFOL_NATIVE_SELECTED_SOURCE_DRIFT");
  const unsigned = { schema_version: "tde.selected-sfol-native-link/v1-candidate" as const,
    case_set_digest: source.case_set_digest, execution, observations,
    status: observations.length === source.cases.length && observations.every(item => item.comparison === "match")
      ? "matched" as const : "not-matched" as const,
    mode: "trusted-local-no-isolation" as const, admission_origin_verification: "not-performed" as const,
    proof_context_verification: "not-performed" as const,
    binary_build_provenance: "not-verified" as const,
    f5_eligibility: "blocked-missing-domainspec-v4-chain" as const,
    evf_join: "forbidden" as const, can_satisfy_obligation: false as const,
    authority_effect: "none" as const, claim_ceiling: CEILING };
  return { ...unsigned, link_digest: digestSfolValue(unsigned) };
}

/** Replay re-executes against a separately selected source and native runtime.
 * Matching replay cannot authenticate the historical origin of a held link. */
export async function replaySelectedSfolNative(root: string, selection: SelectedSfolClaimSources,
  execution: SelectedSfolNativeExecution, held: SelectedSfolNativeLink): Promise<SelectedSfolNativeLink> {
  if (!held || typeof held !== "object" ||
      Object.keys(held).sort().join(",") !== ["schema_version", "case_set_digest", "execution", "observations",
        "status", "mode", "admission_origin_verification", "proof_context_verification", "binary_build_provenance",
        "f5_eligibility", "evf_join", "can_satisfy_obligation", "authority_effect", "claim_ceiling", "link_digest"].sort().join(",") ||
      held.schema_version !== "tde.selected-sfol-native-link/v1-candidate" || held.status !== "matched" ||
      held.mode !== "trusted-local-no-isolation" || held.admission_origin_verification !== "not-performed" ||
      held.proof_context_verification !== "not-performed" || held.binary_build_provenance !== "not-verified" ||
      held.f5_eligibility !== "blocked-missing-domainspec-v4-chain" || held.evf_join !== "forbidden" ||
      held.can_satisfy_obligation !== false || held.authority_effect !== "none" || held.claim_ceiling !== CEILING ||
      !held.execution || typeof held.execution !== "object" ||
      canonicalSfolJson(held.execution) !== canonicalSfolJson(execution) ||
      !Array.isArray(held.observations) || held.observations.length !== 8)
    throw new Error("SFOL_NATIVE_LINK_REPLAY_MISMATCH");
  const { link_digest: _linkDigest, ...unsigned } = held;
  if (held.link_digest !== digestSfolValue(unsigned)) throw new Error("SFOL_NATIVE_LINK_REPLAY_MISMATCH");
  requirePinnedAuthSelection(selection);
  const source = deriveSelectedSfolClaimCases(root, selection);
  if (source.case_set_digest !== held.case_set_digest)
    throw new Error("SFOL_NATIVE_LINK_REPLAY_MISMATCH");
  for (const [index, derived] of source.cases.entries()) {
    const row = held.observations[index];
    const oracle = source.oracles[index];
    const argv = INPUT_ORDER.map(name => {
      const value = derived.inputs[name];
      if (value?.tag !== "boolean") throw new Error("SFOL_NATIVE_LINK_REPLAY_MISMATCH");
      return String(value.value);
    });
    if (!row || !oracle || oracle.expected_value.tag !== "boolean" ||
        Object.keys(row).sort().join(",") !== ["case_id", "witness_input_digest", "argv", "exit_code",
          "signal", "timed_out", "output_limit_exceeded", "stdout_base64", "stderr_base64",
          "observed_value", "expected_value", "comparison"].sort().join(",") ||
        row.case_id !== derived.case_id || row.witness_input_digest !== oracle.witness_input_digest ||
        canonicalSfolJson(row.argv) !== canonicalSfolJson(argv) ||
        row.expected_value !== oracle.expected_value.value || row.observed_value !== oracle.expected_value.value ||
        row.comparison !== "match" || row.exit_code !== 0 || row.signal !== null ||
        row.timed_out || row.output_limit_exceeded || row.stderr_base64 !== "" ||
        Buffer.from(row.stdout_base64, "base64").toString("utf8") !== `${oracle.expected_value.value}\n`)
      throw new Error("SFOL_NATIVE_LINK_REPLAY_MISMATCH");
  }
  const current = await observeSelectedSfolNative(root, selection, execution);
  if (current.status !== "matched" || canonicalSfolJson(current) !== canonicalSfolJson(held))
    throw new Error("SFOL_NATIVE_LINK_REPLAY_MISMATCH");
  return current;
}
