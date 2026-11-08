import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {beforeAll, describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {pythonEntityV1Provider} from
  "../../../../factory/registry/providers/python-entity-v1.js";
import {PYTHON_ENTITY_RAW_PATHS, type PythonEntityRawInputs} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
let raw: PythonEntityRawInputs;

beforeAll(async () => {
  const entries = await Promise.all(Object.entries(PYTHON_ENTITY_RAW_PATHS)
    .map(async ([role, path]) => [role,
      await readFile(resolve(repositoryRoot, path), "utf8")] as const));
  raw = Object.freeze(Object.fromEntries(entries)) as PythonEntityRawInputs;
});

describe("Python Entity realization and direct unregistered provider", () => {
  it("executes the exact target twice with separate target and family controls", async () => {
    const result = await pythonEntityV1Provider.execute({raw_inputs: raw,
      upstream: Object.freeze({})});
    expect(result).toMatchObject({result: "pass", provider_id: "python-entity-v1",
      accounting: {positives_declared: 5, positives_passed: 5,
        mutants_declared: 18, mutants_killed: 18},
      semantic_output: {workspace: {isolated: true, cleaned: true,
        symlinks: false}, proof: {family_evaluation: {verdict: "pass"},
        process_evidence: {executions: 2, distinct_pids: 2,
          semantic_replay_equal: true, pids_redacted_from_semantic_proof: true},
        accounting: {positives: {declared: 5, passed: 5},
          construction_routes: {declared: 4, passed: 4},
          target_source_controls: {declared: 11, rejected: 11},
          predecessor_family_controls: {declared: 7, killed: 7}}}}});
  });

  it("rejects every stale proof input and a stale binding digest", async () => {
    for (const role of Object.keys(PYTHON_ENTITY_RAW_PATHS).filter(
      (role) => role !== "binding") as readonly (
        keyof typeof PYTHON_ENTITY_RAW_PATHS
      )[]) {
      await expect(pythonEntityV1Provider.execute({raw_inputs: {...raw,
        [role]: `${raw[role]}\n`}, upstream: Object.freeze({})}))
        .rejects.toThrow(`PY_ENTITY_BINDING_INPUT_STALE:${role}`);
    }
    const binding = JSON.parse(raw.binding) as Record<string, unknown>;
    binding.binding_sha256 = "0".repeat(64);
    await expect(pythonEntityV1Provider.execute({raw_inputs: {...raw,
      binding: `${JSON.stringify(binding)}\n`}, upstream: Object.freeze({})}))
      .rejects.toThrow("PY_ENTITY_BINDING_DIGEST_STALE");
  });

  it("snapshots caller inputs and remains unavailable through the registry", async () => {
    const mutable = {...raw};
    const pending = pythonEntityV1Provider.execute({raw_inputs: mutable,
      upstream: Object.freeze({})});
    mutable.source = `${mutable.source}\n`;
    await expect(pending).resolves.toMatchObject({result: "pass"});
    expect(listFactoryNodeProvidersV1().some(({provider_id: id}) =>
      id === "python-entity-v1")).toBe(false);
  });
});
