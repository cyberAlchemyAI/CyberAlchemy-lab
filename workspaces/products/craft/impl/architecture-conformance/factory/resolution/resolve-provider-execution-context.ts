import { lstat, readFile, realpath } from "node:fs/promises";
import { isAbsolute, resolve } from "node:path";

import type { FactoryNodeProviderV1 } from
  "../contracts/factory-node-provider-v1.js";
import type { FactoryProviderExecutionContextV1 } from
  "../contracts/factory-provider-execution-context-v1.js";
import type { LockedFactoryNodeV1 } from "../contracts/factory-run-lock-v1.js";
import { resolveFactoryComponentClosure } from "./resolve-component-closure.js";
import {
  resolveFactoryArtifactHandleV1,
  resolveFactoryToolHandleV1,
} from "./resolve-toolchain.js";
import { canonicalJson, fail, sha256 } from "../shared/canonical.js";

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const deepFreeze = <T>(value: T): T => {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
};

const sortedUnique = (values: readonly string[], detail: string): readonly string[] => {
  if (new Set(values).size !== values.length) {
    return fail("FACTORY_RUNTIME_MATERIAL_DUPLICATE", detail);
  }
  return Object.freeze([...values].sort(compareUtf8));
};

const effectiveProviderMaterial = (provider: FactoryNodeProviderV1) => {
  const materialAware = provider.artifact_ids !== undefined ||
    provider.execution_timeout_ms !== undefined;
  if (materialAware && (provider.artifact_ids === undefined ||
      provider.execution_timeout_ms === undefined)) {
    return fail("FACTORY_PROVIDER_TIMEOUT_INVALID", provider.provider_id);
  }
  const toolIds = sortedUnique(provider.tool_ids, provider.provider_id);
  const artifactIds = sortedUnique(provider.artifact_ids ?? [], provider.provider_id);
  if (toolIds.some((id) => artifactIds.includes(id))) {
    fail("FACTORY_RUNTIME_MATERIAL_DUPLICATE", provider.provider_id);
  }
  if (materialAware && (JSON.stringify(toolIds) !== JSON.stringify(provider.tool_ids) ||
      JSON.stringify(artifactIds) !== JSON.stringify(provider.artifact_ids))) {
    fail("FACTORY_RUNTIME_MATERIAL_DUPLICATE", provider.provider_id);
  }
  const executionTimeoutMs = provider.execution_timeout_ms ?? 70_000;
  if (!Number.isInteger(executionTimeoutMs) || executionTimeoutMs < 1 ||
      executionTimeoutMs > 300_000) {
    fail("FACTORY_PROVIDER_TIMEOUT_INVALID", provider.provider_id);
  }
  return Object.freeze({ toolIds, artifactIds, executionTimeoutMs });
};

const componentIdentity = async (input: Readonly<{
  repositoryRoot: string;
  provider: FactoryNodeProviderV1;
  lockedNode: LockedFactoryNodeV1;
}>): Promise<string> => {
  const root = await realpath(input.repositoryRoot).catch(() =>
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", input.lockedNode.node_id));
  const currentPaths = await resolveFactoryComponentClosure({
    repositoryRoot: root,
    rootPaths: input.provider.component_paths,
  }).catch(() => fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", input.lockedNode.node_id));
  const locked = [...input.lockedNode.components].sort((left, right) =>
    compareUtf8(left.path, right.path));
  if (JSON.stringify(currentPaths) !== JSON.stringify(locked.map(({ path }) => path))) {
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", input.lockedNode.node_id);
  }
  const observed = await Promise.all(locked.map(async (ref) => {
    const target = resolve(root, ref.path);
    if (!target.startsWith(`${root}/`)) {
      return fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", ref.path);
    }
    const stat = await lstat(target).catch(() =>
      fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", ref.path));
    if (!stat.isFile() || stat.isSymbolicLink()) {
      fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", ref.path);
    }
    const bytes = await readFile(target);
    if (bytes.byteLength !== ref.byte_length || sha256(bytes) !== ref.sha256) {
      fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", ref.path);
    }
    return Object.freeze({
      path: ref.path,
      sha256: ref.sha256,
      byte_length: ref.byte_length,
    });
  }));
  return sha256(canonicalJson(observed));
};

export type ResolvedFactoryProviderExecutionV1 = Readonly<{
  context: FactoryProviderExecutionContextV1;
  provider_identity_sha256: string;
  component_identity_sha256: string;
  runtime_material_identity_sha256: string;
  execution_identity_sha256: string;
}>;

export type FactoryProviderExecutionIdentityV1 = Readonly<{
  provider_identity_sha256: string;
  component_identity_sha256: string;
  runtime_material_identity_sha256: string;
  execution_identity_sha256: string;
  execution_timeout_ms: number;
}>;

export const resolveLockedProviderExecutionIdentityV1 = async (input: Readonly<{
  provider: FactoryNodeProviderV1;
  lockedNode: LockedFactoryNodeV1;
  verifiedComponentIdentitySha256: string;
}>): Promise<FactoryProviderExecutionIdentityV1> => {
  const { provider, lockedNode } = input;
  if (provider.provider_id !== lockedNode.provider_id ||
      provider.provider_version !== lockedNode.provider_version) {
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", lockedNode.node_id);
  }
  const declared = effectiveProviderMaterial(provider);
  const lockedArtifacts = lockedNode.artifacts ?? [];
  const lockedTimeoutMs = lockedNode.execution_timeout_ms ?? 70_000;
  if (JSON.stringify(declared.toolIds) !== JSON.stringify(
    lockedNode.tools.map(({ tool_id: id }) => id),
  ) || JSON.stringify(declared.artifactIds) !== JSON.stringify(
    lockedArtifacts.map(({ artifact_id: id }) => id),
  ) || declared.executionTimeoutMs !== lockedTimeoutMs) {
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", lockedNode.node_id);
  }
  const tools = await Promise.all(declared.toolIds.map(resolveFactoryToolHandleV1));
  const artifacts = await Promise.all(
    declared.artifactIds.map(resolveFactoryArtifactHandleV1),
  );
  if (canonicalJson(tools.map(({ locked }) => locked)) !==
      canonicalJson(lockedNode.tools)) fail("FACTORY_TOOL_INVALID", lockedNode.node_id);
  if (canonicalJson(artifacts.map(({ locked }) => locked)) !==
      canonicalJson(lockedArtifacts)) fail("FACTORY_ARTIFACT_INVALID", lockedNode.node_id);
  const providerIdentitySha256 = sha256(canonicalJson({
    provider_id: provider.provider_id,
    provider_version: provider.provider_version,
  }));
  const runtimeMaterialIdentitySha256 = sha256(canonicalJson({
    executables: tools.map(({ locked }) => ({
      kind: "executable",
      tool_id: locked.tool_id,
      version: locked.version,
      sha256: locked.executable_sha256,
    })),
    artifacts: artifacts.map(({ locked }) => ({
      kind: "artifact",
      artifact_id: locked.artifact_id,
      version: locked.version,
      sha256: locked.sha256,
    })),
  }));
  const executionIdentitySha256 = sha256(canonicalJson({
    provider_identity_sha256: providerIdentitySha256,
    component_identity_sha256: input.verifiedComponentIdentitySha256,
    runtime_material_identity_sha256: runtimeMaterialIdentitySha256,
    execution_timeout_ms: lockedTimeoutMs,
  }));
  return Object.freeze({
    provider_identity_sha256: providerIdentitySha256,
    component_identity_sha256: input.verifiedComponentIdentitySha256,
    runtime_material_identity_sha256: runtimeMaterialIdentitySha256,
    execution_identity_sha256: executionIdentitySha256,
    execution_timeout_ms: lockedTimeoutMs,
  });
};

export const providerSelectorEnvironmentKeysV1 = (
  provider: FactoryNodeProviderV1,
): readonly string[] => Object.freeze([
  ...(provider.tool_ids.includes("java") ? ["DOMAINSPEC_FACTORY_JAVA_BIN"] : []),
  ...((provider.artifact_ids ?? []).includes("tla2tools")
    ? ["DOMAINSPEC_FACTORY_TLA2TOOLS_JAR"] : []),
]);

export const resolveProviderExecutionContextV1 = async (input: Readonly<{
  repositoryRoot: string;
  provider: FactoryNodeProviderV1;
  lockedNode: LockedFactoryNodeV1;
  scratchPath: string;
  outputLimitBytes: number;
  terminationGraceMs: number;
}>): Promise<ResolvedFactoryProviderExecutionV1> => {
  const { provider, lockedNode } = input;
  if (!isAbsolute(input.scratchPath)) {
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", lockedNode.node_id);
  }
  const scratchStat = await lstat(input.scratchPath).catch(() =>
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", lockedNode.node_id));
  if (!scratchStat.isDirectory() || scratchStat.isSymbolicLink()) {
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", lockedNode.node_id);
  }
  if (provider.provider_id !== lockedNode.provider_id ||
      provider.provider_version !== lockedNode.provider_version) {
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", lockedNode.node_id);
  }
  const declared = effectiveProviderMaterial(provider);
  const lockedToolIds = sortedUnique(
    lockedNode.tools.map(({ tool_id: id }) => id),
    lockedNode.node_id,
  );
  const lockedArtifacts = lockedNode.artifacts ?? [];
  const lockedArtifactIds = sortedUnique(
    lockedArtifacts.map(({ artifact_id: id }) => id),
    lockedNode.node_id,
  );
  const lockedTimeoutMs = lockedNode.execution_timeout_ms ?? 70_000;
  if (!Number.isInteger(lockedTimeoutMs) ||
      lockedTimeoutMs < 1 || lockedTimeoutMs > 300_000) {
    fail("FACTORY_PROVIDER_TIMEOUT_INVALID", lockedNode.node_id);
  }
  if (JSON.stringify(declared.toolIds) !== JSON.stringify(lockedToolIds) ||
      JSON.stringify(declared.artifactIds) !== JSON.stringify(lockedArtifactIds) ||
      declared.executionTimeoutMs !== lockedTimeoutMs) {
    fail("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT", lockedNode.node_id);
  }
  const resolvedTools = await Promise.all(declared.toolIds.map(resolveFactoryToolHandleV1));
  const resolvedArtifacts = await Promise.all(
    declared.artifactIds.map(resolveFactoryArtifactHandleV1),
  );
  if (canonicalJson(resolvedTools.map(({ locked }) => locked)) !==
      canonicalJson(lockedNode.tools)) {
    fail("FACTORY_TOOL_INVALID", lockedNode.node_id);
  }
  if (canonicalJson(resolvedArtifacts.map(({ locked }) => locked)) !==
      canonicalJson(lockedArtifacts)) {
    fail("FACTORY_ARTIFACT_INVALID", lockedNode.node_id);
  }
  const context = deepFreeze({
    schema_version: "FactoryProviderExecutionContext/v1" as const,
    node_id: lockedNode.node_id,
    scratch_path: input.scratchPath,
    executables: resolvedTools.map(({ locked, path }) => ({
      kind: "executable" as const,
      tool_id: locked.tool_id,
      version: locked.version,
      sha256: locked.executable_sha256,
      path,
    })),
    artifacts: resolvedArtifacts.map(({ locked, path }) => ({
      kind: "artifact" as const,
      artifact_id: locked.artifact_id,
      version: locked.version,
      sha256: locked.sha256,
      path,
    })),
    process_bounds: {
      timeout_ms: lockedTimeoutMs,
      output_limit_bytes: input.outputLimitBytes,
      termination_grace_ms: input.terminationGraceMs,
    },
    authority_effect: "none" as const,
  });
  const providerIdentitySha256 = sha256(canonicalJson({
    provider_id: provider.provider_id,
    provider_version: provider.provider_version,
  }));
  const componentIdentitySha256 = await componentIdentity(input);
  const runtimeMaterialIdentitySha256 = sha256(canonicalJson({
    executables: context.executables.map(({ path: _path, ...identity }) => identity),
    artifacts: context.artifacts.map(({ path: _path, ...identity }) => identity),
  }));
  const executionIdentitySha256 = sha256(canonicalJson({
    provider_identity_sha256: providerIdentitySha256,
    component_identity_sha256: componentIdentitySha256,
    runtime_material_identity_sha256: runtimeMaterialIdentitySha256,
    execution_timeout_ms: lockedTimeoutMs,
  }));
  return Object.freeze({
    context,
    provider_identity_sha256: providerIdentitySha256,
    component_identity_sha256: componentIdentitySha256,
    runtime_material_identity_sha256: runtimeMaterialIdentitySha256,
    execution_identity_sha256: executionIdentitySha256,
  });
};

export const verifyProviderExecutionContextV1 = async (input: Readonly<{
  before: ResolvedFactoryProviderExecutionV1;
  repositoryRoot: string;
  provider: FactoryNodeProviderV1;
  lockedNode: LockedFactoryNodeV1;
}>): Promise<ResolvedFactoryProviderExecutionV1> => {
  try {
    const declared = effectiveProviderMaterial(input.provider);
    const lockedArtifacts = input.lockedNode.artifacts ?? [];
    const lockedTimeoutMs = input.lockedNode.execution_timeout_ms ?? 70_000;
    if (lockedTimeoutMs !== input.before.context.process_bounds.timeout_ms ||
        declared.executionTimeoutMs !== lockedTimeoutMs) {
      fail("FACTORY_RUNTIME_MATERIAL_TAMPERED", input.lockedNode.node_id);
    }
    const tools = await Promise.all(declared.toolIds.map(resolveFactoryToolHandleV1));
    const artifacts = await Promise.all(
      declared.artifactIds.map(resolveFactoryArtifactHandleV1),
    );
    if (canonicalJson(tools.map(({ locked }) => locked)) !==
        canonicalJson(input.lockedNode.tools) ||
        canonicalJson(artifacts.map(({ locked }) => locked)) !==
          canonicalJson(lockedArtifacts)) {
      fail("FACTORY_RUNTIME_MATERIAL_TAMPERED", input.lockedNode.node_id);
    }
    const runtimeMaterialIdentitySha256 = sha256(canonicalJson({
      executables: tools.map(({ locked }) => ({
        kind: "executable",
        tool_id: locked.tool_id,
        version: locked.version,
        sha256: locked.executable_sha256,
      })),
      artifacts: artifacts.map(({ locked }) => ({
        kind: "artifact",
        artifact_id: locked.artifact_id,
        version: locked.version,
        sha256: locked.sha256,
      })),
    }));
    if (runtimeMaterialIdentitySha256 !== input.before.runtime_material_identity_sha256) {
      fail("FACTORY_RUNTIME_MATERIAL_TAMPERED", input.lockedNode.node_id);
    }
  } catch {
    return fail("FACTORY_RUNTIME_MATERIAL_TAMPERED", input.lockedNode.node_id);
  }
  return input.before;
};
