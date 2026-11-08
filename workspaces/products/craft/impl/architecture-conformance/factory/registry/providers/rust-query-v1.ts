import {mkdtemp, mkdir, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";

import {
  buildRustQueryProof,
  RUST_QUERY_RAW_PATHS,
  type RustQueryRawInputs,
} from "../../../realizations/query/rust/read-model-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {resolveFactoryExecutablePath} from "../../resolution/resolve-toolchain.js";
import {fail} from "../../shared/canonical.js";

export const rustQueryV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "rust-query-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(RUST_QUERY_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-query-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/rust/read-model-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/rust/read-model-v1/closed-subset.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/rust/read-model-v1/rust-binding.json",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/query_v1.rs",
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "rustc"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const roles = Object.keys(RUST_QUERY_RAW_PATHS) as readonly (
      keyof typeof RUST_QUERY_RAW_PATHS
    )[];
    const rawSnapshot = Object.freeze(Object.fromEntries(roles.map((role) => [
      role,
      rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role),
    ]))) as RustQueryRawInputs;
    const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-factory-rust-query-"));
    try {
      for (const role of roles) {
        const target = resolve(workspace, RUST_QUERY_RAW_PATHS[role]);
        await mkdir(dirname(target), {recursive: true});
        await writeFile(target, rawSnapshot[role], {
          encoding: "utf8",
          flag: "wx",
        });
      }
      const rustc = await resolveFactoryExecutablePath("rustc");
      const proof = await buildRustQueryProof({
        raw_inputs: rawSnapshot,
        workspace,
        rustc,
      });
      return Object.freeze({
        schema_version: "FactoryNodeSemanticResult/v1" as const,
        result: "pass" as const,
        provider_id: "rust-query-v1",
        semantic_output: Object.freeze({
          proof,
          workspace: Object.freeze({
            isolated: true,
            cleaned: true,
            symlinks: false,
          }),
        }),
        accounting: Object.freeze({
          positives_declared: proof.accounting.positives.declared,
          positives_passed: proof.accounting.positives.passed,
          mutants_declared: proof.accounting.source_hostiles.declared,
          mutants_killed: proof.accounting.source_hostiles.killed,
        }),
        claim_ceiling: proof.claim_ceiling,
        authority_effect: "none" as const,
      });
    } catch (error: unknown) {
      return fail(
        "FACTORY_RUST_QUERY_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      );
    } finally {
      await rm(workspace, {recursive: true, force: true});
    }
  },
});
