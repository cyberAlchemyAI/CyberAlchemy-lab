import {execFile} from "node:child_process";
import {
  lstat,
  mkdir,
  mkdtemp,
  readFile,
  rm,
  writeFile,
} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {promisify} from "node:util";

import {
  composePythonOperationProof,
  PYTHON_OPERATION_RAW_PATHS,
  type PythonOperationRawInputs,
  validatePythonOperationRawInputs,
} from "../../../realizations/operation/python/state-changing-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {resolveFactoryExecutablePath} from
  "../../resolution/resolve-toolchain.js";
import {fail} from "../../shared/canonical.js";

const executeFile = promisify(execFile);

export const operationPythonV1Provider:
FactoryNodeProviderV1 = Object.freeze({
  provider_id: "operation-python-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(
    Object.keys(PYTHON_OPERATION_RAW_PATHS),
  ),
  component_paths: Object.freeze([
    ...new Set(Object.values(PYTHON_OPERATION_RAW_PATHS)),
  ]),
  tool_ids: Object.freeze(["node", "tsx", "python"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const roles = Object.keys(PYTHON_OPERATION_RAW_PATHS) as readonly (
      keyof typeof PYTHON_OPERATION_RAW_PATHS
    )[];
    const actualRoles = Object.keys(rawInputs).sort();
    const expectedRoles = [...roles].sort();
    if (JSON.stringify(actualRoles) !== JSON.stringify(expectedRoles)) {
      return fail("PY_OP_PROVIDER_INPUT_ROLES_INVALID");
    }
    const snapshot = Object.freeze(Object.fromEntries(roles.map((role) => [
      role,
      `${rawInputs[role] ?? fail(
        "PY_OP_PROVIDER_INPUT_ROLES_INVALID",
        role,
      )}`,
    ]))) as PythonOperationRawInputs;
    validatePythonOperationRawInputs(snapshot);

    const workspace = await mkdtemp(resolve(
      tmpdir(),
      "domainspec-factory-python-operation-",
    ));
    let proof: ReturnType<typeof composePythonOperationProof> | undefined;
    let cleaned = false;
    try {
      for (const role of roles) {
        const target = resolve(
          workspace,
          PYTHON_OPERATION_RAW_PATHS[role],
        );
        await mkdir(dirname(target), {recursive: true});
        await writeFile(target, snapshot[role], {
          encoding: "utf8",
          flag: "wx",
        });
      }
      const output = resolve(workspace, "python-operation-proof.json");
      const python = await resolveFactoryExecutablePath("python");
      await executeFile(python, [
        "-I",
        "-B",
        resolve(workspace, PYTHON_OPERATION_RAW_PATHS.supervisor),
        "--repository-root",
        workspace,
        "--output",
        output,
      ], {
        env: {
          PATH: process.env.PATH ?? "",
          PYTHONDONTWRITEBYTECODE: "1",
          PYTHONHASHSEED: "0",
        },
        timeout: 60_000,
        maxBuffer: 1_048_576,
      }).catch((error: unknown) => fail(
        "FACTORY_PYTHON_OPERATION_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      ));
      proof = composePythonOperationProof({
        raw_inputs: snapshot,
        native_proof: JSON.parse(await readFile(output, "utf8")),
      });
    } finally {
      await rm(workspace, {recursive: true, force: true});
      try {
        await lstat(workspace);
      } catch (error) {
        if (error instanceof Error && "code" in error &&
            error.code === "ENOENT") {
          cleaned = true;
        } else {
          throw error;
        }
      }
      if (!cleaned) fail("FACTORY_PYTHON_OPERATION_WORKSPACE_RESIDUE");
    }
    if (!proof) return fail("FACTORY_PYTHON_OPERATION_PROVIDER_FAILED");
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "operation-python-v1",
      semantic_output: Object.freeze({
        proof,
        workspace: Object.freeze({
          isolated: true,
          cleaned,
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
