import {readFile, stat} from "node:fs/promises";
import {resolve} from "node:path";

import {describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/factory-node-registry-v1.js";
import {operationPythonV1Provider} from
  "../../../../factory/registry/providers/operation-python-v1.js";
import {operationRustV1Provider} from
  "../../../../factory/registry/providers/operation-rust-v1.js";
import {operationTypeScriptV1Provider} from
  "../../../../factory/registry/providers/operation-typescript-v1.js";
import {PYTHON_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/python/state-changing-v1/index.js";
import {RUST_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/rust/state-changing-v1/index.js";
import {TYPESCRIPT_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/typescript/state-changing-v1/index.js";
import {
  computeBindingSha256,
  evaluateOperationRegistryNegative,
  sha256Bytes,
  type OperationRegistryNegativeInput,
} from "./evaluate-operation-registry-negative.js";

type JsonObject = Record<string, any>;
const repositoryRoot = process.cwd();
const bindingPath =
  "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
  "operation/wp-rmt-002/registry-negative/" +
  "operation-registry-negative-binding.json";
const registryPath =
  "projects/domainspec-v2/impl/architecture-conformance/factory/registry/" +
  "factory-node-registry-v1.ts";

const PROVIDER_CASES = Object.freeze([
  Object.freeze({
    language: "typescript",
    export_name: "operationTypeScriptV1Provider",
    provider: operationTypeScriptV1Provider,
    paths: TYPESCRIPT_OPERATION_RAW_PATHS,
  }),
  Object.freeze({
    language: "python",
    export_name: "operationPythonV1Provider",
    provider: operationPythonV1Provider,
    paths: PYTHON_OPERATION_RAW_PATHS,
  }),
  Object.freeze({
    language: "rust",
    export_name: "operationRustV1Provider",
    provider: operationRustV1Provider,
    paths: RUST_OPERATION_RAW_PATHS,
  }),
]);

const readRaw = async (
  paths: Readonly<Record<string, string>>,
): Promise<Record<string, string>> => Object.fromEntries(await Promise.all(
  Object.entries(paths).map(async ([role, path]) => [
    role,
    await readFile(resolve(repositoryRoot, path), "utf8"),
  ]),
));

const statProjection = async (path: string): Promise<Record<string, string>> => {
  const value = await stat(resolve(repositoryRoot, path), {bigint: true});
  return {
    dev: value.dev.toString(),
    ino: value.ino.toString(),
    size: value.size.toString(),
    mtime_ns: value.mtimeNs.toString(),
    ctime_ns: value.ctimeNs.toString(),
  };
};

const buildInput = async (): Promise<OperationRegistryNegativeInput> => {
  const beforeRaw = await readFile(resolve(repositoryRoot, registryPath), "utf8");
  const beforeStat = await statProjection(registryPath);
  const bindingRaw = await readFile(resolve(repositoryRoot, bindingPath), "utf8");
  const binding = JSON.parse(bindingRaw) as JsonObject;
  const rawInputs = Object.fromEntries(await Promise.all(
    binding.sources.map(async ({role, path}: JsonObject) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ]),
  ));
  const providerObservations = await Promise.all(PROVIDER_CASES.map(
    async ({language, export_name: exportName, provider, paths}) => ({
      language,
      export_name: exportName,
      provider_id: provider.provider_id,
      provider_version: provider.provider_version,
      required_input_roles: [...provider.required_input_roles],
      raw_paths: {...paths},
      raw_inputs: await readRaw(paths),
    }),
  ));
  const runtimeProviders = listFactoryNodeProvidersV1().map((provider) => ({
    provider_id: provider.provider_id,
    provider_version: provider.provider_version,
  }));
  const afterRaw = await readFile(resolve(repositoryRoot, registryPath), "utf8");
  const afterStat = await statProjection(registryPath);
  expect(beforeRaw).toBe(rawInputs.canonical_registry);
  return {
    binding_raw: bindingRaw,
    raw_inputs: rawInputs,
    registry_observation: {
      after_raw: afterRaw,
      before_stat: beforeStat,
      after_stat: afterStat,
      runtime_providers: runtimeProviders,
    },
    provider_observations: providerObservations,
  };
};

const cloneInput = (
  input: OperationRegistryNegativeInput,
): JsonObject => structuredClone(input) as JsonObject;

const rebindSource = (
  input: JsonObject,
  role: string,
  raw: string,
): void => {
  const binding = JSON.parse(input.binding_raw) as JsonObject;
  const source = binding.sources.find((entry: JsonObject) =>
    entry.role === role) as JsonObject | undefined;
  if (!source) throw new Error(`missing source role ${role}`);
  source.sha256 = sha256Bytes(raw);
  source.size_bytes = Buffer.byteLength(raw, "utf8");
  binding.binding_sha256 = computeBindingSha256(binding);
  input.binding_raw = `${JSON.stringify(binding, null, 2)}\n`;
  input.raw_inputs[role] = raw;
  if (role === "canonical_registry") {
    input.registry_observation.after_raw = raw;
  }
};

const expectCode = (input: JsonObject, code: string): void => {
  try {
    evaluateOperationRegistryNegative(
      input as unknown as OperationRegistryNegativeInput,
    );
    throw new Error("unexpected pass");
  } catch (error) {
    expect(error).toMatchObject({code});
    expect((error as Error).message).toBe(code);
  }
};

describe("RMT-OP-009 exact Operation provider registry non-membership", () => {
  it("proves the three exact direct providers remain unregistered and bound", async () => {
    const input = await buildInput();
    const proof = evaluateOperationRegistryNegative(input);
    expect(proof).toMatchObject({
      schema_version: "OperationRegistryNegativeProof/v1",
      result: "pass",
      semantic_plan_epoch_id: "WP-RMT-002/S1/2026-08-16",
      semantic_contract_digest:
        "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7",
      source_count: 8,
      source_size_bytes: 2749128,
      provider_files_exact: true,
      canonical_registry_snapshot_exact: true,
      s1_providers_unregistered: true,
      s1_binding_retained: true,
      no_registration_write: true,
      no_self_authored_authority: true,
      authority_effect: "none",
      claim_ceiling: "exact-live-snapshot-nonmembership-and-no-write-only",
      registry: {
        sha256:
          "2497f2e047e023de2738bac4b815e6b0212560dcfc8053982c94f4a529a9f51b",
        size_bytes: 5105,
        provider_import_count: 39,
        provider_symbol_count: 39,
        runtime_identity_count: 39,
        legacy_operation_provider_id: "typescript-operation-v1",
        legacy_operation_provider_present: true,
        direct_provider_ids_absent: true,
        before_after_bytes_equal: true,
        before_after_stat_equal: true,
      },
    });
    expect(proof.direct_providers).toEqual([
      expect.objectContaining({
        language: "typescript",
        provider_id: "operation-typescript-v1",
        registered: false,
        binding_retained: true,
        binding_id: "typescript.complete-settlement.bound-operation/v1",
        bound_ref_count: 34,
      }),
      expect.objectContaining({
        language: "python",
        provider_id: "operation-python-v1",
        registered: false,
        binding_retained: true,
        binding_id: "python.complete-settlement.bound-operation/v1",
        bound_ref_count: 35,
      }),
      expect.objectContaining({
        language: "rust",
        provider_id: "operation-rust-v1",
        registered: false,
        binding_retained: true,
        binding_id: "rust.complete-settlement.bound-operation/v1",
        bound_ref_count: 34,
      }),
    ]);
    expect(proof.proof_sha256).toMatch(/^[a-f0-9]{64}$/u);
  });

  it("keeps the legacy TypeScript provider distinct from the direct provider", async () => {
    const input = await buildInput();
    const ids = input.registry_observation.runtime_providers.map(
      ({provider_id: providerId}) => providerId,
    );
    expect(ids).toContain("typescript-operation-v1");
    expect(ids).not.toContain("operation-typescript-v1");
    expect(ids.filter((id) => id === "typescript-operation-v1")).toHaveLength(1);
  });

  it("rejects direct registration, direct imports, and aliases exactly", async () => {
    const base = await buildInput();

    const present = cloneInput(base);
    const appended = present.raw_inputs.canonical_registry.replace(
      "] as const);",
      "  operationTypeScriptV1Provider,\n] as const);",
    );
    rebindSource(present, "canonical_registry", appended);
    present.registry_observation.runtime_providers.push({
      provider_id: "operation-typescript-v1",
      provider_version: "1.0.0",
    });
    expectCode(present, "RMT_OP_REGISTRY_DIRECT_PROVIDER_PRESENT");

    const imported = cloneInput(base);
    const directImport =
      "import {operationTypeScriptV1Provider} from " +
      '"./providers/operation-typescript-v1.js";\n' +
      imported.raw_inputs.canonical_registry;
    rebindSource(imported, "canonical_registry", directImport);
    expectCode(imported, "RMT_OP_REGISTRY_DIRECT_PROVIDER_IMPORT");

    const aliased = cloneInput(base);
    const aliasImport =
      "import {operationTypeScriptV1Provider as hiddenProvider} from " +
      '"./providers/operation-typescript-v1.js";\n' +
      aliased.raw_inputs.canonical_registry;
    rebindSource(aliased, "canonical_registry", aliasImport);
    expectCode(aliased, "RMT_OP_REGISTRY_DIRECT_PROVIDER_IMPORT");
  });

  it("rejects duplicate identities and registry order or byte drift", async () => {
    const base = await buildInput();
    const duplicate = cloneInput(base);
    const duplicatedSource = duplicate.raw_inputs.canonical_registry.replace(
      "  typeScriptRuleV1Provider,\n",
      "  typeScriptRuleV1Provider,\n  typeScriptRuleV1Provider,\n",
    );
    rebindSource(duplicate, "canonical_registry", duplicatedSource);
    duplicate.registry_observation.runtime_providers.push(
      structuredClone(duplicate.registry_observation.runtime_providers[0]),
    );
    expectCode(duplicate, "RMT_OP_REGISTRY_DUPLICATE_IDENTITY");

    const reordered = cloneInput(base);
    const reorderedSource = reordered.raw_inputs.canonical_registry.replace(
      "  typeScriptRuleV1Provider,\n  pythonRuleV1Provider,\n",
      "  pythonRuleV1Provider,\n  typeScriptRuleV1Provider,\n",
    );
    rebindSource(reordered, "canonical_registry", reorderedSource);
    [
      reordered.registry_observation.runtime_providers[0],
      reordered.registry_observation.runtime_providers[1],
    ] = [
      reordered.registry_observation.runtime_providers[1],
      reordered.registry_observation.runtime_providers[0],
    ];
    expectCode(reordered, "RMT_OP_REGISTRY_SNAPSHOT_DRIFT");

    const whitespace = cloneInput(base);
    rebindSource(
      whitespace,
      "canonical_registry",
      `${whitespace.raw_inputs.canonical_registry}\n`,
    );
    expectCode(whitespace, "RMT_OP_REGISTRY_SNAPSHOT_DRIFT");
  });

  it("rejects changed provider identity and retained-binding drift", async () => {
    const base = await buildInput();
    const providerDrift = cloneInput(base);
    const changedProvider = providerDrift.raw_inputs.provider_typescript
      .replaceAll('"operation-typescript-v1"', '"operation-typescript-v2"');
    rebindSource(providerDrift, "provider_typescript", changedProvider);
    expectCode(providerDrift, "RMT_OP_PROVIDER_FILE_DRIFT");

    const bindingDrift = cloneInput(base);
    const rawBinding = JSON.parse(
      bindingDrift.provider_observations[0].raw_inputs.binding,
    ) as JsonObject;
    rawBinding.observer_id = "observer.fabricated/v1";
    bindingDrift.provider_observations[0].raw_inputs.binding =
      `${JSON.stringify(rawBinding, null, 2)}\n`;
    expectCode(bindingDrift, "RMT_OP_PROVIDER_BINDING_DRIFT");

    const staleRef = cloneInput(base);
    const reboundBinding = JSON.parse(
      staleRef.provider_observations[1].raw_inputs.binding,
    ) as JsonObject;
    reboundBinding.refs.source.sha256 = "e".repeat(64);
    reboundBinding.binding_sha256 = computeBindingSha256(reboundBinding);
    staleRef.provider_observations[1].raw_inputs.binding =
      `${JSON.stringify(reboundBinding, null, 2)}\n`;
    expectCode(staleRef, "RMT_OP_PROVIDER_BINDING_DRIFT");
  });

  it("rejects a registry write even when the runtime identities still look valid", async () => {
    const input = cloneInput(await buildInput());
    input.registry_observation.after_raw =
      `${input.registry_observation.after_raw}\n`;
    expectCode(input, "RMT_OP_REGISTRY_WRITE_DETECTED");

    const metadataWrite = cloneInput(await buildInput());
    metadataWrite.registry_observation.after_stat.mtime_ns =
      (BigInt(metadataWrite.registry_observation.after_stat.mtime_ns) + 1n)
        .toString();
    expectCode(metadataWrite, "RMT_OP_REGISTRY_WRITE_DETECTED");
  });

  it("strictly rejects nested surplus input and authority inflation", async () => {
    const nested = cloneInput(await buildInput());
    nested.provider_observations[0].oracle_hint = "accept";
    expectCode(nested, "RMT_OP_PROVIDER_OBSERVATION_INVALID");

    const authority = cloneInput(await buildInput());
    const binding = JSON.parse(authority.binding_raw) as JsonObject;
    binding.authority_effect = "registration";
    binding.binding_sha256 = computeBindingSha256(binding);
    authority.binding_raw = `${JSON.stringify(binding, null, 2)}\n`;
    expectCode(authority, "RMT_OP_REGISTRY_BINDING_INVALID");
  });
});
