import {createHash} from "node:crypto";

import ts from "typescript";

type JsonObject = Record<string, unknown>;
type RawInputs = Readonly<Record<string, string>>;

export const REQUIRED_SEMANTIC_PLAN_EPOCH = "WP-RMT-002/S1/2026-08-16";
export const REQUIRED_SEMANTIC_CONTRACT_DIGEST =
  "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7";

const REGISTRY_PATH =
  "projects/domainspec-v2/impl/architecture-conformance/factory/registry/" +
  "factory-node-registry-v1.ts";
const REQUIRED_COMMAND =
  "projects/domainspec-v2/impl/node_modules/.bin/vitest run --root " +
  "projects/domainspec-v2/impl architecture-conformance/acceptance/" +
  "operation/wp-rmt-002/registry-negative";

const SOURCE_EXPECTATIONS = Object.freeze([
  Object.freeze({
    role: "swu_contracts",
    path: "projects/domainspec-v2/development/refinement-runs/" +
      "20260814T193343Z-active-meta-type-implementations/refreshes/" +
      "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
      "SWU-CONTRACTS.json",
    sha256: "a1e9158f7fff7f78d5820237c6f276a07c4c658610a51fc91ca026f7e41faa11",
    size_bytes: 2679223,
  }),
  Object.freeze({
    role: "write_scope_baseline",
    path: "projects/domainspec-v2/development/refinement-runs/" +
      "20260814T193343Z-active-meta-type-implementations/refreshes/" +
      "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
      "WRITE-SCOPE-BASELINE.json",
    sha256: "2cba40effd0df63936b53a4337edf22bce5cb39745e26a65cfcef196be76a141",
    size_bytes: 44582,
  }),
  Object.freeze({
    role: "task_operation",
    path: "projects/domainspec-v2/development/refinement-runs/" +
      "20260814T193343Z-active-meta-type-implementations/refreshes/" +
      "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
      "tasks/TASK-RMT-OP.md",
    sha256: "a042af716feda5e77b68ace4bb5018a9264fb8f4e40cae0fb260547c3d9b6869",
    size_bytes: 1507,
  }),
  Object.freeze({
    role: "canonical_registry",
    path: REGISTRY_PATH,
    sha256: "2497f2e047e023de2738bac4b815e6b0212560dcfc8053982c94f4a529a9f51b",
    size_bytes: 5105,
  }),
  Object.freeze({
    role: "provider_typescript",
    path: "projects/domainspec-v2/impl/architecture-conformance/factory/" +
      "registry/providers/operation-typescript-v1.ts",
    sha256: "1bc82cc0284069bfaa115f4bd51e423e259c6b38428a6a8d980132e9ba05a06f",
    size_bytes: 2150,
  }),
  Object.freeze({
    role: "provider_python",
    path: "projects/domainspec-v2/impl/architecture-conformance/factory/" +
      "registry/providers/operation-python-v1.ts",
    sha256: "04c5931e9daa3a281f49d506889058df991170f5f21b8766a5b48d7ff2f9a967",
    size_bytes: 4504,
  }),
  Object.freeze({
    role: "provider_rust",
    path: "projects/domainspec-v2/impl/architecture-conformance/factory/" +
      "registry/providers/operation-rust-v1.ts",
    sha256: "c34962ceef4fa5eabd6ccef9f7df100e31e3296ae7beef1f68d19aeb317f3629",
    size_bytes: 3928,
  }),
  Object.freeze({
    role: "op006_live_parity_test",
    path: "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
      "operation/wp-rmt-002/parity/live-operation-parity.test.ts",
    sha256: "a830f1e19134830db139639b9babf894ddadbef0e859068ead162af6bb0dda9c",
    size_bytes: 8129,
  }),
]);

const ORDERED_PROVIDER_IDS = Object.freeze([
  "typescript-rule-v1",
  "python-rule-v1",
  "rust-rule-v1",
  "rule-parity-v1",
  "reference-readiness-v1",
  "typescript-operation-v1",
  "typescript-enforces-v1",
  "typescript-enum-order-status-v1",
  "typescript-enum-shipment-priority-v1",
  "typescript-enum-shipment-priority-semantic-slice-v1",
  "python-enum-v1",
  "rust-enum-v1",
  "enum-composition-v1",
  "enum-parity-v1",
  "typescript-calculation-v1",
  "python-calculation-v1",
  "rust-calculation-v1",
  "calculation-parity-v1",
  "typescript-policy-v1",
  "python-policy-v1",
  "rust-policy-v1",
  "policy-parity-v1",
  "policy-selects-strategy-v1",
  "typescript-query-v1",
  "python-query-v1",
  "rust-query-v1",
  "query-parity-v1",
  "typescript-value-object-v1",
  "python-value-object-v1",
  "rust-value-object-v1",
  "value-object-parity-v1",
  "value-object-relations-v1",
  "typescript-entity-v1",
  "python-entity-v1",
  "rust-entity-v1",
  "entity-parity-v1",
  "entity-relations-v1",
  "typescript-w3-effects-connections-v1",
  "typescript-w4-orchestration-lifecycle-v1",
]);

const DIRECT_EXPECTATIONS = Object.freeze([
  Object.freeze({
    language: "typescript",
    provider_id: "operation-typescript-v1",
    provider_version: "1.0.0",
    export_name: "operationTypeScriptV1Provider",
    source_role: "provider_typescript",
    path: SOURCE_EXPECTATIONS[4]!.path,
    sha256: SOURCE_EXPECTATIONS[4]!.sha256,
    size_bytes: SOURCE_EXPECTATIONS[4]!.size_bytes,
    module_path: "./providers/operation-typescript-v1.js",
    binding: Object.freeze({
      path: "projects/domainspec-v2/impl/architecture-conformance/" +
        "realizations/operation/typescript/state-changing-v1/" +
        "typescript-binding.json",
      file_sha256:
        "c54431ee5d946415df30fffab71528df1928bc8b8f2bdfb49ccc6df7784952b1",
      size_bytes: 9655,
      binding_id: "typescript.complete-settlement.bound-operation/v1",
      binding_sha256:
        "f6bd733fca57611f4849a2f1775fa4cb92cb6252797f1796fc84a5f8e5a4725e",
      required_input_role_count: 35,
      bound_ref_count: 34,
    }),
  }),
  Object.freeze({
    language: "python",
    provider_id: "operation-python-v1",
    provider_version: "1.0.0",
    export_name: "operationPythonV1Provider",
    source_role: "provider_python",
    path: SOURCE_EXPECTATIONS[5]!.path,
    sha256: SOURCE_EXPECTATIONS[5]!.sha256,
    size_bytes: SOURCE_EXPECTATIONS[5]!.size_bytes,
    module_path: "./providers/operation-python-v1.js",
    binding: Object.freeze({
      path: "projects/domainspec-v2/impl/architecture-conformance/" +
        "realizations/operation/python/state-changing-v1/python-binding.json",
      file_sha256:
        "15545ea614fd9521b53f8f2605fcefbce8d6be334bd9909a7f9271cd1d6774d2",
      size_bytes: 9900,
      binding_id: "python.complete-settlement.bound-operation/v1",
      binding_sha256:
        "588b2018a8180e6a6def4ace3196ae8f28fe6d080cb2a5bc4d641352e434bd4b",
      required_input_role_count: 36,
      bound_ref_count: 35,
    }),
  }),
  Object.freeze({
    language: "rust",
    provider_id: "operation-rust-v1",
    provider_version: "1.0.0",
    export_name: "operationRustV1Provider",
    source_role: "provider_rust",
    path: SOURCE_EXPECTATIONS[6]!.path,
    sha256: SOURCE_EXPECTATIONS[6]!.sha256,
    size_bytes: SOURCE_EXPECTATIONS[6]!.size_bytes,
    module_path: "./providers/operation-rust-v1.js",
    binding: Object.freeze({
      path: "projects/domainspec-v2/impl/architecture-conformance/" +
        "realizations/operation/rust/state-changing-v1/rust-binding.json",
      file_sha256:
        "e3ab4c0f5c3cae3edebc136eea34c6277214cb5e9a1878d81bad73ff07623db2",
      size_bytes: 9616,
      binding_id: "rust.complete-settlement.bound-operation/v1",
      binding_sha256:
        "473702d02b93fd1e8ea1d48da61387aed93d414be7f116f9209ca017645444d1",
      required_input_role_count: 35,
      bound_ref_count: 34,
    }),
  }),
]);

const EXPECTED_REGISTRY = Object.freeze({
  path: REGISTRY_PATH,
  sha256: SOURCE_EXPECTATIONS[3]!.sha256,
  size_bytes: SOURCE_EXPECTATIONS[3]!.size_bytes,
  provider_import_count: 39,
  provider_import_sha256:
    "d656b25c10bb3824a801e76492d200b1dbd944ccaf417f3b2c823bce69e700e4",
  provider_symbol_count: 39,
  provider_symbol_sha256:
    "5e30c252614de2870da892c8c20caa6985f6754a1712130b31703fefb8518fab",
  runtime_identity_count: 39,
  runtime_identity_sha256:
    "3e0655fd4cb24c68c3070fe4bf1a7d7e8e6f949e4dafea33d6c66896926bd910",
  legacy_operation_provider_id: "typescript-operation-v1",
  ordered_provider_ids: ORDERED_PROVIDER_IDS,
});

const SHA256 = /^[a-f0-9]{64}$/u;
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const exactKeys = (value: JsonObject, keys: readonly string[]): boolean =>
  canonicalJson(Object.keys(value).sort()) === canonicalJson([...keys].sort());
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};
const requireObject = (value: unknown, code: string): JsonObject =>
  isObject(value) ? value : fail(code);
const requireString = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);
const requireNumber = (value: unknown, code: string): number =>
  typeof value === "number" && Number.isSafeInteger(value) && value >= 0
    ? value
    : fail(code);
const requireStringArray = (value: unknown, code: string): string[] => {
  if (!Array.isArray(value) || !value.every((entry) =>
    typeof entry === "string" && entry.length > 0)) return fail(code);
  return [...value];
};
const parseObject = (raw: string, code: string): JsonObject => {
  try {
    return requireObject(JSON.parse(raw) as unknown, code);
  } catch (error) {
    if (error instanceof Error && error.message === code) throw error;
    return fail(code);
  }
};

const canonicalValue = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalValue)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value).sort(([left], [right]) =>
      Buffer.from(left).compare(Buffer.from(right))).map(([key, child]) =>
      [key, canonicalValue(child)]))
    : value;

export const canonicalJson = (value: unknown): string =>
  JSON.stringify(canonicalValue(value));
export const sha256Bytes = (value: string | Buffer): string =>
  createHash("sha256").update(value).digest("hex");
export const sha256Value = (value: unknown): string =>
  sha256Bytes(canonicalJson(value));
export const computeBindingSha256 = (value: JsonObject): string => {
  const {binding_sha256: _ignored, ...body} = value;
  return sha256Value(body);
};

type SourceBinding = Readonly<{
  role: string;
  path: string;
  sha256: string;
  size_bytes: number;
}>;

type DirectBindingExpectation = Readonly<{
  path: string;
  file_sha256: string;
  size_bytes: number;
  binding_id: string;
  binding_sha256: string;
  required_input_role_count: number;
  bound_ref_count: number;
}>;

type DirectProviderExpectation = Readonly<{
  language: string;
  provider_id: string;
  provider_version: string;
  export_name: string;
  source_role: string;
  path: string;
  sha256: string;
  size_bytes: number;
  binding: DirectBindingExpectation;
}>;

type RegistrySnapshot = Readonly<{
  path: string;
  sha256: string;
  size_bytes: number;
  provider_import_count: number;
  provider_import_sha256: string;
  provider_symbol_count: number;
  provider_symbol_sha256: string;
  runtime_identity_count: number;
  runtime_identity_sha256: string;
  legacy_operation_provider_id: string;
  ordered_provider_ids: readonly string[];
}>;

type DecodedBinding = Readonly<{
  semantic_plan_epoch_id: string;
  semantic_contract_digest: string;
  sources: readonly SourceBinding[];
  registry_snapshot: RegistrySnapshot;
  direct_providers: readonly DirectProviderExpectation[];
  authority_effect: "none";
  claim_ceiling: string;
  binding_sha256: string;
}>;

const decodeBinding = (raw: string): DecodedBinding => {
  const code = "RMT_OP_REGISTRY_BINDING_INVALID";
  const value = parseObject(raw, code);
  if (!exactKeys(value, [
    "schema_version", "binding_id", "semantic_plan_epoch_id",
    "semantic_contract_digest", "sources", "registry_snapshot",
    "direct_providers", "authority_effect", "claim_ceiling",
    "binding_sha256",
  ])) return fail(code);
  if (value.schema_version !== "OperationRegistryNegativeBinding/v1" ||
      value.binding_id !== "operation.wp-rmt-002.registry-negative/v1" ||
      value.semantic_plan_epoch_id !== REQUIRED_SEMANTIC_PLAN_EPOCH ||
      value.semantic_contract_digest !== REQUIRED_SEMANTIC_CONTRACT_DIGEST ||
      value.authority_effect !== "none" ||
      value.claim_ceiling !==
        "exact-live-snapshot-nonmembership-and-no-write-only" ||
      typeof value.binding_sha256 !== "string" ||
      !SHA256.test(value.binding_sha256) ||
      computeBindingSha256(value) !== value.binding_sha256) return fail(code);

  if (!Array.isArray(value.sources)) return fail(code);
  const sources = value.sources.map((entry): SourceBinding => {
    const source = requireObject(entry, code);
    if (!exactKeys(source, ["role", "path", "sha256", "size_bytes"])) {
      return fail(code);
    }
    const sha256 = requireString(source.sha256, code);
    if (!SHA256.test(sha256)) return fail(code);
    return Object.freeze({
      role: requireString(source.role, code),
      path: requireString(source.path, code),
      sha256,
      size_bytes: requireNumber(source.size_bytes, code),
    });
  });
  if (sources.length !== SOURCE_EXPECTATIONS.length ||
      new Set(sources.map(({role}) => role)).size !== sources.length) {
    return fail(code);
  }

  const registry = requireObject(value.registry_snapshot, code);
  if (!exactKeys(registry, [
    "path", "sha256", "size_bytes", "provider_import_count",
    "provider_import_sha256", "provider_symbol_count",
    "provider_symbol_sha256", "runtime_identity_count",
    "runtime_identity_sha256", "legacy_operation_provider_id",
    "ordered_provider_ids",
  ])) return fail(code);
  const registrySha = requireString(registry.sha256, code);
  const importSha = requireString(registry.provider_import_sha256, code);
  const symbolSha = requireString(registry.provider_symbol_sha256, code);
  const runtimeSha = requireString(registry.runtime_identity_sha256, code);
  if (![registrySha, importSha, symbolSha, runtimeSha].every((digest) =>
    SHA256.test(digest))) return fail(code);
  const registrySnapshot: RegistrySnapshot = Object.freeze({
    path: requireString(registry.path, code),
    sha256: registrySha,
    size_bytes: requireNumber(registry.size_bytes, code),
    provider_import_count: requireNumber(registry.provider_import_count, code),
    provider_import_sha256: importSha,
    provider_symbol_count: requireNumber(registry.provider_symbol_count, code),
    provider_symbol_sha256: symbolSha,
    runtime_identity_count: requireNumber(registry.runtime_identity_count, code),
    runtime_identity_sha256: runtimeSha,
    legacy_operation_provider_id: requireString(
      registry.legacy_operation_provider_id, code,
    ),
    ordered_provider_ids: Object.freeze(requireStringArray(
      registry.ordered_provider_ids, code,
    )),
  });

  if (!Array.isArray(value.direct_providers)) return fail(code);
  const directProviders = value.direct_providers.map(
    (entry): DirectProviderExpectation => {
      const provider = requireObject(entry, code);
      if (!exactKeys(provider, [
        "language", "provider_id", "provider_version", "export_name",
        "source_role", "path", "sha256", "size_bytes", "binding",
      ])) return fail(code);
      const binding = requireObject(provider.binding, code);
      if (!exactKeys(binding, [
        "path", "file_sha256", "size_bytes", "binding_id",
        "binding_sha256", "required_input_role_count", "bound_ref_count",
      ])) return fail(code);
      const providerSha = requireString(provider.sha256, code);
      const bindingFileSha = requireString(binding.file_sha256, code);
      const bindingSha = requireString(binding.binding_sha256, code);
      if (![providerSha, bindingFileSha, bindingSha].every((digest) =>
        SHA256.test(digest))) return fail(code);
      return Object.freeze({
        language: requireString(provider.language, code),
        provider_id: requireString(provider.provider_id, code),
        provider_version: requireString(provider.provider_version, code),
        export_name: requireString(provider.export_name, code),
        source_role: requireString(provider.source_role, code),
        path: requireString(provider.path, code),
        sha256: providerSha,
        size_bytes: requireNumber(provider.size_bytes, code),
        binding: Object.freeze({
          path: requireString(binding.path, code),
          file_sha256: bindingFileSha,
          size_bytes: requireNumber(binding.size_bytes, code),
          binding_id: requireString(binding.binding_id, code),
          binding_sha256: bindingSha,
          required_input_role_count: requireNumber(
            binding.required_input_role_count, code,
          ),
          bound_ref_count: requireNumber(binding.bound_ref_count, code),
        }),
      });
    },
  );
  if (directProviders.length !== DIRECT_EXPECTATIONS.length ||
      new Set(directProviders.map(({provider_id: id}) => id)).size !==
        directProviders.length) return fail(code);

  return Object.freeze({
    semantic_plan_epoch_id: value.semantic_plan_epoch_id,
    semantic_contract_digest: value.semantic_contract_digest,
    sources: Object.freeze(sources),
    registry_snapshot: registrySnapshot,
    direct_providers: Object.freeze(directProviders),
    authority_effect: "none",
    claim_ceiling: value.claim_ceiling,
    binding_sha256: value.binding_sha256,
  }) as DecodedBinding;
};

type ProviderImport = Readonly<{
  module_path: string;
  imported_name: string;
  local_name: string;
}>;

const unwrapExpression = (expression: ts.Expression): ts.Expression => {
  let current = expression;
  while (ts.isAsExpression(current) || ts.isTypeAssertionExpression(current) ||
      ts.isParenthesizedExpression(current) ||
      ts.isSatisfiesExpression(current)) current = current.expression;
  return current;
};

export const parseRegistrySurface = (raw: string): Readonly<{
  imports: readonly ProviderImport[];
  provider_symbols: readonly string[];
}> => {
  const code = "RMT_OP_REGISTRY_SOURCE_SHAPE";
  const file = ts.createSourceFile(
    "factory-node-registry-v1.ts", raw, ts.ScriptTarget.Latest, true,
    ts.ScriptKind.TS,
  );
  if (file.parseDiagnostics.length > 0) return fail(code);
  const imports: ProviderImport[] = [];
  for (const statement of file.statements) {
    if (!ts.isImportDeclaration(statement) ||
        !ts.isStringLiteral(statement.moduleSpecifier) ||
        !statement.moduleSpecifier.text.startsWith("./providers/")) continue;
    const bindings = statement.importClause?.namedBindings;
    if (!bindings || !ts.isNamedImports(bindings)) return fail(code);
    for (const element of bindings.elements) {
      imports.push(Object.freeze({
        module_path: statement.moduleSpecifier.text,
        imported_name: element.propertyName?.text ?? element.name.text,
        local_name: element.name.text,
      }));
    }
  }
  let providerSymbols: string[] | undefined;
  const visit = (node: ts.Node): void => {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) &&
        node.name.text === "providers" && node.initializer) {
      const call = unwrapExpression(node.initializer);
      if (!ts.isCallExpression(call) || call.arguments.length !== 1) {
        return fail(code);
      }
      const array = unwrapExpression(call.arguments[0]!);
      if (!ts.isArrayLiteralExpression(array)) return fail(code);
      if (providerSymbols !== undefined || !array.elements.every(ts.isIdentifier)) {
        return fail(code);
      }
      providerSymbols = array.elements.map((entry) =>
        (entry as ts.Identifier).text);
    }
    ts.forEachChild(node, visit);
  };
  visit(file);
  if (!providerSymbols) return fail(code);
  return Object.freeze({
    imports: Object.freeze(imports),
    provider_symbols: Object.freeze(providerSymbols),
  });
};

const parseProviderIdentity = (
  raw: string,
  exportName: string,
): Readonly<{provider_id: string; provider_version: string}> => {
  const code = "RMT_OP_PROVIDER_SOURCE_SHAPE";
  const file = ts.createSourceFile(
    "operation-provider.ts", raw, ts.ScriptTarget.Latest, true,
    ts.ScriptKind.TS,
  );
  if (file.parseDiagnostics.length > 0) return fail(code);
  const matches: ts.VariableDeclaration[] = [];
  for (const statement of file.statements) {
    if (!ts.isVariableStatement(statement) ||
        !statement.modifiers?.some((modifier) =>
          modifier.kind === ts.SyntaxKind.ExportKeyword)) continue;
    for (const declaration of statement.declarationList.declarations) {
      if (ts.isIdentifier(declaration.name) &&
          declaration.name.text === exportName) matches.push(declaration);
    }
  }
  if (matches.length !== 1 || !matches[0]!.initializer) return fail(code);
  const call = unwrapExpression(matches[0]!.initializer!);
  if (!ts.isCallExpression(call) || call.arguments.length !== 1) return fail(code);
  const object = unwrapExpression(call.arguments[0]!);
  if (!ts.isObjectLiteralExpression(object)) return fail(code);
  const stringProperty = (name: string): string => {
    const matches = object.properties.filter((property) =>
      ts.isPropertyAssignment(property) &&
      ((ts.isIdentifier(property.name) && property.name.text === name) ||
       (ts.isStringLiteral(property.name) && property.name.text === name)));
    if (matches.length !== 1 || !ts.isPropertyAssignment(matches[0]!)) {
      return fail(code);
    }
    const value = unwrapExpression(matches[0]!.initializer);
    return ts.isStringLiteral(value) ? value.text : fail(code);
  };
  return Object.freeze({
    provider_id: stringProperty("provider_id"),
    provider_version: stringProperty("provider_version"),
  });
};

type FileStatProjection = Readonly<{
  dev: string;
  ino: string;
  size: string;
  mtime_ns: string;
  ctime_ns: string;
}>;

type RuntimeIdentity = Readonly<{
  provider_id: string;
  provider_version: string;
}>;

export type ProviderObservation = Readonly<{
  language: string;
  export_name: string;
  provider_id: string;
  provider_version: string;
  required_input_roles: readonly string[];
  raw_paths: Readonly<Record<string, string>>;
  raw_inputs: RawInputs;
}>;

export type RegistryObservation = Readonly<{
  after_raw: string;
  before_stat: FileStatProjection;
  after_stat: FileStatProjection;
  runtime_providers: readonly RuntimeIdentity[];
}>;

export type OperationRegistryNegativeInput = Readonly<{
  binding_raw: string;
  raw_inputs: RawInputs;
  registry_observation: RegistryObservation;
  provider_observations: readonly ProviderObservation[];
}>;

const validateStat = (value: unknown): FileStatProjection => {
  const code = "RMT_OP_REGISTRY_OBSERVATION_INVALID";
  const stat = requireObject(value, code);
  if (!exactKeys(stat, ["dev", "ino", "size", "mtime_ns", "ctime_ns"])) {
    return fail(code);
  }
  return Object.freeze({
    dev: requireString(stat.dev, code),
    ino: requireString(stat.ino, code),
    size: requireString(stat.size, code),
    mtime_ns: requireString(stat.mtime_ns, code),
    ctime_ns: requireString(stat.ctime_ns, code),
  });
};

const validateRuntimeIdentities = (value: unknown): RuntimeIdentity[] => {
  const code = "RMT_OP_REGISTRY_OBSERVATION_INVALID";
  if (!Array.isArray(value)) return fail(code);
  return value.map((entry) => {
    const identity = requireObject(entry, code);
    if (!exactKeys(identity, ["provider_id", "provider_version"])) {
      return fail(code);
    }
    return Object.freeze({
      provider_id: requireString(identity.provider_id, code),
      provider_version: requireString(identity.provider_version, code),
    });
  });
};

const validatePlanBinding = (raw: string): void => {
  const code = "RMT_OP_REGISTRY_PLAN_DRIFT";
  const root = parseObject(raw, code);
  const plan = requireObject(root.semantic_plan_binding, code);
  if (plan.epoch_id !== REQUIRED_SEMANTIC_PLAN_EPOCH ||
      plan.contract_digest !== REQUIRED_SEMANTIC_CONTRACT_DIGEST ||
      !Array.isArray(root.contracts)) return fail(code);
  const rows = root.contracts.filter((entry) =>
    isObject(entry) && entry.swu_id === "RMT-OP-009");
  if (rows.length !== 1) return fail(code);
  const row = rows[0]!;
  if (row.type !== "Operation" || row.stage !== "registry-negative" ||
      row.semantic_plan_epoch_id !== REQUIRED_SEMANTIC_PLAN_EPOCH ||
      row.semantic_contract_digest !== REQUIRED_SEMANTIC_CONTRACT_DIGEST) {
    return fail(code);
  }
  const verification = requireObject(row.verification, code);
  if (!Array.isArray(verification.commands) ||
      canonicalJson(verification.commands) !== canonicalJson([REQUIRED_COMMAND])) {
    return fail(code);
  }
};

const validateWriteScope = (raw: string): void => {
  const code = "RMT_OP_REGISTRY_WRITE_SCOPE_DRIFT";
  const root = parseObject(raw, code);
  if (!Array.isArray(root.entries)) return fail(code);
  const rows = root.entries.filter((entry) =>
    isObject(entry) && entry.owner_swu === "RMT-OP-009");
  if (rows.length !== 0) return fail(code);
};

const validateProviderObservation = (
  observationValue: unknown,
  expected: typeof DIRECT_EXPECTATIONS[number],
): Readonly<{binding_id: string; binding_sha256: string; bound_ref_count: number}> => {
  const invalid = "RMT_OP_PROVIDER_OBSERVATION_INVALID";
  const drift = "RMT_OP_PROVIDER_FILE_DRIFT";
  const bindingDrift = "RMT_OP_PROVIDER_BINDING_DRIFT";
  const observation = requireObject(observationValue, invalid);
  if (!exactKeys(observation, [
    "language", "export_name", "provider_id", "provider_version",
    "required_input_roles", "raw_paths", "raw_inputs",
  ])) return fail(invalid);
  if (observation.language !== expected.language ||
      observation.export_name !== expected.export_name ||
      observation.provider_id !== expected.provider_id ||
      observation.provider_version !== expected.provider_version) {
    return fail(drift);
  }
  const roles = requireStringArray(observation.required_input_roles, invalid);
  const paths = requireObject(observation.raw_paths, invalid);
  const rawInputs = requireObject(observation.raw_inputs, invalid);
  if (roles.length !== expected.binding.required_input_role_count ||
      new Set(roles).size !== roles.length ||
      canonicalJson([...roles].sort()) !== canonicalJson(Object.keys(paths).sort()) ||
      canonicalJson([...roles].sort()) !==
        canonicalJson(Object.keys(rawInputs).sort()) ||
      paths.binding !== expected.binding.path) return fail(bindingDrift);
  for (const role of roles) {
    if (typeof paths[role] !== "string" ||
        typeof rawInputs[role] !== "string") return fail(invalid);
  }

  const providerRaw = rawInputs.provider;
  if (typeof providerRaw !== "string" || providerRaw !== undefined &&
      sha256Bytes(providerRaw) !== expected.sha256) return fail(drift);
  const bindingRaw = rawInputs.binding;
  if (typeof bindingRaw !== "string" ||
      Buffer.byteLength(bindingRaw, "utf8") !== expected.binding.size_bytes ||
      sha256Bytes(bindingRaw) !== expected.binding.file_sha256) {
    return fail(bindingDrift);
  }
  const binding = parseObject(bindingRaw, bindingDrift);
  if (!exactKeys(binding, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "symbol_name", "observer_id", "observer_owner_ref", "proof_mechanism",
    "refs", "authority_effect", "binding_sha256",
  ]) || binding.binding_id !== expected.binding.binding_id ||
      binding.authority_effect !== "none" ||
      binding.binding_sha256 !== expected.binding.binding_sha256 ||
      computeBindingSha256(binding) !== binding.binding_sha256) {
    return fail(bindingDrift);
  }
  const refs = requireObject(binding.refs, bindingDrift);
  const boundRoles = roles.filter((role) => role !== "binding").sort();
  if (boundRoles.length !== expected.binding.bound_ref_count ||
      canonicalJson(Object.keys(refs).sort()) !== canonicalJson(boundRoles)) {
    return fail(bindingDrift);
  }
  for (const role of boundRoles) {
    const ref = requireObject(refs[role], bindingDrift);
    if (!exactKeys(ref, ["path", "sha256"]) ||
        ref.path !== paths[role] ||
        ref.sha256 !== sha256Bytes(rawInputs[role] as string)) {
      return fail(bindingDrift);
    }
  }
  return Object.freeze({
    binding_id: expected.binding.binding_id,
    binding_sha256: expected.binding.binding_sha256,
    bound_ref_count: expected.binding.bound_ref_count,
  });
};

export const evaluateOperationRegistryNegative = (
  inputValue: OperationRegistryNegativeInput,
): Readonly<Record<string, unknown>> => {
  const invalid = "RMT_OP_REGISTRY_INPUT_INVALID";
  const input = requireObject(inputValue, invalid);
  if (!exactKeys(input, [
    "binding_raw", "raw_inputs", "registry_observation",
    "provider_observations",
  ])) return fail(invalid);
  const bindingRaw = requireString(input.binding_raw, invalid);
  const rawInputsObject = requireObject(input.raw_inputs, invalid);
  const rawInputs: Record<string, string> = {};
  for (const [role, raw] of Object.entries(rawInputsObject)) {
    if (typeof raw !== "string") return fail(invalid);
    rawInputs[role] = raw;
  }
  const binding = decodeBinding(bindingRaw);
  if (canonicalJson(Object.keys(rawInputs).sort()) !==
      canonicalJson(binding.sources.map(({role}) => role).sort())) {
    return fail(invalid);
  }
  for (const source of binding.sources) {
    const raw = rawInputs[source.role];
    if (raw === undefined || sha256Bytes(raw) !== source.sha256 ||
        Buffer.byteLength(raw, "utf8") !== source.size_bytes) {
      return fail("RMT_OP_REGISTRY_SOURCE_BINDING_STALE");
    }
  }

  const registryObservation = requireObject(
    input.registry_observation, "RMT_OP_REGISTRY_OBSERVATION_INVALID",
  );
  if (!exactKeys(registryObservation, [
    "after_raw", "before_stat", "after_stat", "runtime_providers",
  ])) return fail("RMT_OP_REGISTRY_OBSERVATION_INVALID");
  const afterRaw = requireString(
    registryObservation.after_raw, "RMT_OP_REGISTRY_OBSERVATION_INVALID",
  );
  const beforeStat = validateStat(registryObservation.before_stat);
  const afterStat = validateStat(registryObservation.after_stat);
  const runtimeProviders = validateRuntimeIdentities(
    registryObservation.runtime_providers,
  );
  const registryRaw = rawInputs.canonical_registry;
  if (registryRaw === undefined || afterRaw !== registryRaw ||
      canonicalJson(beforeStat) !== canonicalJson(afterStat)) {
    return fail("RMT_OP_REGISTRY_WRITE_DETECTED");
  }

  const surface = parseRegistrySurface(registryRaw);
  const directModulePaths = new Set(DIRECT_EXPECTATIONS.map(
    ({module_path: path}) => path,
  ));
  if (surface.imports.some(({module_path: path}) =>
    directModulePaths.has(path))) {
    return fail("RMT_OP_REGISTRY_DIRECT_PROVIDER_IMPORT");
  }
  const directIds = new Set(DIRECT_EXPECTATIONS.map(({provider_id: id}) => id));
  if (runtimeProviders.some(({provider_id: id}) => directIds.has(id))) {
    return fail("RMT_OP_REGISTRY_DIRECT_PROVIDER_PRESENT");
  }
  const runtimeIds = runtimeProviders.map(({provider_id: id}) => id);
  if (new Set(runtimeIds).size !== runtimeIds.length ||
      new Set(surface.provider_symbols).size !== surface.provider_symbols.length) {
    return fail("RMT_OP_REGISTRY_DUPLICATE_IDENTITY");
  }

  const registrySnapshot = binding.registry_snapshot;
  const importDigest = sha256Value(surface.imports);
  const symbolDigest = sha256Value(surface.provider_symbols);
  const runtimeDigest = sha256Value(runtimeProviders);
  if (sha256Bytes(registryRaw) !== registrySnapshot.sha256 ||
      Buffer.byteLength(registryRaw, "utf8") !== registrySnapshot.size_bytes ||
      surface.imports.length !== registrySnapshot.provider_import_count ||
      importDigest !== registrySnapshot.provider_import_sha256 ||
      surface.provider_symbols.length !== registrySnapshot.provider_symbol_count ||
      symbolDigest !== registrySnapshot.provider_symbol_sha256 ||
      runtimeProviders.length !== registrySnapshot.runtime_identity_count ||
      runtimeDigest !== registrySnapshot.runtime_identity_sha256 ||
      canonicalJson(runtimeIds) !==
        canonicalJson(registrySnapshot.ordered_provider_ids) ||
      !runtimeIds.includes(registrySnapshot.legacy_operation_provider_id) ||
      canonicalJson(registrySnapshot) !== canonicalJson(EXPECTED_REGISTRY)) {
    return fail("RMT_OP_REGISTRY_SNAPSHOT_DRIFT");
  }

  if (!Array.isArray(input.provider_observations) ||
      input.provider_observations.length !== DIRECT_EXPECTATIONS.length) {
    return fail("RMT_OP_PROVIDER_OBSERVATION_INVALID");
  }
  const providerEvidence = [];
  for (let index = 0; index < DIRECT_EXPECTATIONS.length; index += 1) {
    const expected = DIRECT_EXPECTATIONS[index]!;
    const declared = binding.direct_providers[index];
    if (!declared) return fail("RMT_OP_PROVIDER_FILE_DRIFT");
    const declaredProvider = {
      language: declared.language,
      provider_id: declared.provider_id,
      provider_version: declared.provider_version,
      export_name: declared.export_name,
      source_role: declared.source_role,
      path: declared.path,
      sha256: declared.sha256,
      size_bytes: declared.size_bytes,
    };
    const expectedProvider = {
      language: expected.language,
      provider_id: expected.provider_id,
      provider_version: expected.provider_version,
      export_name: expected.export_name,
      source_role: expected.source_role,
      path: expected.path,
      sha256: expected.sha256,
      size_bytes: expected.size_bytes,
    };
    if (canonicalJson(declaredProvider) !== canonicalJson(expectedProvider)) {
      return fail("RMT_OP_PROVIDER_FILE_DRIFT");
    }
    if (canonicalJson(declared.binding) !== canonicalJson(expected.binding)) {
      return fail("RMT_OP_PROVIDER_BINDING_DRIFT");
    }
    const providerRaw = rawInputs[expected.source_role];
    if (providerRaw === undefined) return fail("RMT_OP_PROVIDER_FILE_DRIFT");
    const sourceIdentity = parseProviderIdentity(providerRaw, expected.export_name);
    if (sourceIdentity.provider_id !== expected.provider_id ||
        sourceIdentity.provider_version !== expected.provider_version ||
        sha256Bytes(providerRaw) !== expected.sha256 ||
        Buffer.byteLength(providerRaw, "utf8") !== expected.size_bytes) {
      return fail("RMT_OP_PROVIDER_FILE_DRIFT");
    }
    const retained = validateProviderObservation(
      input.provider_observations[index], expected,
    );
    providerEvidence.push(Object.freeze({
      language: expected.language,
      provider_id: expected.provider_id,
      provider_version: expected.provider_version,
      export_name: expected.export_name,
      source_sha256: expected.sha256,
      registered: false,
      binding_retained: true,
      ...retained,
    }));
  }

  validatePlanBinding(rawInputs.swu_contracts!);
  validateWriteScope(rawInputs.write_scope_baseline!);
  if (canonicalJson(binding.sources) !== canonicalJson(SOURCE_EXPECTATIONS)) {
    return fail("RMT_OP_REGISTRY_SOURCE_DRIFT");
  }
  if (canonicalJson(binding.direct_providers.map((provider) => ({
    ...provider,
  }))) !== canonicalJson(DIRECT_EXPECTATIONS.map(({module_path: _path, ...rest}) =>
    rest))) return fail("RMT_OP_PROVIDER_FILE_DRIFT");

  const sourceAggregate = sha256Bytes([...binding.sources]
    .sort((left, right) => Buffer.from(left.path).compare(Buffer.from(right.path)))
    .map(({path, sha256, size_bytes: size}) =>
      `${sha256}\t${size}\t${path}\n`).join(""));
  const proofBody = {
    schema_version: "OperationRegistryNegativeProof/v1",
    result: "pass",
    semantic_plan_epoch_id: REQUIRED_SEMANTIC_PLAN_EPOCH,
    semantic_contract_digest: REQUIRED_SEMANTIC_CONTRACT_DIGEST,
    source_count: binding.sources.length,
    source_size_bytes: binding.sources.reduce((total, source) =>
      total + source.size_bytes, 0),
    source_aggregate_sha256: sourceAggregate,
    registry: Object.freeze({
      path: REGISTRY_PATH,
      sha256: registrySnapshot.sha256,
      size_bytes: registrySnapshot.size_bytes,
      provider_import_count: surface.imports.length,
      provider_import_sha256: importDigest,
      provider_symbol_count: surface.provider_symbols.length,
      provider_symbol_sha256: symbolDigest,
      runtime_identity_count: runtimeProviders.length,
      runtime_identity_sha256: runtimeDigest,
      ordered_provider_ids: Object.freeze(runtimeIds),
      legacy_operation_provider_id: "typescript-operation-v1",
      legacy_operation_provider_present: true,
      direct_provider_ids_absent: true,
      before_after_bytes_equal: true,
      before_after_stat_equal: true,
    }),
    direct_providers: Object.freeze(providerEvidence),
    provider_files_exact: true,
    canonical_registry_snapshot_exact: true,
    s1_providers_unregistered: true,
    s1_binding_retained: true,
    no_registration_write: true,
    no_self_authored_authority: true,
    authority_effect: "none",
    claim_ceiling: binding.claim_ceiling,
  };
  return Object.freeze({
    ...proofBody,
    proof_sha256: sha256Value(proofBody),
  });
};
