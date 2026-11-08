import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {
  DECLARED_READ_LIFECYCLE_PATHS,
  EFFECT_CHANNELS,
  mintDeclaredReadLifecycleObservationV1,
  mintEffectObservationV1,
  type LockedEffectObserverRefV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import type {
  ReadModelQueryDefinitionV1,
  ReadModelQueryDenominatorV1,
  ReadModelQueryMutationCatalogueV1,
  ReadModelQueryObservationV1,
} from "../contracts/read-model-contracts.js";
import {applyReadModelQueryMutant} from
  "../mutations/apply-read-model-query-mutant.js";
import {
  decodeReadModelQueryDefinitionV1,
  decodeReadModelQueryDenominatorV1,
  decodeReadModelQueryMutationCatalogueV1,
  decodeReadModelQueryObservationV1,
  mintReadModelQueryObservationV1,
  sha256ReadModelQueryValue,
} from "../providers/decode-read-model.js";
import {evaluateReadModelQuery} from "./evaluate-read-model-query.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtureRoot = resolve(here, "../fixtures/complete-settlement");
const repositoryRoot = resolve(here, "../../../../../../..");
const descriptorPath = "projects/domainspec-v2/development/remaining-meta-types/admissions/query/cross-language-realization-descriptor.json";
const definitionPath = "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/definition.json";
const digest = (character: string): string => character.repeat(64).slice(0, 64);
const observer: LockedEffectObserverRefV1 = Object.freeze({
  role: "independent-effect-observer",
  observer_id: "observer.query-family-harness/v1",
  observer_sha256: digest("a"),
  owner_ref: "query-family-proof-owner",
  provider_id: "family-fixture.query-complete-settlement/v1",
  provider_sha256: digest("b"),
});
const target = Object.freeze({
  target_id: "query.fixture.complete-settlement/v1",
  target_sha256: digest("c"),
});

let definition: ReadModelQueryDefinitionV1;
let denominator: ReadModelQueryDenominatorV1;
let mutations: ReadModelQueryMutationCatalogueV1;
let positive: ReadModelQueryObservationV1;
let definitionBytes: string;
let denominatorBytes: string;
let mutationBytes: string;
let descriptorBytes: string;

beforeAll(async () => {
  [definitionBytes, denominatorBytes, mutationBytes, descriptorBytes] =
    await Promise.all([
      readFile(resolve(fixtureRoot, "definition.json"), "utf8"),
      readFile(resolve(fixtureRoot, "denominator.json"), "utf8"),
      readFile(resolve(fixtureRoot, "mutants.json"), "utf8"),
      readFile(resolve(repositoryRoot, descriptorPath), "utf8"),
    ]);
  definition = decodeReadModelQueryDefinitionV1(
    definitionBytes, descriptorPath, descriptorBytes,
  );
  denominator = decodeReadModelQueryDenominatorV1(
    denominatorBytes, definitionBytes, definition, definitionPath,
  );
  mutations = decodeReadModelQueryMutationCatalogueV1(mutationBytes, denominator);
  const ownerCase = definition.cases[0]!;
  const readsByChannel = new Map<string, number>();
  for (const {channel} of definition.read_targets) {
    readsByChannel.set(channel, (readsByChannel.get(channel) ?? 0) + 1);
  }
  const effect = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.query.fixture.complete-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: target,
    observer_ref: observer,
    channels: EFFECT_CHANNELS.map((channel) => ({
      channel,
      coverage: "supported" as const,
      read_count: readsByChannel.get(channel) ?? 0,
      write_count: 0,
      escape_count: 0,
      deferred_count: 0,
    })),
    result: {consumption: "complete", mutable_alias_observed: false},
    quiescence: {observed: true, pending_count: 0},
    authority_effect: "none",
  });
  positive = mintReadModelQueryObservationV1({
    schema_version: "ReadModelQueryObservation/v1",
    observation_id: "observation.query.fixture.complete-settlement/v1",
    source_kind: "independent-family-fixture",
    target: {...target, language: "family-fixture",
      protocol_id: "family.read-model-query-observation/v1"},
    definition_ref: denominator.owner_definition_ref,
    binding: {
      descriptor_id: definition.descriptor_ref.descriptor_id,
      descriptor_sha256: definition.descriptor_ref.sha256,
      provider_id: observer.provider_id,
      provider_sha256: observer.provider_sha256,
    },
    observed_result: {
      case_id: ownerCase.case_id,
      input_sha256: sha256ReadModelQueryValue(ownerCase.inputs),
      result: ownerCase.expected_result,
      result_sha256: sha256ReadModelQueryValue(ownerCase.expected_result),
      declared_failure: null,
    },
    read_lifecycle_observation: mintDeclaredReadLifecycleObservationV1({
      schema_version: "DeclaredReadLifecycleObservation/v1",
      observation_id: "observation.declared-read.query.complete-settlement/v1",
      source_kind: "independent-owner-observation",
      target_ref: target,
      observer_ref: observer,
      declared_read_attempts: definition.read_targets.map((readTarget, ordinal) => ({
        ordinal,
        target_id: readTarget.target_id,
        channel: readTarget.channel,
        lifecycle_path: ordinal === 0 ? "return" : "iterate-or-await",
        outcome: "success",
      })),
      lifecycle_paths: DECLARED_READ_LIFECYCLE_PATHS.map((lifecycle_path) => ({
        lifecycle_path, coverage: "supported" as const,
      })),
      effect_observation: effect,
      source_support: "supported-static",
      write_then_restore_observed: false,
      authority_effect: "none",
    }),
    authority_effect: "none",
  });
});

describe("independent complete-settlement read-model Query denominator", () => {
  it("keeps the target lane expected-red until the later provider SWUs", async () => {
    const expectedRed = JSON.parse(await readFile(
      resolve(fixtureRoot, "expected-red.json"), "utf8",
    )) as {observation: null; expected_verdict: "fail";
      expected_finding_codes: string[]};
    const result = evaluateReadModelQuery({definition, denominator,
      observation: expectedRed.observation, locked_observer_ref: observer,
      locked_target_ref: target});
    expect(result.verdict).toBe(expectedRed.expected_verdict);
    expect(result.findings.map(({code}) => code))
      .toEqual(expectedRed.expected_finding_codes);
    expect(result.positive_decision_accounting)
      .toEqual({declared: 4, passed: 0, failed: 4, unaccounted: 0});
  });

  it("accepts an independently constructed family observation", () => {
    const result = evaluateReadModelQuery({definition, denominator,
      observation: positive, locked_observer_ref: observer,
      locked_target_ref: target});
    expect(result.verdict).toBe("pass");
    expect(result.findings).toEqual([]);
    expect(result.positive_decision_accounting)
      .toEqual({declared: 4, passed: 4, failed: 0, unaccounted: 0});
  });

  it("kills exactly seven hostile classes including lifecycle variants", () => {
    expect(mutations.mutations).toHaveLength(7);
    for (const mutation of mutations.mutations) {
      for (const variant of mutation.variants) {
        const mutated = applyReadModelQueryMutant(positive, mutation, variant);
        const result = evaluateReadModelQuery({definition, denominator,
          observation: mutated, locked_observer_ref: observer,
          locked_target_ref: target});
        expect(result.verdict, `${mutation.mutation_id}:${variant}`).toBe("fail");
        const codes = [...new Set(result.findings.map(({code}) => code))];
        for (const expected of mutation.expected_finding_codes) {
          expect(codes, `${mutation.mutation_id}:${variant}`).toContain(expected);
        }
      }
    }
  });

  it("fails closed on stale definition, denominator, observation, and catalogue bytes", () => {
    expect(() => decodeReadModelQueryDefinitionV1(
      definitionBytes, descriptorPath, `${descriptorBytes}\n`,
    )).toThrow("FAMILY_QUERY_DEFINITION_DESCRIPTOR_STALE");
    expect(() => decodeReadModelQueryDenominatorV1(
      denominatorBytes.replace(denominator.denominator_sha256, digest("0")),
      definitionBytes, definition, definitionPath,
    )).toThrow("FAMILY_QUERY_DENOMINATOR_DIGEST_STALE");
    expect(() => decodeReadModelQueryObservationV1(JSON.stringify({
      ...positive, observation_sha256: digest("0"),
    }))).toThrow("FAMILY_QUERY_OBSERVATION_DIGEST_STALE");
    expect(() => decodeReadModelQueryMutationCatalogueV1(
      mutationBytes.replace(mutations.catalogue_sha256, digest("0")), denominator,
    )).toThrow("FAMILY_QUERY_MUTATION_CATALOGUE_DIGEST_STALE");
  });

  it("keeps owner expectations outside evaluator and mutation execution", async () => {
    const [evaluator, mutator] = await Promise.all([
      readFile(resolve(here, "evaluate-read-model-query.ts"), "utf8"),
      readFile(resolve(here, "../mutations/apply-read-model-query-mutant.ts"),
        "utf8"),
    ]);
    for (const source of [evaluator, mutator]) {
      expect(source).not.toContain("fixtures/");
      expect(source).not.toContain("expected_finding_codes");
      expect(source).not.toContain("targets/typescript");
      expect(source).not.toContain("targets/python");
      expect(source).not.toContain("targets/rust");
    }
  });
});
