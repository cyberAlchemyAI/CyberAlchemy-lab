import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {beforeAll, describe, expect, it} from "vitest";

import {rustEntityV1Provider} from
  "../../../../factory/registry/providers/rust-entity-v1.js";
import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {RUST_ENTITY_RAW_PATHS, type RustEntityRawInputs} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
let raw: RustEntityRawInputs;

beforeAll(async () => {
  const entries = await Promise.all(Object.entries(RUST_ENTITY_RAW_PATHS)
    .map(async ([role, path]) => [role,
      await readFile(resolve(repositoryRoot, path), "utf8")] as const));
  raw = Object.freeze(Object.fromEntries(entries)) as RustEntityRawInputs;
});

describe("Rust Entity exact realization and unregistered direct provider", () => {
  it("executes exact native bytes twice and separates source from family controls",
    async () => {
      const result = await rustEntityV1Provider.execute({raw_inputs: raw,
        upstream: Object.freeze({})});
      expect(result).toMatchObject({result: "pass", provider_id: "rust-entity-v1",
        accounting: {positives_declared: 5, positives_passed: 5,
          mutants_declared: 12, mutants_killed: 12},
        semantic_output: {workspace: {isolated: true, cleaned: true,
          symlinks: false}, proof: {native_runtime: {compiled: true,
          executed: true, process_count: 2, distinct_processes: true,
          pid_and_workspace_redacted_from_semantic_digest: true,
          direct_constructor_inaccessible: true},
          evaluation: {verdict: "pass",
            positive_obligation_accounting: {declared: 5, passed: 5},
            construction_route_accounting: {declared: 4, conforming: 4}},
          accounting: {source_hostiles: {declared: 12, killed: 12,
            mechanism: "static-exact-source-rejection"},
            predecessor_family_controls: {declared: 7, killed: 7,
              mechanism: "portable-observation-evaluation"}}}}});
    });

  it("rejects stale proof components and stale binding digest", async () => {
    for (const role of ["source", "observer", "proof_builder", "provider",
      "family_api", "family_evaluator", "kernel_api", "kernel_evaluator"] as const) {
      await expect(rustEntityV1Provider.execute({raw_inputs: {...raw,
        [role]: `${raw[role]}\n`}, upstream: Object.freeze({})}))
        .rejects.toThrow(`RUST_ENTITY_BINDING_INPUT_STALE:${role}`);
    }
    const binding = JSON.parse(raw.binding) as Record<string, unknown>;
    binding.binding_sha256 = "0".repeat(64);
    await expect(rustEntityV1Provider.execute({raw_inputs: {...raw,
      binding: `${JSON.stringify(binding)}\n`}, upstream: Object.freeze({})}))
      .rejects.toThrow("RUST_ENTITY_BINDING_DIGEST_STALE");
  });

  it("snapshots caller inputs and stays unregistered before Entity-006", async () => {
    const mutable = {...raw};
    const pending = rustEntityV1Provider.execute({raw_inputs: mutable,
      upstream: Object.freeze({})});
    mutable.source = `${mutable.source}\n`;
    await expect(pending).resolves.toMatchObject({result: "pass"});
    expect(listFactoryNodeProvidersV1().some(({provider_id: id}) =>
      id === "rust-entity-v1")).toBe(false);
  });
});
