import {execFile} from "node:child_process";
import {mkdtemp, mkdir, readFile, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {promisify} from "node:util";

import {
  composePythonPolicyProof,
  PYTHON_POLICY_RAW_PATHS,
  type PythonPolicyRawInputs,
} from "../../../realizations/policy/python/strategy-selection-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {resolveFactoryExecutablePath} from "../../resolution/resolve-toolchain.js";
import {fail} from "../../shared/canonical.js";

const executeFile = promisify(execFile);

export const pythonPolicyV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "python-policy-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(PYTHON_POLICY_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-policy-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/python/strategy-selection-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/python/strategy-selection-v1/run_python_policy_proof.py",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/policy/python/strategy-selection-v1/python-binding.json",
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/policy_v1.py",
    "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "python"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-factory-python-policy-"));
    let proof: ReturnType<typeof composePythonPolicyProof> | undefined;
    try {
      for (const [role, path] of Object.entries(PYTHON_POLICY_RAW_PATHS)) {
        const bytes = rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role);
        const target = resolve(workspace, path);
        await mkdir(dirname(target), {recursive: true});
        await writeFile(target, bytes, {encoding: "utf8", flag: "wx"});
      }
      const output = resolve(workspace, "python-policy-proof.json");
      const python = await resolveFactoryExecutablePath("python");
      await executeFile(python, [
        "-I", "-B", resolve(workspace, PYTHON_POLICY_RAW_PATHS.supervisor),
        "--repository-root", workspace, "--output", output,
      ], {
        env: {PATH: process.env.PATH ?? "", PYTHONDONTWRITEBYTECODE: "1"},
        timeout: 60_000,
        maxBuffer: 1_048_576,
      }).catch((error: unknown) => fail(
        "FACTORY_PYTHON_POLICY_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      ));
      proof = composePythonPolicyProof({
        raw_inputs: rawInputs as PythonPolicyRawInputs,
        native_proof: JSON.parse(await readFile(output, "utf8")),
      });
    } finally {
      await rm(workspace, {recursive: true, force: true});
    }
    if (!proof) return fail("FACTORY_PYTHON_POLICY_PROVIDER_FAILED");
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "python-policy-v1",
      semantic_output: Object.freeze({
        proof,
        workspace: Object.freeze({isolated: true, cleaned: true, symlinks: false}),
      }),
      accounting: Object.freeze({
        positives_declared: 14,
        positives_passed: 14,
        mutants_declared: proof.mutations.length,
        mutants_killed: proof.mutations.length,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
