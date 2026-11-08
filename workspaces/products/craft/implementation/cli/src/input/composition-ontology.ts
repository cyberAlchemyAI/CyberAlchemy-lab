/** Shared composition evidence contract. Admission is always a separate decision. */
export const COMPOSITION_ONTOLOGY_SCHEMA = "domainspec.composition-ontology/v1" as const;
export const LEGACY_ALCHLANG_ONTOLOGY_SCHEMA = "alchlang.derived-ontology/v1" as const;

export function normalizeCompositionOntology(value: unknown): Record<string, any> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("DS_PROJECT_COMPOSITION: ontology object required");
  }
  const ontology = value as Record<string, any>;
  if (ontology.schema_version === LEGACY_ALCHLANG_ONTOLOGY_SCHEMA) {
    if (Object.hasOwn(ontology, "source_format")) {
      throw new Error("DS_PROJECT_COMPOSITION: legacy ontology cannot override source format");
    }
    return { ...ontology, schema_version: COMPOSITION_ONTOLOGY_SCHEMA, source_format: "alchlang" };
  }
  if (ontology.schema_version !== COMPOSITION_ONTOLOGY_SCHEMA ||
      !["alchlang", "domainspec-json"].includes(ontology.source_format)) {
    throw new Error("DS_PROJECT_COMPOSITION: unsupported ontology schema/source format");
  }
  // This adapter selects the format only. The compiler validates all semantic
  // bindings, source evidence and claim limits against the composition.
  return { ...ontology };
}
