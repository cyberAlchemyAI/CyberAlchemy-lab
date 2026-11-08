import { createHash } from "node:crypto";

import type {
  ArchitectureConstraintOperator,
  ArchitecturePropertyRequirement,
  ArchitectureRealizationFailure,
  ArchitectureRealizationSpec,
  EnumRealizationProjectionInput,
} from "../contracts/architecture-realization-spec.js";

type JsonObject = Record<string, unknown>;

const ENUM_TYPE = "architecture.EnumImplementation";
const REQUIRED_ENUM_PROPERTIES = Object.freeze([
  "binding.concept_id",
  "binding.current",
  "enum.composition_kind",
  "enum.implemented_members",
]);

const fail = (code: string, detail?: Readonly<Record<string, unknown>>): never => {
  throw Object.assign(new Error(code), { code, ...(detail === undefined ? {} : { detail }) }) as ArchitectureRealizationFailure;
};

const asObject = (value: unknown, code: string): JsonObject => {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail(code);
  return value as JsonObject;
};

const asString = (value: unknown, code: string): string => {
  if (typeof value !== "string" || value.length === 0) fail(code);
  return value as string;
};

const asArray = (value: unknown, code: string): unknown[] => {
  if (!Array.isArray(value)) fail(code);
  return value as unknown[];
};

const parseObject = (source: string, code: string): JsonObject => {
  try {
    return asObject(JSON.parse(source), code);
  } catch (error) {
    if ((error as ArchitectureRealizationFailure).code === code) throw error;
    return fail(code, { message: error instanceof Error ? error.message : String(error) });
  }
};

const canonicalize = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as JsonObject)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, child]) => [key, canonicalize(child)]),
    );
  }
  return value;
};

const canonicalJson = (value: unknown): string => JSON.stringify(canonicalize(value));
const sha256 = (value: string): string => createHash("sha256").update(value).digest("hex");

const indexBy = (
  values: unknown[],
  key: string,
  duplicateCode: string,
): Map<string, JsonObject> => {
  const indexed = new Map<string, JsonObject>();
  for (const value of values) {
    const object = asObject(value, "ARCH_REALIZATION_INPUT_SHAPE_INVALID");
    const identifier = asString(object[key], "ARCH_REALIZATION_INPUT_SHAPE_INVALID");
    if (indexed.has(identifier)) fail(duplicateCode, { [key]: identifier });
    indexed.set(identifier, object);
  }
  return indexed;
};

const isSubtype = (
  concepts: ReadonlyMap<string, JsonObject>,
  actualType: string,
  expectedType: string,
): boolean => {
  let current = concepts.get(actualType);
  const visited = new Set<string>();
  while (current !== undefined) {
    const conceptId = asString(current.concept_id, "ARCH_REALIZATION_INPUT_SHAPE_INVALID");
    if (visited.has(conceptId)) fail("ARCH_REALIZATION_TYPE_CYCLE", { concept_id: conceptId });
    visited.add(conceptId);
    if (conceptId === expectedType) return true;
    const parent = current.extends;
    if (parent === null || parent === undefined) return false;
    current = concepts.get(asString(parent, "ARCH_REALIZATION_INPUT_SHAPE_INVALID"));
  }
  return false;
};

const exactEnumConstraints = (profile: JsonObject): JsonObject[] =>
  asArray(profile.constraints ?? [], "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID")
    .map((value) => asObject(value, "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID"))
    .filter((constraint) =>
      asArray(constraint.applies_to ?? [], "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID")
        .includes(ENUM_TYPE),
    );

const propertyRequirement = (
  property: JsonObject,
): ArchitecturePropertyRequirement => ({
  property_id: asString(property.property_id, "ARCH_REALIZATION_PROPERTY_METADATA_INCOMPLETE"),
  value_type: asObject(property.value_type, "ARCH_REALIZATION_PROPERTY_METADATA_INCOMPLETE"),
  observation_stage: asString(property.observation_stage, "ARCH_REALIZATION_PROPERTY_METADATA_INCOMPLETE"),
  owner_route: asString(property.owner_route, "ARCH_REALIZATION_PROPERTY_METADATA_INCOMPLETE"),
  forbidden_inference: asString(property.forbidden_inference, "ARCH_REALIZATION_PROPERTY_METADATA_INCOMPLETE"),
});

const constraintOperator = (operator: JsonObject): ArchitectureConstraintOperator => ({
  operator_id: asString(operator.operator_id, "ARCH_REALIZATION_OPERATOR_METADATA_INCOMPLETE"),
  accepted_value_types: asArray(
    operator.accepted_value_types,
    "ARCH_REALIZATION_OPERATOR_METADATA_INCOMPLETE",
  ).map((value) => asString(value, "ARCH_REALIZATION_OPERATOR_METADATA_INCOMPLETE")),
  expected_operand_kinds: asArray(
    operator.expected_operand_kinds,
    "ARCH_REALIZATION_OPERATOR_METADATA_INCOMPLETE",
  ).map((value) => asString(value, "ARCH_REALIZATION_OPERATOR_METADATA_INCOMPLETE")),
});

export const deriveEnumArchitectureRealizationSpec = (
  input: EnumRealizationProjectionInput,
): ArchitectureRealizationSpec => {
  const actualDigests = {
    ontology_sha256: sha256(input.ontology_json),
    base_profile_sha256: sha256(input.base_profile_json),
    typescript_profile_sha256: sha256(input.typescript_profile_json),
  };
  for (const [name, actual] of Object.entries(actualDigests)) {
    if (actual !== input.expected_source_digests[name as keyof typeof actualDigests]) {
      fail("ARCH_REALIZATION_SOURCE_DIGEST_STALE", { source: name, actual });
    }
  }

  const ontology = parseObject(input.ontology_json, "ARCH_REALIZATION_ONTOLOGY_JSON_INVALID");
  const baseProfile = parseObject(input.base_profile_json, "ARCH_REALIZATION_BASE_PROFILE_JSON_INVALID");
  const typescriptProfile = parseObject(
    input.typescript_profile_json,
    "ARCH_REALIZATION_TYPESCRIPT_PROFILE_JSON_INVALID",
  );
  const concepts = indexBy(
    asArray(ontology.concept_types, "ARCH_REALIZATION_ONTOLOGY_TYPES_INVALID"),
    "concept_id",
    "ARCH_REALIZATION_TYPE_DUPLICATE",
  );
  const properties = indexBy(
    asArray(ontology.property_definitions, "ARCH_REALIZATION_ONTOLOGY_PROPERTIES_INVALID"),
    "property_id",
    "ARCH_REALIZATION_PROPERTY_DUPLICATE",
  );
  const operators = indexBy(
    asArray(ontology.constraint_operators, "ARCH_REALIZATION_ONTOLOGY_OPERATORS_INVALID"),
    "operator_id",
    "ARCH_REALIZATION_OPERATOR_DUPLICATE",
  );
  const enumType = concepts.get(ENUM_TYPE) ?? fail("ARCH_REALIZATION_ENUM_TYPE_MISSING");
  const definitionType = asString(
    enumType.canonical_meta_type_ref,
    "ARCH_REALIZATION_DEFINITION_TYPE_MISSING",
  );

  const overlays = asArray(
    typescriptProfile.representation_overlays,
    "ARCH_REALIZATION_PROFILE_OVERLAYS_INVALID",
  ).map((value) => asObject(value, "ARCH_REALIZATION_PROFILE_OVERLAYS_INVALID"));
  const matchingOverlays = overlays.filter(({ contract_id }) => contract_id === "enum.profile-representation");
  if (matchingOverlays.length !== 1) fail("ARCH_REALIZATION_PROFILE_OVERLAY_MISSING");
  const overlay = matchingOverlays[0] as JsonObject;
  const constraints = [
    ...exactEnumConstraints(baseProfile),
    ...asArray(
      overlay.representation_constraints ?? [],
      "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID",
    )
      .map((value) => asObject(value, "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID"))
      .filter((constraint) =>
        asArray(constraint.applies_to ?? [], "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID")
          .includes(ENUM_TYPE),
      ),
  ];
  const propertyIds = new Set([
    ...REQUIRED_ENUM_PROPERTIES,
    ...constraints.map((constraint) =>
      asString(constraint.property_id, "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID")),
  ]);
  const requiredProperties = [...propertyIds].sort().map((propertyId) => {
    const property = properties.get(propertyId)
      ?? fail("ARCH_REALIZATION_PROPERTY_MISSING", { property_id: propertyId });
    const appliesTo = asObject(
      property.applies_to,
      "ARCH_REALIZATION_PROPERTY_APPLICABILITY_INVALID",
    );
    const allowedTypes = asArray(
      appliesTo.types,
      "ARCH_REALIZATION_PROPERTY_APPLICABILITY_INVALID",
    ).map((value) => asString(value, "ARCH_REALIZATION_PROPERTY_APPLICABILITY_INVALID"));
    if (!allowedTypes.some((type) => isSubtype(concepts, ENUM_TYPE, type))) {
      fail("ARCH_REALIZATION_PROPERTY_APPLICABILITY_INVALID", { property_id: propertyId });
    }
    return propertyRequirement(property);
  });

  const operatorIds = new Set(
    constraints.map((constraint) =>
      asString(constraint.operator, "ARCH_REALIZATION_PROFILE_CONSTRAINTS_INVALID")),
  );
  const requiredOperators = [...operatorIds].sort().map((operatorId) => {
    const operator = operators.get(operatorId)
      ?? fail("ARCH_REALIZATION_OPERATOR_MISSING", { operator_id: operatorId });
    return constraintOperator(operator);
  });
  const unsupportedOutcomes = [
    ...asArray(overlay.unsupported_forms ?? [], "ARCH_REALIZATION_UNSUPPORTED_OUTCOMES_INVALID")
      .map((value) => asString(value, "ARCH_REALIZATION_UNSUPPORTED_OUTCOMES_INVALID")),
    asString(overlay.missing_decision_outcome, "ARCH_REALIZATION_UNSUPPORTED_OUTCOMES_INVALID"),
    asString(overlay.language_mismatch_outcome, "ARCH_REALIZATION_UNSUPPORTED_OUTCOMES_INVALID"),
  ].sort();

  const withoutDigest = {
    schema_version: "ArchitectureRealizationSpec/v1" as const,
    spec_id: input.spec_id,
    ontology_ref: {
      ontology_id: asString(ontology.ontology_id, "ARCH_REALIZATION_ONTOLOGY_ID_MISSING"),
      schema_version: asString(ontology.schema_version, "ARCH_REALIZATION_ONTOLOGY_VERSION_MISSING"),
      sha256: actualDigests.ontology_sha256,
    },
    profile_ref: {
      profile_id: asString(typescriptProfile.profile_id, "ARCH_REALIZATION_PROFILE_ID_MISSING"),
      schema_version: asString(
        typescriptProfile.schema_version,
        "ARCH_REALIZATION_PROFILE_VERSION_MISSING",
      ),
      sha256: actualDigests.typescript_profile_sha256,
      extends: [{
        profile_id: asString(baseProfile.profile_id, "ARCH_REALIZATION_PROFILE_ID_MISSING"),
        schema_version: asString(baseProfile.schema_version, "ARCH_REALIZATION_PROFILE_VERSION_MISSING"),
        sha256: actualDigests.base_profile_sha256,
      }],
    },
    realization_type: ENUM_TYPE as "architecture.EnumImplementation",
    definition_type_ref: definitionType,
    required_properties: requiredProperties,
    required_relations: [] as const,
    constraint_operators: requiredOperators,
    composition_kind: "direct" as const,
    unsupported_outcomes: unsupportedOutcomes,
    authority_effect: "none" as const,
  };
  return {
    schema_version: withoutDigest.schema_version,
    spec_id: withoutDigest.spec_id,
    ontology_ref: withoutDigest.ontology_ref,
    profile_ref: withoutDigest.profile_ref,
    realization_type: withoutDigest.realization_type,
    definition_type_ref: withoutDigest.definition_type_ref,
    required_properties: withoutDigest.required_properties,
    required_relations: withoutDigest.required_relations,
    constraint_operators: withoutDigest.constraint_operators,
    composition_kind: withoutDigest.composition_kind,
    unsupported_outcomes: withoutDigest.unsupported_outcomes,
    spec_sha256: sha256(canonicalJson(withoutDigest)),
    authority_effect: withoutDigest.authority_effect,
  };
};

const compactJson = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(compactJson).join(", ")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.entries(value as JsonObject)
      .map(([key, child]) => `${JSON.stringify(key)}: ${compactJson(child)}`)
      .join(", ")}}`;
  }
  return JSON.stringify(value);
};

const renderNode = (value: unknown, depth: number, path: readonly string[]): string => {
  const valueTypeObject = value !== null && typeof value === "object" && !Array.isArray(value)
    ? value as JsonObject
    : undefined;
  const valueTypeItems = valueTypeObject?.items !== undefined
    ? asObject(valueTypeObject.items, "ARCH_REALIZATION_VALUE_TYPE_INVALID")
    : undefined;
  const complexValueType = path.at(-1) === "value_type" && valueTypeItems?.kind === "object";
  const compact =
    (path.at(-1) === "value_type" && !complexValueType)
    || path.at(-1) === "accepted_value_types"
    || path.at(-1) === "expected_operand_kinds"
    || (path.includes("value_type") && ["required", "properties"].includes(path.at(-1) ?? ""));
  if (compact) return compactJson(value);
  if (Array.isArray(value)) {
    if (value.length === 0) return "[]";
    const indentation = "  ".repeat(depth + 1);
    return `[\n${value
      .map((child, index) => `${indentation}${renderNode(child, depth + 1, [...path, String(index)])}`)
      .join(",\n")}\n${"  ".repeat(depth)}]`;
  }
  if (value !== null && typeof value === "object") {
    const entries = Object.entries(value as JsonObject);
    if (entries.length === 0) return "{}";
    const indentation = "  ".repeat(depth + 1);
    return `{\n${entries
      .map(([key, child]) =>
        `${indentation}${JSON.stringify(key)}: ${renderNode(child, depth + 1, [...path, key])}`)
      .join(",\n")}\n${"  ".repeat(depth)}}`;
  }
  return JSON.stringify(value);
};

export const renderArchitectureRealizationSpec = (
  spec: ArchitectureRealizationSpec,
): string => `${renderNode(spec, 0, [])}\n`;
