import { spawn } from "node:child_process";
import { lstat, mkdir, readFile, realpath, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type {
  FactoryNodeSemanticResultV1,
  FactoryUpstreamResultV1,
} from "../contracts/factory-node-provider-v1.js";
import type {
  FactoryRunLockV1,
  LockedFactoryNodeV1,
  LockedFactoryRefV1,
} from "../contracts/factory-run-lock-v1.js";
import { decodeProofEvidenceV1 } from
  "../../kernel/evidence/recompute-proof-accounting.js";
import {
  canonicalJson,
  exactKeys,
  fail,
  isRecord,
  json,
  safeRelativePath,
  sha256,
} from "../shared/canonical.js";
import { getFactoryNodeProviderV1 } from "../registry/factory-node-registry-v1.js";
import {
  providerSelectorEnvironmentKeysV1,
  resolveLockedProviderExecutionIdentityV1,
} from "../resolution/resolve-provider-execution-context.js";

const here = dirname(fileURLToPath(import.meta.url));
const implementationRoot = resolve(here, "../../..");
const repositoryRoot = resolve(implementationRoot, "../../..");
const childEntry = resolve(here, "replay-child.ts");
const SHA256 = /^[a-f0-9]{64}$/u;

export type FactoryReplayKindV1 = "same-oracle-deterministic";

type LockedComponentIdentityV1 = Readonly<{
  path: string;
  sha256: string;
  byte_length: number;
}>;

type ChildProtocolPolicyV1 = Readonly<{
  timeout_ms: number;
  output_limit_bytes: number;
  termination_grace_ms: number;
}>;

type ChildProtocolFailure = Error & Readonly<{
  code: string;
  detail: string | null;
  child_pid: number | null;
}>;

type LockedExecutionIdentityV1 = Readonly<{
  provider_identity_sha256: string;
  component_identity_sha256: string;
  runtime_material_identity_sha256: string;
  execution_identity_sha256: string;
  execution_timeout_ms: number;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const childFailure = (
  code: string,
  detail: string | undefined,
  childPid: number | undefined,
): never => {
  throw Object.assign(
    new Error(detail === undefined ? code : `${code}:${detail}`),
    { code, detail: detail ?? null, child_pid: childPid ?? null },
  ) as ChildProtocolFailure;
};

const normalizeComponents = (
  refs: readonly Pick<LockedFactoryRefV1, "path" | "sha256" | "byte_length">[],
): readonly LockedComponentIdentityV1[] => Object.freeze(refs
  .map(({ path, sha256: digest, byte_length: byteLength }) => Object.freeze({
    path,
    sha256: digest,
    byte_length: byteLength,
  }))
  .sort((left, right) => compareUtf8(left.path, right.path)));

export const lockedComponentSetSha256 = (
  refs: readonly Pick<LockedFactoryRefV1, "path" | "sha256" | "byte_length">[],
): string => sha256(canonicalJson(normalizeComponents(refs)));

export const verifyLockedComponentSet = async (input: Readonly<{
  repositoryRoot: string;
  refs: readonly LockedFactoryRefV1[];
}>): Promise<readonly LockedComponentIdentityV1[]> => {
  const root = await realpath(input.repositoryRoot);
  const paths = input.refs.map(({ path }) => path);
  if (new Set(paths).size !== paths.length || paths.some((path) => !safeRelativePath(path))) {
    fail("FACTORY_REPLAY_COMPONENT_SET_INVALID");
  }
  const observed = await Promise.all(input.refs.map(async (ref) => {
    const target = resolve(root, ref.path);
    if (!target.startsWith(`${root}/`)) fail("FACTORY_REPLAY_COMPONENT_SET_INVALID");
    const stat = await lstat(target).catch(() =>
      fail("FACTORY_REPLAY_COMPONENT_MISSING", ref.path));
    if (!stat.isFile() || stat.isSymbolicLink()) {
      fail("FACTORY_REPLAY_COMPONENT_INVALID", ref.path);
    }
    const owned = await realpath(target);
    if (!owned.startsWith(`${root}/`)) fail("FACTORY_REPLAY_COMPONENT_INVALID", ref.path);
    const bytes = await readFile(owned);
    if (bytes.byteLength !== ref.byte_length || sha256(bytes) !== ref.sha256) {
      fail("FACTORY_REPLAY_COMPONENT_TAMPERED", ref.path);
    }
    return Object.freeze({
      path: ref.path,
      sha256: ref.sha256,
      byte_length: ref.byte_length,
    });
  }));
  return normalizeComponents(observed);
};

export const runChildJsonProtocol = async (input: Readonly<{
  executable: string;
  args: readonly string[];
  cwd: string;
  environment: NodeJS.ProcessEnv;
  policy: ChildProtocolPolicyV1;
  nodeId: string;
  resultPath?: string;
}>): Promise<Readonly<{
  rendered: string;
  child_pid: number;
  stdout_bytes: number;
  stderr_bytes: number;
  protocol_bytes: number;
}>> => {
  if (!Number.isInteger(input.policy.timeout_ms) || input.policy.timeout_ms <= 0 ||
      !Number.isInteger(input.policy.output_limit_bytes) ||
      input.policy.output_limit_bytes <= 0 ||
      !Number.isInteger(input.policy.termination_grace_ms) ||
      input.policy.termination_grace_ms < 0) {
    fail("FACTORY_REPLAY_POLICY_INVALID", input.nodeId);
  }
  const child = spawn(input.executable, [...input.args], {
    cwd: input.cwd,
    env: input.environment,
    shell: false,
    stdio: ["ignore", "pipe", "pipe"],
  });
  const childPid = child.pid;
  const stdout: Buffer[] = [];
  const stderr: Buffer[] = [];
  let stdoutBytes = 0;
  let stderrBytes = 0;
  let terminationCause: "output-limit" | "timeout" | null = null;
  const stopForOutputLimit = (): void => {
    if (terminationCause !== null) return;
    terminationCause = "output-limit";
    child.kill("SIGKILL");
  };
  const capture = (target: Buffer[], chunk: Buffer, stream: "stdout" | "stderr"): void => {
    if (stream === "stdout") stdoutBytes += chunk.byteLength;
    else stderrBytes += chunk.byteLength;
    if (stdoutBytes + stderrBytes > input.policy.output_limit_bytes) {
      stopForOutputLimit();
      return;
    }
    target.push(Buffer.from(chunk));
  };
  child.stdout.on("data", (chunk: Buffer) => capture(stdout, chunk, "stdout"));
  child.stderr.on("data", (chunk: Buffer) => capture(stderr, chunk, "stderr"));

  let escalationTimer: NodeJS.Timeout | undefined;
  let spawnError: Error | undefined;
  child.once("error", (error) => {
    spawnError = error;
  });
  const inspectResultSize = async (): Promise<void> => {
    if (input.resultPath === undefined || terminationCause !== null) return;
    const stat = await lstat(input.resultPath).catch(() => undefined);
    if (stat !== undefined && stat.size + stdoutBytes + stderrBytes >
        input.policy.output_limit_bytes) {
      stopForOutputLimit();
    }
  };
  let resultInspection: Promise<void> | undefined;
  const scheduleResultInspection = (): void => {
    if (resultInspection !== undefined) return;
    resultInspection = inspectResultSize().finally(() => {
      resultInspection = undefined;
    });
  };
  const resultMonitor = input.resultPath === undefined ? undefined :
    setInterval(scheduleResultInspection, 100);
  resultMonitor?.unref();
  const timeoutTimer = setTimeout(() => {
    if (terminationCause !== null) return;
    terminationCause = "timeout";
    child.kill("SIGTERM");
    escalationTimer = setTimeout(() => {
      child.kill("SIGKILL");
    }, input.policy.termination_grace_ms);
    escalationTimer.unref();
  }, input.policy.timeout_ms);

  const completion = await new Promise<Readonly<{
    code: number | null;
    signal: NodeJS.Signals | null;
  }>>((accept) => child.once("close", (code, signal) => accept({ code, signal })));
  clearTimeout(timeoutTimer);
  if (escalationTimer !== undefined) clearTimeout(escalationTimer);
  if (resultMonitor !== undefined) clearInterval(resultMonitor);
  if (resultInspection !== undefined) await resultInspection;
  await inspectResultSize();

  if (terminationCause === "output-limit") {
    childFailure("FACTORY_REPLAY_OUTPUT_LIMIT", input.nodeId, childPid);
  }
  if (terminationCause === "timeout") {
    childFailure("FACTORY_REPLAY_TIMEOUT", input.nodeId, childPid);
  }
  if (spawnError !== undefined || childPid === undefined) {
    return childFailure(
      "FACTORY_REPLAY_SPAWN_FAILED",
      spawnError?.message ?? input.nodeId,
      childPid,
    );
  }
  if (completion.code !== 0) {
    const detail = Buffer.concat(stderr).toString("utf8").trim() ||
      Buffer.concat(stdout).toString("utf8").trim() ||
      `${completion.signal ?? completion.code}`;
    childFailure("FACTORY_REPLAY_CHILD_FAILED", detail.slice(0, 4096), childPid);
  }
  let rendered = Buffer.concat(stdout).toString("utf8");
  let protocolBytes = stdoutBytes;
  if (input.resultPath !== undefined) {
    const stat = await lstat(input.resultPath).catch(() =>
      childFailure("FACTORY_REPLAY_OUTPUT_INVALID", "result-missing", childPid));
    if (!stat.isFile() || stat.isSymbolicLink()) {
      childFailure("FACTORY_REPLAY_OUTPUT_INVALID", "result-file", childPid);
    }
    const bytes = await readFile(input.resultPath);
    protocolBytes = bytes.byteLength;
    if (bytes.byteLength !== stat.size ||
        bytes.byteLength + stdoutBytes + stderrBytes > input.policy.output_limit_bytes) {
      childFailure("FACTORY_REPLAY_OUTPUT_LIMIT", input.nodeId, childPid);
    }
    rendered = bytes.toString("utf8");
  }
  return Object.freeze({
    rendered,
    child_pid: childPid,
    stdout_bytes: stdoutBytes,
    stderr_bytes: stderrBytes,
    protocol_bytes: protocolBytes,
  });
};

const validateSemanticResult = (
  value: unknown,
  providerId: string,
): FactoryNodeSemanticResultV1 => {
  if (!isRecord(value)) return fail("FACTORY_REPLAY_OUTPUT_INVALID", "semantic-result");
  exactKeys(value, [
    "schema_version",
    "result",
    "provider_id",
    "semantic_output",
    "accounting",
    "claim_ceiling",
    "authority_effect",
  ], "FACTORY_REPLAY_OUTPUT_INVALID");
  if (!isRecord(value.accounting)) {
    return fail("FACTORY_REPLAY_OUTPUT_INVALID", "accounting");
  }
  const accounting = value.accounting;
  const accountingKeys = [
    "positives_declared",
    "positives_passed",
    "mutants_declared",
    "mutants_killed",
  ];
  if (Object.prototype.hasOwnProperty.call(accounting, "proof")) {
    accountingKeys.push("proof");
    try {
      decodeProofEvidenceV1(accounting.proof);
    } catch {
      fail("FACTORY_REPLAY_OUTPUT_INVALID", "proof-evidence");
    }
  }
  exactKeys(accounting, accountingKeys, "FACTORY_REPLAY_OUTPUT_INVALID");
  const counts = accountingKeys.slice(0, 4).map((key) => accounting[key]);
  if (value.schema_version !== "FactoryNodeSemanticResult/v1" ||
      value.result !== "pass" || value.provider_id !== providerId ||
      value.authority_effect !== "none" || typeof value.claim_ceiling !== "string" ||
      value.claim_ceiling.length === 0 ||
      counts.some((count) => !Number.isInteger(count) || (count as number) < 0)) {
    fail("FACTORY_REPLAY_OUTPUT_INVALID", "semantic-result");
  }
  return value as FactoryNodeSemanticResultV1;
};

export const decodeLockedChildOutput = (input: Readonly<{
  rendered: string;
  nodeId: string;
  providerId: string;
  providerVersion: string;
  lockedComponentSetSha256: string;
  lockedExecutionIdentity?: LockedExecutionIdentityV1;
}>): FactoryNodeSemanticResultV1 => {
  if (!input.rendered.endsWith("\n") || input.rendered.includes("\r") ||
      input.rendered.slice(0, -1).length === 0 ||
      input.rendered.slice(0, -1).includes("\n")) {
    fail("FACTORY_REPLAY_OUTPUT_INVALID", "single-json-line");
  }
  let decoded: unknown;
  try {
    decoded = JSON.parse(input.rendered.slice(0, -1));
  } catch {
    return fail("FACTORY_REPLAY_OUTPUT_INVALID", "json");
  }
  if (!isRecord(decoded)) return fail("FACTORY_REPLAY_OUTPUT_INVALID", "envelope");
  exactKeys(decoded, [
    "schema_version",
    "result",
    "replay_mode",
    "node_id",
    "provider_id",
    "provider_version",
    "component_identity",
    ...(input.lockedExecutionIdentity === undefined ? [] : ["execution_identity"]),
    "semantic_result",
    "semantic_result_sha256",
    "authority_effect",
  ], "FACTORY_REPLAY_OUTPUT_INVALID");
  if (!isRecord(decoded.component_identity)) {
    return fail("FACTORY_REPLAY_OUTPUT_INVALID", "component-identity");
  }
  exactKeys(decoded.component_identity, [
    "algorithm",
    "locked_set_sha256",
    "pre_load_sha256",
    "post_execute_sha256",
  ], "FACTORY_REPLAY_OUTPUT_INVALID");
  const identity = decoded.component_identity;
  if (decoded.schema_version !== "FactoryReplayChildResult/v1" ||
      decoded.result !== "pass" ||
      decoded.replay_mode !== "same-oracle-deterministic" ||
      decoded.node_id !== input.nodeId || decoded.provider_id !== input.providerId ||
      decoded.provider_version !== input.providerVersion ||
      decoded.authority_effect !== "none" || identity.algorithm !== "sha256" ||
      identity.locked_set_sha256 !== input.lockedComponentSetSha256 ||
      identity.pre_load_sha256 !== input.lockedComponentSetSha256 ||
      identity.post_execute_sha256 !== input.lockedComponentSetSha256 ||
      !SHA256.test(String(decoded.semantic_result_sha256))) {
    fail("FACTORY_REPLAY_OUTPUT_INVALID", "envelope");
  }
  if (input.lockedExecutionIdentity !== undefined) {
    if (!isRecord(decoded.execution_identity)) {
      return fail("FACTORY_REPLAY_OUTPUT_INVALID", "execution-identity");
    }
    exactKeys(decoded.execution_identity, [
      "algorithm",
      "provider_identity_sha256",
      "component_identity_sha256",
      "runtime_material_identity_sha256",
      "post_runtime_material_identity_sha256",
      "execution_identity_sha256",
      "execution_timeout_ms",
    ], "FACTORY_REPLAY_OUTPUT_INVALID");
    const executionIdentity = decoded.execution_identity;
    const lockedIdentity = input.lockedExecutionIdentity;
    if (executionIdentity.algorithm !== "sha256" ||
        executionIdentity.provider_identity_sha256 !== lockedIdentity.provider_identity_sha256 ||
        executionIdentity.component_identity_sha256 !== lockedIdentity.component_identity_sha256 ||
        executionIdentity.runtime_material_identity_sha256 !==
          lockedIdentity.runtime_material_identity_sha256 ||
        executionIdentity.post_runtime_material_identity_sha256 !==
          lockedIdentity.runtime_material_identity_sha256 ||
        executionIdentity.execution_identity_sha256 !== lockedIdentity.execution_identity_sha256) {
      fail("FACTORY_REPLAY_RUNTIME_MATERIAL_DRIFT", input.nodeId);
    }
    if (executionIdentity.execution_timeout_ms !== lockedIdentity.execution_timeout_ms) {
      fail("FACTORY_REPLAY_TIMEOUT_IDENTITY_DRIFT", input.nodeId);
    }
  }
  const result = validateSemanticResult(decoded.semantic_result, input.providerId);
  if (sha256(canonicalJson(result)) !== decoded.semantic_result_sha256) {
    fail("FACTORY_REPLAY_OUTPUT_INVALID", "semantic-digest");
  }
  return result;
};

export const runLockedChild = async (input: Readonly<{
  scratchRoot: string;
  nodeId: string;
  providerId: string;
  rawInputs: Readonly<Record<string, string>>;
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>;
  lock: FactoryRunLockV1;
}>): Promise<Readonly<{
  result: FactoryNodeSemanticResultV1;
  result_sha256: string;
  replay_kind: FactoryReplayKindV1;
  locked_component_set_sha256: string;
  child_pid: number;
  stdout_bytes: number;
  stderr_bytes: number;
  protocol_bytes: number;
}>> => {
  const root = resolve(input.scratchRoot);
  const scratch = resolve(root, input.nodeId);
  if (!scratch.startsWith(`${root}/`)) fail("FACTORY_REPLAY_SCRATCH_INVALID", input.nodeId);
  await mkdir(scratch, { recursive: false });
  try {
    const lockedNode = input.lock.nodes.find(({ node_id: id }) => id === input.nodeId);
    if (lockedNode === undefined || lockedNode.provider_id !== input.providerId) {
      return fail("FACTORY_REPLAY_NODE_INVALID", input.nodeId);
    }
    const effectiveLockedNode: LockedFactoryNodeV1 = Object.freeze({
      ...lockedNode,
      artifacts: Object.freeze(lockedNode.artifacts ?? []),
      execution_timeout_ms: lockedNode.execution_timeout_ms ?? 70_000,
    });
    const effectiveTimeoutMs = effectiveLockedNode.execution_timeout_ms ?? 70_000;
    const provider = getFactoryNodeProviderV1(input.providerId);
    const preSpawnComponents = await verifyLockedComponentSet({
      repositoryRoot,
      refs: effectiveLockedNode.components,
    });
    const componentSetSha256 = lockedComponentSetSha256(preSpawnComponents);
    const executionIdentity = await resolveLockedProviderExecutionIdentityV1({
      provider,
      lockedNode: effectiveLockedNode,
      verifiedComponentIdentitySha256: componentSetSha256,
    });
    const payloadPath = resolve(scratch, "payload.json");
    const resultPath = resolve(scratch, "result.json");
    await writeFile(payloadPath, json(Object.freeze({
      schema_version: "FactoryReplayChildRequest/v1",
      node_id: input.nodeId,
      provider_id: input.providerId,
      provider_version: lockedNode.provider_version,
      repository_root: repositoryRoot,
      raw_inputs: input.rawInputs,
      upstream: input.upstream,
      locked_components: preSpawnComponents,
      locked_component_set_sha256: componentSetSha256,
      locked_tools: effectiveLockedNode.tools,
      locked_artifacts: effectiveLockedNode.artifacts,
      process_bounds: Object.freeze({
        timeout_ms: effectiveTimeoutMs,
        output_limit_bytes: input.lock.replay_policy.output_limit_bytes,
        termination_grace_ms: input.lock.replay_policy.termination_grace_ms,
      }),
      locked_execution_identity: executionIdentity,
      replay_mode: "same-oracle-deterministic",
      authority_effect: "none",
    })), { encoding: "utf8", flag: "wx" });
    const policy = Object.freeze({
      timeout_ms: effectiveTimeoutMs,
      output_limit_bytes: input.lock.replay_policy.output_limit_bytes,
      termination_grace_ms: input.lock.replay_policy.termination_grace_ms,
    });
    const selectorKeys = providerSelectorEnvironmentKeysV1(provider);
    const environment = Object.fromEntries(input.lock.replay_policy.environment_keys
      .filter((key) => !key.startsWith("DOMAINSPEC_FACTORY_") || selectorKeys.includes(key))
      .filter((key) => process.env[key] !== undefined)
      .map((key) => [key, process.env[key]!])) as NodeJS.ProcessEnv;
    const protocol = await runChildJsonProtocol({
      executable: process.execPath,
      args: ["--import", "tsx", childEntry, payloadPath],
      cwd: implementationRoot,
      environment,
      policy,
      nodeId: input.nodeId,
      resultPath,
    });
    const result = decodeLockedChildOutput({
      rendered: protocol.rendered,
      nodeId: input.nodeId,
      providerId: input.providerId,
      providerVersion: lockedNode.provider_version,
      lockedComponentSetSha256: componentSetSha256,
      lockedExecutionIdentity: executionIdentity,
    });
    try {
      const postIdentity = await resolveLockedProviderExecutionIdentityV1({
        provider,
        lockedNode: effectiveLockedNode,
        verifiedComponentIdentitySha256: componentSetSha256,
      });
      if (postIdentity.runtime_material_identity_sha256 !==
          executionIdentity.runtime_material_identity_sha256 ||
          postIdentity.execution_identity_sha256 !== executionIdentity.execution_identity_sha256) {
        fail("FACTORY_REPLAY_RUNTIME_MATERIAL_DRIFT", input.nodeId);
      }
    } catch {
      fail("FACTORY_REPLAY_RUNTIME_MATERIAL_DRIFT", input.nodeId);
    }
    const postChildComponents = await verifyLockedComponentSet({
      repositoryRoot,
      refs: effectiveLockedNode.components,
    });
    if (lockedComponentSetSha256(postChildComponents) !== componentSetSha256) {
      fail("FACTORY_REPLAY_COMPONENT_TAMPERED", input.nodeId);
    }
    return Object.freeze({
      result,
      result_sha256: sha256(canonicalJson(result)),
      replay_kind: "same-oracle-deterministic",
      locked_component_set_sha256: componentSetSha256,
      child_pid: protocol.child_pid,
      stdout_bytes: protocol.stdout_bytes,
      stderr_bytes: protocol.stderr_bytes,
      protocol_bytes: protocol.protocol_bytes,
    });
  } finally {
    await rm(scratch, { recursive: true, force: true });
  }
};
