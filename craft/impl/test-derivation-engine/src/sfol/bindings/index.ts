export const SFOL_BINDING_SCHEMA_VERSION =
  "domainspec-sfol-binding/v1" as const;

export type SfolBindingSchemaVersion =
  typeof SFOL_BINDING_SCHEMA_VERSION;

export interface PureBindingSelector {
  readonly module_id: string;
  readonly clause_id: string;
  readonly case_id: string;
  readonly role: string;
  readonly module_digest: string;
  readonly clause_digest: string;
  readonly case_digest: string;
  readonly fixture_digest: string;
}

export type BindingAdapterKind = "pure-function" | "effect-harness";

export interface BindingTarget {
  readonly adapter_kind: BindingAdapterKind;
  readonly module: string;
  readonly symbol: string;
  readonly target_digest: string;
  readonly runtime_digest: string;
}

export interface ArgumentProjection {
  readonly parameter: string;
  readonly input_name: string;
}

export type ObservationProjection =
  | {
      readonly kind: "return";
    }
  | {
      readonly kind: "field";
      readonly field: string;
    };

export interface LogicBinding {
  readonly binding_id: string;
  readonly selector: PureBindingSelector;
  readonly target: BindingTarget;
  readonly argument_map: readonly ArgumentProjection[];
  readonly observation_map: ObservationProjection;
}

export interface LogicBindingRegistry {
  readonly schema_version: SfolBindingSchemaVersion;
  readonly registry_id: string;
  readonly bindings: readonly LogicBinding[];
}

export interface PureBindingRequest {
  readonly selector: PureBindingSelector;
  readonly adapter_kind: "pure-function";
}

export interface ResolvedPureBinding {
  readonly resolution_key: string;
  readonly selector: PureBindingSelector;
  readonly binding: LogicBinding;
}

export type SfolBindingDiagnosticCode =
  | "SFOL_BINDING_UNKNOWN_VERSION"
  | "SFOL_BINDING_INVALID_SHAPE"
  | "SFOL_BINDING_UNKNOWN_FIELD"
  | "SFOL_BINDING_ORACLE_FIELD"
  | "SFOL_BINDING_FIRST_MATCH_FORBIDDEN"
  | "SFOL_BINDING_PARTIAL_SELECTOR"
  | "SFOL_BINDING_INVALID_DIGEST"
  | "SFOL_BINDING_DUPLICATE_ID"
  | "SFOL_BINDING_DUPLICATE_ARGUMENT"
  | "SFOL_BINDING_EMPTY_REGISTRY"
  | "SFOL_BINDING_UNBOUND"
  | "SFOL_BINDING_MULTIPLE"
  | "SFOL_BINDING_STALE"
  | "SFOL_BINDING_WRONG_ADAPTER_KIND"
  | "SFOL_BINDING_INVALID_REQUEST";

export interface SfolBindingDiagnostic {
  readonly code: SfolBindingDiagnosticCode;
  readonly stage: "binding-schema" | "binding-resolution";
  readonly path: string;
  readonly detail: string;
}

export type BindingRegistryDecodeResult =
  | {
      readonly ok: true;
      readonly value: LogicBindingRegistry;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly SfolBindingDiagnostic[];
    };

export type BindingResolutionResult =
  | {
      readonly ok: true;
      readonly value: ResolvedPureBinding;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly SfolBindingDiagnostic[];
    };

const SELECTOR_KEYS = [
  "module_id",
  "clause_id",
  "case_id",
  "role",
  "module_digest",
  "clause_digest",
  "case_digest",
  "fixture_digest",
] as const;

const DIGEST_PATTERN = /^[0-9a-f]{64}$/;
const ORACLE_FIELD_PATTERN =
  /^(?:expected(?:_|$)|oracle(?:_|$)|acceptance(?:_|$)|predicate(?:_|$)|assert(?:_|$)|verdict(?:_|$))/i;

class BindingSchemaAbort extends Error {
  readonly diagnostic: SfolBindingDiagnostic;

  constructor(diagnostic: SfolBindingDiagnostic) {
    super(`${diagnostic.code} at ${diagnostic.path}: ${diagnostic.detail}`);
    this.name = "BindingSchemaAbort";
    this.diagnostic = diagnostic;
  }
}

export function decodeLogicBindingRegistry(
  input: unknown,
): BindingRegistryDecodeResult {
  try {
    rejectOracleFields(input, "$");
    const root = requireRecord(input, "$");
    exactKeys(
      root,
      ["schema_version", "registry_id", "bindings"],
      "$",
    );
    if (root.schema_version !== SFOL_BINDING_SCHEMA_VERSION) {
      schemaFail(
        "SFOL_BINDING_UNKNOWN_VERSION",
        "$.schema_version",
        `expected ${SFOL_BINDING_SCHEMA_VERSION}`,
      );
    }
    const registryId = requireNonEmptyString(
      root.registry_id,
      "$.registry_id",
    );
    if (!Array.isArray(root.bindings)) {
      schemaFail(
        "SFOL_BINDING_INVALID_SHAPE",
        "$.bindings",
        "bindings must be an array",
      );
    }

    const bindings = root.bindings.map((binding, index) =>
      decodeBinding(binding, `$.bindings[${index}]`),
    );
    const seenIds = new Set<string>();
    for (const binding of bindings) {
      if (seenIds.has(binding.binding_id)) {
        schemaFail(
          "SFOL_BINDING_DUPLICATE_ID",
          "$.bindings",
          `duplicate binding_id ${binding.binding_id}`,
        );
      }
      seenIds.add(binding.binding_id);
    }

    bindings.sort((left, right) =>
      bindingSortKey(left).localeCompare(bindingSortKey(right)),
    );

    return Object.freeze({
      ok: true,
      value: Object.freeze({
        schema_version: SFOL_BINDING_SCHEMA_VERSION,
        registry_id: registryId,
        bindings: Object.freeze(bindings),
      }),
    });
  } catch (error: unknown) {
    if (error instanceof BindingSchemaAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_BINDING_INVALID_SHAPE",
          stage: "binding-schema",
          path: "$",
          detail: "binding registry input is structurally invalid",
        }),
      ]),
    });
  }
}

export function resolvePureBinding(
  request: PureBindingRequest,
  registry: LogicBindingRegistry,
): BindingResolutionResult {
  const requestDiagnostic = validateRequest(request);
  if (requestDiagnostic !== null) {
    return resolutionFailure(requestDiagnostic);
  }
  if (registry.bindings.length === 0) {
    return resolutionFailure({
      code: "SFOL_BINDING_EMPTY_REGISTRY",
      stage: "binding-resolution",
      path: "$.bindings",
      detail: `registry ${registry.registry_id} has no bindings`,
    });
  }

  const identityMatches = registry.bindings.filter((binding) =>
    identityEquals(binding.selector, request.selector),
  );
  if (identityMatches.length === 0) {
    return resolutionFailure({
      code: "SFOL_BINDING_UNBOUND",
      stage: "binding-resolution",
      path: "$.selector",
      detail: `no binding owns ${identityKey(request.selector)}`,
    });
  }

  const exactMatches = identityMatches.filter((binding) =>
    digestSetEquals(binding.selector, request.selector),
  );
  if (exactMatches.length === 0) {
    const staleIds = identityMatches
      .map((binding) => binding.binding_id)
      .sort()
      .join(", ");
    return resolutionFailure({
      code: "SFOL_BINDING_STALE",
      stage: "binding-resolution",
      path: "$.selector",
      detail: `identity matches stale binding(s): ${staleIds}`,
    });
  }
  if (exactMatches.length > 1) {
    const bindingIds = exactMatches
      .map((binding) => binding.binding_id)
      .sort()
      .join(", ");
    return resolutionFailure({
      code: "SFOL_BINDING_MULTIPLE",
      stage: "binding-resolution",
      path: "$.selector",
      detail: `exact selector resolves multiple bindings: ${bindingIds}`,
    });
  }

  const binding = exactMatches[0];
  if (binding === undefined) {
    return resolutionFailure({
      code: "SFOL_BINDING_UNBOUND",
      stage: "binding-resolution",
      path: "$.selector",
      detail: "exact binding disappeared during deterministic resolution",
    });
  }
  if (binding.target.adapter_kind !== request.adapter_kind) {
    return resolutionFailure({
      code: "SFOL_BINDING_WRONG_ADAPTER_KIND",
      stage: "binding-resolution",
      path: "$.target.adapter_kind",
      detail: `expected ${request.adapter_kind}; found ${binding.target.adapter_kind}`,
    });
  }

  return Object.freeze({
    ok: true,
    value: Object.freeze({
      resolution_key: exactSelectorKey(request.selector),
      selector: binding.selector,
      binding,
    }),
  });
}

function decodeBinding(input: unknown, path: string): LogicBinding {
  const binding = requireRecord(input, path);
  if (Object.hasOwn(binding, "match")) {
    schemaFail(
      "SFOL_BINDING_FIRST_MATCH_FORBIDDEN",
      `${path}.match`,
      "first-match and subset selectors are not admitted",
    );
  }
  exactKeys(
    binding,
    [
      "binding_id",
      "selector",
      "target",
      "argument_map",
      "observation_map",
    ],
    path,
  );
  const bindingId = requireNonEmptyString(
    binding.binding_id,
    `${path}.binding_id`,
  );
  const selector = decodeSelector(binding.selector, `${path}.selector`);
  const target = decodeTarget(binding.target, `${path}.target`);
  const argumentMap = decodeArgumentMap(
    binding.argument_map,
    `${path}.argument_map`,
  );
  const observationMap = decodeObservationMap(
    binding.observation_map,
    `${path}.observation_map`,
  );

  return Object.freeze({
    binding_id: bindingId,
    selector,
    target,
    argument_map: argumentMap,
    observation_map: observationMap,
  });
}

function decodeSelector(input: unknown, path: string): PureBindingSelector {
  const selector = requireRecord(input, path);
  const presentKeys = Object.keys(selector);
  const missing = SELECTOR_KEYS.filter(
    (key) => !Object.hasOwn(selector, key),
  );
  if (missing.length > 0) {
    schemaFail(
      "SFOL_BINDING_PARTIAL_SELECTOR",
      path,
      `selector is missing exact key(s): ${missing.join(", ")}`,
    );
  }
  exactKeys(selector, SELECTOR_KEYS, path);

  const decoded: Record<(typeof SELECTOR_KEYS)[number], string> = {
    module_id: "",
    clause_id: "",
    case_id: "",
    role: "",
    module_digest: "",
    clause_digest: "",
    case_digest: "",
    fixture_digest: "",
  };
  for (const key of SELECTOR_KEYS) {
    decoded[key] = requireNonEmptyString(selector[key], `${path}.${key}`);
  }
  for (const key of [
    "module_digest",
    "clause_digest",
    "case_digest",
    "fixture_digest",
  ] as const) {
    requireDigest(decoded[key], `${path}.${key}`);
  }
  if (presentKeys.length !== SELECTOR_KEYS.length) {
    schemaFail(
      "SFOL_BINDING_UNKNOWN_FIELD",
      path,
      "selector contains non-exact fields",
    );
  }
  return Object.freeze(decoded);
}

function decodeTarget(input: unknown, path: string): BindingTarget {
  const target = requireRecord(input, path);
  exactKeys(
    target,
    [
      "adapter_kind",
      "module",
      "symbol",
      "target_digest",
      "runtime_digest",
    ],
    path,
  );
  if (
    target.adapter_kind !== "pure-function" &&
    target.adapter_kind !== "effect-harness"
  ) {
    schemaFail(
      "SFOL_BINDING_INVALID_SHAPE",
      `${path}.adapter_kind`,
      "adapter_kind must be pure-function or effect-harness",
    );
  }
  const module = requireNonEmptyString(target.module, `${path}.module`);
  const symbol = requireNonEmptyString(target.symbol, `${path}.symbol`);
  const targetDigest = requireNonEmptyString(
    target.target_digest,
    `${path}.target_digest`,
  );
  const runtimeDigest = requireNonEmptyString(
    target.runtime_digest,
    `${path}.runtime_digest`,
  );
  requireDigest(targetDigest, `${path}.target_digest`);
  requireDigest(runtimeDigest, `${path}.runtime_digest`);
  return Object.freeze({
    adapter_kind: target.adapter_kind,
    module,
    symbol,
    target_digest: targetDigest,
    runtime_digest: runtimeDigest,
  });
}

function decodeArgumentMap(
  input: unknown,
  path: string,
): readonly ArgumentProjection[] {
  if (!Array.isArray(input)) {
    schemaFail(
      "SFOL_BINDING_INVALID_SHAPE",
      path,
      "argument_map must be an array",
    );
  }
  const decoded = input.map((value, index) => {
    const itemPath = `${path}[${index}]`;
    const item = requireRecord(value, itemPath);
    exactKeys(item, ["parameter", "input_name"], itemPath);
    return Object.freeze({
      parameter: requireNonEmptyString(
        item.parameter,
        `${itemPath}.parameter`,
      ),
      input_name: requireNonEmptyString(
        item.input_name,
        `${itemPath}.input_name`,
      ),
    });
  });
  decoded.sort((left, right) =>
    `${left.parameter}\u0000${left.input_name}`.localeCompare(
      `${right.parameter}\u0000${right.input_name}`,
    ),
  );
  for (let index = 1; index < decoded.length; index += 1) {
    if (decoded[index - 1]?.parameter === decoded[index]?.parameter) {
      schemaFail(
        "SFOL_BINDING_DUPLICATE_ARGUMENT",
        path,
        `duplicate parameter projection ${decoded[index]?.parameter ?? ""}`,
      );
    }
  }
  return Object.freeze(decoded);
}

function decodeObservationMap(
  input: unknown,
  path: string,
): ObservationProjection {
  const observation = requireRecord(input, path);
  if (observation.kind === "return") {
    exactKeys(observation, ["kind"], path);
    return Object.freeze({ kind: "return" });
  }
  if (observation.kind === "field") {
    exactKeys(observation, ["kind", "field"], path);
    return Object.freeze({
      kind: "field",
      field: requireNonEmptyString(
        observation.field,
        `${path}.field`,
      ),
    });
  }
  schemaFail(
    "SFOL_BINDING_INVALID_SHAPE",
    `${path}.kind`,
    "observation kind must be return or field",
  );
}

function validateRequest(
  request: PureBindingRequest,
): SfolBindingDiagnostic | null {
  if (request.adapter_kind !== "pure-function") {
    return {
      code: "SFOL_BINDING_INVALID_REQUEST",
      stage: "binding-resolution",
      path: "$.adapter_kind",
      detail: "pure resolution requires adapter_kind pure-function",
    };
  }
  for (const key of SELECTOR_KEYS) {
    if (
      typeof request.selector[key] !== "string" ||
      request.selector[key].length === 0
    ) {
      return {
        code: "SFOL_BINDING_INVALID_REQUEST",
        stage: "binding-resolution",
        path: `$.selector.${key}`,
        detail: "request selectors require all exact non-empty identities",
      };
    }
  }
  for (const key of [
    "module_digest",
    "clause_digest",
    "case_digest",
    "fixture_digest",
  ] as const) {
    if (!DIGEST_PATTERN.test(request.selector[key])) {
      return {
        code: "SFOL_BINDING_INVALID_REQUEST",
        stage: "binding-resolution",
        path: `$.selector.${key}`,
        detail: "request digest must be 64 lowercase hexadecimal characters",
      };
    }
  }
  return null;
}

function identityEquals(
  left: PureBindingSelector,
  right: PureBindingSelector,
): boolean {
  return (
    left.module_id === right.module_id &&
    left.clause_id === right.clause_id &&
    left.case_id === right.case_id &&
    left.role === right.role
  );
}

function digestSetEquals(
  left: PureBindingSelector,
  right: PureBindingSelector,
): boolean {
  return (
    left.module_digest === right.module_digest &&
    left.clause_digest === right.clause_digest &&
    left.case_digest === right.case_digest &&
    left.fixture_digest === right.fixture_digest
  );
}

function identityKey(selector: PureBindingSelector): string {
  return [
    selector.module_id,
    selector.clause_id,
    selector.case_id,
    selector.role,
  ].join("|");
}

function exactSelectorKey(selector: PureBindingSelector): string {
  return [
    identityKey(selector),
    selector.module_digest,
    selector.clause_digest,
    selector.case_digest,
    selector.fixture_digest,
  ].join("|");
}

function bindingSortKey(binding: LogicBinding): string {
  return `${exactSelectorKey(binding.selector)}|${binding.binding_id}`;
}

function resolutionFailure(
  diagnostic: SfolBindingDiagnostic,
): BindingResolutionResult {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze([Object.freeze(diagnostic)]),
  });
}

function rejectOracleFields(input: unknown, path: string): void {
  if (Array.isArray(input)) {
    input.forEach((value, index) =>
      rejectOracleFields(value, `${path}[${index}]`),
    );
    return;
  }
  if (!isRecord(input)) {
    return;
  }
  for (const [key, value] of Object.entries(input)) {
    if (ORACLE_FIELD_PATTERN.test(key)) {
      schemaFail(
        "SFOL_BINDING_ORACLE_FIELD",
        `${path}.${key}`,
        `binding registries cannot carry oracle field ${key}`,
      );
    }
    rejectOracleFields(value, `${path}.${key}`);
  }
}

function exactKeys(
  value: Readonly<Record<string, unknown>>,
  allowed: readonly string[],
  path: string,
): void {
  const allowedSet = new Set(allowed);
  const unknown = Object.keys(value)
    .filter((key) => !allowedSet.has(key))
    .sort();
  if (unknown.length > 0) {
    schemaFail(
      "SFOL_BINDING_UNKNOWN_FIELD",
      path,
      `unknown field(s): ${unknown.join(", ")}`,
    );
  }
  const missing = allowed
    .filter((key) => !Object.hasOwn(value, key))
    .sort();
  if (missing.length > 0) {
    schemaFail(
      "SFOL_BINDING_INVALID_SHAPE",
      path,
      `missing field(s): ${missing.join(", ")}`,
    );
  }
}

function requireRecord(
  input: unknown,
  path: string,
): Readonly<Record<string, unknown>> {
  if (!isRecord(input)) {
    schemaFail(
      "SFOL_BINDING_INVALID_SHAPE",
      path,
      "expected an object",
    );
  }
  return input;
}

function isRecord(
  input: unknown,
): input is Readonly<Record<string, unknown>> {
  return typeof input === "object" && input !== null && !Array.isArray(input);
}

function requireNonEmptyString(input: unknown, path: string): string {
  if (typeof input !== "string" || input.length === 0) {
    schemaFail(
      "SFOL_BINDING_INVALID_SHAPE",
      path,
      "expected a non-empty string",
    );
  }
  return input;
}

function requireDigest(value: string, path: string): void {
  if (!DIGEST_PATTERN.test(value)) {
    schemaFail(
      "SFOL_BINDING_INVALID_DIGEST",
      path,
      "digest must be 64 lowercase hexadecimal characters",
    );
  }
}

function schemaFail(
  code: SfolBindingDiagnosticCode,
  path: string,
  detail: string,
): never {
  throw new BindingSchemaAbort({
    code,
    stage: "binding-schema",
    path,
    detail,
  });
}
