import {readdir, readFile} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {rustPolicyV1Provider} from
  "../../../../factory/registry/providers/rust-policy-v1.js";
import {
  inspectRustPolicyClosedSubset,
  rustPolicyHostileSource,
} from "./closed-subset.js";
import {RUST_POLICY_RAW_PATHS} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
const rawInputs = async (): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(
    Object.entries(RUST_POLICY_RAW_PATHS).map(async ([role, path]) =>
      [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const),
  ));
const workspaces = async (): Promise<readonly string[]> => (await readdir(tmpdir()))
  .filter((name) => name.startsWith("domainspec-factory-rust-policy-"))
  .sort();

describe("Rust Policy direct provider", () => {
  it("proves owner cases in fresh processes without executing strategies", async () => {
    const before = await workspaces();
    const first = await rustPolicyV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    const second = await rustPolicyV1Provider.execute({
      raw_inputs: await rawInputs(),
      upstream: {},
    });
    expect(first).toEqual(second);
    expect(first).toMatchObject({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "rust-policy-v1",
      accounting: {
        positives_declared: 14,
        positives_passed: 14,
        mutants_declared: 16,
        mutants_killed: 16,
      },
      semantic_output: {
        workspace: {isolated: true, cleaned: true, symlinks: false},
        proof: {
          schema_version: "RustPolicyComposedProof/v1",
          result: "pass",
          native_mechanism: {
            runtime_proof: {
              cases_executed: 5,
              fresh_processes_executed: 10,
              distinct_pid_pairs: 5,
              strategy_execution_attempts: 0,
            },
            hostile_probes: {length: 12},
          },
          family_evaluation: {verdict: "pass"},
          accounting: {
            positives: {declared: 14, passed: 14},
            mutants: {declared: 16, killed: 16},
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
      "catalogue", "definition", "denominator", "mutations", "descriptor",
      "source", "observer", "proof_builder", "provider",
    ] as const) {
      const inputs = await rawInputs();
      inputs[role] = `${inputs[role]}\n`;
      await expect(rustPolicyV1Provider.execute({
        raw_inputs: inputs,
        upstream: {},
      })).rejects.toMatchObject({code: "FACTORY_RUST_POLICY_PROVIDER_FAILED"});
    }
  }, 30_000);

  it("executes all twelve static hostile probes through the closed subset", async () => {
    const source = (await rawInputs()).source;
    const channels = [
      "clock", "random", "environment", "filesystem", "network", "process",
      "global-cache", "delayed-lazy", "callback", "iterator-future",
      "finalizer-drop", "mutable-output",
    ] as const;
    expect(inspectRustPolicyClosedSubset(source).supported_effect_channels)
      .toEqual(channels);
    for (const channel of channels) {
      expect(() => inspectRustPolicyClosedSubset(
        rustPolicyHostileSource(source, channel),
      )).toThrowError("RUST_POLICY_CLOSED_SUBSET_SOURCE_MISMATCH");
    }
  });

  it("remains unregistered until RMT-POLICY-007", () => {
    expect(rustPolicyV1Provider.required_input_roles)
      .toEqual(Object.keys(RUST_POLICY_RAW_PATHS));
    expect(listFactoryNodeProvidersV1().some(({provider_id: providerId}) =>
      providerId === rustPolicyV1Provider.provider_id)).toBe(false);
  });
});
