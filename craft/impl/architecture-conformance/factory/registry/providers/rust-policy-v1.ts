import {mkdtemp, mkdir, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";

import {
  buildRustPolicyProof,
  RUST_POLICY_RAW_PATHS,
  type RustPolicyRawInputs,
} from "../../../realizations/policy/rust/strategy-selection-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {resolveFactoryExecutablePath} from "../../resolution/resolve-toolchain.js";
import {fail} from "../../shared/canonical.js";

export const rustPolicyV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "rust-policy-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(RUST_POLICY_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-policy-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/rust/strategy-selection-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/rust/strategy-selection-v1/closed-subset.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/rust/strategy-selection-v1/rust-binding.json",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/policy_v1.rs",
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "rustc"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-factory-rust-policy-"));
    try {
      for (const [role, path] of Object.entries(RUST_POLICY_RAW_PATHS)) {
        const bytes = rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role);
        const target = resolve(workspace, path);
        await mkdir(dirname(target), {recursive: true});
        await writeFile(target, bytes, {encoding: "utf8", flag: "wx"});
      }
      const rustc = await resolveFactoryExecutablePath("rustc");
      const proof = await buildRustPolicyProof({
        raw_inputs: rawInputs as RustPolicyRawInputs,
        workspace,
        rustc,
      });
      return Object.freeze({
        schema_version: "FactoryNodeSemanticResult/v1" as const,
        result: "pass" as const,
        provider_id: "rust-policy-v1",
        semantic_output: Object.freeze({
          proof,
          workspace: Object.freeze({isolated: true, cleaned: true, symlinks: false}),
        }),
        accounting: Object.freeze({
          positives_declared: proof.accounting.positives.declared,
          positives_passed: proof.accounting.positives.passed,
          mutants_declared: proof.accounting.mutants.declared,
          mutants_killed: proof.accounting.mutants.killed,
        }),
        claim_ceiling: proof.claim_ceiling,
        authority_effect: "none" as const,
      });
    } catch (error: unknown) {
      return fail(
        "FACTORY_RUST_POLICY_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      );
    } finally {
      await rm(workspace, {recursive: true, force: true});
    }
  },
});
