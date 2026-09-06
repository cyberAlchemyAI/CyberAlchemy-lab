import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {pythonCalculationV1Provider} from
  "../../factory/registry/providers/python-calculation-v1.js";
import {rustCalculationV1Provider} from
  "../../factory/registry/providers/rust-calculation-v1.js";
import {typeScriptCalculationV1Provider} from
  "../../factory/registry/providers/typescript-calculation-v1.js";
import {canonicalJson, sha256} from "../../factory/shared/canonical.js";
import {PYTHON_CALCULATION_RAW_PATHS} from
  "../../realizations/calculation/python/value-computation-v1/index.js";
import {RUST_CALCULATION_RAW_PATHS} from
  "../../realizations/calculation/rust/value-computation-v1/index.js";
import {TYPESCRIPT_CALCULATION_RAW_PATHS} from
  "../../realizations/calculation/typescript/value-computation-v1/index.js";
import {
  CALCULATION_DIRECT_HANDLES,
  evaluateCalculationParity,
  proveCalculationParity,
} from "./evaluate-calculation-parity.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../..");
const ownerPaths = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/calculation/cross-language-realization-descriptor.json",
});
const readPaths = async (paths: Readonly<Record<string, string>>): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(Object.entries(paths).map(async ([role, path]) =>
    [role, await readFile(resolve(repositoryRoot, path), "utf8")] as const)));
const clone = <T>(value: T): T => structuredClone(value);

let upstream: Record<string, FactoryUpstreamResultV1>;
let rawInputs: Record<string, string>;

beforeAll(async () => {
  rawInputs = await readPaths(ownerPaths);
  const results = await Promise.all([
    typeScriptCalculationV1Provider.execute({
      raw_inputs: await readPaths(TYPESCRIPT_CALCULATION_RAW_PATHS),
      upstream: {},
    }),
    pythonCalculationV1Provider.execute({
      raw_inputs: await readPaths(PYTHON_CALCULATION_RAW_PATHS),
      upstream: {},
    }),
    rustCalculationV1Provider.execute({
      raw_inputs: await readPaths(RUST_CALCULATION_RAW_PATHS),
      upstream: {},
    }),
  ]);
  upstream = Object.fromEntries(results.map((result, index) => {
    const handle = CALCULATION_DIRECT_HANDLES[index]!;
    return [handle.node_id, Object.freeze({
      node_id: handle.node_id,
      provider_id: result.provider_id,
      semantic_sha256: sha256(canonicalJson(result)),
      semantic_output: result.semantic_output,
    })];
  }));
}, 60_000);

describe("Calculation exact-target parity", () => {
  it("proves 13 obligations and kills 13 executed join mutations", () => {
    const proof = proveCalculationParity(upstream, rawInputs);
    expect(proof).toMatchObject({
      schema_version: "CalculationParityProof/v1",
      result: "pass",
      authority_effect: "none",
    });
    expect(proof.composed_from.map(({language}) => language))
      .toEqual(["typescript", "python", "rust"]);
    expect(proof.obligations).toHaveLength(13);
    expect(proof.obligations.every(({status}) => status === "passed")).toBe(true);
    expect(proof.hostile_mutations).toHaveLength(13);
    expect(proof.hostile_mutations.every(({status}) => status === "killed")).toBe(true);
    expect(proof.native_evidence_by_language).toHaveLength(3);
    expect(JSON.stringify(proof)).not.toContain('"pid"');
  });

  it("preserves exact owner cases and excludes target-native keys from portable equality", () => {
    const proof = proveCalculationParity(upstream, rawInputs);
    expect((proof.portable_projection.cases as unknown[])).toHaveLength(4);
    expect(proof.native_evidence_by_language.map(({language}) => language))
      .toEqual(["typescript", "python", "rust"]);
    expect(proof.claim_ceiling).toContain("native mechanism evidence is retained");
    expect(proof.claim_ceiling).toContain("not full-domain equivalence");
  });

  it("rejects handle drift and unsafe portable values", () => {
    const missing = clone(upstream);
    delete missing[CALCULATION_DIRECT_HANDLES[0].node_id];
    expect(() => evaluateCalculationParity(missing, rawInputs))
      .toThrowError("CALC_PARITY_HANDLE_SET_MISMATCH");
    const unsafe = clone(upstream) as any;
    unsafe[CALCULATION_DIRECT_HANDLES[0].node_id]
      .semantic_output.proof.observation.cases[0].result_value = true;
    expect(() => evaluateCalculationParity(unsafe, rawInputs))
      .toThrowError(/CALC_PARITY_VALUE_INVALID/u);
  });

  it("rejects stale owner material before parity", () => {
    expect(() => proveCalculationParity(upstream, {
      ...rawInputs,
      descriptor: `${rawInputs.descriptor}\n`,
    })).toThrowError(/CALC_PARITY_(?:RAW_INPUT_INVALID|DESCRIPTOR_MISMATCH)/u);
  });
});
