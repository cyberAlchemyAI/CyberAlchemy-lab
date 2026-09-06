import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {pythonPolicyV1Provider} from
  "../../../../factory/registry/providers/python-policy-v1.js";
import {PYTHON_POLICY_RAW_PATHS} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
let raw: Readonly<Record<string, string>>;

beforeAll(async () => {
  raw = Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(PYTHON_POLICY_RAW_PATHS).map(async ([role, path]) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ]),
  )));
});

describe("Python Policy provider", () => {
  it("runs an isolated native proof and composes the family contract", async () => {
    const result = await pythonPolicyV1Provider.execute({
      raw_inputs: raw,
      upstream: Object.freeze({}),
    });
    expect(result).toMatchObject({
      result: "pass",
      provider_id: "python-policy-v1",
      accounting: {
        positives_declared: 14,
        positives_passed: 14,
        mutants_declared: 16,
        mutants_killed: 16,
      },
      semantic_output: {
        workspace: {isolated: true, cleaned: true, symlinks: false},
        proof: {
          native_mechanism: {
            fresh_processes_executed: 10,
            distinct_processes: 10,
            strategy_execution_attempts: 0,
          },
          family_evaluation: {verdict: "pass"},
        },
      },
    });
  });

  it("rejects stale target and supervisor bytes", async () => {
    await expect(pythonPolicyV1Provider.execute({
      raw_inputs: {...raw, source: `${raw.source}\n`},
      upstream: Object.freeze({}),
    })).rejects.toThrow("PY_POLICY_BINDING_INPUT_STALE:source");
    await expect(pythonPolicyV1Provider.execute({
      raw_inputs: {...raw, supervisor: `${raw.supervisor}\n`},
      upstream: Object.freeze({}),
    })).rejects.toThrow("PY_POLICY_BINDING_INPUT_STALE:supervisor");
  });
});
