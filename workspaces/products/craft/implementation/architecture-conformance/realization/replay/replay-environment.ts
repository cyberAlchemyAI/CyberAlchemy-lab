import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { resolve } from "node:path";

import type {
  ReplayComponentName,
  ReplayEnvironment,
} from "../contracts/replay-result.js";
import { enumMutationConfigSha256 } from "../mutation/remove-enum-member.js";
import { typescriptCompilerConfigSha256 } from "../../typescript/compiler/enum/compile-generated-enum.js";

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};

export const REPLAY_COMPONENT_PATHS: Readonly<
  Record<ReplayComponentName, string>
> = Object.freeze({
  generator:
    "projects/domainspec-v2/impl/architecture-conformance/typescript/generator/enum/emit-enum.ts",
  adapter:
    "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter/enum/index.ts",
  evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/realization/evaluator/evaluate-enum-bijection.ts",
  compiler:
    "projects/domainspec-v2/impl/architecture-conformance/typescript/compiler/enum/compile-generated-enum.ts",
  mutator:
    "projects/domainspec-v2/impl/architecture-conformance/realization/mutation/remove-enum-member.ts",
  registry:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/registry/realization-registry-v2.ts",
  family:
    "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/index.ts",
  target:
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/index.ts",
  realization:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/typescript/owned-const-object-v1/index.ts",
  registration:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/typescript/owned-const-object-v1/registration.ts",
  replay_parent:
    "projects/domainspec-v2/impl/architecture-conformance/realization/replay/replay-enum-proof.ts",
  replay_child:
    "projects/domainspec-v2/impl/architecture-conformance/realization/replay/child-entry.ts",
});

const replayProtocolConfigSha256 = sha256(
  JSON.stringify({
    schema_version: "ReplayRawIndex/v2",
    child_transport: "node-import-tsx-request-path/v1",
    raw_input_mode: "exact-file-digest",
    terminal_receipt_input: "forbidden",
  }),
);

const packageVersion = async (path: string): Promise<string> => {
  const parsed = JSON.parse(await readFile(path, "utf8")) as { version?: unknown };
  if (typeof parsed.version !== "string" || parsed.version.length === 0) {
    return fail("ARCH_REPLAY_TOOLCHAIN_INVALID");
  }
  return parsed.version;
};

export const createReplayEnvironment = async (
  repositoryRoot: string,
): Promise<ReplayEnvironment> => {
  const root = resolve(repositoryRoot);
  const implementationRoot = resolve(root, "projects/domainspec-v2/impl");
  const require = createRequire(resolve(implementationRoot, "package.json"));
  const tsxPath = require.resolve("tsx");
  const typescriptPath = require.resolve("typescript");
  const [nodeBytes, tsxBytes, typescriptBytes, tsxVersion, typescriptVersion] =
    await Promise.all([
      readFile(process.execPath),
      readFile(tsxPath),
      readFile(typescriptPath),
      packageVersion(require.resolve("tsx/package.json")),
      packageVersion(require.resolve("typescript/package.json")),
    ]);
  const components = Object.fromEntries(
    await Promise.all(
      Object.entries(REPLAY_COMPONENT_PATHS).map(async ([name, path]) => [
        name,
        Object.freeze({
          path,
          sha256: sha256(await readFile(resolve(root, path))),
        }),
      ]),
    ),
  ) as ReplayEnvironment["components"];
  return Object.freeze({
    components: Object.freeze(components),
    toolchain: Object.freeze({
      node: Object.freeze({
        path: process.execPath,
        version: process.version,
        sha256: sha256(nodeBytes),
      }),
      tsx_loader: Object.freeze({
        path: tsxPath,
        version: tsxVersion,
        sha256: sha256(tsxBytes),
      }),
      typescript: Object.freeze({
        path: typescriptPath,
        version: typescriptVersion,
        sha256: sha256(typescriptBytes),
      }),
    }),
    config: Object.freeze({
      compiler_sha256: typescriptCompilerConfigSha256,
      mutator_sha256: enumMutationConfigSha256,
      replay_protocol_sha256: replayProtocolConfigSha256,
    }),
  });
};

const exactKeys = (actual: object, expected: readonly string[]): boolean => {
  const keys = Object.keys(actual).sort();
  return keys.length === expected.length &&
    keys.every((key, index) => key === [...expected].sort()[index]);
};

export const validateReplayEnvironment = async (
  repositoryRoot: string,
  admitted: ReplayEnvironment,
): Promise<ReplayEnvironment> => {
  if (!exactKeys(admitted.components, Object.keys(REPLAY_COMPONENT_PATHS)) ||
      !exactKeys(admitted.toolchain, ["node", "tsx_loader", "typescript"]) ||
      !exactKeys(admitted.config, [
        "compiler_sha256",
        "mutator_sha256",
        "replay_protocol_sha256",
      ])) {
    return fail("ARCH_REPLAY_ENVIRONMENT_INVALID");
  }
  const current = await createReplayEnvironment(repositoryRoot);
  for (const name of Object.keys(REPLAY_COMPONENT_PATHS) as ReplayComponentName[]) {
    const expected = current.components[name];
    const supplied = admitted.components[name];
    if (supplied.path !== expected.path || supplied.sha256 !== expected.sha256) {
      return fail("ARCH_REPLAY_COMPONENT_TAMPERED");
    }
  }
  if (JSON.stringify(admitted.toolchain) !== JSON.stringify(current.toolchain)) {
    return fail("ARCH_REPLAY_TOOLCHAIN_TAMPERED");
  }
  if (JSON.stringify(admitted.config) !== JSON.stringify(current.config)) {
    return fail("ARCH_REPLAY_CONFIG_TAMPERED");
  }
  return current;
};
