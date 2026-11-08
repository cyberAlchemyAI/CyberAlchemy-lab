import { lstat, mkdir, readFile, realpath, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import type {
  FactoryNodeSemanticResultV1,
  FactoryUpstreamResultV1,
} from "../contracts/factory-node-provider-v1.js";
import type { LockedFactoryArtifactV1 } from
  "../contracts/factory-locked-artifact-v1.js";
import type { LockedFactoryToolV1 } from "../contracts/factory-run-lock-v1.js";
import {
  canonicalJson,
  exactKeys,
  fail,
  isRecord,
  safeRelativePath,
  sha256,
} from "../shared/canonical.js";
import { resolveFactoryComponentClosure } from
  "../resolution/resolve-component-closure.js";
import {
  resolveProviderExecutionContextV1,
  verifyProviderExecutionContextV1,
} from "../resolution/resolve-provider-execution-context.js";

type LockedComponentIdentityV1 = Readonly<{
  path: string;
  sha256: string;
  byte_length: number;
}>;

type ReplayPayload = Readonly<{
  schema_version: "FactoryReplayChildRequest/v1";
  node_id: string;
  provider_id: string;
  provider_version: string;
  repository_root: string;
  raw_inputs: Readonly<Record<string, string>>;
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>;
  locked_components: readonly LockedComponentIdentityV1[];
  locked_component_set_sha256: string;
  locked_tools: readonly LockedFactoryToolV1[];
  locked_artifacts: readonly LockedFactoryArtifactV1[];
  process_bounds: Readonly<{
    timeout_ms: number;
    output_limit_bytes: number;
    termination_grace_ms: number;
  }>;
  locked_execution_identity: Readonly<{
    provider_identity_sha256: string;
    component_identity_sha256: string;
    runtime_material_identity_sha256: string;
    execution_identity_sha256: string;
    execution_timeout_ms: number;
  }>;
  replay_mode: "same-oracle-deterministic";
  authority_effect: "none";
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const SHA256 = /^[a-f0-9]{64}$/u;

const decodeTool = (value: unknown): LockedFactoryToolV1 => {
  if (!isRecord(value)) return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "tool");
  exactKeys(value, ["tool_id", "version", "executable_sha256"],
    "FACTORY_REPLAY_PAYLOAD_INVALID");
  if (typeof value.tool_id !== "string" || value.tool_id.length === 0 ||
      typeof value.version !== "string" || value.version.length === 0 ||
      typeof value.executable_sha256 !== "string" ||
      !SHA256.test(value.executable_sha256)) {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "tool");
  }
  return Object.freeze({
    tool_id: value.tool_id,
    version: value.version,
    executable_sha256: value.executable_sha256,
  });
};

const decodeArtifact = (value: unknown): LockedFactoryArtifactV1 => {
  if (!isRecord(value)) return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "artifact");
  exactKeys(value, ["schema_version", "artifact_id", "version", "sha256"],
    "FACTORY_REPLAY_PAYLOAD_INVALID");
  if (value.schema_version !== "LockedFactoryArtifact/v1" ||
      typeof value.artifact_id !== "string" || value.artifact_id.length === 0 ||
      typeof value.version !== "string" || value.version.length === 0 ||
      typeof value.sha256 !== "string" || !SHA256.test(value.sha256)) {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "artifact");
  }
  return Object.freeze({
    schema_version: "LockedFactoryArtifact/v1",
    artifact_id: value.artifact_id,
    version: value.version,
    sha256: value.sha256,
  });
};

const normalizeComponents = (
  refs: readonly LockedComponentIdentityV1[],
): readonly LockedComponentIdentityV1[] => Object.freeze([...refs]
  .map((ref) => Object.freeze({ ...ref }))
  .sort((left, right) => compareUtf8(left.path, right.path)));

const componentSetSha256 = (refs: readonly LockedComponentIdentityV1[]): string =>
  sha256(canonicalJson(normalizeComponents(refs)));

const decodePayload = (value: unknown): ReplayPayload => {
  if (!isRecord(value)) return fail("FACTORY_REPLAY_PAYLOAD_INVALID");
  exactKeys(value, [
    "schema_version",
    "node_id",
    "provider_id",
    "provider_version",
    "repository_root",
    "raw_inputs",
    "upstream",
    "locked_components",
    "locked_component_set_sha256",
    "locked_tools",
    "locked_artifacts",
    "process_bounds",
    "locked_execution_identity",
    "replay_mode",
    "authority_effect",
  ], "FACTORY_REPLAY_PAYLOAD_INVALID");
  if (value.schema_version !== "FactoryReplayChildRequest/v1" ||
      typeof value.node_id !== "string" || value.node_id.length === 0 ||
      typeof value.provider_id !== "string" || value.provider_id.length === 0 ||
      typeof value.provider_version !== "string" || value.provider_version.length === 0 ||
      typeof value.repository_root !== "string" || value.repository_root.length === 0 ||
      !isRecord(value.raw_inputs) || !isRecord(value.upstream) ||
      !Array.isArray(value.locked_components) ||
      typeof value.locked_component_set_sha256 !== "string" ||
      !Array.isArray(value.locked_tools) || !Array.isArray(value.locked_artifacts) ||
      !isRecord(value.process_bounds) || !isRecord(value.locked_execution_identity) ||
      value.replay_mode !== "same-oracle-deterministic" ||
      value.authority_effect !== "none") {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID");
  }
  const components = value.locked_components.map((candidate) => {
    if (!isRecord(candidate)) {
      return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "component");
    }
    exactKeys(candidate, ["path", "sha256", "byte_length"],
      "FACTORY_REPLAY_PAYLOAD_INVALID");
    if (typeof candidate.path !== "string" || !safeRelativePath(candidate.path) ||
        typeof candidate.sha256 !== "string" ||
        !/^[a-f0-9]{64}$/u.test(candidate.sha256) ||
        !Number.isInteger(candidate.byte_length) ||
        (candidate.byte_length as number) < 0) {
      return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "component");
    }
    return Object.freeze({
      path: candidate.path,
      sha256: candidate.sha256,
      byte_length: candidate.byte_length as number,
    });
  });
  const paths = components.map(({ path }) => path);
  if (new Set(paths).size !== paths.length ||
      componentSetSha256(components) !== value.locked_component_set_sha256) {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "component-set");
  }
  if (Object.values(value.raw_inputs).some((raw) => typeof raw !== "string")) {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "raw-inputs");
  }
  const tools = value.locked_tools.map(decodeTool);
  const artifacts = value.locked_artifacts.map(decodeArtifact);
  const toolIds = tools.map(({ tool_id: id }) => id);
  const artifactIds = artifacts.map(({ artifact_id: id }) => id);
  if (new Set(toolIds).size !== toolIds.length ||
      new Set(artifactIds).size !== artifactIds.length ||
      toolIds.some((id) => artifactIds.includes(id)) ||
      JSON.stringify([...toolIds].sort(compareUtf8)) !== JSON.stringify(toolIds) ||
      JSON.stringify([...artifactIds].sort(compareUtf8)) !== JSON.stringify(artifactIds)) {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "runtime-material");
  }
  exactKeys(value.process_bounds,
    ["timeout_ms", "output_limit_bytes", "termination_grace_ms"],
    "FACTORY_REPLAY_PAYLOAD_INVALID");
  const bounds = value.process_bounds;
  if (!Number.isInteger(bounds.timeout_ms) || (bounds.timeout_ms as number) < 1 ||
      (bounds.timeout_ms as number) > 300_000 ||
      !Number.isInteger(bounds.output_limit_bytes) ||
      (bounds.output_limit_bytes as number) < 1 ||
      !Number.isInteger(bounds.termination_grace_ms) ||
      (bounds.termination_grace_ms as number) < 0) {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "process-bounds");
  }
  exactKeys(value.locked_execution_identity, [
    "provider_identity_sha256",
    "component_identity_sha256",
    "runtime_material_identity_sha256",
    "execution_identity_sha256",
    "execution_timeout_ms",
  ], "FACTORY_REPLAY_PAYLOAD_INVALID");
  const identity = value.locked_execution_identity;
  if ([
    identity.provider_identity_sha256,
    identity.component_identity_sha256,
    identity.runtime_material_identity_sha256,
    identity.execution_identity_sha256,
  ].some((digest) => typeof digest !== "string" || !SHA256.test(digest)) ||
      identity.execution_timeout_ms !== bounds.timeout_ms) {
    return fail("FACTORY_REPLAY_PAYLOAD_INVALID", "execution-identity");
  }
  return Object.freeze({
    schema_version: "FactoryReplayChildRequest/v1",
    node_id: value.node_id,
    provider_id: value.provider_id,
    provider_version: value.provider_version,
    repository_root: value.repository_root,
    raw_inputs: Object.freeze(value.raw_inputs as Record<string, string>),
    upstream: Object.freeze(value.upstream as Record<string, FactoryUpstreamResultV1>),
    locked_components: normalizeComponents(components),
    locked_component_set_sha256: value.locked_component_set_sha256,
    locked_tools: Object.freeze(tools),
    locked_artifacts: Object.freeze(artifacts),
    process_bounds: Object.freeze({
      timeout_ms: bounds.timeout_ms as number,
      output_limit_bytes: bounds.output_limit_bytes as number,
      termination_grace_ms: bounds.termination_grace_ms as number,
    }),
    locked_execution_identity: Object.freeze({
      provider_identity_sha256: identity.provider_identity_sha256 as string,
      component_identity_sha256: identity.component_identity_sha256 as string,
      runtime_material_identity_sha256: identity.runtime_material_identity_sha256 as string,
      execution_identity_sha256: identity.execution_identity_sha256 as string,
      execution_timeout_ms: identity.execution_timeout_ms as number,
    }),
    replay_mode: "same-oracle-deterministic",
    authority_effect: "none",
  });
};

const verifyComponents = async (
  rootInput: string,
  refs: readonly LockedComponentIdentityV1[],
): Promise<string> => {
  const root = await realpath(rootInput);
  await Promise.all(refs.map(async (ref) => {
    const target = resolve(root, ref.path);
    if (!target.startsWith(`${root}/`)) fail("FACTORY_REPLAY_COMPONENT_INVALID", ref.path);
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
  }));
  return componentSetSha256(refs);
};

const payloadPath = process.argv[2];
if (payloadPath === undefined) fail("FACTORY_REPLAY_PAYLOAD_MISSING");

const payload = decodePayload(JSON.parse(await readFile(payloadPath, "utf8")));
const preLoadSha256 = await verifyComponents(
  payload.repository_root,
  payload.locked_components,
);
const moduleRuntime = await import("node:module") as unknown as {
  enableCompileCache?: () => unknown;
};
moduleRuntime.enableCompileCache?.();
const { getFactoryNodeProviderV1 } = await import(
  "../registry/factory-node-registry-v1.js"
);
const provider = getFactoryNodeProviderV1(payload.provider_id);
const providerPaths = await resolveFactoryComponentClosure({
  repositoryRoot: payload.repository_root,
  rootPaths: provider.component_paths,
});
const lockedPaths = payload.locked_components.map(({ path }) => path).sort(compareUtf8);
if (provider.provider_id !== payload.provider_id ||
    provider.provider_version !== payload.provider_version ||
    JSON.stringify(providerPaths) !== JSON.stringify(lockedPaths)) {
  fail("FACTORY_REPLAY_PROVIDER_IDENTITY_MISMATCH", payload.provider_id);
}
const providerScratch = resolve(dirname(payloadPath), "provider-context");
await mkdir(providerScratch);
const lockedNode = Object.freeze({
  node_id: payload.node_id,
  kind: "direct-proof" as const,
  provider_id: payload.provider_id,
  provider_version: payload.provider_version,
  depends_on: Object.freeze([]),
  inputs: Object.freeze([]),
  components: Object.freeze(payload.locked_components.map((component) => Object.freeze({
    role: "component",
    ...component,
  }))),
  tools: payload.locked_tools,
  artifacts: payload.locked_artifacts,
  execution_timeout_ms: payload.process_bounds.timeout_ms,
  claim_ceiling: "replay-child-runtime-only",
});
let semanticResult: FactoryNodeSemanticResultV1;
let childExecution;
try {
  childExecution = await resolveProviderExecutionContextV1({
    repositoryRoot: payload.repository_root,
    provider,
    lockedNode,
    scratchPath: providerScratch,
    outputLimitBytes: payload.process_bounds.output_limit_bytes,
    terminationGraceMs: payload.process_bounds.termination_grace_ms,
  });
  const lockedIdentity = payload.locked_execution_identity;
  if (childExecution.context.process_bounds.timeout_ms !== lockedIdentity.execution_timeout_ms) {
    fail("FACTORY_REPLAY_TIMEOUT_IDENTITY_DRIFT", payload.node_id);
  }
  if (childExecution.provider_identity_sha256 !== lockedIdentity.provider_identity_sha256 ||
      childExecution.component_identity_sha256 !== lockedIdentity.component_identity_sha256 ||
      childExecution.runtime_material_identity_sha256 !==
        lockedIdentity.runtime_material_identity_sha256 ||
      childExecution.execution_identity_sha256 !== lockedIdentity.execution_identity_sha256) {
    fail("FACTORY_REPLAY_RUNTIME_MATERIAL_DRIFT", payload.node_id);
  }
  const result = await provider.execute({
    raw_inputs: payload.raw_inputs,
    upstream: payload.upstream,
    execution_context: childExecution.context,
  });
  await verifyProviderExecutionContextV1({
    before: childExecution,
    repositoryRoot: payload.repository_root,
    provider,
    lockedNode,
  });
  semanticResult = result as FactoryNodeSemanticResultV1;
} finally {
  await rm(providerScratch, { recursive: true, force: true });
}
const postExecuteSha256 = await verifyComponents(
  payload.repository_root,
  payload.locked_components,
);
const envelope = Object.freeze({
  schema_version: "FactoryReplayChildResult/v1",
  result: "pass",
  replay_mode: "same-oracle-deterministic",
  node_id: payload.node_id,
  provider_id: payload.provider_id,
  provider_version: payload.provider_version,
  component_identity: Object.freeze({
    algorithm: "sha256",
    locked_set_sha256: payload.locked_component_set_sha256,
    pre_load_sha256: preLoadSha256,
    post_execute_sha256: postExecuteSha256,
  }),
  execution_identity: Object.freeze({
    algorithm: "sha256",
    provider_identity_sha256: childExecution.provider_identity_sha256,
    component_identity_sha256: childExecution.component_identity_sha256,
    runtime_material_identity_sha256: childExecution.runtime_material_identity_sha256,
    post_runtime_material_identity_sha256: childExecution.runtime_material_identity_sha256,
    execution_identity_sha256: childExecution.execution_identity_sha256,
    execution_timeout_ms: childExecution.context.process_bounds.timeout_ms,
  }),
  semantic_result: semanticResult,
  semantic_result_sha256: sha256(canonicalJson(semanticResult)),
  authority_effect: "none",
});
await writeFile(resolve(dirname(payloadPath), "result.json"),
  `${JSON.stringify(envelope)}\n`, { encoding: "utf8", flag: "wx" });
