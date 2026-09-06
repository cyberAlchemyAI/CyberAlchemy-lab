import { chmod, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { decodeFactoryRunLockV1 } from "../codecs/decode-factory-run-lock-v1.js";
import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";
import {
  resolveFactoryArtifactHandleV1,
  resolveFactoryToolHandleV1,
  resolveFactoryToolV1,
} from "../resolution/resolve-toolchain.js";
import { canonicalJson, sha256 } from "../shared/canonical.js";

const roots: string[] = [];
const originalJava = process.env.DOMAINSPEC_FACTORY_JAVA_BIN;
const originalJar = process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR;
const originalPath = process.env.PATH;

afterEach(async () => {
  await Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true, force: true })));
  if (originalJava === undefined) delete process.env.DOMAINSPEC_FACTORY_JAVA_BIN;
  else process.env.DOMAINSPEC_FACTORY_JAVA_BIN = originalJava;
  if (originalJar === undefined) delete process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR;
  else process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR = originalJar;
  process.env.PATH = originalPath;
});

const temporaryRoot = async (): Promise<string> => {
  const root = await mkdtemp(resolve(tmpdir(), "domainspec-material-lock-"));
  roots.push(root);
  return root;
};

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

const rulePlan = async () => {
  const request = decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
    repositoryRoot,
    "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rule-only.request.json",
  ), "utf8")));
  return planFactoryRun({ repositoryRoot, request });
};

const rehashLock = (value: Record<string, unknown>): Record<string, unknown> => {
  const body = Object.fromEntries(Object.entries(value).filter(([key]) => key !== "lock_sha256"));
  return { ...body, lock_sha256: sha256(canonicalJson(body)) };
};

describe("SWU-FMP2-002 runtime material lock", () => {
  it("emits canonical material fields for legacy providers", async () => {
    const plan = await rulePlan();
    for (const node of plan.lock.nodes) {
      expect(node.artifacts).toEqual([]);
      expect(node.execution_timeout_ms).toBe(70_000);
      expect(node.tools.map(({ tool_id: id }) => id)).toEqual(
        [...node.tools.map(({ tool_id: id }) => id)].sort(),
      );
    }
    expect(plan.lock.replay_policy.environment_keys).toContain(
      "DOMAINSPEC_FACTORY_TLA2TOOLS_JAR",
    );
  });

  it("normalizes historical v1 locks only in memory after verifying original bytes", async () => {
    const plan = await rulePlan();
    const historicalNodes = plan.lock.nodes.map((node) => Object.fromEntries(
      Object.entries(node).filter(([key]) =>
        key !== "artifacts" && key !== "execution_timeout_ms"),
    ));
    const historical = rehashLock({ ...plan.lock, nodes: historicalNodes });
    const original = JSON.stringify(historical);
    const decoded = decodeFactoryRunLockV1(historical);
    expect(decoded.nodes.every((node) => node.execution_timeout_ms === 70_000)).toBe(true);
    expect(decoded.nodes.every((node) => node.artifacts?.length === 0)).toBe(true);
    expect(JSON.stringify(historical)).toBe(original);
    expect(decoded.lock_sha256).toBe(historical.lock_sha256);
  });

  it("rejects partial compatibility fields, duplicate IDs, and invalid timeouts", async () => {
    const plan = await rulePlan();
    const first = plan.lock.nodes[0]!;
    const withoutArtifacts = Object.fromEntries(Object.entries(first)
      .filter(([key]) => key !== "artifacts"));
    const partial = rehashLock({
      ...plan.lock,
      nodes: [withoutArtifacts],
    });
    expect(() => decodeFactoryRunLockV1(partial)).toThrow("FACTORY_LOCK_INVALID");

    const duplicate = rehashLock({
      ...plan.lock,
      nodes: [{ ...first, tools: [first.tools[0]!, first.tools[0]!] }],
    });
    expect(() => decodeFactoryRunLockV1(duplicate))
      .toThrow("FACTORY_RUNTIME_MATERIAL_DUPLICATE");

    const invalidTimeout = rehashLock({
      ...plan.lock,
      nodes: [{ ...first, execution_timeout_ms: 300_001 }],
    });
    expect(() => decodeFactoryRunLockV1(invalidTimeout))
      .toThrow("FACTORY_PROVIDER_TIMEOUT_INVALID");
  });

  it("keeps executable and artifact kinds separate", async () => {
    await expect(resolveFactoryToolV1("tla2tools"))
      .rejects.toThrow("FACTORY_ARTIFACT_KIND_INVALID");
    await expect(resolveFactoryArtifactHandleV1("java"))
      .rejects.toThrow("FACTORY_ARTIFACT_KIND_INVALID");
  });

  it("uses explicit Java and JAR selectors and ignores PATH shadows", async () => {
    const root = await temporaryRoot();
    const java = resolve(root, "java-explicit");
    const shadow = resolve(root, "java");
    const jar = resolve(root, "tla2tools.jar");
    await writeFile(java, "#!/bin/sh\nprintf 'java fixture 17.0.1\\n' >&2\n");
    await writeFile(shadow, "#!/bin/sh\nprintf 'shadow\\n' >&2\n");
    await Promise.all([chmod(java, 0o755), chmod(shadow, 0o755)]);
    await writeFile(jar, storedJar("1.8.0-fixture"));
    process.env.PATH = root;
    process.env.DOMAINSPEC_FACTORY_JAVA_BIN = java;
    process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR = jar;

    const tool = await resolveFactoryToolHandleV1("java");
    const artifact = await resolveFactoryArtifactHandleV1("tla2tools");
    expect(tool.path).toBe(java);
    expect(tool.locked.version).toBe("java fixture 17.0.1");
    expect(artifact.path).toBe(jar);
    expect(artifact.locked.version).toBe("1.8.0-fixture");
  });

  it("rejects relative, symlinked, missing, and malformed selectors", async () => {
    const root = await temporaryRoot();
    const java = resolve(root, "java-real");
    const linked = resolve(root, "java-linked");
    const jar = resolve(root, "bad.jar");
    await writeFile(java, "#!/bin/sh\nprintf 'java fixture\\n' >&2\n");
    await chmod(java, 0o755);
    await symlink(java, linked);
    process.env.DOMAINSPEC_FACTORY_JAVA_BIN = "relative/java";
    await expect(resolveFactoryToolHandleV1("java")).rejects.toThrow("FACTORY_TOOL_INVALID");
    process.env.DOMAINSPEC_FACTORY_JAVA_BIN = linked;
    await expect(resolveFactoryToolHandleV1("java")).rejects.toThrow("FACTORY_TOOL_INVALID");
    process.env.DOMAINSPEC_FACTORY_JAVA_BIN = resolve(root, "missing-java");
    await expect(resolveFactoryToolHandleV1("java")).rejects.toThrow("FACTORY_TOOL_INVALID");
    await writeFile(jar, Buffer.from("not-a-jar"));
    process.env.DOMAINSPEC_FACTORY_TLA2TOOLS_JAR = jar;
    await expect(resolveFactoryArtifactHandleV1("tla2tools"))
      .rejects.toThrow("FACTORY_ARTIFACT_INVALID");
  });
});
