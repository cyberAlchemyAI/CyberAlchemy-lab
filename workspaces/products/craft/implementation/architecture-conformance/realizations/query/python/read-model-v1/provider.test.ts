import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {getFactoryNodeProviderV1} from
  "../../../../factory/registry/factory-node-registry-v1.js";
import {pythonQueryV1Provider} from
  "../../../../factory/registry/providers/python-query-v1.js";
import {
  PYTHON_QUERY_RAW_PATHS,
  type PythonQueryRawInputs,
} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
let raw: PythonQueryRawInputs;

beforeAll(async () => {
  raw = Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(PYTHON_QUERY_RAW_PATHS).map(async ([role, path]) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ]),
  ))) as PythonQueryRawInputs;
});

describe("Python Query realization and registered provider", () => {
  it("runs the native target twice and composes the family proof", async () => {
    const result = await pythonQueryV1Provider.execute({
      raw_inputs: raw,
      upstream: Object.freeze({}),
    });
    expect(result).toMatchObject({
      result: "pass",
      provider_id: "python-query-v1",
      accounting: {
        positives_declared: 4,
        positives_passed: 4,
        mutants_declared: 8,
        mutants_killed: 8,
      },
      semantic_output: {
        workspace: {isolated: true, cleaned: true, symlinks: false},
        proof: {
          target: {
            language: "python",
            protocol_id: "python.bound-query/v1",
            output_concept_id: "settlement.CompleteSettlementView",
          },
          family_evaluation: {verdict: "pass"},
          native_process_evidence: {
            executions: 2,
            distinct_pids: 2,
            pids_redacted_from_semantic_proof: true,
            semantic_replay_equal: true,
            lifecycle_basis:
              "synchronous-return-plus-closed-plain-data-static-exclusion",
          },
          accounting: {
            positives: {declared: 4, passed: 4},
            source_hostiles: {declared: 8, killed: 8},
            predecessor_family_controls: {
              declared_classes: 7,
              killed_classes: 7,
            },
          },
        },
      },
    });
  });

  it("rejects stale target observer supervisor builder provider and binding", async () => {
    for (const role of [
      "source",
      "observer",
      "supervisor",
      "proof_builder",
      "provider",
    ] as const) {
      await expect(pythonQueryV1Provider.execute({
        raw_inputs: {...raw, [role]: `${raw[role]}\n`},
        upstream: Object.freeze({}),
      })).rejects.toThrow(`PY_QUERY_BINDING_INPUT_STALE:${role}`);
    }
    await expect(pythonQueryV1Provider.execute({
      raw_inputs: {
        ...raw,
        binding: raw.binding.replace(
          /"binding_sha256": "[a-f0-9]{64}"/u,
          `"binding_sha256": "${"0".repeat(64)}"`,
        ),
      },
      upstream: Object.freeze({}),
    })).rejects.toThrow("PY_QUERY_BINDING_POLICY_INVALID");
  });

  it("resolves the exact registered provider identity", () => {
    expect(getFactoryNodeProviderV1("python-query-v1"))
      .toBe(pythonQueryV1Provider);
  });
});
