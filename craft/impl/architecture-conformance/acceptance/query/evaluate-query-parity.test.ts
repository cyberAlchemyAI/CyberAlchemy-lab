import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import type {FactoryUpstreamResultV1} from
  "../../factory/contracts/factory-node-provider-v1.js";
import {pythonQueryV1Provider} from
  "../../factory/registry/providers/python-query-v1.js";
import {rustQueryV1Provider} from
  "../../factory/registry/providers/rust-query-v1.js";
import {typeScriptQueryV1Provider} from
  "../../factory/registry/providers/typescript-query-v1.js";
import {canonicalJson, sha256} from "../../factory/shared/canonical.js";
import {PYTHON_QUERY_RAW_PATHS} from
  "../../realizations/query/python/read-model-v1/index.js";
import {RUST_QUERY_RAW_PATHS} from
  "../../realizations/query/rust/read-model-v1/index.js";
import {TYPESCRIPT_QUERY_RAW_PATHS} from
  "../../realizations/query/typescript/read-model-v1/index.js";
import {
  evaluateQueryParity,
  proveQueryParity,
  QUERY_DIRECT_HANDLES,
} from "./evaluate-query-parity.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../..");
const ownerPaths = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/query/cross-language-realization-descriptor.json",
});
const readPaths = async (
  paths: Readonly<Record<string, string>>,
): Promise<Record<string, string>> => Object.fromEntries(await Promise.all(
  Object.entries(paths).map(async ([role, path]) => [
    role,
    await readFile(resolve(repositoryRoot, path), "utf8"),
  ] as const),
));
const clone = <T>(value: T): T => structuredClone(value);

let upstream: Record<string, FactoryUpstreamResultV1>;
let rawInputs: Record<string, string>;

beforeAll(async () => {
  rawInputs = await readPaths(ownerPaths);
  const results = await Promise.all([
    typeScriptQueryV1Provider.execute({
      raw_inputs: await readPaths(TYPESCRIPT_QUERY_RAW_PATHS),
      upstream: {},
    }),
    pythonQueryV1Provider.execute({
      raw_inputs: await readPaths(PYTHON_QUERY_RAW_PATHS),
      upstream: {},
    }),
    rustQueryV1Provider.execute({
      raw_inputs: await readPaths(RUST_QUERY_RAW_PATHS),
      upstream: {},
    }),
  ]);
  upstream = Object.fromEntries(results.map((result, index) => {
    const handle = QUERY_DIRECT_HANDLES[index]!;
    return [handle.node_id, Object.freeze({
      node_id: handle.node_id,
      provider_id: result.provider_id,
      semantic_sha256: sha256(canonicalJson(result)),
      semantic_output: result.semantic_output,
    })];
  }));
}, 70_000);

describe("Query exact-target parity", () => {
  it("proves 16 obligations and kills 20 executed join hostiles", () => {
    const proof = proveQueryParity(upstream, rawInputs);
    expect(proof).toMatchObject({
      schema_version: "QueryParityProof/v1",
      result: "pass",
      authority_effect: "none",
    });
    expect(proof.composed_from.map(({language}) => language))
      .toEqual(["typescript", "python", "rust"]);
    expect(proof.obligations).toHaveLength(16);
    expect(proof.obligations.every(({status}) => status === "passed")).toBe(true);
    expect(proof.hostile_mutations).toHaveLength(20);
    expect(proof.hostile_mutations.every(({status}) => status === "killed"))
      .toBe(true);
    expect(proof.native_evidence_by_language).toHaveLength(3);
    expect(JSON.stringify(proof)).not.toContain('"pid"');
  });

  it("preserves the exact result read trace lifecycle and effect perimeter", () => {
    const proof = proveQueryParity(upstream, rawInputs);
    expect(proof.portable_projection).toMatchObject({
      case_id: "complete-settlement-recorded-payout",
      output_concept_id: "settlement.CompleteSettlementView",
      result: {
        settlement_id: "settlement-001",
        settlement_status: "complete",
        gross_amount_minor: 125000,
        payout_id: "payout-001",
        payout_status: "recorded",
      },
      result_consumption: {
        consumption: "complete",
        mutable_alias_observed: false,
      },
      quiescence: {observed: true, pending_count: 0},
    });
    expect(proof.portable_projection.read_attempts).toHaveLength(2);
    expect(proof.portable_projection.effect_channels).toHaveLength(12);
    expect(proof.portable_projection.lifecycle_paths).toHaveLength(7);
    expect(proof.claim_ceiling).toContain("native mechanisms");
  });

  it("rejects missing handles and forged lifecycle evidence", () => {
    const missing = clone(upstream);
    delete missing[QUERY_DIRECT_HANDLES[0].node_id];
    expect(() => evaluateQueryParity(missing, rawInputs))
      .toThrowError("QUERY_PARITY_HANDLE_SET_MISMATCH");
    const unsupported = clone(upstream) as any;
    unsupported[QUERY_DIRECT_HANDLES[0].node_id]
      .semantic_output.proof.observation.read_lifecycle_observation
      .lifecycle_paths[0].coverage = "unsupported";
    expect(() => evaluateQueryParity(unsupported, rawInputs))
      .toThrowError(/QUERY_PARITY_LIFECYCLE_INVALID/u);
  });

  it("rejects stale owner material before parity", () => {
    expect(() => proveQueryParity(upstream, {
      ...rawInputs,
      descriptor: `${rawInputs.descriptor}\n`,
    })).toThrowError(/QUERY_PARITY_RAW_INPUT_INVALID/u);
  });
});
