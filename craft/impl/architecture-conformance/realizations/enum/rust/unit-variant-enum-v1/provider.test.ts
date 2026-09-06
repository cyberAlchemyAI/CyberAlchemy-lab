import { readdir, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { rustEnumV1Provider } from
  "../../../../factory/registry/providers/rust-enum-v1.js";

const repositoryRoot = process.cwd().endsWith("projects/domainspec-v2/impl")
  ? resolve(process.cwd(), "../../..")
  : process.cwd();
const rawPaths = Object.freeze({
  owner_catalogue:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/fixtures/shipment-priority/denominator.json",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/rust/unit-variant-enum-v1/rust-binding.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/enum_v1.rs",
});

const rawInputs = async (): Promise<Record<string, string>> => Object.fromEntries(
  await Promise.all(Object.entries(rawPaths).map(async ([role, path]) =>
    [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const)),
);

const enumWorkspaces = async (): Promise<readonly string[]> => (await readdir(tmpdir()))
  .filter((name) => name.startsWith("domainspec-factory-rust-enum-")
    || name.startsWith("domainspec-rust-enum-native-"))
  .sort();

const cwdMetadata = async (): Promise<readonly string[]> => (await readdir(process.cwd()))
  .filter((name) => name.endsWith(".rmeta"))
  .sort();

describe("Rust unit-variant Enum direct provider", () => {
  it("separates inspected/compiled/runtime properties from executed hostiles", async () => {
    const workspacesBefore = await enumWorkspaces();
    const metadataBefore = await cwdMetadata();
    const result = await rustEnumV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    expect(result).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "rust-enum-v1",
      accounting: {
        positives_declared: 14,
        positives_passed: 14,
        mutants_declared: 4,
        mutants_killed: 4,
      },
      authority_effect: "none",
    });
    expect(result.semantic_output).toMatchObject({
      proof: {
        schema_version: "RustEnumComposedProof/v1",
        result: "pass",
        family_evaluation: {
          verdict: "pass",
          portable_claim: "owner-bound-finite-member-wire-bijection",
          native_identity_diagnostic: {
            relation: "nominal",
            claim_scope: "native-diagnostic-only",
          },
        },
        native_proof: {
          native_properties: {
            exact_unit_variant_set: true,
            required_traits_satisfied: true,
            explicit_total_member_mappings: true,
            known_emit_parse_total: true,
          },
          native_property_evidence: {
            exact_unit_variant_set:
              "owner-derived-source-inspection-and-exhaustive-compile",
            required_traits_satisfied: "compile-bound-trait-assertion",
            explicit_total_member_mappings:
              "owner-derived-source-inspection-and-native-runtime",
            known_emit_parse_total: "native-runtime-observation",
          },
          hostile_probes: {
            non_exhaustive_match_rejected: true,
            payload_constructor_rejected: true,
            wrong_type_emit_rejected: true,
            unknown_wire_structured_failure: true,
          },
          compiler: {
            diagnostic_format: "rustc-json",
            probes: {
              non_exhaustive_match_rejected: {
                expected_code: "E0004",
                observed_codes: ["E0004"],
                rejected: true,
              },
              payload_constructor_rejected: {
                expected_code: "E0618",
                observed_codes: ["E0618"],
                rejected: true,
              },
              wrong_type_emit_rejected: {
                expected_code: "E0308",
                observed_codes: ["E0308"],
                rejected: true,
              },
            },
          },
        },
      },
      workspace: { isolated: true, cleaned: true, symlinks: false },
    });
    expect(await enumWorkspaces()).toEqual(workspacesBefore);
    expect(await cwdMetadata()).toEqual(metadataBefore);
  }, 60_000);

  it("rejects stale raw owner, denominator, binding, and source bytes", async () => {
    for (const role of [
      "owner_catalogue",
      "denominator",
      "binding",
      "source",
    ] as const) {
      const inputs = await rawInputs();
      inputs[role] = `${inputs[role]}\n`;
      await expect(rustEnumV1Provider.execute({ raw_inputs: inputs, upstream: {} }))
        .rejects.toMatchObject({ code: "FACTORY_RUST_ENUM_INPUT_STALE" });
    }
  }, 60_000);

  it("keeps proof expectations independent and the provider unregistered", async () => {
    const proofPaths = [
      "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-enum-v1.ts",
      "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/rust/unit-variant-enum-v1/index.ts",
      "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/rust/unit-variant-enum-v1/run_rust_enum_proof.ts",
    ];
    for (const path of proofPaths) {
      const source = await readFile(resolve(repositoryRoot, path), "utf8");
      expect(source).not.toContain("expected_finding_codes");
      expect(source).not.toContain("mutants.json");
      expect(source).not.toContain("positive-observation.json");
    }
    const registry = await readFile(resolve(
      repositoryRoot,
      "projects/domainspec-v2/impl/architecture-conformance/factory/registry/factory-node-registry-v1.ts",
    ), "utf8");
    expect(registry).not.toContain("rust-enum-v1");
    expect(registry).not.toContain("rustEnumV1Provider");
  });
});
