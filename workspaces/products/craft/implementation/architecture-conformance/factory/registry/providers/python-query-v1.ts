import {execFile} from "node:child_process";
import {mkdtemp, mkdir, readFile, rm, writeFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {promisify} from "node:util";

import {
  composePythonQueryProof,
  PYTHON_QUERY_RAW_PATHS,
  type PythonQueryRawInputs,
} from "../../../realizations/query/python/read-model-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {resolveFactoryExecutablePath} from "../../resolution/resolve-toolchain.js";
import {fail} from "../../shared/canonical.js";

const executeFile = promisify(execFile);

export const pythonQueryV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "python-query-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(PYTHON_QUERY_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-query-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/observe_python_query_case.py",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/run_python_query_proof.py",
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/python/read-model-v1/python-binding.json",
    "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/query_v1.py",
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "python"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const roles = Object.keys(PYTHON_QUERY_RAW_PATHS) as readonly (
      keyof typeof PYTHON_QUERY_RAW_PATHS
    )[];
    const rawSnapshot = Object.freeze(Object.fromEntries(
      roles.map((role) => [
        role,
        rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role),
      ]),
    )) as PythonQueryRawInputs;
    const workspace = await mkdtemp(resolve(tmpdir(),
      "domainspec-factory-python-query-"));
    let proof: ReturnType<typeof composePythonQueryProof> | undefined;
    try {
      for (const role of roles) {
        const bytes = rawSnapshot[role];
        const path = PYTHON_QUERY_RAW_PATHS[role];
        const target = resolve(workspace, path);
        await mkdir(dirname(target), {recursive: true});
        await writeFile(target, bytes, {encoding: "utf8", flag: "wx"});
      }
      const output = resolve(workspace, "python-query-proof.json");
      const python = await resolveFactoryExecutablePath("python");
      await executeFile(python, [
        "-I",
        "-B",
        resolve(workspace, PYTHON_QUERY_RAW_PATHS.supervisor),
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
        "FACTORY_PYTHON_QUERY_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      ));
      proof = composePythonQueryProof({
        raw_inputs: rawSnapshot,
        native_proof: JSON.parse(await readFile(output, "utf8")),
      });
    } finally {
      await rm(workspace, {recursive: true, force: true});
    }
    if (!proof) return fail("FACTORY_PYTHON_QUERY_PROVIDER_FAILED");
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "python-query-v1",
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
  },
});
