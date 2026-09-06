import {readFile, readdir} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {pythonCalculationV1Provider} from
  "../../../../factory/registry/providers/python-calculation-v1.js";
import {PYTHON_CALCULATION_RAW_PATHS} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");

const rawInputs = async (): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(
    Object.entries(PYTHON_CALCULATION_RAW_PATHS).map(async ([role, path]) =>
      [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const),
  ));
const workspaces = async (): Promise<readonly string[]> => (await readdir(tmpdir()))
  .filter((name) => name.startsWith("domainspec-factory-python-calc-"))
  .sort();

describe("Python Calculation direct provider", () => {
  it("proves native closure and portable family behavior without replay-unstable PIDs", async () => {
    const before = await workspaces();
    const first = await pythonCalculationV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    const second = await pythonCalculationV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    expect(first).toEqual(second);
    expect(first).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "python-calculation-v1",
      accounting: {
        positives_declared: 11,
        positives_passed: 11,
        mutants_declared: 13,
        mutants_killed: 13,
      },
      semantic_output: {
        workspace: {isolated: true, cleaned: true, symlinks: false},
        proof: {
          schema_version: "PythonCalculationComposedProof/v1",
          result: "pass",
          native_mechanism: {
            runtime_proof: {
              cases_executed: 4,
              fresh_processes_executed: 8,
              distinct_pid_pairs: 4,
              result_kind: "primitive-number",
            },
            process_identity_evidence:
              "distinct-pairs-observed-redacted-from-semantic-output",
          },
          family_evaluation: {
            verdict: "pass",
            portable_claim:
              "owner-bound-deterministic-zero-effect-value-under-declared-perimeter",
          },
          accounting: {
            positives: {declared: 11, passed: 11},
            mutants: {declared: 13, killed: 13},
            native_hostiles: {declared: 12, killed: 12},
          },
        },
      },
      authority_effect: "none",
    });
    expect(JSON.stringify(first.semantic_output)).not.toContain('"pid"');
    expect(first.claim_ceiling).toContain("not arbitrary Python");
    expect(await workspaces()).toEqual(before);
  }, 30_000);

  it("rejects stale bytes for every proof-producing raw role", async () => {
    for (const role of [
      "definition",
      "denominator",
      "mutations",
      "descriptor",
      "source",
      "observer",
      "supervisor",
      "proof_builder",
      "provider",
    ] as const) {
      const inputs = await rawInputs();
      inputs[role] = `${inputs[role]}\n`;
      await expect(pythonCalculationV1Provider.execute({
        raw_inputs: inputs,
        upstream: {},
      })).rejects.toMatchObject({code: "FACTORY_PYTHON_CALC_PROVIDER_FAILED"});
    }
  }, 30_000);

  it("keeps owner expected values and portable mutations outside the target observer", async () => {
    for (const role of ["source", "observer"] as const) {
      const source = await readFile(
        resolve(repositoryRoot, PYTHON_CALCULATION_RAW_PATHS[role]),
        "utf8",
      );
      expect(source).not.toContain("expected_value");
      expect(source).not.toContain("expected_finding_codes");
      expect(source).not.toContain("mutants.json");
    }
  });

  it("remains explicitly unregistered until RMT-CALC-006", () => {
    expect(pythonCalculationV1Provider.required_input_roles)
      .toEqual(Object.keys(PYTHON_CALCULATION_RAW_PATHS));
    expect(listFactoryNodeProvidersV1().some(({provider_id: providerId}) =>
      providerId === pythonCalculationV1Provider.provider_id)).toBe(false);
  });
});
