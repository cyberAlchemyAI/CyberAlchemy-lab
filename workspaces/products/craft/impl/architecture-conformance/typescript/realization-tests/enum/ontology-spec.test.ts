import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  deriveEnumArchitectureRealizationSpec,
  renderArchitectureRealizationSpec,
} from "../../../realization/spec/derive-enum-realization-spec.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(
  process.env.DOMAINSPEC_REPOSITORY_ROOT ?? resolve(here, "../../../../../../.."),
);
const paths = {
  ontology: resolve(
    repositoryRoot,
    "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/ontology.json",
  ),
  baseProfile: resolve(
    repositoryRoot,
    "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/base-domain.profile.json",
  ),
  typescriptProfile: resolve(
    repositoryRoot,
    "projects/domainspec-v2/development/implementation-conformance/ontology-experiment/semantic-slices/legacy-whole-file-snapshots/enum-v1/typescript-strict.profile.json",
  ),
  expected: resolve(
    repositoryRoot,
    "projects/domainspec-v2/development/architecture-realization-compiler/fixtures/order-status/realization-spec.expected.json",
  ),
} as const;

const loadInputs = async () => {
  const [ontology_json, base_profile_json, typescript_profile_json, expected] = await Promise.all([
    readFile(paths.ontology, "utf8"),
    readFile(paths.baseProfile, "utf8"),
    readFile(paths.typescriptProfile, "utf8"),
    readFile(paths.expected, "utf8"),
  ]);
  const expectedSpec = JSON.parse(expected) as {
    spec_id: string;
    ontology_ref: { sha256: string };
    profile_ref: { sha256: string; extends: [{ sha256: string }] };
  };
  return {
    input: {
      spec_id: expectedSpec.spec_id,
      ontology_json,
      base_profile_json,
      typescript_profile_json,
      expected_source_digests: {
        ontology_sha256: expectedSpec.ontology_ref.sha256,
        base_profile_sha256: expectedSpec.profile_ref.extends[0].sha256,
        typescript_profile_sha256: expectedSpec.profile_ref.sha256,
      },
    },
    expected,
  } as const;
};

describe("Enum architecture realization projector", () => {
  it("derives the frozen ArchitectureRealizationSpec byte-for-byte", async () => {
    const { input, expected } = await loadInputs();
    const first = renderArchitectureRealizationSpec(deriveEnumArchitectureRealizationSpec(input));
    const second = renderArchitectureRealizationSpec(deriveEnumArchitectureRealizationSpec(input));
    expect(first).toBe(expected);
    expect(second).toBe(first);
    expect(JSON.parse(first)).toMatchObject({
      realization_type: "architecture.EnumImplementation",
      definition_type_ref: "DS-D1.3",
      authority_effect: "none",
    });
  });

  it("rejects one removed required property with one exact diagnostic", async () => {
    const { input } = await loadInputs();
    const ontology = JSON.parse(input.ontology_json) as {
      property_definitions: { property_id: string }[];
    };
    ontology.property_definitions = ontology.property_definitions.filter(
      ({ property_id }) => property_id !== "runtime.provider_sha256",
    );
    const ontology_json = `${JSON.stringify(ontology, null, 2)}\n`;
    const crypto = await import("node:crypto");
    expect(() => deriveEnumArchitectureRealizationSpec({
      ...input,
      ontology_json,
      expected_source_digests: {
        ...input.expected_source_digests,
        ontology_sha256: crypto.createHash("sha256").update(ontology_json).digest("hex"),
      },
    })).toThrowError(expect.objectContaining({
      code: "ARCH_REALIZATION_PROPERTY_MISSING",
      detail: { property_id: "runtime.provider_sha256" },
    }));
  });

  it("blocks stale profile bytes before deriving any property", async () => {
    const { input } = await loadInputs();
    expect(() => deriveEnumArchitectureRealizationSpec({
      ...input,
      typescript_profile_json: `${input.typescript_profile_json}\n`,
    })).toThrowError(expect.objectContaining({ code: "ARCH_REALIZATION_SOURCE_DIGEST_STALE" }));
  });
});
