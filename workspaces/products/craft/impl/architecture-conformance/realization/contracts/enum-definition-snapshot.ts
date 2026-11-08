import { createHash } from "node:crypto";

type JsonObject = Record<string, unknown>;

export type EnumDefinitionMember = Readonly<{
  member_id: string;
  semantic_value: string;
}>;

export type EnumDefinitionSnapshot = Readonly<{
  schema_version: "EnumDefinitionSnapshot/v1";
  definition_id: string;
  definition_version: string;
  concept_id: string;
  composition_kind: "direct";
  order_semantics: "none";
  members: readonly EnumDefinitionMember[];
  definition_sha256: string;
  authority_ref: string;
  authority_status: "candidate-fixture" | "owner-issued";
  authority_effect: "none";
}>;

export class EnumDefinitionSnapshotError extends Error {
  readonly code: string;
  readonly detail?: Readonly<Record<string, unknown>>;

  constructor(code: string, detail?: Readonly<Record<string, unknown>>) {
    super(code);
    this.name = "EnumDefinitionSnapshotError";
    this.code = code;
    this.detail = detail;
  }
}

const fail = (code: string, detail?: Readonly<Record<string, unknown>>): never => {
  throw new EnumDefinitionSnapshotError(code, detail);
};

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left, "utf8").compare(Buffer.from(right, "utf8"));

const canonicalize = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as JsonObject)
        .sort(([left], [right]) => compareUtf8(left, right))
        .map(([key, child]) => [key, canonicalize(child)]),
    );
  }
  return value;
};

export const canonicalEnumDefinitionJson = (value: unknown): string =>
  JSON.stringify(canonicalize(value));

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");

const exactKeys = (value: JsonObject, expected: readonly string[]): boolean => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  return actual.length === wanted.length && actual.every((key, index) => key === wanted[index]);
};

const asObject = (value: unknown): JsonObject => {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    return fail("ARCH_ENUM_DEFINITION_SHAPE_INVALID");
  }
  return value as JsonObject;
};

const identity = (value: unknown, code: string): string => {
  if (typeof value !== "string" || value.length === 0 || /[\u0000-\u001f\u007f]/u.test(value)) {
    return fail(code);
  }
  return value;
};

const normalizedMembers = (value: unknown): readonly EnumDefinitionMember[] => {
  if (!Array.isArray(value)) return fail("ARCH_ENUM_DEFINITION_SHAPE_INVALID");
  if (value.length === 0) return fail("ARCH_ENUM_DEFINITION_MEMBERS_EMPTY");
  const members = value.map((raw) => {
    const member = asObject(raw);
    if (!exactKeys(member, ["member_id", "semantic_value"])) {
      return fail("ARCH_ENUM_DEFINITION_SHAPE_INVALID");
    }
    return {
      member_id: identity(member.member_id, "ARCH_ENUM_DEFINITION_MEMBER_ID_INVALID"),
      semantic_value: identity(
        member.semantic_value,
        "ARCH_ENUM_DEFINITION_MEMBER_VALUE_INVALID",
      ),
    };
  }).sort((left, right) => compareUtf8(left.member_id, right.member_id));
  const memberIds = new Set<string>();
  const semanticValues = new Set<string>();
  for (const member of members) {
    if (memberIds.has(member.member_id)) {
      fail("ARCH_ENUM_DEFINITION_MEMBER_ID_DUPLICATE", { member_id: member.member_id });
    }
    if (semanticValues.has(member.semantic_value)) {
      fail("ARCH_ENUM_DEFINITION_MEMBER_VALUE_DUPLICATE", {
        semantic_value: member.semantic_value,
      });
    }
    memberIds.add(member.member_id);
    semanticValues.add(member.semantic_value);
  }
  return members;
};

const withoutDigest = (snapshot: Omit<EnumDefinitionSnapshot, "definition_sha256">) => ({
  schema_version: snapshot.schema_version,
  definition_id: snapshot.definition_id,
  definition_version: snapshot.definition_version,
  concept_id: snapshot.concept_id,
  composition_kind: snapshot.composition_kind,
  order_semantics: snapshot.order_semantics,
  members: [...snapshot.members].sort((left, right) => compareUtf8(left.member_id, right.member_id)),
  authority_ref: snapshot.authority_ref,
  authority_status: snapshot.authority_status,
  authority_effect: snapshot.authority_effect,
});

export const computeEnumDefinitionSha256 = (
  snapshot: Omit<EnumDefinitionSnapshot, "definition_sha256">,
): string => sha256(canonicalEnumDefinitionJson(withoutDigest(snapshot)));

const deepFreeze = <Value>(value: Value): Readonly<Value> => {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    for (const key of Reflect.ownKeys(value)) {
      deepFreeze((value as Record<PropertyKey, unknown>)[key]);
    }
    Object.freeze(value);
  }
  return value;
};

export const validateEnumDefinitionSnapshot = (value: unknown): EnumDefinitionSnapshot => {
  const source = asObject(value);
  if (!exactKeys(source, [
    "schema_version",
    "definition_id",
    "definition_version",
    "concept_id",
    "composition_kind",
    "order_semantics",
    "members",
    "definition_sha256",
    "authority_ref",
    "authority_status",
    "authority_effect",
  ])) return fail("ARCH_ENUM_DEFINITION_SHAPE_INVALID");
  if (source.schema_version !== "EnumDefinitionSnapshot/v1"
      || source.composition_kind !== "direct"
      || source.order_semantics !== "none") {
    return fail("ARCH_ENUM_DEFINITION_SHAPE_INVALID");
  }
  const authorityStatus = source.authority_status;
  if (authorityStatus === "canonical-promoted" || source.authority_effect !== "none") {
    return fail("ARCH_ENUM_DEFINITION_AUTHORITY_INFLATION");
  }
  if (authorityStatus !== "candidate-fixture" && authorityStatus !== "owner-issued") {
    return fail("ARCH_ENUM_DEFINITION_AUTHORITY_STATUS_INVALID");
  }
  const validAuthorityStatus = authorityStatus as EnumDefinitionSnapshot["authority_status"];
  const digest = source.definition_sha256;
  if (typeof digest !== "string" || !/^[a-f0-9]{64}$/u.test(digest)) {
    return fail("ARCH_ENUM_DEFINITION_DIGEST_INVALID");
  }
  const snapshotWithoutDigest = {
    schema_version: "EnumDefinitionSnapshot/v1" as const,
    definition_id: identity(source.definition_id, "ARCH_ENUM_DEFINITION_IDENTITY_INVALID"),
    definition_version: identity(
      source.definition_version,
      "ARCH_ENUM_DEFINITION_IDENTITY_INVALID",
    ),
    concept_id: identity(source.concept_id, "ARCH_ENUM_DEFINITION_IDENTITY_INVALID"),
    composition_kind: "direct" as const,
    order_semantics: "none" as const,
    members: normalizedMembers(source.members),
    authority_ref: identity(
      source.authority_ref,
      "ARCH_ENUM_DEFINITION_AUTHORITY_REF_INVALID",
    ),
    authority_status: validAuthorityStatus,
    authority_effect: "none" as const,
  };
  const actualDigest = computeEnumDefinitionSha256(snapshotWithoutDigest);
  if (actualDigest !== digest) {
    return fail("ARCH_ENUM_DEFINITION_DIGEST_STALE", { expected: digest, actual: actualDigest });
  }
  return deepFreeze({
    ...snapshotWithoutDigest,
    definition_sha256: digest,
  }) as EnumDefinitionSnapshot;
};
