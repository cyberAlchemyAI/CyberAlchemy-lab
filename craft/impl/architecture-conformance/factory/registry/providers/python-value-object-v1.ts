import {execFile} from "node:child_process";
import {mkdtemp, mkdir, readFile, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {promisify} from "node:util";

import {
  composePythonValueObjectProof,
  PYTHON_VALUE_OBJECT_RAW_PATHS,
  type PythonValueObjectRawInputs,
} from "../../../realizations/value-object/python/complete-value-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {resolveFactoryExecutablePath} from "../../resolution/resolve-toolchain.js";
import {fail} from "../../shared/canonical.js";

const executeFile = promisify(execFile);

export const pythonValueObjectV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "python-value-object-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(PYTHON_VALUE_OBJECT_RAW_PATHS)),
  component_paths: Object.freeze(Object.values(PYTHON_VALUE_OBJECT_RAW_PATHS)),
  tool_ids: Object.freeze(["node", "tsx", "python"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const roles = Object.keys(PYTHON_VALUE_OBJECT_RAW_PATHS) as readonly (
      keyof typeof PYTHON_VALUE_OBJECT_RAW_PATHS
    )[];
    const snapshot = Object.freeze(Object.fromEntries(roles.map((role) => {
      const value = rawInputs[role];
      return [role, typeof value === "string"
        ? `${value}` : fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role)];
    }))) as PythonValueObjectRawInputs;
    const workspace = await mkdtemp(resolve(tmpdir(),
      "domainspec-factory-python-value-object-"));
    let proof: ReturnType<typeof composePythonValueObjectProof> | undefined;
    try {
      for (const role of roles) {
        const target = resolve(workspace, PYTHON_VALUE_OBJECT_RAW_PATHS[role]);
        await mkdir(dirname(target), {recursive: true});
        await writeFile(target, snapshot[role], {encoding: "utf8", flag: "wx"});
      }
      const output = resolve(workspace, "python-value-object-proof.json");
      const python = await resolveFactoryExecutablePath("python");
      await executeFile(python, [
        "-I", "-B", resolve(workspace, PYTHON_VALUE_OBJECT_RAW_PATHS.supervisor),
        "--repository-root", workspace, "--output", output,
      ], {env: {PATH: process.env.PATH ?? "", PYTHONDONTWRITEBYTECODE: "1",
        PYTHONHASHSEED: "0"}, timeout: 60_000, maxBuffer: 2_097_152})
        .catch((error: unknown) => fail("FACTORY_PYTHON_VALUE_OBJECT_FAILED",
          error instanceof Error ? error.message : String(error)));
      proof = composePythonValueObjectProof({raw_inputs: snapshot,
        native_proof: JSON.parse(await readFile(output, "utf8"))});
    } finally {
      await rm(workspace, {recursive: true, force: true});
    }
    if (!proof) return fail("FACTORY_PYTHON_VALUE_OBJECT_FAILED");
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "python-value-object-v1",
      semantic_output: Object.freeze({proof, workspace: Object.freeze({
        isolated: true, cleaned: true, symlinks: false,
      })}),
      accounting: Object.freeze({
        positives_declared: proof.accounting.positives.declared,
        positives_passed: proof.accounting.positives.passed,
        mutants_declared: proof.accounting.predecessor_family_controls.declared,
        mutants_killed: proof.accounting.predecessor_family_controls.killed,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
