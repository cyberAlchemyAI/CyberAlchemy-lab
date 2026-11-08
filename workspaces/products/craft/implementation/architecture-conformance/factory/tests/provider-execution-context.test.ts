import { chmod, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import type {
  FactoryNodeProviderV1,
  FactoryNodeSemanticResultV1,
} from "../contracts/factory-node-provider-v1.js";
import type { LockedFactoryNodeV1 } from "../contracts/factory-run-lock-v1.js";
import {
  decodeLockedChildOutput,
  lockedComponentSetSha256,
} from "../replay/run-locked-child.js";
import {
  providerSelectorEnvironmentKeysV1,
  resolveProviderExecutionContextV1,
  verifyProviderExecutionContextV1,
} from "../resolution/resolve-provider-execution-context.js";
import {
  resolveFactoryArtifactHandleV1,
  resolveFactoryToolHandleV1,
} from "../resolution/resolve-toolchain.js";
import { canonicalJson, sha256 } from "../shared/canonical.js";

const roots: string[] = [];
const originalJava = process.env.DOMAINSPEC_FACTORY_JAVA_BIN;
const originalJar = process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR;

afterEach(async () => {
  await Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true, force: true })));
  if (originalJava === undefined) delete process.env.DOMAINSPEC_FACTORY_JAVA_BIN;
  else process.env.DOMAINSPEC_FACTORY_JAVA_BIN = originalJava;
  if (originalJar === undefined) delete process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR;
  else process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR = originalJar;
});

const storedJar = (version: string): Buffer => {
  const name = Buffer.from("META-INF/MANIFEST.MF");
  const content = Buffer.from(
    `Manifest-Version: 1.0\r\nImplementation-Version: ${version}\r\n\r\n`,
  );
  const local = Buffer.alloc(30);
  local.writeUInt32LE(0x04034b50, 0);
  local.writeUInt16LE(20, 4);
  local.writeUInt32LE(content.byteLength, 18);
  local.writeUInt32LE(content.byteLength, 22);
  local.writeUInt16LE(name.byteLength, 26);
  const central = Buffer.alloc(46);
  central.writeUInt32LE(0x02014b50, 0);
  central.writeUInt16LE(20, 4);
  central.writeUInt16LE(20, 6);
  central.writeUInt32LE(content.byteLength, 20);
  central.writeUInt32LE(content.byteLength, 24);
  central.writeUInt16LE(name.byteLength, 28);
  const directoryOffset = local.byteLength + name.byteLength + content.byteLength;
  const directorySize = central.byteLength + name.byteLength;
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(1, 8);
  eocd.writeUInt16LE(1, 10);
  eocd.writeUInt32LE(directorySize, 12);
  eocd.writeUInt32LE(directoryOffset, 16);
  return Buffer.concat([local, name, content, central, name, eocd]);
};

const semanticResult: FactoryNodeSemanticResultV1 = Object.freeze({
  schema_version: "FactoryNodeSemanticResult/v1",
  result: "pass",
  provider_id: "fixture-material-provider-v1",
  semantic_output: Object.freeze({ fixture: true }),
  accounting: Object.freeze({
    positives_declared: 1,
    positives_passed: 1,
    mutants_declared: 1,
    mutants_killed: 1,
  }),
  claim_ceiling: "fixture only",
  authority_effect: "none",
});

const fixture = async () => {
  const root = await mkdtemp(resolve(tmpdir(), "domainspec-provider-context-"));
  roots.push(root);
  const componentPath = "provider.ts";
  const component = resolve(root, componentPath);
  const java = resolve(root, "java-explicit");
  const jar = resolve(root, "tla2tools.jar");
  const scratch = resolve(root, "scratch");
  await writeFile(component, "export const fixture = true;\n");
  await writeFile(java, "#!/bin/sh\nprintf 'java fixture 17.0.1\\n' >&2\n");
  await chmod(java, 0o755);
  await writeFile(jar, storedJar("1.8.0-fixture"));
  await mkdir(scratch);
  process.env.DOMAINSPEC_FACTORY_JAVA_BIN = java;
  process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR = jar;
  const tool = await resolveFactoryToolHandleV1("java");
  const artifact = await resolveFactoryArtifactHandleV1("tla2tools");
  const componentBytes = await readFile(component);
  const componentRef = Object.freeze({
    role: "component",
    path: componentPath,
    sha256: sha256(componentBytes),
    byte_length: componentBytes.byteLength,
  });
  const provider = Object.freeze<FactoryNodeProviderV1>({
    provider_id: "fixture-material-provider-v1",
    provider_version: "1.0.0",
    compatible_kinds: Object.freeze(["direct-proof"]),
    required_input_roles: Object.freeze([]),
    component_paths: Object.freeze([componentPath]),
    tool_ids: Object.freeze(["java"]),
    artifact_ids: Object.freeze(["tla2tools"]),
    execution_timeout_ms: 300_000,
    execute: async ({ execution_context: context }: Parameters<
      FactoryNodeProviderV1["execute"]
    >[0]) => {
      if (context === undefined) throw new Error("context missing");
      return semanticResult;
    },
  });
  const lockedNode: LockedFactoryNodeV1 = Object.freeze({
    node_id: "fixture-node",
    kind: "direct-proof",
    provider_id: provider.provider_id,
    provider_version: provider.provider_version,
    depends_on: Object.freeze([]),
    inputs: Object.freeze([]),
    components: Object.freeze([componentRef]),
    tools: Object.freeze([tool.locked]),
    artifacts: Object.freeze([artifact.locked]),
    execution_timeout_ms: 300_000,
    claim_ceiling: "fixture only",
  });
  return { root, component, java, jar, scratch, provider, lockedNode, componentRef };
};

const resolveFixture = async (value: Awaited<ReturnType<typeof fixture>>) =>
  resolveProviderExecutionContextV1({
    repositoryRoot: value.root,
    provider: value.provider,
    lockedNode: value.lockedNode,
    scratchPath: value.scratch,
    outputLimitBytes: 1_048_576,
    terminationGraceMs: 1_000,
  });

describe("SWU-FMP2-002 provider execution context", () => {
  it("builds one closed deep-frozen context without putting paths in lock identity", async () => {
    const value = await fixture();
    const resolved = await resolveFixture(value);
    expect(resolved.context).toMatchObject({
      schema_version: "FactoryProviderExecutionContext/v1",
      node_id: "fixture-node",
      scratch_path: value.scratch,
      process_bounds: { timeout_ms: 300_000 },
      authority_effect: "none",
    });
    expect(Object.isFrozen(resolved.context)).toBe(true);
    expect(Object.isFrozen(resolved.context.executables[0])).toBe(true);
    expect(Object.isFrozen(resolved.context.process_bounds)).toBe(true);
    expect(canonicalJson(value.lockedNode)).not.toContain(value.root);
    expect(resolved.execution_identity_sha256).toMatch(/^[a-f0-9]{64}$/u);
    await expect(verifyProviderExecutionContextV1({
      before: resolved,
      repositoryRoot: value.root,
      provider: value.provider,
      lockedNode: value.lockedNode,
    })).resolves.toMatchObject({ execution_identity_sha256: resolved.execution_identity_sha256 });
  });

  it("rejects wrong locked executable and artifact identities", async () => {
    const value = await fixture();
    await expect(resolveProviderExecutionContextV1({
      repositoryRoot: value.root,
      provider: value.provider,
      lockedNode: Object.freeze({
        ...value.lockedNode,
        tools: Object.freeze([Object.freeze({
          ...value.lockedNode.tools[0]!,
          executable_sha256: "0".repeat(64),
        })]),
      }),
      scratchPath: value.scratch,
      outputLimitBytes: 1024,
      terminationGraceMs: 1,
    })).rejects.toThrow("FACTORY_TOOL_INVALID");
    await expect(resolveProviderExecutionContextV1({
      repositoryRoot: value.root,
      provider: value.provider,
      lockedNode: Object.freeze({
        ...value.lockedNode,
        artifacts: Object.freeze([Object.freeze({
          ...value.lockedNode.artifacts![0]!,
          sha256: "0".repeat(64),
        })]),
      }),
      scratchPath: value.scratch,
      outputLimitBytes: 1024,
      terminationGraceMs: 1,
    })).rejects.toThrow("FACTORY_ARTIFACT_INVALID");
  });

  it("rejects provider, component, timeout, and duplicate declaration drift", async () => {
    const value = await fixture();
    await expect(resolveProviderExecutionContextV1({
      repositoryRoot: value.root,
      provider: Object.freeze({ ...value.provider, provider_version: "2.0.0" }),
      lockedNode: value.lockedNode,
      scratchPath: value.scratch,
      outputLimitBytes: 1024,
      terminationGraceMs: 1,
    })).rejects.toThrow("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT");
    await expect(resolveProviderExecutionContextV1({
      repositoryRoot: value.root,
      provider: value.provider,
      lockedNode: Object.freeze({ ...value.lockedNode, execution_timeout_ms: 70_000 }),
      scratchPath: value.scratch,
      outputLimitBytes: 1024,
      terminationGraceMs: 1,
    })).rejects.toThrow("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT");
    await expect(resolveProviderExecutionContextV1({
      repositoryRoot: value.root,
      provider: Object.freeze({ ...value.provider, tool_ids: Object.freeze(["java", "java"]) }),
      lockedNode: value.lockedNode,
      scratchPath: value.scratch,
      outputLimitBytes: 1024,
      terminationGraceMs: 1,
    })).rejects.toThrow("FACTORY_RUNTIME_MATERIAL_DUPLICATE");
    await writeFile(value.component, "export const fixture = false;\n");
    await expect(resolveFixture(value))
      .rejects.toThrow("FACTORY_PROVIDER_EXECUTION_IDENTITY_DRIFT");
  });

  it("detects runtime material replacement after provider return", async () => {
    const value = await fixture();
    const before = await resolveFixture(value);
    await writeFile(value.jar, storedJar("1.8.1-replaced"));
    await expect(verifyProviderExecutionContextV1({
      before,
      repositoryRoot: value.root,
      provider: value.provider,
      lockedNode: value.lockedNode,
    })).rejects.toThrow("FACTORY_RUNTIME_MATERIAL_TAMPERED");
  });

  it("binds replay runtime and timeout identity independently", async () => {
    const value = await fixture();
    const resolved = await resolveFixture(value);
    const componentSet = lockedComponentSetSha256([value.componentRef]);
    const executionIdentity = {
      provider_identity_sha256: resolved.provider_identity_sha256,
      component_identity_sha256: resolved.component_identity_sha256,
      runtime_material_identity_sha256: resolved.runtime_material_identity_sha256,
      execution_identity_sha256: resolved.execution_identity_sha256,
      execution_timeout_ms: 300_000,
    };
    const envelope = (identity: Record<string, unknown>) => ({
      schema_version: "FactoryReplayChildResult/v1",
      result: "pass",
      replay_mode: "same-oracle-deterministic",
      node_id: "fixture-node",
      provider_id: value.provider.provider_id,
      provider_version: value.provider.provider_version,
      component_identity: {
        algorithm: "sha256",
        locked_set_sha256: componentSet,
        pre_load_sha256: componentSet,
        post_execute_sha256: componentSet,
      },
      execution_identity: { algorithm: "sha256", ...identity },
      semantic_result: semanticResult,
      semantic_result_sha256: sha256(canonicalJson(semanticResult)),
      authority_effect: "none",
    });
    const decode = (identity: Record<string, unknown>) => decodeLockedChildOutput({
      rendered: `${JSON.stringify(envelope(identity))}\n`,
      nodeId: "fixture-node",
      providerId: value.provider.provider_id,
      providerVersion: value.provider.provider_version,
      lockedComponentSetSha256: componentSet,
      lockedExecutionIdentity: executionIdentity,
    });
    expect(decode({
      ...executionIdentity,
      post_runtime_material_identity_sha256: executionIdentity.runtime_material_identity_sha256,
    })).toEqual(semanticResult);
    expect(() => decode({
      ...executionIdentity,
      runtime_material_identity_sha256: "0".repeat(64),
      post_runtime_material_identity_sha256: executionIdentity.runtime_material_identity_sha256,
    })).toThrow("FACTORY_REPLAY_RUNTIME_MATERIAL_DRIFT");
    expect(() => decode({
      ...executionIdentity,
      execution_timeout_ms: 70_000,
      post_runtime_material_identity_sha256: executionIdentity.runtime_material_identity_sha256,
    })).toThrow("FACTORY_REPLAY_TIMEOUT_IDENTITY_DRIFT");
  });

  it("passes only selectors declared by the provider", async () => {
    const value = await fixture();
    expect(providerSelectorEnvironmentKeysV1(value.provider)).toEqual([
      "DOMAINSPEC_FACTORY_JAVA_BIN",
      "DOMAINSPEC_FACTORY_TLA2TOOLS_JAR",
    ]);
    expect(providerSelectorEnvironmentKeysV1(Object.freeze({
      ...value.provider,
      tool_ids: Object.freeze([]),
      artifact_ids: Object.freeze([]),
    }))).toEqual([]);
  });
});
