import { execFile } from "node:child_process";
import { access, lstat, readFile, realpath } from "node:fs/promises";
import { delimiter, dirname, isAbsolute, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import { inflateRawSync } from "node:zlib";

import type { LockedFactoryArtifactV1 } from
  "../contracts/factory-locked-artifact-v1.js";
import type { LockedFactoryToolV1 } from "../contracts/factory-run-lock-v1.js";
import { fail, sha256 } from "../shared/canonical.js";

const here = dirname(fileURLToPath(import.meta.url));
const implementationRoot = resolve(here, "../../..");
const execute = promisify(execFile);

export type ResolvedFactoryToolV1 = Readonly<{
  locked: LockedFactoryToolV1;
  path: string;
}>;

export type ResolvedFactoryArtifactV1 = Readonly<{
  locked: LockedFactoryArtifactV1;
  path: string;
}>;

export const resolveFactoryExecutablePath = async (toolId: string): Promise<string> => {
  const executableName = toolId === "python" ? "python3" : toolId;
  for (const directory of (process.env.PATH ?? "").split(delimiter)) {
    if (directory.length === 0) continue;
    const candidate = resolve(directory, executableName);
    try {
      await access(candidate);
      return candidate;
    } catch {
      // Continue through the explicit PATH search.
    }
  }
  return fail("FACTORY_TOOL_MISSING", toolId);
};

const executableTool = async (toolId: "python" | "cargo" | "rustc") => {
  const executable = await resolveFactoryExecutablePath(toolId);
  const { stdout, stderr } = await execute(executable, ["--version"], {
    env: {},
    timeout: 10_000,
  }).catch(() => fail("FACTORY_TOOL_INVALID", toolId));
  const version = `${stdout}${stderr}`.trim();
  if (version.length === 0) fail("FACTORY_TOOL_INVALID", toolId);
  return Object.freeze({
    tool_id: toolId,
    version,
    executable_sha256: sha256(await readFile(await realpath(executable))),
  });
};

const packageTool = async (toolId: "tsx" | "typescript"): Promise<ResolvedFactoryToolV1> => {
  const path = resolve(implementationRoot, `node_modules/${toolId}/package.json`);
  let bytes: Buffer;
  let owned: string;
  try {
    owned = await realpath(path);
    bytes = await readFile(owned);
  } catch {
    return fail("FACTORY_TOOL_MISSING", toolId);
  }
  const parsed = JSON.parse(bytes.toString("utf8")) as { version?: unknown };
  const version = typeof parsed.version === "string"
    ? parsed.version : fail("FACTORY_TOOL_INVALID", toolId);
  return Object.freeze({
    locked: Object.freeze({
      tool_id: toolId,
      version,
      executable_sha256: sha256(bytes),
    }),
    path: owned,
  });
};

const explicitSelector = async (
  environmentKey: string,
  code: "FACTORY_TOOL_INVALID" | "FACTORY_ARTIFACT_INVALID",
  id: string,
): Promise<Readonly<{ path: string; bytes: Buffer }>> => {
  const selected = process.env[environmentKey] ?? fail(code, id);
  if (!isAbsolute(selected)) fail(code, id);
  const stat = await lstat(selected).catch(() => fail(code, id));
  if (!stat.isFile() || stat.isSymbolicLink()) fail(code, id);
  const owned = await realpath(selected).catch(() => fail(code, id));
  if (owned !== selected) fail(code, id);
  const bytes = await readFile(owned).catch(() => fail(code, id));
  return Object.freeze({ path: owned, bytes });
};

const javaTool = async (): Promise<ResolvedFactoryToolV1> => {
  const selected = await explicitSelector(
    "DOMAINSPEC_FACTORY_JAVA_BIN",
    "FACTORY_TOOL_INVALID",
    "java",
  );
  const { stdout, stderr } = await execute(selected.path, ["-version"], {
    env: {},
    timeout: 10_000,
  }).catch(() => fail("FACTORY_TOOL_INVALID", "java"));
  const version = `${stdout}${stderr}`.trim();
  if (version.length === 0) fail("FACTORY_TOOL_INVALID", "java");
  return Object.freeze({
    locked: Object.freeze({
      tool_id: "java",
      version,
      executable_sha256: sha256(selected.bytes),
    }),
    path: selected.path,
  });
};

const readJarManifestVersion = (jar: Buffer): string => {
  const minimumEocd = 22;
  const searchStart = Math.max(0, jar.length - 65_557);
  let eocd = -1;
  for (let offset = jar.length - minimumEocd; offset >= searchStart; offset -= 1) {
    if (jar.readUInt32LE(offset) === 0x06054b50) {
      eocd = offset;
      break;
    }
  }
  if (eocd < 0 || eocd + minimumEocd > jar.length) {
    return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
  }
  const entryCount = jar.readUInt16LE(eocd + 10);
  const directorySize = jar.readUInt32LE(eocd + 12);
  const directoryOffset = jar.readUInt32LE(eocd + 16);
  if (directoryOffset + directorySize > eocd) {
    return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
  }
  let cursor = directoryOffset;
  for (let index = 0; index < entryCount; index += 1) {
    if (cursor + 46 > jar.length || jar.readUInt32LE(cursor) !== 0x02014b50) {
      return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
    }
    const method = jar.readUInt16LE(cursor + 10);
    const compressedSize = jar.readUInt32LE(cursor + 20);
    const uncompressedSize = jar.readUInt32LE(cursor + 24);
    const nameLength = jar.readUInt16LE(cursor + 28);
    const extraLength = jar.readUInt16LE(cursor + 30);
    const commentLength = jar.readUInt16LE(cursor + 32);
    const localOffset = jar.readUInt32LE(cursor + 42);
    const nameEnd = cursor + 46 + nameLength;
    if (nameEnd > jar.length) fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
    const name = jar.subarray(cursor + 46, nameEnd).toString("utf8");
    if (name === "META-INF/MANIFEST.MF") {
      if (localOffset + 30 > jar.length || jar.readUInt32LE(localOffset) !== 0x04034b50) {
        return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
      }
      const localNameLength = jar.readUInt16LE(localOffset + 26);
      const localExtraLength = jar.readUInt16LE(localOffset + 28);
      const dataOffset = localOffset + 30 + localNameLength + localExtraLength;
      if (dataOffset + compressedSize > jar.length || uncompressedSize > 1_048_576) {
        return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
      }
      const compressed = jar.subarray(dataOffset, dataOffset + compressedSize);
      let manifest: Buffer;
      try {
        manifest = method === 0 ? Buffer.from(compressed)
          : method === 8 ? inflateRawSync(compressed)
            : fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
      } catch {
        return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
      }
      if (manifest.byteLength !== uncompressedSize) {
        return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
      }
      const logical: string[] = [];
      for (const line of manifest.toString("utf8").replaceAll("\r\n", "\n").split("\n")) {
        if (line.startsWith(" ") && logical.length > 0) logical[logical.length - 1] += line.slice(1);
        else logical.push(line);
      }
      const fields = new Map(logical.flatMap((line) => {
        const separator = line.indexOf(": ");
        return separator < 1 ? [] : [[line.slice(0, separator), line.slice(separator + 2)]];
      }));
      const version = fields.get("Implementation-Version") ??
        fields.get("Specification-Version") ?? fields.get("Bundle-Version");
      return version !== undefined && version.length > 0
        ? version : fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
    }
    cursor = nameEnd + extraLength + commentLength;
  }
  return fail("FACTORY_ARTIFACT_INVALID", "tla2tools");
};

export const resolveFactoryToolHandleV1 = async (
  toolId: string,
): Promise<ResolvedFactoryToolV1> => {
  if (toolId === "tla2tools") fail("FACTORY_ARTIFACT_KIND_INVALID", toolId);
  if (toolId === "java") return javaTool();
  if (toolId === "node") {
    const executable = await realpath(process.execPath);
    return Object.freeze({
      locked: Object.freeze({
        tool_id: "node",
        version: process.version,
        executable_sha256: sha256(await readFile(executable)),
      }),
      path: executable,
    });
  }
  if (toolId === "tsx" || toolId === "typescript") return packageTool(toolId);
  if (toolId === "python" || toolId === "cargo" || toolId === "rustc") {
    const locked = await executableTool(toolId);
    return Object.freeze({
      locked,
      path: await realpath(await resolveFactoryExecutablePath(toolId)),
    });
  }
  return fail("FACTORY_TOOL_UNKNOWN", toolId);
};

export const resolveFactoryToolV1 = async (toolId: string): Promise<LockedFactoryToolV1> =>
  (await resolveFactoryToolHandleV1(toolId)).locked;

export const resolveFactoryArtifactHandleV1 = async (
  artifactId: string,
): Promise<ResolvedFactoryArtifactV1> => {
  if (artifactId === "java") fail("FACTORY_ARTIFACT_KIND_INVALID", artifactId);
  if (artifactId !== "tla2tools") return fail("FACTORY_ARTIFACT_INVALID", artifactId);
  const selected = await explicitSelector(
    "DOMAINSPEC_FACTORY_TLA2TOOLS_JAR",
    "FACTORY_ARTIFACT_INVALID",
    artifactId,
  );
  return Object.freeze({
    locked: Object.freeze({
      schema_version: "LockedFactoryArtifact/v1",
      artifact_id: artifactId,
      version: readJarManifestVersion(selected.bytes),
      sha256: sha256(selected.bytes),
    }),
    path: selected.path,
  });
};

export const resolveFactoryArtifactV1 = async (
  artifactId: string,
): Promise<LockedFactoryArtifactV1> =>
  (await resolveFactoryArtifactHandleV1(artifactId)).locked;
