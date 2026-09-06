import { createHash } from "node:crypto";

import {
  buildShipmentPriorityProof,
  type ShipmentPriorityRawInputs,
} from "./run-shipment-priority-proof.js";

type JsonRecord = Record<string, unknown>;

export type ShipmentPrioritySemanticSliceInputs = Readonly<{
  case: string;
  expected: string;
  ontology_slice: string;
  typescript_profile_slice: string;
  provider: string;
}>;

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const isRecord = (value: unknown): value is JsonRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};
const canonicalize = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (isRecord(value)) return Object.fromEntries(Object.entries(value)
    .sort(([left], [right]) => Buffer.from(left).compare(Buffer.from(right)))
    .map(([key, child]) => [key, canonicalize(child)]));
  return value;
};
const canonicalJson = (value: unknown): string => JSON.stringify(canonicalize(value));

const decodeSlice = (
  bytes: string,
  expectedRole: "ontology" | "language-profile",
  expectedLanguage: string | null,
): Readonly<{ artifact_sha256: string; semantic_sha256: string; content: JsonRecord }> => {
  let value: unknown;
  try {
    value = JSON.parse(bytes);
  } catch {
    return fail("ENUM_SEMANTIC_SLICE_JSON_INVALID");
  }
  if (!isRecord(value) || value.schema_version !== "MetaTypeSemanticSlice/v1" ||
      value.meta_type_id !== "DS-D1.3" ||
      value.architecture_type_id !== "architecture.EnumImplementation" ||
      value.source_role !== expectedRole || value.language !== expectedLanguage ||
      value.status !== "candidate" || value.authority_effect !== "none" ||
      !isRecord(value.semantic_content) || typeof value.semantic_sha256 !== "string" ||
      sha256(canonicalJson(value.semantic_content)) !== value.semantic_sha256) {
    return fail("ENUM_SEMANTIC_SLICE_INVALID");
  }
  return Object.freeze({
    artifact_sha256: sha256(bytes),
    semantic_sha256: value.semantic_sha256,
    content: value.semantic_content,
  });
};

export const buildShipmentPrioritySemanticSliceProof = async (
  input: ShipmentPrioritySemanticSliceInputs,
) => {
  const ontologySlice = decodeSlice(input.ontology_slice, "ontology", null);
  const profileSlice = decodeSlice(input.typescript_profile_slice, "language-profile", "typescript");
  const ontologyDocument = ontologySlice.content.ontology_document;
  const profileDocument = profileSlice.content.profile_document;
  const inheritedProfiles = profileSlice.content.inherited_profiles;
  if (!isRecord(ontologyDocument) || !isRecord(profileDocument) ||
      !Array.isArray(inheritedProfiles) || !isRecord(inheritedProfiles[0])) {
    return fail("ENUM_SEMANTIC_SLICE_CONTENT_INVALID");
  }
  const raw: ShipmentPriorityRawInputs = Object.freeze({
    case: input.case,
    expected: input.expected,
    ontology: JSON.stringify(ontologyDocument),
    base_profile: JSON.stringify(inheritedProfiles[0]),
    typescript_profile: JSON.stringify(profileDocument),
    provider: input.provider,
  });
  const proof = await buildShipmentPriorityProof(raw);
  return Object.freeze({
    ...proof,
    input_model: "MetaTypeSemanticSlice/v1" as const,
    semantic_slice_refs: Object.freeze({
      ontology: Object.freeze({
        artifact_sha256: ontologySlice.artifact_sha256,
        semantic_sha256: ontologySlice.semantic_sha256,
      }),
      typescript_profile: Object.freeze({
        artifact_sha256: profileSlice.artifact_sha256,
        semantic_sha256: profileSlice.semantic_sha256,
      }),
    }),
    claim_ceiling: "one candidate-local direct TypeScript Enum proof bound to concordant immutable Enum semantic slices",
  });
};
