import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { lstatSync, readFileSync, readlinkSync, realpathSync, statSync } from "node:fs";
import { isAbsolute } from "node:path";

import { canonicalSfolJson, digestSfolValue } from "../cases/index.js";
import { deriveSelectedSfolClaimCases, type SelectedSfolClaimSources } from "./index.js";
import type { ExactNativeExecutable } from "./native-link.js";

const INPUT_ORDER = ["unique_trusted_authentication_evidence", "unique_complete_route_binding",
  "candidate_command_provenance"] as const;
const CEILING = "replayed local Auth SFOL case observations under a selected bwrap network namespace and RLIMIT_AS virtual-address-space limit; probes are separate from case behavior; no complete network denial, physical-memory ceiling, build provenance, DomainSpec v4 chain, EVF satisfaction or runtime_guarantees_observed" as const;
const PINNED_CLAIM = "AF-ADMIT-AUTHORIZATION-COMMAND-001-SFOL";
const PINNED_AUTH_SOURCES = {
  decision: ["formalization/decisions/AF-ADMIT-AUTHORIZATION-COMMAND-001/sfol-formal-claim-admission-001.json", "c321f051840f56a8cacd5e1b3a29efddc4708f1d438d356a0927237d33199fa5"],
  claim: ["formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/FORMAL-CLAIM-SFOL.v1.json", "50ce8c6d7aa49050345cac5ef192b8485dfc3cfb5541c153e382cd4c4d2bd37e"],
  module: ["formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/SFOL-MODULE.v1.json", "e9ba011a399d61e5310d1863306681c0c9907bcfb95ce85f53107dd18ee28742"],
  clause_manifest: ["formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/SFOL-CLAUSE-ADMISSION-MANIFEST.v1.json", "f3a8c7ca8598d3eccaef749df376537c7c902c5f42bc8101694dcffdf06a5431"],
} as const;
const PROBE_SCRIPT = `import errno,json,os,resource,socket,sys\n` +
  `limit=int(__import__('sys').argv[1])\n` +
  `host_netns=sys.argv[2]\n` +
  `netns=os.readlink('/proc/self/ns/net')\n` +
  `soft,hard=resource.getrlimit(resource.RLIMIT_AS)\n` +
  `names=sorted(name for _,name in socket.if_nameindex())\n` +
  `routes=open('/proc/net/route',encoding='ascii').read().splitlines()[1:]\n` +
  `default=any(line.split()[1]=='00000000' for line in routes if len(line.split())>1)\n` +
  `if netns==host_netns or names!=['lo'] or default: raise RuntimeError('network namespace not isolated')\n` +
  `network_errno=None\n` +
  `try: socket.socket().connect(('192.0.2.1',9))\n` +
  `except OSError as error: network_errno=error.errno\n` +
  `failed=False\n` +
  `try: bytearray(limit+1048576)\n` +
  `except MemoryError: failed=True\n` +
  `print(json.dumps({'netns':netns,'interfaces':names,'default_route':default,'network_errno':network_errno,'as_soft':soft,'as_hard':hard,'allocation_failed':failed},sort_keys=True))\n`;

export type SelectedSfolPolicyExecution = Readonly<{
  executable: ExactNativeExecutable;
  bwrap: ExactNativeExecutable;
  prlimit: ExactNativeExecutable;
  probe_python: ExactNativeExecutable;
  address_space_limit_bytes: number;
  probe_timeout_ms: number;
  probe_max_output_bytes: number;
  timeout_ms: number;
  max_output_bytes: number;
}>;
type ProcessResult = Readonly<{
  exit_code: number | null;
  signal: NodeJS.Signals | null;
  timed_out: boolean;
  output_limit_exceeded: boolean;
  stdout_base64: string;
  stderr_base64: string;
}>;
export type SelectedSfolPolicyObservation = ProcessResult & Readonly<{
  case_id: string;
  witness_input_digest: string;
  argv: readonly string[];
  observed_value: boolean | null;
  expected_value: boolean;
  comparison: "match" | "mismatch" | "incomplete";
}>;
export type SelectedSfolPolicyLink = Readonly<{
  schema_version: "tde.selected-sfol-native-policy-link/v3-candidate";
  case_set_digest: string;
  execution: SelectedSfolPolicyExecution;
  launcher_probe: Readonly<{
    network_namespace_separate: true;
    interfaces: readonly ["lo"];
    default_route: false;
    network_attempt_errno: 101;
    address_space_soft_limit_bytes: number;
    address_space_hard_limit_bytes: number;
    over_limit_allocation_failed: true;
  }>;
  observations: readonly SelectedSfolPolicyObservation[];
  status: "matched" | "not-matched";
  execution_control_scope: "network-namespace-and-virtual-address-space-only";
  f5_acceptance_item: "runtime_guarantees_observed";
  f5_eligibility: "blocked-missing-domainspec-v4-chain-and-finalized-request-binding";
  evf_join: "forbidden";
  can_satisfy_obligation: false;
  authority_effect: "none";
  claim_ceiling: typeof CEILING;
  link_digest: string;
}>;

function exactFile(ref: ExactNativeExecutable): string {
  if (!ref || Object.keys(ref).sort().join(",") !== "path,sha256,size_bytes" ||
      typeof ref.path !== "string" || !isAbsolute(ref.path) ||
      typeof ref.sha256 !== "string" || !/^[a-f0-9]{64}$/.test(ref.sha256) ||
      !Number.isSafeInteger(ref.size_bytes) || ref.size_bytes < 1 || ref.size_bytes > 64 * 1024 * 1024)
    throw new Error("SFOL_POLICY_EXACT_REF_INVALID");
  const stat = lstatSync(ref.path);
  if (!stat.isFile() || stat.isSymbolicLink() || realpathSync(ref.path) !== ref.path)
    throw new Error("SFOL_POLICY_EXACT_REF_INVALID");
  if (stat.size !== ref.size_bytes || stat.size > 64 * 1024 * 1024)
    throw new Error("SFOL_POLICY_EXACT_REF_DRIFT");
  const before = statSync(ref.path);
  if (before.size !== ref.size_bytes || before.dev !== stat.dev || before.ino !== stat.ino ||
      before.mtimeMs !== stat.mtimeMs)
    throw new Error("SFOL_POLICY_EXACT_REF_DRIFT");
  const bytes = readFileSync(ref.path);
  const after = statSync(ref.path);
  if (bytes.length !== ref.size_bytes || before.ino !== after.ino || before.dev !== after.dev ||
      before.mtimeMs !== after.mtimeMs || before.size !== after.size ||
      createHash("sha256").update(bytes).digest("hex") !== ref.sha256)
    throw new Error("SFOL_POLICY_EXACT_REF_DRIFT");
  return ref.path;
}
function validate(root: string, policy: SelectedSfolPolicyExecution): void {
  if (process.platform !== "linux" || realpathSync(root) !== root ||
      !policy || Object.keys(policy).sort().join(",") !==
        "address_space_limit_bytes,bwrap,executable,max_output_bytes,prlimit,probe_max_output_bytes,probe_python,probe_timeout_ms,timeout_ms" ||
      !Number.isSafeInteger(policy.address_space_limit_bytes) || policy.address_space_limit_bytes < 64 * 1024 * 1024 ||
      policy.address_space_limit_bytes > 512 * 1024 * 1024 ||
      !Number.isSafeInteger(policy.probe_timeout_ms) || policy.probe_timeout_ms < 1 || policy.probe_timeout_ms > 30_000 ||
      !Number.isSafeInteger(policy.probe_max_output_bytes) || policy.probe_max_output_bytes < 1 || policy.probe_max_output_bytes > 64 * 1024 ||
      !Number.isSafeInteger(policy.timeout_ms) || policy.timeout_ms < 1 || policy.timeout_ms > 30_000 ||
      !Number.isSafeInteger(policy.max_output_bytes) || policy.max_output_bytes < 1 || policy.max_output_bytes > 64 * 1024)
    throw new Error("SFOL_POLICY_EXECUTION_INVALID");
  for (const ref of [policy.executable, policy.bwrap, policy.prlimit, policy.probe_python]) exactFile(ref);
  if (policy.bwrap.path !== "/usr/bin/bwrap" || policy.prlimit.path !== "/usr/bin/prlimit" ||
      policy.probe_python.path !== realpathSync("/usr/bin/python3"))
    throw new Error("SFOL_POLICY_LAUNCHER_PATH_INVALID");
}
function requirePinnedAuthSelection(selection: SelectedSfolClaimSources): void {
  for (const name of Object.keys(PINNED_AUTH_SOURCES) as (keyof typeof PINNED_AUTH_SOURCES)[]) {
    const expected = PINNED_AUTH_SOURCES[name];
    const actual = selection?.[name];
    if (actual?.path !== expected[0] || actual.sha256 !== expected[1])
      throw new Error(`SFOL_POLICY_AUTH_SOURCE_NOT_PINNED:${name}`);
  }
}
function launcherArgv(root: string, policy: SelectedSfolPolicyExecution, program: string, args: readonly string[],
  selectedCase: boolean): string[] {
  const selectedMount = selectedCase
    ? ["--ro-bind", policy.executable.path, policy.executable.path] : [];
  return [`--as=${policy.address_space_limit_bytes}`, "--", policy.bwrap.path,
    "--unshare-net", "--die-with-parent", "--ro-bind", "/usr", "/usr",
    "--ro-bind", "/bin", "/bin", "--ro-bind", "/lib", "/lib",
    "--ro-bind", "/lib64", "/lib64", "--ro-bind", root, root,
    "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp",
    // Mount only the selected file after private /tmp: its parent may be /tmp
    // itself, and a directory bind would expose unselected host files.
    ...selectedMount,
    "--chdir", root, "--", program, ...args];
}
async function run(root: string, policy: SelectedSfolPolicyExecution,
  program: string, args: readonly string[], timeoutMs: number, maxOutputBytes: number,
  selectedCase: boolean): Promise<ProcessResult> {
  return await new Promise((resolve, reject) => {
    const child = spawn(policy.prlimit.path, launcherArgv(root, policy, program, args, selectedCase), {
      cwd: root, shell: false, detached: true, stdio: ["ignore", "pipe", "pipe"],
      env: { LANG: "C", LC_ALL: "C", TZ: "UTC" },
    });
    const stdout: Buffer[] = [], stderr: Buffer[] = [];
    let bytes = 0, timedOut = false, outputLimitExceeded = false, settled = false;
    const killGroup = () => {
      if (child.pid) try { process.kill(-child.pid, "SIGKILL"); }
      catch (error) { if ((error as NodeJS.ErrnoException).code !== "ESRCH") child.kill("SIGKILL"); }
    };
    const timer = setTimeout(() => { timedOut = true; killGroup(); }, timeoutMs);
    const collect = (target: Buffer[]) => (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > maxOutputBytes) { outputLimitExceeded = true; killGroup(); }
      else target.push(chunk);
    };
    child.stdout.on("data", collect(stdout));
    child.stderr.on("data", collect(stderr));
    child.once("error", error => { if (!settled) { settled = true; clearTimeout(timer); killGroup(); reject(error); } });
    child.once("close", (exit_code, signal) => {
      if (settled) return;
      settled = true; clearTimeout(timer); killGroup();
      resolve({ exit_code, signal, timed_out: timedOut, output_limit_exceeded: outputLimitExceeded,
        stdout_base64: Buffer.concat(stdout).toString("base64"), stderr_base64: Buffer.concat(stderr).toString("base64") });
    });
  });
}
async function probe(root: string, policy: SelectedSfolPolicyExecution): Promise<SelectedSfolPolicyLink["launcher_probe"]> {
  const hostNetns = readlinkSync("/proc/self/ns/net");
  const result = await run(root, policy, policy.probe_python.path,
    ["-c", PROBE_SCRIPT, String(policy.address_space_limit_bytes), hostNetns],
    policy.probe_timeout_ms, policy.probe_max_output_bytes, false);
  if (result.timed_out) throw new Error("SFOL_POLICY_PROBE_FAILED:timeout");
  if (result.output_limit_exceeded) throw new Error("SFOL_POLICY_PROBE_FAILED:output-limit");
  if (result.signal !== null) throw new Error("SFOL_POLICY_PROBE_FAILED:signal");
  if (result.exit_code !== 0) throw new Error("SFOL_POLICY_PROBE_FAILED:exit");
  if (result.stderr_base64 !== "") throw new Error("SFOL_POLICY_PROBE_FAILED:stderr");
  let value: unknown;
  try { value = JSON.parse(Buffer.from(result.stdout_base64, "base64").toString("utf8")); }
  catch { throw new Error("SFOL_POLICY_PROBE_FAILED:invalid-output"); }
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error("SFOL_POLICY_PROBE_FAILED:invalid-output");
  const row = value as Record<string, unknown>;
  if (Object.keys(row).sort().join(",") !== "allocation_failed,as_hard,as_soft,default_route,interfaces,netns,network_errno" ||
      typeof row.netns !== "string" || !/^net:\[[0-9]+\]$/.test(row.netns) || row.netns === hostNetns ||
      canonicalSfolJson(row.interfaces) !== '["lo"]' || row.default_route !== false ||
      row.network_errno !== 101 || row.as_soft !== policy.address_space_limit_bytes ||
      row.as_hard !== policy.address_space_limit_bytes || row.allocation_failed !== true)
    throw new Error("SFOL_POLICY_PROBE_FAILED:invalid-output");
  return { network_namespace_separate: true, interfaces: ["lo"], default_route: false, network_attempt_errno: 101,
    address_space_soft_limit_bytes: policy.address_space_limit_bytes,
    address_space_hard_limit_bytes: policy.address_space_limit_bytes, over_limit_allocation_failed: true };
}

export async function observeSelectedSfolNativePolicy(root: string, selection: SelectedSfolClaimSources,
  execution: SelectedSfolPolicyExecution): Promise<SelectedSfolPolicyLink> {
  requirePinnedAuthSelection(selection);
  validate(root, execution);
  const source = deriveSelectedSfolClaimCases(root, selection);
  if (source.claim_id !== PINNED_CLAIM || source.cases.length !== 8 || source.oracles.length !== 8)
    throw new Error("SFOL_POLICY_CLAIM_SCOPE_INVALID");
  const selectedExecution = canonicalSfolJson(execution);
  const launcher_probe = await probe(root, execution);
  const observations: SelectedSfolPolicyObservation[] = [];
  for (const derived of source.cases) {
    const oracle = source.oracles.find(item => item.case_id === derived.case_id);
    if (!oracle || oracle.expected_value.tag !== "boolean") throw new Error("SFOL_POLICY_ORACLE_MISSING");
    const argv = INPUT_ORDER.map(name => {
      const value = derived.inputs[name];
      if (value?.tag !== "boolean") throw new Error("SFOL_POLICY_INPUT_INVALID");
      return String(value.value);
    });
    const raw = await run(root, execution, execution.executable.path, argv,
      execution.timeout_ms, execution.max_output_bytes, true);
    const stdout = Buffer.from(raw.stdout_base64, "base64").toString("utf8");
    const observed = !raw.timed_out && !raw.output_limit_exceeded && raw.exit_code === 0 &&
      raw.stderr_base64 === "" && (stdout === "true\n" || stdout === "false\n") ? stdout === "true\n" : null;
    const comparison = observed === null ? "incomplete" as const :
      observed === oracle.expected_value.value ? "match" as const : "mismatch" as const;
    observations.push({ case_id: derived.case_id, witness_input_digest: oracle.witness_input_digest,
      argv, ...raw, observed_value: observed, expected_value: oracle.expected_value.value, comparison });
    if (comparison === "incomplete") break;
  }
  if (canonicalSfolJson(execution) !== selectedExecution ||
      [execution.executable, execution.bwrap, execution.prlimit, execution.probe_python].some(ref => exactFile(ref) !== ref.path) ||
      deriveSelectedSfolClaimCases(root, selection).case_set_digest !== source.case_set_digest)
    throw new Error("SFOL_POLICY_SELECTED_SOURCE_DRIFT");
  const unsigned = { schema_version: "tde.selected-sfol-native-policy-link/v3-candidate" as const,
    case_set_digest: source.case_set_digest, execution, launcher_probe, observations,
    status: observations.length === 8 && observations.every(item => item.comparison === "match")
      ? "matched" as const : "not-matched" as const,
    execution_control_scope: "network-namespace-and-virtual-address-space-only" as const,
    f5_acceptance_item: "runtime_guarantees_observed" as const,
    f5_eligibility: "blocked-missing-domainspec-v4-chain-and-finalized-request-binding" as const,
    evf_join: "forbidden" as const, can_satisfy_obligation: false as const,
    authority_effect: "none" as const, claim_ceiling: CEILING };
  return { ...unsigned, link_digest: digestSfolValue(unsigned) };
}

export async function replaySelectedSfolNativePolicy(root: string, selection: SelectedSfolClaimSources,
  execution: SelectedSfolPolicyExecution, held: SelectedSfolPolicyLink): Promise<SelectedSfolPolicyLink> {
  if (!held || typeof held !== "object" || held.schema_version !== "tde.selected-sfol-native-policy-link/v3-candidate" ||
      held.status !== "matched" || held.evf_join !== "forbidden" || held.can_satisfy_obligation !== false ||
      held.authority_effect !== "none" || held.claim_ceiling !== CEILING ||
      held.f5_acceptance_item !== "runtime_guarantees_observed" ||
      held.f5_eligibility !== "blocked-missing-domainspec-v4-chain-and-finalized-request-binding" ||
      held.execution_control_scope !== "network-namespace-and-virtual-address-space-only" ||
      canonicalSfolJson(held.execution) !== canonicalSfolJson(execution))
    throw new Error("SFOL_POLICY_REPLAY_MISMATCH");
  const { link_digest: _digest, ...unsigned } = held;
  if (held.link_digest !== digestSfolValue(unsigned)) throw new Error("SFOL_POLICY_REPLAY_MISMATCH");
  const current = await observeSelectedSfolNativePolicy(root, selection, execution);
  if (current.status !== "matched" || canonicalSfolJson(current) !== canonicalSfolJson(held))
    throw new Error("SFOL_POLICY_REPLAY_MISMATCH");
  return current;
}
