import { createHash } from "node:crypto";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";

import {
  composeRustEnumFamilyProof,
  type RustEnumComposedProofV1,
} from "../../../realizations/enum/rust/unit-variant-enum-v1/index.js";
import { runRustEnumNativeProof } from
  "../../../realizations/enum/rust/unit-variant-enum-v1/run_rust_enum_proof.js";
import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";
import { resolveFactoryExecutablePath } from "../../resolution/resolve-toolchain.js";
import { fail } from "../../shared/canonical.js";

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

const rawDigests = Object.freeze({
  owner_catalogue: "f0c8d1003e046b420d6aa0875caadea16ca7420c97c6932d53b81820c1ec8fd3",
  denominator: "9987888406c32c1a4aa77c6d4fabe86ff80693d20245501557d69dc70844ac7a",
  binding: "d4ec900b8b08a1f548ddb4a07b5e0d7d4c7903de61562aa6181d46a43f8d56d3",
  source: "e1e3bce9d4cf3249b66a80125bb50dc9c085d60b1a5bf70d222c0aff48922897",
});

const sha256 = (bytes: string): string =>
  createHash("sha256").update(bytes, "utf8").digest("hex");

export const rustEnumV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "rust-enum-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(rawPaths)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-enum-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/rust/unit-variant-enum-v1/run_rust_enum_proof.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/rust/unit-variant-enum-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/enum/rust/unit-variant-enum-v1/rust-binding.json",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/enum_v1.rs",
    "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "rustc"]),
  execute: async ({ raw_inputs: rawInputs }) => {
    for (const [role, digest] of Object.entries(rawDigests)) {
      const bytes = rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role);
      if (sha256(bytes) !== digest) return fail("FACTORY_RUST_ENUM_INPUT_STALE", role);
    }
    const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-factory-rust-enum-"));
    let proof: RustEnumComposedProofV1 | undefined;
    try {
      for (const [role, path] of Object.entries(rawPaths)) {
        const bytes = rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role);
        const target = resolve(workspace, path);
        await mkdir(dirname(target), { recursive: true });
        await writeFile(target, bytes, { encoding: "utf8", flag: "wx" });
      }
      const output = resolve(workspace, "rust-enum-proof.json");
      const rustc = await resolveFactoryExecutablePath("rustc");
      const nativeProof = runRustEnumNativeProof({
        repositoryRoot: workspace,
        output,
        rustc,
      });
      const materializedProof = JSON.parse(await readFile(output, "utf8")) as unknown;
      if (JSON.stringify(nativeProof) !== JSON.stringify(materializedProof)) {
        return fail("FACTORY_RUST_ENUM_NATIVE_PROOF_MATERIALIZATION_MISMATCH");
      }
      proof = composeRustEnumFamilyProof({
        owner_catalogue_bytes: rawInputs.owner_catalogue
          ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", "owner_catalogue"),
        denominator_bytes: rawInputs.denominator
          ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", "denominator"),
        native_proof: materializedProof,
      });
    } catch (error: unknown) {
      return fail(
        "FACTORY_RUST_ENUM_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      );
    } finally {
      await rm(workspace, { recursive: true, force: true });
    }
    if (proof === undefined) return fail("FACTORY_RUST_ENUM_PROVIDER_FAILED");
    const positives = proof.accounting.portable_decisions.declared
      + proof.accounting.native_properties.declared;
    const passed = proof.accounting.portable_decisions.passed
      + proof.accounting.native_properties.passed;
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "rust-enum-v1",
      semantic_output: Object.freeze({
        proof,
        workspace: Object.freeze({ isolated: true, cleaned: true, symlinks: false }),
      }),
      accounting: Object.freeze({
        positives_declared: positives,
        positives_passed: passed,
        mutants_declared: proof.accounting.hostile_probes.declared,
        mutants_killed: proof.accounting.hostile_probes.killed,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
