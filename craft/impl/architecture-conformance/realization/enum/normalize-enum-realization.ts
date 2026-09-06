import { createHash } from "node:crypto";

import type { ArchitectureRealizationSpec } from "../contracts/architecture-realization-spec.js";
import {
  validateEnumDefinitionSnapshot,
  type EnumDefinitionSnapshot,
} from "../contracts/enum-definition-snapshot.js";
import type { EnumRealizationIR } from "../contracts/enum-realization-ir.js";

type JsonObject = Record<string, unknown>;

export class EnumRealizationNormalizationError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "EnumRealizationNormalizationError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new EnumRealizationNormalizationError(code);
};
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : value !== null && typeof value === "object"
    ? Object.fromEntries(Object.entries(value as JsonObject)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;
const sha256 = (value: unknown): string =>
  createHash("sha256").update(JSON.stringify(canonicalize(value))).digest("hex");

export const computeEnumRealizationIrSha256 = (
  ir: Omit<EnumRealizationIR, "ir_sha256">,
): string => sha256({
  ...ir,
  members: [...ir.members].sort((left, right) => compareUtf8(left.member_id, right.member_id)),
});

const validateSpec = (spec: ArchitectureRealizationSpec): void => {
  if (spec.schema_version !== "ArchitectureRealizationSpec/v1"
      || spec.realization_type !== "architecture.EnumImplementation"
      || spec.definition_type_ref !== "DS-D1.3"
      || spec.composition_kind !== "direct"
      || spec.authority_effect !== "none"
      || !/^[a-f0-9]{64}$/u.test(spec.spec_sha256)) {
    fail("ARCH_ENUM_IR_REALIZATION_SPEC_INVALID");
  }
};

export const normalizeEnumRealization = (
  definitionInput: unknown,
  spec: ArchitectureRealizationSpec,
): EnumRealizationIR => {
  const definition: EnumDefinitionSnapshot = validateEnumDefinitionSnapshot(definitionInput);
  validateSpec(spec);
  if (definition.composition_kind !== spec.composition_kind) {
    return fail("ARCH_ENUM_IR_COMPOSITION_MISMATCH");
  }
  const members = [...definition.members]
    .sort((left, right) => compareUtf8(left.member_id, right.member_id));
  if (members.length !== definition.members.length
      || new Set(members.map(({ member_id: memberId }) => memberId)).size !== members.length
      || new Set(members.map(({ semantic_value: value }) => value)).size !== members.length) {
    return fail("ARCH_ENUM_IR_MEMBER_BIJECTION_INVALID");
  }
  const withoutDigest = {
    schema_version: "EnumRealizationIR/v1" as const,
    definition_ref: {
      definition_id: definition.definition_id,
      definition_version: definition.definition_version,
      definition_sha256: definition.definition_sha256,
    },
    realization_spec_ref: {
      spec_id: spec.spec_id,
      spec_sha256: spec.spec_sha256,
    },
    concept_id: definition.concept_id,
    composition_kind: "direct" as const,
    order_semantics: "none" as const,
    members,
    authority_effect: "none" as const,
  };
  return Object.freeze({
    ...withoutDigest,
    members: Object.freeze(members.map((member) => Object.freeze({ ...member }))),
    ir_sha256: computeEnumRealizationIrSha256(withoutDigest),
  });
};
