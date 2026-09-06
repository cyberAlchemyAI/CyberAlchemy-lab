import {
  access, lstat, mkdir, mkdtemp, rm, writeFile,
} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";

import {
  buildRustOperationProof,
  RUST_OPERATION_RAW_PATHS,
  type RustOperationRawInputs,
} from "../../../realizations/operation/rust/state-changing-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {resolveFactoryExecutablePath} from "../../resolution/resolve-toolchain.js";
import {fail} from "../../shared/canonical.js";

export const operationRustV1Provider:
FactoryNodeProviderV1 = Object.freeze({
  provider_id: "operation-rust-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(
    Object.keys(RUST_OPERATION_RAW_PATHS),
  ),
  component_paths: Object.freeze([
    ...new Set(Object.values(RUST_OPERATION_RAW_PATHS)),
  ]),
  tool_ids: Object.freeze(["node", "tsx", "rustc"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const roles = Object.keys(RUST_OPERATION_RAW_PATHS) as readonly (
      keyof typeof RUST_OPERATION_RAW_PATHS
    )[];
    const actualRoles = Object.keys(rawInputs).sort();
    const expectedRoles = [...roles].sort();
    if (JSON.stringify(actualRoles) !== JSON.stringify(expectedRoles)) {
      return fail("RUST_OP_PROVIDER_INPUT_ROLES_INVALID");
    }
    const snapshot = Object.freeze(Object.fromEntries(
      roles.map((role) => [
        role,
        `${rawInputs[role] ?? fail(
          "RUST_OP_PROVIDER_INPUT_ROLES_INVALID",
          role,
        )}`,
      ]),
    )) as RustOperationRawInputs;
    const workspace = await mkdtemp(resolve(
      tmpdir(),
      "domainspec-factory-rust-operation-",
    ));
    let proof: Awaited<ReturnType<typeof buildRustOperationProof>>;
    try {
      const workspaceStat = await lstat(workspace);
      if (!workspaceStat.isDirectory() || workspaceStat.isSymbolicLink()) {
        return fail("RUST_OP_WORKSPACE_INVALID");
      }
      for (const role of roles) {
        const target = resolve(workspace, RUST_OPERATION_RAW_PATHS[role]);
        await mkdir(dirname(target), {recursive: true});
        await writeFile(target, snapshot[role], {
          encoding: "utf8",
          flag: "wx",
        });
      }
      const rustc = await resolveFactoryExecutablePath("rustc");
      proof = await buildRustOperationProof(snapshot, workspace, rustc);
    } catch (error: unknown) {
      if (error !== null && typeof error === "object" &&
          "code" in error &&
          error.code === "RMT_OP_S1_RESIDUE_INCOHERENT") {
        throw error;
      }
      return fail(
        "FACTORY_RUST_OPERATION_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      );
    } finally {
      await rm(workspace, {recursive: true, force: true});
    }
    try {
      await access(workspace);
      return fail("RUST_OP_WORKSPACE_CLEANUP_FAILED");
    } catch (error: unknown) {
      if (!(error instanceof Error) ||
          !("code" in error) || error.code !== "ENOENT") {
        return fail("RUST_OP_WORKSPACE_CLEANUP_UNVERIFIED");
      }
    }
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "operation-rust-v1",
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
        mutants_declared: proof.accounting.mutants.declared,
        mutants_killed: proof.accounting.mutants.killed,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
