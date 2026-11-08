import {
  canonicalSfolJson,
  digestSfolValue,
  type PureInvocation,
} from "../../cases/index.js";
import type { SemanticValue } from "../../evaluator/index.js";
import type { ResolvedPureBinding } from "../../bindings/index.js";

export interface RawJsonObject {
  readonly [key: string]: RawJsonValue;
}

export interface RawJsonArray extends ReadonlyArray<RawJsonValue> {}

export type RawJsonValue =
  | null
  | boolean
  | number
  | string
  | RawJsonArray
  | RawJsonObject;

export interface PureTargetHandle {
  readonly target_digest: string;
  readonly runtime_digest: string;
  readonly invoke: (...arguments_: SemanticValue[]) => unknown;
}

export interface PureTargetResolver {
  resolve(module: string, symbol: string): PureTargetHandle | null;
}

export type PureRunDiagnosticCode =
  | "SFOL_RUN_BINDING_MISMATCH"
  | "SFOL_RUN_ARGUMENT_UNBOUND"
  | "SFOL_RUN_TARGET_UNBOUND"
  | "SFOL_RUN_TARGET_STALE"
  | "SFOL_RUN_RAW_VALUE_INVALID";

export interface PureRunDiagnostic {
  readonly code: PureRunDiagnosticCode;
  readonly stage: "pure-run";
  readonly detail: string;
}

interface ObservationBase {
  readonly schema_version: "domainspec-sfol-pure-observation/v1";
  readonly case_id: string;
  readonly case_digest: string;
  readonly binding_id: string;
  readonly target_digest: string;
  readonly runtime_digest: string;
  readonly argument_digest: string;
  readonly observation_digest: string;
}

export interface ReturnedPureObservation extends ObservationBase {
  readonly status: "returned";
  readonly raw_return: RawJsonValue;
}

export interface ThrownPureObservation extends ObservationBase {
  readonly status: "threw";
  readonly raw_error: {
    readonly name: string;
    readonly message: string;
  };
}

export interface IndeterminatePureObservation extends ObservationBase {
  readonly status: "indeterminate";
  readonly diagnostic: PureRunDiagnostic;
}

export type RawPureObservation =
  | ReturnedPureObservation
  | ThrownPureObservation
  | IndeterminatePureObservation;

export function runPureCase(
  invocation: PureInvocation,
  resolved: ResolvedPureBinding,
  targets: PureTargetResolver,
): RawPureObservation {
  const binding = resolved.binding;
  if (
    resolved.selector.case_id !== invocation.case_id ||
    resolved.selector.case_digest !== invocation.case_digest ||
    resolved.selector.module_id !== invocation.module_id ||
    resolved.selector.module_digest !== invocation.module_digest ||
    resolved.selector.clause_id !== invocation.clause_id ||
    resolved.selector.clause_digest !== invocation.clause_digest ||
    resolved.selector.fixture_digest !== invocation.fixture_digest ||
    resolved.selector.role !== invocation.role
  ) {
    return indeterminateObservation(
      invocation,
      binding.binding_id,
      binding.target.target_digest,
      binding.target.runtime_digest,
      [],
      {
        code: "SFOL_RUN_BINDING_MISMATCH",
        stage: "pure-run",
        detail: "resolved selector does not exactly match the invocation",
      },
    );
  }

  const arguments_: SemanticValue[] = [];
  for (const projection of binding.argument_map) {
    const value = invocation.inputs[projection.input_name];
    if (value === undefined) {
      return indeterminateObservation(
        invocation,
        binding.binding_id,
        binding.target.target_digest,
        binding.target.runtime_digest,
        arguments_,
        {
          code: "SFOL_RUN_ARGUMENT_UNBOUND",
          stage: "pure-run",
          detail: `case input ${projection.input_name} is absent`,
        },
      );
    }
    arguments_.push(value);
  }

  const target = targets.resolve(
    binding.target.module,
    binding.target.symbol,
  );
  if (target === null) {
    return indeterminateObservation(
      invocation,
      binding.binding_id,
      binding.target.target_digest,
      binding.target.runtime_digest,
      arguments_,
      {
        code: "SFOL_RUN_TARGET_UNBOUND",
        stage: "pure-run",
        detail: `target ${binding.target.module}#${binding.target.symbol} is absent`,
      },
    );
  }
  if (
    target.target_digest !== binding.target.target_digest ||
    target.runtime_digest !== binding.target.runtime_digest
  ) {
    return indeterminateObservation(
      invocation,
      binding.binding_id,
      target.target_digest,
      target.runtime_digest,
      arguments_,
      {
        code: "SFOL_RUN_TARGET_STALE",
        stage: "pure-run",
        detail: "resolved target or runtime digest is stale",
      },
    );
  }

  try {
    const raw = cloneRawJson(target.invoke(...arguments_));
    return returnedObservation(
      invocation,
      binding.binding_id,
      target.target_digest,
      target.runtime_digest,
      arguments_,
      raw,
    );
  } catch (error: unknown) {
    if (error instanceof RawValueAbort) {
      return indeterminateObservation(
        invocation,
        binding.binding_id,
        target.target_digest,
        target.runtime_digest,
        arguments_,
        {
          code: "SFOL_RUN_RAW_VALUE_INVALID",
          stage: "pure-run",
          detail: error.message,
        },
      );
    }
    const rawError =
      error instanceof Error
        ? { name: error.name, message: error.message }
        : { name: "NonErrorThrow", message: String(error) };
    return thrownObservation(
      invocation,
      binding.binding_id,
      target.target_digest,
      target.runtime_digest,
      arguments_,
      rawError,
    );
  }
}

function returnedObservation(
  invocation: PureInvocation,
  bindingId: string,
  targetDigest: string,
  runtimeDigest: string,
  arguments_: readonly SemanticValue[],
  rawReturn: RawJsonValue,
): ReturnedPureObservation {
  const unsigned = {
    schema_version: "domainspec-sfol-pure-observation/v1" as const,
    case_id: invocation.case_id,
    case_digest: invocation.case_digest,
    binding_id: bindingId,
    target_digest: targetDigest,
    runtime_digest: runtimeDigest,
    argument_digest: digestSfolValue(arguments_),
    status: "returned" as const,
    raw_return: rawReturn,
  };
  return deepFreeze({
    ...unsigned,
    observation_digest: digestSfolValue(unsigned),
  });
}

function thrownObservation(
  invocation: PureInvocation,
  bindingId: string,
  targetDigest: string,
  runtimeDigest: string,
  arguments_: readonly SemanticValue[],
  rawError: { readonly name: string; readonly message: string },
): ThrownPureObservation {
  const unsigned = {
    schema_version: "domainspec-sfol-pure-observation/v1" as const,
    case_id: invocation.case_id,
    case_digest: invocation.case_digest,
    binding_id: bindingId,
    target_digest: targetDigest,
    runtime_digest: runtimeDigest,
    argument_digest: digestSfolValue(arguments_),
    status: "threw" as const,
    raw_error: rawError,
  };
  return deepFreeze({
    ...unsigned,
    observation_digest: digestSfolValue(unsigned),
  });
}

function indeterminateObservation(
  invocation: PureInvocation,
  bindingId: string,
  targetDigest: string,
  runtimeDigest: string,
  arguments_: readonly SemanticValue[],
  diagnostic: PureRunDiagnostic,
): IndeterminatePureObservation {
  const unsigned = {
    schema_version: "domainspec-sfol-pure-observation/v1" as const,
    case_id: invocation.case_id,
    case_digest: invocation.case_digest,
    binding_id: bindingId,
    target_digest: targetDigest,
    runtime_digest: runtimeDigest,
    argument_digest: digestSfolValue(arguments_),
    status: "indeterminate" as const,
    diagnostic,
  };
  return deepFreeze({
    ...unsigned,
    observation_digest: digestSfolValue(unsigned),
  });
}

class RawValueAbort extends Error {
  constructor(detail: string) {
    super(detail);
    this.name = "RawValueAbort";
  }
}

function cloneRawJson(value: unknown, seen = new Set<object>()): RawJsonValue {
  if (
    value === null ||
    typeof value === "boolean" ||
    typeof value === "string"
  ) {
    return value;
  }
  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new RawValueAbort("raw return contains a non-finite number");
    }
    return value;
  }
  if (Array.isArray(value)) {
    enter(value, seen);
    const result = value.map((item) => cloneRawJson(item, seen));
    seen.delete(value);
    return Object.freeze(result);
  }
  if (isPlainRecord(value)) {
    enter(value, seen);
    const result: Record<string, RawJsonValue> = {};
    for (const key of Object.keys(value).sort()) {
      result[key] = cloneRawJson(value[key], seen);
    }
    seen.delete(value);
    canonicalSfolJson(result);
    return Object.freeze(result);
  }
  throw new RawValueAbort(
    `raw return contains unsupported ${typeof value} data`,
  );
}

function enter(value: object, seen: Set<object>): void {
  if (seen.has(value)) {
    throw new RawValueAbort("raw return contains a cycle");
  }
  seen.add(value);
}

function isPlainRecord(
  value: unknown,
): value is Readonly<Record<string, unknown>> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return false;
  }
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) {
      deepFreeze(child);
    }
  }
  return value;
}
