import { digestSfolValue } from "../../cases/index.js";
import {
  integerValue,
  rationalValue,
  type SemanticValue,
} from "../../evaluator/index.js";

export const EFFECT_TRACE_CONTRACT_VERSION =
  "domainspec-sfol-effect-trace-contract/v1" as const;
export const EFFECT_TRACE_VERSION =
  "domainspec-sfol-effect-trace/v1" as const;

export type EffectKind = "call" | "write" | "event" | "error";
export type SemanticValueTag = SemanticValue["tag"];

export interface TypedObservationField {
  readonly name: string;
  readonly value_tag: SemanticValueTag;
}

export interface EffectObservationSlot {
  readonly kind: EffectKind;
  readonly name: string;
  readonly payload_tag: SemanticValueTag;
}

export interface EffectTraceContract {
  readonly schema_version: typeof EFFECT_TRACE_CONTRACT_VERSION;
  readonly contract_id: string;
  readonly pre_record_declaration_id: string;
  readonly post_record_declaration_id: string;
  readonly effect_record_declaration_id: string;
  readonly pre_fields: readonly TypedObservationField[];
  readonly post_fields: readonly TypedObservationField[];
  readonly effect_sequence: readonly EffectObservationSlot[];
  readonly return_observation: {
    readonly value_tag: SemanticValueTag;
  } | null;
  readonly max_effects: number;
}

export interface EffectObservation {
  readonly sequence: number;
  readonly kind: EffectKind;
  readonly name: string;
  readonly payload: SemanticValue;
}

export interface ValidatedEffectTrace {
  readonly schema_version: typeof EFFECT_TRACE_VERSION;
  readonly trace_id: string;
  readonly contract_id: string;
  readonly pre_state: Readonly<Record<string, SemanticValue>>;
  readonly post_state: Readonly<Record<string, SemanticValue>>;
  readonly effects: readonly EffectObservation[];
  readonly return_value: SemanticValue | null;
  readonly trace_digest: string;
}

export type EffectTraceDiagnosticCode =
  | "SFOL_EFFECT_UNKNOWN_VERSION"
  | "SFOL_EFFECT_INVALID_SHAPE"
  | "SFOL_EFFECT_CONTRACT_INVALID"
  | "SFOL_EFFECT_MISSING_OBSERVATION"
  | "SFOL_EFFECT_EXTRA_OBSERVATION"
  | "SFOL_EFFECT_ORDER_MISMATCH"
  | "SFOL_EFFECT_WRONG_TYPE"
  | "SFOL_EFFECT_DUPLICATE_SEQUENCE"
  | "SFOL_EFFECT_RESOURCE_LIMIT";

export interface EffectTraceDiagnostic {
  readonly code: EffectTraceDiagnosticCode;
  readonly stage: "effect-contract";
  readonly path: string;
  readonly detail: string;
}

export type EffectTraceValidationResult =
  | {
      readonly ok: true;
      readonly value: ValidatedEffectTrace;
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly EffectTraceDiagnostic[];
    };

class EffectContractAbort extends Error {
  readonly diagnostic: EffectTraceDiagnostic;

  constructor(diagnostic: EffectTraceDiagnostic) {
    super(`${diagnostic.code} at ${diagnostic.path}: ${diagnostic.detail}`);
    this.name = "EffectContractAbort";
    this.diagnostic = diagnostic;
  }
}

export function validateEffectTrace(
  contract: EffectTraceContract,
  input: unknown,
): EffectTraceValidationResult {
  try {
    validateContract(contract);
    const trace = requireRecord(input, "$");
    exactKeys(
      trace,
      [
        "schema_version",
        "trace_id",
        "contract_id",
        "pre_state",
        "post_state",
        "effects",
        "return_value",
      ],
      "$",
    );
    if (trace.schema_version !== EFFECT_TRACE_VERSION) {
      effectFail(
        "SFOL_EFFECT_UNKNOWN_VERSION",
        "$.schema_version",
        `expected ${EFFECT_TRACE_VERSION}`,
      );
    }
    const traceId = requireNonEmptyString(trace.trace_id, "$.trace_id");
    if (trace.contract_id !== contract.contract_id) {
      effectFail(
        "SFOL_EFFECT_CONTRACT_INVALID",
        "$.contract_id",
        `expected contract ${contract.contract_id}`,
      );
    }
    const preState = decodeState(
      trace.pre_state,
      contract.pre_fields,
      "$.pre_state",
    );
    const postState = decodeState(
      trace.post_state,
      contract.post_fields,
      "$.post_state",
    );
    const effects = decodeEffects(
      trace.effects,
      contract.effect_sequence,
      contract.max_effects,
      "$.effects",
    );
    const returnValue = decodeReturn(
      trace.return_value,
      contract.return_observation,
      "$.return_value",
    );
    const unsigned = {
      schema_version: EFFECT_TRACE_VERSION,
      trace_id: traceId,
      contract_id: contract.contract_id,
      pre_state: preState,
      post_state: postState,
      effects,
      return_value: returnValue,
    };
    return Object.freeze({
      ok: true,
      value: deepFreeze({
        ...unsigned,
        trace_digest: digestSfolValue(unsigned),
      }),
    });
  } catch (error: unknown) {
    if (error instanceof EffectContractAbort) {
      return Object.freeze({
        ok: false,
        diagnostics: Object.freeze([Object.freeze(error.diagnostic)]),
      });
    }
    return Object.freeze({
      ok: false,
      diagnostics: Object.freeze([
        Object.freeze({
          code: "SFOL_EFFECT_INVALID_SHAPE",
          stage: "effect-contract",
          path: "$",
          detail: "effect trace input is structurally invalid",
        }),
      ]),
    });
  }
}

function validateContract(contract: EffectTraceContract): void {
  if (contract.schema_version !== EFFECT_TRACE_CONTRACT_VERSION) {
    effectFail(
      "SFOL_EFFECT_UNKNOWN_VERSION",
      "$contract.schema_version",
      `expected ${EFFECT_TRACE_CONTRACT_VERSION}`,
    );
  }
  for (const [path, value] of [
    ["$contract.contract_id", contract.contract_id],
    [
      "$contract.pre_record_declaration_id",
      contract.pre_record_declaration_id,
    ],
    [
      "$contract.post_record_declaration_id",
      contract.post_record_declaration_id,
    ],
    [
      "$contract.effect_record_declaration_id",
      contract.effect_record_declaration_id,
    ],
  ] as const) {
    requireNonEmptyString(value, path);
  }
  if (
    !Number.isSafeInteger(contract.max_effects) ||
    contract.max_effects < 0
  ) {
    effectFail(
      "SFOL_EFFECT_CONTRACT_INVALID",
      "$contract.max_effects",
      "max_effects must be a non-negative safe integer",
    );
  }
  validateFieldContract(contract.pre_fields, "$contract.pre_fields");
  validateFieldContract(contract.post_fields, "$contract.post_fields");
  if (contract.effect_sequence.length > contract.max_effects) {
    effectFail(
      "SFOL_EFFECT_RESOURCE_LIMIT",
      "$contract.effect_sequence",
      "declared effect sequence exceeds max_effects",
    );
  }
  for (const [index, slot] of contract.effect_sequence.entries()) {
    requireNonEmptyString(
      slot.name,
      `$contract.effect_sequence[${index}].name`,
    );
    requireValueTag(
      slot.payload_tag,
      `$contract.effect_sequence[${index}].payload_tag`,
    );
    if (!["call", "write", "event", "error"].includes(slot.kind)) {
      effectFail(
        "SFOL_EFFECT_CONTRACT_INVALID",
        `$contract.effect_sequence[${index}].kind`,
        `unknown effect kind ${String(slot.kind)}`,
      );
    }
  }
  if (contract.return_observation !== null) {
    requireValueTag(
      contract.return_observation.value_tag,
      "$contract.return_observation.value_tag",
    );
  }
}

function validateFieldContract(
  fields: readonly TypedObservationField[],
  path: string,
): void {
  const names = new Set<string>();
  for (const [index, field] of fields.entries()) {
    requireNonEmptyString(field.name, `${path}[${index}].name`);
    requireValueTag(field.value_tag, `${path}[${index}].value_tag`);
    if (names.has(field.name)) {
      effectFail(
        "SFOL_EFFECT_CONTRACT_INVALID",
        path,
        `duplicate field ${field.name}`,
      );
    }
    names.add(field.name);
  }
}

function decodeState(
  input: unknown,
  fields: readonly TypedObservationField[],
  path: string,
): Readonly<Record<string, SemanticValue>> {
  const state = requireRecord(input, path);
  const expectedNames = fields.map((field) => field.name).sort();
  const actualNames = Object.keys(state).sort();
  const missing = expectedNames.filter((name) => !Object.hasOwn(state, name));
  if (missing.length > 0) {
    effectFail(
      "SFOL_EFFECT_MISSING_OBSERVATION",
      path,
      `missing state field(s): ${missing.join(", ")}`,
    );
  }
  const extra = actualNames.filter((name) => !expectedNames.includes(name));
  if (extra.length > 0) {
    effectFail(
      "SFOL_EFFECT_EXTRA_OBSERVATION",
      path,
      `undeclared state field(s): ${extra.join(", ")}`,
    );
  }
  const decoded: Record<string, SemanticValue> = {};
  for (const field of [...fields].sort((left, right) =>
    left.name.localeCompare(right.name),
  )) {
    decoded[field.name] = decodeTypedValue(
      state[field.name],
      field.value_tag,
      `${path}.${field.name}`,
    );
  }
  return Object.freeze(decoded);
}

function decodeEffects(
  input: unknown,
  slots: readonly EffectObservationSlot[],
  maxEffects: number,
  path: string,
): readonly EffectObservation[] {
  if (!Array.isArray(input)) {
    effectFail(
      "SFOL_EFFECT_INVALID_SHAPE",
      path,
      "effects must be an array",
    );
  }
  if (input.length > maxEffects) {
    effectFail(
      "SFOL_EFFECT_RESOURCE_LIMIT",
      path,
      `received ${input.length} effects; maximum is ${maxEffects}`,
    );
  }
  if (input.length < slots.length) {
    effectFail(
      "SFOL_EFFECT_MISSING_OBSERVATION",
      path,
      `expected ${slots.length} effects; received ${input.length}`,
    );
  }
  if (input.length > slots.length) {
    effectFail(
      "SFOL_EFFECT_EXTRA_OBSERVATION",
      path,
      `expected ${slots.length} effects; received ${input.length}`,
    );
  }
  const decoded = input.map((value, index): EffectObservation => {
    const itemPath = `${path}[${index}]`;
    const effect = requireRecord(value, itemPath);
    exactKeys(effect, ["sequence", "kind", "name", "payload"], itemPath);
    if (!Number.isSafeInteger(effect.sequence) || effect.sequence !== index) {
      effectFail(
        "SFOL_EFFECT_DUPLICATE_SEQUENCE",
        `${itemPath}.sequence`,
        `sequence must equal exact zero-based position ${index}`,
      );
    }
    const slot = slots[index];
    if (slot === undefined) {
      effectFail(
        "SFOL_EFFECT_EXTRA_OBSERVATION",
        itemPath,
        "effect has no declared slot",
      );
    }
    if (effect.kind !== slot.kind || effect.name !== slot.name) {
      effectFail(
        "SFOL_EFFECT_ORDER_MISMATCH",
        itemPath,
        `expected ${slot.kind}:${slot.name}; received ${String(effect.kind)}:${String(effect.name)}`,
      );
    }
    return Object.freeze({
      sequence: index,
      kind: slot.kind,
      name: slot.name,
      payload: decodeTypedValue(
        effect.payload,
        slot.payload_tag,
        `${itemPath}.payload`,
      ),
    });
  });
  return Object.freeze(decoded);
}

function decodeReturn(
  input: unknown,
  contract: EffectTraceContract["return_observation"],
  path: string,
): SemanticValue | null {
  if (contract === null) {
    if (input !== null) {
      effectFail(
        "SFOL_EFFECT_EXTRA_OBSERVATION",
        path,
        "return observation is undeclared",
      );
    }
    return null;
  }
  if (input === null) {
    effectFail(
      "SFOL_EFFECT_MISSING_OBSERVATION",
      path,
      "declared return observation is absent",
    );
  }
  return decodeTypedValue(input, contract.value_tag, path);
}

function decodeTypedValue(
  input: unknown,
  expectedTag: SemanticValueTag,
  path: string,
): SemanticValue {
  const value = requireRecord(input, path);
  if (value.tag !== expectedTag) {
    effectFail(
      "SFOL_EFFECT_WRONG_TYPE",
      path,
      `expected ${expectedTag}; received ${String(value.tag)}`,
    );
  }
  switch (expectedTag) {
    case "boolean":
      exactKeys(value, ["tag", "value"], path);
      if (typeof value.value !== "boolean") {
        wrongValue(path, expectedTag);
      }
      return Object.freeze({ tag: "boolean", value: value.value });
    case "string":
      exactKeys(value, ["tag", "value"], path);
      if (typeof value.value !== "string") {
        wrongValue(path, expectedTag);
      }
      return Object.freeze({ tag: "string", value: value.value });
    case "integer":
      exactKeys(value, ["tag", "value"], path);
      if (typeof value.value !== "string") {
        wrongValue(path, expectedTag);
      }
      try {
        return integerValue(value.value);
      } catch {
        wrongValue(path, expectedTag);
      }
    case "rational":
      exactKeys(value, ["tag", "numerator", "denominator"], path);
      if (
        typeof value.numerator !== "string" ||
        typeof value.denominator !== "string"
      ) {
        wrongValue(path, expectedTag);
      }
      try {
        return rationalValue(value.numerator, value.denominator);
      } catch {
        wrongValue(path, expectedTag);
      }
    case "enum":
      exactKeys(value, ["tag", "declaration_id", "member"], path);
      if (
        typeof value.declaration_id !== "string" ||
        typeof value.member !== "string"
      ) {
        wrongValue(path, expectedTag);
      }
      return Object.freeze({
        tag: "enum",
        declaration_id: value.declaration_id,
        member: value.member,
      });
    case "record": {
      exactKeys(value, ["tag", "declaration_id", "fields"], path);
      if (
        typeof value.declaration_id !== "string" ||
        !isRecord(value.fields)
      ) {
        wrongValue(path, expectedTag);
      }
      const fields: Record<string, SemanticValue> = {};
      for (const key of Object.keys(value.fields).sort()) {
        const raw = value.fields[key];
        if (!isRecord(raw) || typeof raw.tag !== "string") {
          wrongValue(`${path}.fields.${key}`, "record");
        }
        fields[key] = decodeTypedValue(
          raw,
          raw.tag as SemanticValueTag,
          `${path}.fields.${key}`,
        );
      }
      return Object.freeze({
        tag: "record",
        declaration_id: value.declaration_id,
        fields: Object.freeze(fields),
      });
    }
    case "list":
    case "set": {
      exactKeys(value, ["tag", "items"], path);
      if (!Array.isArray(value.items)) {
        wrongValue(path, expectedTag);
      }
      const items = value.items.map((item, index) => {
        if (!isRecord(item) || typeof item.tag !== "string") {
          wrongValue(`${path}.items[${index}]`, expectedTag);
        }
        return decodeTypedValue(
          item,
          item.tag as SemanticValueTag,
          `${path}.items[${index}]`,
        );
      });
      return Object.freeze({
        tag: expectedTag,
        items: Object.freeze(items),
      });
    }
  }
}

function requireValueTag(input: unknown, path: string): SemanticValueTag {
  if (
    typeof input !== "string" ||
    ![
      "boolean",
      "string",
      "integer",
      "rational",
      "enum",
      "record",
      "list",
      "set",
    ].includes(input)
  ) {
    effectFail(
      "SFOL_EFFECT_CONTRACT_INVALID",
      path,
      `unknown semantic value tag ${String(input)}`,
    );
  }
  return input as SemanticValueTag;
}

function wrongValue(path: string, tag: SemanticValueTag): never {
  effectFail(
    "SFOL_EFFECT_WRONG_TYPE",
    path,
    `invalid ${tag} semantic value`,
  );
}

function exactKeys(
  value: Readonly<Record<string, unknown>>,
  expected: readonly string[],
  path: string,
): void {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (
    actual.length !== wanted.length ||
    actual.some((key, index) => key !== wanted[index])
  ) {
    effectFail(
      "SFOL_EFFECT_INVALID_SHAPE",
      path,
      `expected keys ${wanted.join(",")}; received ${actual.join(",")}`,
    );
  }
}

function requireRecord(
  input: unknown,
  path: string,
): Readonly<Record<string, unknown>> {
  if (!isRecord(input)) {
    effectFail(
      "SFOL_EFFECT_INVALID_SHAPE",
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
    effectFail(
      "SFOL_EFFECT_INVALID_SHAPE",
      path,
      "expected a non-empty string",
    );
  }
  return input;
}

function effectFail(
  code: EffectTraceDiagnosticCode,
  path: string,
  detail: string,
): never {
  throw new EffectContractAbort({
    code,
    stage: "effect-contract",
    path,
    detail,
  });
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
