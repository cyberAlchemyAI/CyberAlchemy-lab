import {readdir, readFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {rustCalculationV1Provider} from
  "../../../../factory/registry/providers/rust-calculation-v1.js";
import {
  inspectRustCalculationClosedSubset,
  rustCalculationHostileSource,
} from "./closed-subset.js";
import {RUST_CALCULATION_RAW_PATHS} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
const rawInputs = async (): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(
    Object.entries(RUST_CALCULATION_RAW_PATHS).map(async ([role, path]) =>
      [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const),
  ));
const workspaces = async (): Promise<readonly string[]> => (await readdir(tmpdir()))
  .filter((name) => name.startsWith("domainspec-factory-rust-calc-"))
  .sort();

describe("Rust Calculation direct provider", () => {
  it("proves the exact source under overflow-checked compilation and redacts PIDs", async () => {
    const before = await workspaces();
    const first = await rustCalculationV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    const second = await rustCalculationV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    expect(first).toEqual(second);
    expect(first).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "rust-calculation-v1",
      accounting: {
        positives_declared: 11,
        positives_passed: 11,
        mutants_declared: 13,
        mutants_killed: 13,
      },
      semantic_output: {
        workspace: {isolated: true, cleaned: true, symlinks: false},
        proof: {
          schema_version: "RustCalculationComposedProof/v1",
          result: "pass",
          native_mechanism: {
            compiler: {edition: "2021", overflow_checks: "enabled"},
            runtime_proof: {
              cases_executed: 4,
              fresh_processes_executed: 8,
              distinct_pid_pairs: 4,
              result_kind: "primitive-i64",
              process_identity_evidence:
                "distinct-pairs-observed-redacted-from-semantic-output",
            },
          },
          family_evaluation: {verdict: "pass"},
          accounting: {
            positives: {declared: 11, passed: 11},
            mutants: {declared: 13, killed: 13},
            native_hostiles: {declared: 12, killed: 12},
          },
        },
      },
    });
    expect(JSON.stringify(first.semantic_output)).not.toContain('"pid"');
    expect(first.claim_ceiling).toContain("not arbitrary Rust");
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
      "proof_builder",
      "provider",
    ] as const) {
      const inputs = await rawInputs();
      inputs[role] = `${inputs[role]}\n`;
      await expect(rustCalculationV1Provider.execute({
        raw_inputs: inputs,
        upstream: {},
      })).rejects.toMatchObject({code: "FACTORY_RUST_CALC_PROVIDER_FAILED"});
    }
  }, 30_000);

  it("executes all twelve static hostile probes through the admission oracle", async () => {
    const source = (await rawInputs()).source;
    const channels = [
      "clock", "random", "environment", "filesystem", "network", "process",
      "global-cache", "delayed-lazy", "callback", "iterator-future",
      "finalizer-drop", "mutable-output",
    ] as const;
    expect(inspectRustCalculationClosedSubset(source).supported_effect_channels)
      .toEqual(channels);
    for (const channel of channels) {
      expect(() => inspectRustCalculationClosedSubset(
        rustCalculationHostileSource(source, channel),
      )).toThrowError("RUST_CALC_CLOSED_SUBSET_SOURCE_MISMATCH");
    }
  });

  it("remains unregistered until RMT-CALC-006", () => {
    expect(rustCalculationV1Provider.required_input_roles)
      .toEqual(Object.keys(RUST_CALCULATION_RAW_PATHS));
    expect(listFactoryNodeProvidersV1().some(({provider_id: providerId}) =>
      providerId === rustCalculationV1Provider.provider_id)).toBe(false);
  });
});
