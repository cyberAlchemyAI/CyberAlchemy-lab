import { readdir, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { pythonEnumV1Provider } from
  "../../../../factory/registry/providers/python-enum-v1.js";

const repositoryRoot = process.cwd().endsWith("projects/domainspec-v2/impl")
  ? resolve(process.cwd(), "../../..")
  : process.cwd();
const rawPaths = Object.freeze({
  owner_catalogue:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/fixtures/shipment-priority/denominator.json",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/python/nominal-enum-v1/python-binding.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/enum_v1.py",
});

const rawInputs = async (): Promise<Record<string, string>> => Object.fromEntries(
  await Promise.all(Object.entries(rawPaths).map(async ([role, path]) =>
    [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const)),
);

const enumWorkspaces = async (): Promise<readonly string[]> => (await readdir(tmpdir()))
  .filter((name) => name.startsWith("domainspec-factory-python-enum-"))
  .sort();

describe("Python nominal Enum direct provider", () => {
  it("separates native properties from four executed hostile probes", async () => {
    const before = await enumWorkspaces();
    const result = await pythonEnumV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    expect(result).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "python-enum-v1",
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
        schema_version: "PythonEnumComposedProof/v1",
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
            str_mixin_absent: true,
            aliases_absent: true,
            raw_string_equality_false: true,
            known_emit_parse_total: true,
          },
          hostile_probes: {
            unknown_constructor_rejected: true,
            unknown_wire_structured_failure: true,
            extension_rejected: true,
            invalid_member_emit_rejected: true,
          },
        },
      },
      workspace: { isolated: true, cleaned: true, symlinks: false },
    });
    expect(await enumWorkspaces()).toEqual(before);
  }, 30_000);

  it("rejects stale raw owner, denominator, and source bytes", async () => {
    for (const role of ["owner_catalogue", "denominator", "source"] as const) {
      const inputs = await rawInputs();
      inputs[role] = `${inputs[role]}\n`;
      await expect(pythonEnumV1Provider.execute({ raw_inputs: inputs, upstream: {} }))
        .rejects.toMatchObject({ code: "FACTORY_PYTHON_ENUM_PROVIDER_FAILED" });
    }
  }, 30_000);

  it("does not read target expected findings or mutation catalogues", async () => {
    const paths = [
      "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-enum-v1.ts",
      "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/python/nominal-enum-v1/index.ts",
      "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/python/nominal-enum-v1/run_python_enum_proof.py",
    ];
    for (const path of paths) {
      const source = await readFile(resolve(repositoryRoot, path), "utf8");
      expect(source).not.toContain("expected_finding_codes");
      expect(source).not.toContain("mutants.json");
      expect(source).not.toContain("positive-observation.json");
    }
  });
});
