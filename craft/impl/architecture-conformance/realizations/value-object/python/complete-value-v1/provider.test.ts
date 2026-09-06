import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {beforeAll, describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/reference-node-providers.js";
import {pythonValueObjectV1Provider} from
  "../../../../factory/registry/providers/python-value-object-v1.js";
import {PYTHON_VALUE_OBJECT_RAW_PATHS,
  type PythonValueObjectRawInputs} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
let raw: PythonValueObjectRawInputs;

beforeAll(async () => {
  const entries = await Promise.all(Object.entries(
    PYTHON_VALUE_OBJECT_RAW_PATHS).map(async ([role, path]) => [role,
      await readFile(resolve(repositoryRoot, path), "utf8")] as const));
  raw = Object.freeze(Object.fromEntries(entries)) as PythonValueObjectRawInputs;
});

describe("Python Value Object realization and registered provider", () => {
  it("executes the exact target twice and composes the family proof", async () => {
    const result = await pythonValueObjectV1Provider.execute({raw_inputs: raw,
      upstream: Object.freeze({})});
    expect(result).toMatchObject({result: "pass",
      provider_id: "python-value-object-v1",
      accounting: {positives_declared: 7, positives_passed: 7,
        mutants_declared: 12, mutants_killed: 12},
      semantic_output: {workspace: {isolated: true, cleaned: true,
        symlinks: false}, proof: {family_evaluation: {verdict: "pass"},
        process_evidence: {executions: 2, distinct_pids: 2,
          semantic_replay_equal: true, pids_redacted_from_semantic_proof: true},
        accounting: {positives: {declared: 7, passed: 7},
          static_binding_controls: {declared: 8, rejected: 8},
          predecessor_family_controls: {declared: 12, killed: 12}}}}});
  });

  it("rejects stale proof-producing inputs and a stale binding digest", async () => {
    for (const role of ["source", "observer", "supervisor", "proof_builder",
      "provider"] as const) {
      await expect(pythonValueObjectV1Provider.execute({raw_inputs: {...raw,
        [role]: `${raw[role]}\n`}, upstream: Object.freeze({})}))
        .rejects.toThrow(`PY_VALUE_OBJECT_BINDING_INPUT_STALE:${role}`);
    }
    const binding = JSON.parse(raw.binding) as Record<string, unknown>;
    binding.binding_sha256 = "0".repeat(64);
    await expect(pythonValueObjectV1Provider.execute({raw_inputs: {...raw,
      binding: `${JSON.stringify(binding)}\n`}, upstream: Object.freeze({})}))
      .rejects.toThrow("PY_VALUE_OBJECT_BINDING_DIGEST_STALE");
  });

  it("snapshots caller-owned inputs and resolves its VO-006 registration", async () => {
    const mutable = {...raw};
    const pending = pythonValueObjectV1Provider.execute({raw_inputs: mutable,
      upstream: Object.freeze({})});
    mutable.source = `${mutable.source}\n`;
    await expect(pending).resolves.toMatchObject({result: "pass"});
    expect(listFactoryNodeProvidersV1().some(({provider_id: id}) =>
      id === "python-value-object-v1")).toBe(true);
  });
});
