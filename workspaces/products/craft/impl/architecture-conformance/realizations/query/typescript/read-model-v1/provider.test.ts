import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {
  canonicalReadModelQueryJson,
  mintReadModelQueryObservationV1,
  type ReadModelQueryObservationV1,
} from "../../../../families/read-model/index.js";
import {mintDeclaredReadLifecycleObservationV1} from
  "../../../../kernel/evidence/effect-observation/index.js";
import {getFactoryNodeProviderV1} from
  "../../../../factory/registry/factory-node-registry-v1.js";
import {typeScriptQueryV1Provider} from
  "../../../../factory/registry/providers/typescript-query-v1.js";
import {
  assertTypeScriptQueryAdapterBoundary,
  buildTypeScriptQueryProof,
  TYPESCRIPT_QUERY_RAW_PATHS,
  type TypeScriptQueryRawInputs,
} from "./index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../../..");
const digest = (character: string): string => character.repeat(64).slice(0, 64);
const withoutObservationDigest = (
  value: ReadModelQueryObservationV1,
): Omit<ReadModelQueryObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};

let raw: TypeScriptQueryRawInputs;
let proof: Awaited<ReturnType<typeof buildTypeScriptQueryProof>>;

beforeAll(async () => {
  raw = Object.freeze(Object.fromEntries(await Promise.all(
    Object.entries(TYPESCRIPT_QUERY_RAW_PATHS).map(async ([role, path]) => [
      role,
      await readFile(resolve(repositoryRoot, path), "utf8"),
    ]),
  ))) as TypeScriptQueryRawInputs;
  proof = await buildTypeScriptQueryProof(raw);
});

describe("TypeScript Query realization and registered provider", () => {
  it("executes the exact target twice and passes the family denominator", () => {
    expect(proof.family_evaluation.verdict).toBe("pass");
    expect(proof.family_evaluation.positive_decision_accounting)
      .toEqual({declared: 4, passed: 4, failed: 0, unaccounted: 0});
    expect(proof.process_evidence.executions).toBe(2);
    expect(proof.process_evidence.distinct_pids).toBe(2);
    expect(proof.observation.read_lifecycle_observation
      .declared_read_attempts.map(({target_id: targetId}) => targetId))
      .toEqual([
        "settlement.read.settlement-by-id",
        "settlement.read.payout-by-settlement",
      ]);
    expect(proof.accounting.source_hostiles).toEqual({declared: 8, killed: 8});
    expect(proof.accounting.predecessor_family_controls)
      .toEqual({declared_classes: 7, killed_classes: 7});
  });

  it("direct-calls the provider and resolves the exact registered identity", async () => {
    const result = await typeScriptQueryV1Provider.execute({
      raw_inputs: raw,
      upstream: {},
    });
    expect(result.accounting).toMatchObject({
      positives_declared: 4,
      positives_passed: 4,
      mutants_declared: 8,
      mutants_killed: 8,
    });
    expect(getFactoryNodeProviderV1("typescript-query-v1"))
      .toBe(typeScriptQueryV1Provider);
  });

  it("rejects stale source, observer, proof-builder, provider, and binding semantics", async () => {
    for (const role of [
      "source", "observer", "proof_builder", "provider",
    ] as const) {
      await expect(buildTypeScriptQueryProof({
        ...raw,
        [role]: `${raw[role]}\n`,
      })).rejects.toThrow(/TS_QUERY_BINDING_(INPUT_STALE|DIGEST_STALE)/u);
    }
    await expect(buildTypeScriptQueryProof({
      ...raw,
      binding: raw.binding.replace(
        /"binding_sha256": "[a-f0-9]{64}"/u,
        `"binding_sha256": "${digest("0")}"`,
      ),
    })).rejects.toThrow("TS_QUERY_BINDING_DIGEST_STALE");
  });

  it("enforces adapter language protocol output lifecycle outcome and digest", () => {
    const base = withoutObservationDigest(proof.observation);
    const assertObservation = (
      observation: ReadModelQueryObservationV1,
      overrides: Partial<Parameters<
        typeof assertTypeScriptQueryAdapterBoundary
      >[0]> = {},
    ) => assertTypeScriptQueryAdapterBoundary({
      observation_json: canonicalReadModelQueryJson(observation),
      expected_target_id: proof.target.target_id,
      expected_source_sha256: proof.target.target_sha256,
      expected_protocol_id: "typescript.bound-query/v1",
      expected_output_concept_id: "settlement.CompleteSettlementView",
      observed_output_concept_id: "settlement.CompleteSettlementView",
      lifecycle_basis: proof.closed_subset.lifecycle_basis,
      ...overrides,
    });
    const wrongLanguage = mintReadModelQueryObservationV1({
      ...base,
      target: {...base.target, language: "python"},
    });
    expect(() => assertObservation(wrongLanguage))
      .toThrow("TS_QUERY_ADAPTER_PREFLIGHT_FAILED");
    const wrongProtocol = mintReadModelQueryObservationV1({
      ...base,
      target: {...base.target, protocol_id: "typescript.wrong-query/v1"},
    });
    expect(() => assertObservation(wrongProtocol))
      .toThrow("TS_QUERY_ADAPTER_PREFLIGHT_FAILED");
    expect(() => assertObservation(proof.observation, {
      observed_output_concept_id: "settlement.WrongView",
    })).toThrow("TS_QUERY_ADAPTER_PREFLIGHT_FAILED");
    expect(() => assertObservation(proof.observation, {
      lifecycle_basis: "declared-without-evidence",
    })).toThrow("TS_QUERY_ADAPTER_PREFLIGHT_FAILED");
    const lifecycle = proof.observation.read_lifecycle_observation;
    const {observation_sha256: _lifecycleDigest, ...lifecycleBody} = lifecycle;
    const wrongOutcome = mintReadModelQueryObservationV1({
      ...base,
      read_lifecycle_observation: mintDeclaredReadLifecycleObservationV1({
        ...lifecycleBody,
        declared_read_attempts: lifecycleBody.declared_read_attempts.map(
          (attempt, index) => index === 0
            ? {...attempt, outcome: "declared-failure" as const}
            : attempt,
        ),
      }),
    });
    expect(() => assertObservation(wrongOutcome))
      .toThrow("TS_QUERY_ADAPTER_PREFLIGHT_FAILED");
    expect(() => assertTypeScriptQueryAdapterBoundary({
      observation_json: canonicalReadModelQueryJson({
        ...proof.observation,
        observation_sha256: digest("0"),
      }),
      expected_target_id: proof.target.target_id,
      expected_source_sha256: proof.target.target_sha256,
      expected_protocol_id: "typescript.bound-query/v1",
      expected_output_concept_id: "settlement.CompleteSettlementView",
      observed_output_concept_id: "settlement.CompleteSettlementView",
      lifecycle_basis: proof.closed_subset.lifecycle_basis,
    })).toThrow("FAMILY_QUERY_OBSERVATION_DIGEST_STALE");
  });
});
