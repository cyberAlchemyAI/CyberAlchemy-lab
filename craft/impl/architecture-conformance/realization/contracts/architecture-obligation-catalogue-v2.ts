import { createHash } from "node:crypto";

import type { EnumMemberExpectation } from "./architecture-obligation-catalogue.js";

type JsonObject = Record<string, unknown>;

export type ExactVersionedSourceRef = Readonly<{
  path: string;
  sha256: string;
}>;

export type ArchitectureObligationCatalogueV2 = Readonly<{
  schema_version: "ArchitectureObligationCatalogue/v2";
  catalogue_id: string;
  catalogue_version: "2";
  supersedes_ref: ExactVersionedSourceRef & Readonly<{
    catalogue_id: string;
    catalogue_version: "1";
  }>;
  definition_ref: ExactVersionedSourceRef & Readonly<{
    definition_id: string;
    definition_version: string;
    definition_sha256: string;
    authority_status: "candidate-fixture" | "owner-issued";
  }>;
  ontology_ref: ExactVersionedSourceRef & Readonly<{
    ontology_id: string;
    schema_version: string;
  }>;
  profile_ref: ExactVersionedSourceRef & Readonly<{
    profile_id: string;
    schema_version: string;
    extends: readonly (ExactVersionedSourceRef & Readonly<{
      profile_id: string;
      schema_version: string;
    }>)[];
  }>;
  obligations: readonly Readonly<{
    obligation_key: "enum.member-bijection@1";
    contract_version: "1";
    subject_ref: string;
    operator: "member-bijection";
    expected_payload: Readonly<{
      concept_id: string;
      composition_kind: "direct";
      order_semantics: "none";
      members: readonly EnumMemberExpectation[];
    }>;
    failure_codes: readonly string[];
  }>[];
  catalogue_sha256: string;
  owner_ref: "architecture-obligation-catalogue-owner";
  authority_effect: "none";
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const canonicalize = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalize)
  : value !== null && typeof value === "object"
    ? Object.fromEntries(Object.entries(value as JsonObject)
      .sort(([left], [right]) => compareUtf8(left, right))
      .map(([key, child]) => [key, canonicalize(child)]))
    : value;

export const computeArchitectureObligationCatalogueV2Sha256 = (
  catalogue: ArchitectureObligationCatalogueV2,
): string => {
  const { catalogue_sha256: _digest, ...payload } = catalogue;
  return createHash("sha256")
    .update(JSON.stringify(canonicalize(payload)), "utf8")
    .digest("hex");
};
