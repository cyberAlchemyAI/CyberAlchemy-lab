import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import type {LockedConstructionObserverRefV1} from
  "../../../kernel/evidence/construction-observation/index.js";
import {evaluateIdentityLifecycle} from "./evaluate-identity-lifecycle.js";
import {applyIdentityLifecycleMutant} from
  "../mutations/apply-identity-lifecycle-mutant.js";
import {
  computeIdentityLifecycleCatalogueSha256,
  decodeIdentityLifecycleDefinitionV1,
  decodeIdentityLifecycleDenominatorV1,
  decodeIdentityLifecycleMutationCatalogueV1,
  decodeIdentityLifecycleObservationV1,
} from "../providers/decode-identity-lifecycle.js";
import type {IdentityLifecycleMutationCatalogueV1} from
  "../contracts/identity-lifecycle-contracts.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtureRoot = resolve(here, "../fixtures/settlement-entity");
const repositoryRoot = resolve(here, "../../../../../../..");
const descriptorPath =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/entity/"
  + "cross-language-realization-descriptor.json";
const definitionPath =
  "projects/domainspec-v2/impl/architecture-conformance/families/"
  + "identity-lifecycle/fixtures/settlement-entity/definition.json";
const load = (path: string): Promise<string> => readFile(path, "utf8");

const [descriptorBytes, definitionBytes, denominatorBytes, observationBytes,
  mutationBytes, expectedRedBytes] = await Promise.all([
  load(resolve(repositoryRoot, descriptorPath)),
  load(resolve(fixtureRoot, "definition.json")),
  load(resolve(fixtureRoot, "denominator.json")),
  load(resolve(fixtureRoot, "positive-observation.json")),
  load(resolve(fixtureRoot, "mutants.json")),
  load(resolve(fixtureRoot, "expected-red.json")),
]);
const definition = decodeIdentityLifecycleDefinitionV1(
  definitionBytes,
  descriptorPath,
  descriptorBytes,
);
const denominator = decodeIdentityLifecycleDenominatorV1(
  denominatorBytes,
  definitionBytes,
  definition,
  definitionPath,
);
const positive = decodeIdentityLifecycleObservationV1(observationBytes);
const catalogue = decodeIdentityLifecycleMutationCatalogueV1(
  mutationBytes,
  denominator,
);
const lockedObserver: LockedConstructionObserverRefV1 = positive.observer_ref;
const remintCatalogueBytes = (mutations: readonly unknown[]): string => {
  const parsed = JSON.parse(mutationBytes) as IdentityLifecycleMutationCatalogueV1;
  const {catalogue_sha256: _digest, ...body} = parsed;
  const currentBody = {...body, mutations} as unknown as
    Omit<IdentityLifecycleMutationCatalogueV1, "catalogue_sha256">;
  return JSON.stringify({...currentBody,
    catalogue_sha256: computeIdentityLifecycleCatalogueSha256(currentBody)});
};

describe("identity-lifecycle family", () => {
  it("passes the exact 5 obligations and all 4 policy-specific routes", () => {
    const result = evaluateIdentityLifecycle({definition, denominator,
      observation: positive, locked_observer_ref: lockedObserver});
    expect(result.verdict).toBe("pass");
    expect(result.findings).toEqual([]);
    expect(result.positive_obligation_accounting).toEqual({
      declared: 5, passed: 5, failed: 0, unaccounted: 0,
    });
    expect(result.hostile_class_accounting).toEqual({
      declared: 7, represented: 7, unrepresented: 0,
    });
    expect(result.construction_route_accounting).toEqual({
      declared: 4, observed: 4, conforming: 4, unaccounted: 0,
    });
    const direct = positive.route_traces.find(({route_id}) =>
      route_id === "language-visible-direct-constructor");
    expect(direct).toMatchObject({
      direct_constructor_policy: "private-inaccessible",
      result: {status: "constructor-inaccessible", snapshot_created: false,
        snapshot_id: null},
    });
    const factorySnapshot = positive.snapshots.find(({snapshot_id}) =>
      snapshot_id === "snapshot.settlement-a.created");
    const reconstructedSnapshot = positive.snapshots.find(({snapshot_id}) =>
      snapshot_id === "snapshot.settlement-a.reconstructed");
    expect(reconstructedSnapshot?.identity).toEqual(factorySnapshot?.identity);
    expect(result.native_runtime_claim).toBe(false);
  });

  it("keeps the unimplemented target expected-red observation absent", () => {
    const expectedRed = JSON.parse(expectedRedBytes) as {
      observation: null;
      expected_verdict: "fail";
      expected_finding_codes: readonly string[];
    };
    expect(expectedRed.observation).toBeNull();
    const result = evaluateIdentityLifecycle({definition, denominator,
      observation: expectedRed.observation, locked_observer_ref: lockedObserver});
    expect(result.verdict).toBe(expectedRed.expected_verdict);
    expect(result.findings.map(({code}) => code))
      .toEqual(expectedRed.expected_finding_codes);
    expect(result.positive_obligation_accounting).toEqual({
      declared: 5, passed: 0, failed: 5, unaccounted: 0,
    });
  });

  it("kills exactly all 7 admitted semantic hostile classes", () => {
    expect(catalogue.mutations).toHaveLength(7);
    expect(new Set(catalogue.mutations.map(({hostile_class}) => hostile_class)).size)
      .toBe(7);
    for (const mutation of catalogue.mutations) {
      const observed = applyIdentityLifecycleMutant(positive, mutation);
      const result = evaluateIdentityLifecycle({definition, denominator,
        observation: observed, locked_observer_ref: lockedObserver});
      expect(result.verdict, mutation.mutation_id).toBe("fail");
      expect(result.findings.map(({code}) => code), mutation.mutation_id)
        .toEqual(mutation.expected_finding_codes);
      expect(result.positive_obligation_accounting.unaccounted,
        mutation.mutation_id).toBe(0);
    }
  });

  it("keeps structural integrity controls outside the 7 semantic classes", () => {
    const forged = {...positive, observation_sha256: "0".repeat(64)};
    const result = evaluateIdentityLifecycle({definition, denominator,
      observation: forged, locked_observer_ref: lockedObserver});
    expect(result.verdict).toBe("fail");
    expect(result.findings.map(({code}) => code))
      .toEqual(["FAMILY_ENTITY_OBSERVATION_INTEGRITY_MISMATCH"]);
    expect(result.hostile_class_accounting).toEqual({
      declared: 7, represented: 7, unrepresented: 0,
    });
  });

  it("fails closed on stale definition, denominator, catalogue, and observation", () => {
    expect(() => decodeIdentityLifecycleDefinitionV1(
      definitionBytes,
      descriptorPath,
      `${descriptorBytes}\n`,
    )).toThrow("FAMILY_ENTITY_DEFINITION_DESCRIPTOR_STALE");
    expect(() => decodeIdentityLifecycleDenominatorV1(
      denominatorBytes.replace(denominator.denominator_sha256, "0".repeat(64)),
      definitionBytes,
      definition,
      definitionPath,
    )).toThrow("FAMILY_ENTITY_DENOMINATOR_DIGEST_STALE");
    expect(() => decodeIdentityLifecycleMutationCatalogueV1(
      mutationBytes.replace(catalogue.catalogue_sha256, "0".repeat(64)),
      denominator,
    )).toThrow("FAMILY_ENTITY_MUTATIONS_DIGEST_STALE");
    expect(() => decodeIdentityLifecycleObservationV1(observationBytes.replace(
      positive.observation_sha256,
      "0".repeat(64),
    ))).toThrow("ENTITY_OBSERVATION_DIGEST_STALE");
  });

  it("rejects digest-current overcomplete and remapped hostile catalogues", () => {
    const overcomplete = [...catalogue.mutations, {
      ...catalogue.mutations[0]!,
      mutation_id: "validators/extra-always-true",
    }];
    expect(() => decodeIdentityLifecycleMutationCatalogueV1(
      remintCatalogueBytes(overcomplete),
      denominator,
    )).toThrow("FAMILY_ENTITY_MUTATION_BLUEPRINT_INVALID");

    const remapped = catalogue.mutations.map((mutation) => {
      if (mutation.mutation_id === "validators/per-call-always-true") {
        return {...mutation,
          hostile_class: "remove-base-validator" as const,
          mutation_kind: "remove-base-validator" as const,
          expected_finding_codes: ["FAMILY_ENTITY_BASE_VALIDATOR_REMOVED"] as const};
      }
      if (mutation.mutation_id === "extension/remove-base-validator") {
        return {...mutation,
          hostile_class: "per-call-always-true-validator-bypass" as const,
          mutation_kind: "per-call-validator-bypass" as const,
          expected_finding_codes: ["FAMILY_ENTITY_VALIDATOR_BYPASS"] as const};
      }
      return mutation;
    });
    expect(() => decodeIdentityLifecycleMutationCatalogueV1(
      remintCatalogueBytes(remapped),
      denominator,
    )).toThrow("FAMILY_ENTITY_MUTATION_BLUEPRINT_INVALID");
  });

  it("keeps fixtures and target implementations outside evaluator/mutator logic",
    async () => {
      const [evaluatorSource, mutationSource] = await Promise.all([
        load(resolve(here, "evaluate-identity-lifecycle.ts")),
        load(resolve(here, "../mutations/apply-identity-lifecycle-mutant.ts")),
      ]);
      for (const source of [evaluatorSource, mutationSource]) {
        expect(source).not.toContain("fixtures/");
        expect(source).not.toContain("mutants.json");
        expect(source).not.toContain("expected_finding_codes");
        expect(source).not.toContain("targets/typescript");
        expect(source).not.toContain("targets/python");
        expect(source).not.toContain("targets/rust");
      }
    });
});
