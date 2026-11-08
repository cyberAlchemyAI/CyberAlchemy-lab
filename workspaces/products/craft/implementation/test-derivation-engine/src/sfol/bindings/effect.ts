import {
  digestSfolValue,
} from "../cases/index.js";
import type { DerivedEffectCase } from "../cases/effect.js";

export interface EffectBindingSelector {
  readonly module_id: string;
  readonly clause_id: string;
  readonly case_id: string;
  readonly role: "effects";
  readonly module_digest: string;
  readonly clause_digest: string;
  readonly case_digest: string;
  readonly fixture_digest: string;
  readonly trace_contract_digest: string;
  readonly contract_admission_digest: string;
  readonly source_proposal_digest: string;
}

export interface EffectBindingTarget {
  readonly adapter_kind: "effect-harness";
  readonly module: string;
  readonly symbol: string;
  readonly target_digest: string;
  readonly runtime_digest: string;
  readonly adapter_id: string;
  readonly adapter_digest: string;
}

export interface EffectBinding {
  readonly binding_id: string;
  readonly selector: EffectBindingSelector;
  readonly target: EffectBindingTarget;
}

export interface EffectBindingRegistry {
  readonly schema_version: "domainspec-sfol-effect-binding/v1";
  readonly registry_id: string;
  readonly bindings: readonly EffectBinding[];
}

export interface EffectBindingRequest {
  readonly selector: EffectBindingSelector;
  readonly adapter_kind: "effect-harness";
}

export interface ResolvedEffectBinding {
  readonly resolution_key: string;
  readonly selector: EffectBindingSelector;
  readonly binding: EffectBinding;
  readonly binding_digest: string;
}

export type EffectBindingDiagnosticCode =
  | "SFOL_EFFECT_BINDING_INVALID_SHAPE"
  | "SFOL_EFFECT_BINDING_ORACLE_FIELD"
  | "SFOL_EFFECT_BINDING_INVALID_DIGEST"
  | "SFOL_EFFECT_BINDING_EMPTY_REGISTRY"
  | "SFOL_EFFECT_BINDING_DUPLICATE_ID"
  | "SFOL_EFFECT_BINDING_UNBOUND"
  | "SFOL_EFFECT_BINDING_MULTIPLE"
  | "SFOL_EFFECT_BINDING_STALE"
  | "SFOL_EFFECT_BINDING_WRONG_ADAPTER_KIND"
  | "SFOL_EFFECT_BINDING_INVALID_REQUEST";

export interface EffectBindingDiagnostic {
  readonly code: EffectBindingDiagnosticCode;
  readonly stage: "effect-binding-resolution";
  readonly path: string;
  readonly detail: string;
}

export type EffectBindingResolutionResult =
  | {
      readonly ok: true;
      readonly value: ResolvedEffectBinding;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly EffectBindingDiagnostic[];
    };

const SHA256 = /^[0-9a-f]{64}$/;
const ORACLE_FIELD =
  /^(?:expected(?:_|$)|oracle(?:_|$)|acceptance(?:_|$)|assert(?:_|$)|verdict(?:_|$))/i;
const SELECTOR_DIGEST_KEYS = [
  "module_digest",
  "clause_digest",
  "case_digest",
  "fixture_digest",
  "trace_contract_digest",
  "contract_admission_digest",
  "source_proposal_digest",
] as const;

export function effectBindingSelectorForCase(
  derived: DerivedEffectCase,
): EffectBindingSelector {
  return Object.freeze({
    module_id: derived.module_id,
    clause_id: derived.clause_id,
    case_id: derived.case_id,
    role: derived.role,
    module_digest: derived.module_digest,
    clause_digest: derived.clause_digest,
    case_digest: derived.case_digest,
    fixture_digest: derived.fixture_digest,
    trace_contract_digest: derived.trace_contract_digest,
    contract_admission_digest: derived.contract_admission_digest,
    source_proposal_digest: derived.source_proposal_digest,
  });
}

export function resolveEffectBinding(
  request: EffectBindingRequest,
  registry: EffectBindingRegistry,
): EffectBindingResolutionResult {
  try {
    rejectOracleFields(registry, "$registry");
    rejectOracleFields(request, "$request");
    validateRequest(request);
    validateRegistry(registry);
    const identityMatches = registry.bindings.filter((binding) =>
      identityEquals(binding.selector, request.selector),
    );
    if (identityMatches.length === 0) {
      bindingFail(
        "SFOL_EFFECT_BINDING_UNBOUND",
        "$.selector",
        `no binding owns ${identityKey(request.selector)}`,
      );
    }
    const exactMatches = identityMatches.filter((binding) =>
      digestSetEquals(binding.selector, request.selector),
    );
    if (exactMatches.length === 0) {
      bindingFail(
        "SFOL_EFFECT_BINDING_STALE",
        "$.selector",
        `identity matches stale binding(s): ${identityMatches
          .map((binding) => binding.binding_id)
          .sort()
          .join(", ")}`,
      );
    }
    if (exactMatches.length > 1) {
      bindingFail(
        "SFOL_EFFECT_BINDING_MULTIPLE",
        "$.selector",
        `exact selector resolves multiple bindings: ${exactMatches
          .map((binding) => binding.binding_id)
          .sort()
          .join(", ")}`,
      );
    }
    const binding = exactMatches[0];
    if (binding === undefined) {
      bindingFail(
        "SFOL_EFFECT_BINDING_UNBOUND",
        "$.selector",
        "exact binding disappeared during deterministic resolution",
      );
    }
    if (binding.target.adapter_kind !== request.adapter_kind) {
      bindingFail(
        "SFOL_EFFECT_BINDING_WRONG_ADAPTER_KIND",
        "$.target.adapter_kind",
        `expected ${request.adapter_kind}; found ${binding.target.adapter_kind}`,
      );
    }
    const unsigned = {
      resolution_key: exactSelectorKey(request.selector),
      selector: binding.selector,
      binding,
    };
    return Object.freeze({
      ok: true,
      value: deepFreeze({
        ...unsigned,
        binding_digest: digestSfolValue(unsigned),
      }),
    });
  } catch (error: unknown) {
    if (error instanceof EffectBindingAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_EFFECT_BINDING_INVALID_SHAPE",
          stage: "effect-binding-resolution",
          path: "$",
          detail: "effect binding input is structurally invalid",
        }),
      ]),
    });
  }
}

class EffectBindingAbort extends Error {
  readonly diagnostic: EffectBindingDiagnostic;

  constructor(diagnostic: EffectBindingDiagnostic) {
    super(`${diagnostic.code}:${diagnostic.path}:${diagnostic.detail}`);
    this.name = "EffectBindingAbort";
    this.diagnostic = diagnostic;
  }
}

function validateRegistry(registry: EffectBindingRegistry): void {
  if (
    registry.schema_version !== "domainspec-sfol-effect-binding/v1" ||
    typeof registry.registry_id !== "string" ||
    registry.registry_id.length === 0 ||
    !Array.isArray(registry.bindings)
  ) {
    bindingFail(
      "SFOL_EFFECT_BINDING_INVALID_SHAPE",
      "$registry",
      "registry version, identity, or bindings are invalid",
    );
  }
  if (registry.bindings.length === 0) {
    bindingFail(
      "SFOL_EFFECT_BINDING_EMPTY_REGISTRY",
      "$registry.bindings",
      `registry ${registry.registry_id} has no bindings`,
    );
  }
  const bindingIds = registry.bindings.map(
    (binding) => binding.binding_id,
  );
  if (new Set(bindingIds).size !== bindingIds.length) {
    bindingFail(
      "SFOL_EFFECT_BINDING_DUPLICATE_ID",
      "$registry.bindings",
      "binding IDs must be unique",
    );
  }
  for (const [index, binding] of registry.bindings.entries()) {
    if (
      typeof binding.binding_id !== "string" ||
      binding.binding_id.length === 0
    ) {
      bindingFail(
        "SFOL_EFFECT_BINDING_INVALID_SHAPE",
        `$registry.bindings[${index}].binding_id`,
        "binding_id must be non-empty",
      );
    }
    validateSelector(
      binding.selector,
      `$registry.bindings[${index}].selector`,
    );
    validateTarget(
      binding.target,
      `$registry.bindings[${index}].target`,
    );
  }
}

function validateRequest(request: EffectBindingRequest): void {
  if (request.adapter_kind !== "effect-harness") {
    bindingFail(
      "SFOL_EFFECT_BINDING_INVALID_REQUEST",
      "$request.adapter_kind",
      "effect resolution requires adapter_kind effect-harness",
    );
  }
  validateSelector(request.selector, "$request.selector");
}

function validateSelector(
  selector: EffectBindingSelector,
  path: string,
): void {
  for (const [key, value] of Object.entries(selector)) {
    if (typeof value !== "string" || value.length === 0) {
      bindingFail(
        "SFOL_EFFECT_BINDING_INVALID_REQUEST",
        `${path}.${key}`,
        "selector identities must be non-empty strings",
      );
    }
  }
  if (selector.role !== "effects") {
    bindingFail(
      "SFOL_EFFECT_BINDING_INVALID_REQUEST",
      `${path}.role`,
      "effect bindings require role effects",
    );
  }
  for (const key of SELECTOR_DIGEST_KEYS) {
    requireDigest(selector[key], `${path}.${key}`);
  }
}

function validateTarget(
  target: EffectBindingTarget,
  path: string,
): void {
  if (target.adapter_kind !== "effect-harness") {
    bindingFail(
      "SFOL_EFFECT_BINDING_WRONG_ADAPTER_KIND",
      `${path}.adapter_kind`,
      "effect binding target must use the contained effect harness",
    );
  }
  for (const [key, value] of Object.entries(target)) {
    if (typeof value !== "string" || value.length === 0) {
      bindingFail(
        "SFOL_EFFECT_BINDING_INVALID_SHAPE",
        `${path}.${key}`,
        "target fields must be non-empty strings",
      );
    }
  }
  for (const key of [
    "target_digest",
    "runtime_digest",
    "adapter_digest",
  ] as const) {
    requireDigest(target[key], `${path}.${key}`);
  }
}

function requireDigest(value: string, path: string): void {
  if (!SHA256.test(value)) {
    bindingFail(
      "SFOL_EFFECT_BINDING_INVALID_DIGEST",
      path,
      "digest must be 64 lowercase hexadecimal characters",
    );
  }
}

function identityEquals(
  left: EffectBindingSelector,
  right: EffectBindingSelector,
): boolean {
  return (
    left.module_id === right.module_id &&
    left.clause_id === right.clause_id &&
    left.case_id === right.case_id &&
    left.role === right.role
  );
}

function digestSetEquals(
  left: EffectBindingSelector,
  right: EffectBindingSelector,
): boolean {
  return SELECTOR_DIGEST_KEYS.every(
    (key) => left[key] === right[key],
  );
}

function identityKey(selector: EffectBindingSelector): string {
  return [
    selector.module_id,
    selector.clause_id,
    selector.case_id,
    selector.role,
  ].join("|");
}

function exactSelectorKey(selector: EffectBindingSelector): string {
  return [
    identityKey(selector),
    ...SELECTOR_DIGEST_KEYS.map((key) => selector[key]),
  ].join("|");
}

function rejectOracleFields(value: unknown, path: string): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) =>
      rejectOracleFields(item, `${path}[${index}]`),
    );
    return;
  }
  if (!isRecord(value)) {
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    if (ORACLE_FIELD.test(key)) {
      bindingFail(
        "SFOL_EFFECT_BINDING_ORACLE_FIELD",
        `${path}.${key}`,
        `effect bindings cannot carry oracle field ${key}`,
      );
    }
    rejectOracleFields(child, `${path}.${key}`);
  }
}

function bindingFail(
  code: EffectBindingDiagnosticCode,
  path: string,
  detail: string,
): never {
  throw new EffectBindingAbort({
    code,
    stage: "effect-binding-resolution",
    path,
    detail,
  });
}

function isRecord(
  value: unknown,
): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function deepFreeze<T>(value: T): T {
  if (
    typeof value === "object" &&
    value !== null &&
    !Object.isFrozen(value)
  ) {
    Object.freeze(value);
    for (const child of Object.values(value)) {
      deepFreeze(child);
    }
  }
  return value;
}
