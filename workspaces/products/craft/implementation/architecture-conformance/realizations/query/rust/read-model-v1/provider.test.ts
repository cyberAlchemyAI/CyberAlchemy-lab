import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {getFactoryNodeProviderV1} from
  "../../../../factory/registry/factory-node-registry-v1.js";
import {rustQueryV1Provider} from
  "../../../../factory/registry/providers/rust-query-v1.js";
import {
  assertRustQueryReadKeys,
  RUST_QUERY_RAW_PATHS,
  type RustQueryRawInputs,
} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
let raw: RustQueryRawInputs;

beforeAll(async () => {
  raw = Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(RUST_QUERY_RAW_PATHS).map(async ([role, path]) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ]),
  ))) as RustQueryRawInputs;
});

describe("Rust Query realization and registered provider", () => {
  it("compiles and executes the target twice then composes the family proof", async () => {
    const result = await rustQueryV1Provider.execute({
      raw_inputs: raw,
      upstream: Object.freeze({}),
    });
    expect(result).toMatchObject({
      result: "pass",
      provider_id: "rust-query-v1",
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
            language: "rust",
            protocol_id: "rust.bound-query/v1",
            output_concept_id: "settlement.CompleteSettlementView",
          },
          family_evaluation: {verdict: "pass"},
          process_evidence: {
            executions: 2,
            distinct_pids: 2,
            pids_redacted_from_semantic_proof: true,
            semantic_replay_equal: true,
            read_keys_observed: 2,
            read_keys_matching_owner_input: 2,
            read_keys_validated: 2,
            lifecycle_basis:
              "synchronous-return-plus-owned-plain-data-static-exclusion",
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

  it("rejects a payout read made with a different owner key", () => {
    expect(() => assertRustQueryReadKeys([
      {settlement_id: "settlement-001"},
      {settlement_id: "settlement-002"},
    ], "settlement-001")).toThrow("RUST_QUERY_NATIVE_READ_KEY_INVALID");
  });

  it("rejects stale source observer builder provider and binding", async () => {
    for (const role of [
      "source",
      "observer",
      "proof_builder",
      "provider",
    ] as const) {
      await expect(rustQueryV1Provider.execute({
        raw_inputs: {...raw, [role]: `${raw[role]}\n`},
        upstream: Object.freeze({}),
      })).rejects.toThrow(new RegExp(`RUST_QUERY_BINDING_INPUT_STALE:${role}`, "u"));
    }
    await expect(rustQueryV1Provider.execute({
      raw_inputs: {
        ...raw,
        binding: raw.binding.replace(
          /"binding_sha256": "[a-f0-9]{64}"/u,
          `"binding_sha256": "${"0".repeat(64)}"`,
        ),
      },
      upstream: Object.freeze({}),
    })).rejects.toThrow("RUST_QUERY_BINDING_DIGEST_STALE");
  });

  it("resolves the exact registered provider identity", () => {
    expect(getFactoryNodeProviderV1("rust-query-v1"))
      .toBe(rustQueryV1Provider);
  });
});
