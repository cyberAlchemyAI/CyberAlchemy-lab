import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { beforeAll, describe, expect, it } from "vitest";

import type {
  FiniteVocabularyDenominatorV1,
  FiniteVocabularyMutationCatalogueV1,
  FiniteVocabularyObservationV1,
  OwnerEnumCatalogueV1,
} from "../contracts/finite-vocabulary-contracts.js";
import { applyFiniteVocabularyMutant } from
  "../mutations/apply-finite-vocabulary-mutant.js";
import {
  decodeFiniteVocabularyDenominatorV1,
  decodeFiniteVocabularyMutationCatalogueV1,
  decodeFiniteVocabularyObservationV1,
  mintFiniteVocabularyObservationV1,
} from "../providers/decode-finite-vocabulary.js";
import { evaluateFiniteVocabulary } from "./evaluate-finite-vocabulary.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtureRoot = resolve(here, "../fixtures/shipment-priority");
const implRoot = process.cwd().endsWith("projects/domainspec-v2/impl")
  ? process.cwd()
  : resolve(here, "../../../../../..");
const repositoryRoot = resolve(implRoot, "../../..");
const ownerPath = "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json";

let denominator: FiniteVocabularyDenominatorV1;
let ownerCatalogue: OwnerEnumCatalogueV1;
let positive: FiniteVocabularyObservationV1;
let mutations: FiniteVocabularyMutationCatalogueV1;
let denominatorBytes: string;
let ownerBytes: string;

beforeAll(async () => {
  [denominatorBytes, ownerBytes] = await Promise.all([
    readFile(resolve(fixtureRoot, "denominator.json"), "utf8"),
    readFile(resolve(repositoryRoot, ownerPath), "utf8"),
  ]);
  ({ denominator, owner_catalogue: ownerCatalogue } =
    decodeFiniteVocabularyDenominatorV1(denominatorBytes, ownerBytes, ownerPath));
  positive = decodeFiniteVocabularyObservationV1(
    await readFile(resolve(fixtureRoot, "positive-observation.json"), "utf8"),
  );
  mutations = decodeFiniteVocabularyMutationCatalogueV1(
    await readFile(resolve(fixtureRoot, "mutants.json"), "utf8"),
    denominator,
  );
});

describe("independent finite-vocabulary Enum denominator", () => {
  it("proves ten portable decisions without claiming native identity parity", () => {
    const result = evaluateFiniteVocabulary({
      denominator,
      owner_catalogue: ownerCatalogue,
      observation: positive,
    });
    expect(result.verdict).toBe("pass");
    expect(result.findings).toEqual([]);
    expect(result.positive_decision_accounting).toEqual({
      declared: 10,
      passed: 10,
      failed: 0,
      unaccounted: 0,
    });
    expect(result.portable_claim).toBe("owner-bound-finite-member-wire-bijection");
    expect(result.native_identity_diagnostic).toEqual({
      relation: "not-observed",
      claim_scope: "native-diagnostic-only",
    });
  });

  it("keeps order non-semantic and produces the same proof identity", () => {
    const { observation_sha256: _digest, ...body } = positive;
    const reordered = mintFiniteVocabularyObservationV1({
      ...body,
      members: [...positive.members].reverse(),
    });
    expect(reordered.observation_sha256).toBe(positive.observation_sha256);
    expect(evaluateFiniteVocabulary({
      denominator,
      owner_catalogue: ownerCatalogue,
      observation: reordered,
    })).toEqual(evaluateFiniteVocabulary({
      denominator,
      owner_catalogue: ownerCatalogue,
      observation: positive,
    }));
  });

  it("keeps collapsed TypeScript and nominal Python/Rust identity as diagnostics", () => {
    const { observation_sha256: _digest, ...body } = positive;
    const collapsed = mintFiniteVocabularyObservationV1({
      ...body,
      native_identity_diagnostic: {
        relation: "collapsed-literal",
        claim_scope: "native-diagnostic-only",
      },
    });
    const nominal = mintFiniteVocabularyObservationV1({
      ...body,
      native_identity_diagnostic: {
        relation: "nominal",
        claim_scope: "native-diagnostic-only",
      },
    });
    const collapsedResult = evaluateFiniteVocabulary({
      denominator,
      owner_catalogue: ownerCatalogue,
      observation: collapsed,
    });
    const nominalResult = evaluateFiniteVocabulary({
      denominator,
      owner_catalogue: ownerCatalogue,
      observation: nominal,
    });
    expect([collapsedResult.verdict, nominalResult.verdict]).toEqual(["pass", "pass"]);
    expect(collapsedResult.positive_decision_accounting)
      .toEqual(nominalResult.positive_decision_accounting);
    expect(collapsedResult.native_identity_diagnostic.relation).toBe("collapsed-literal");
    expect(nominalResult.native_identity_diagnostic.relation).toBe("nominal");
  });

  it("keeps all nine hostile classes red with exact independent findings", () => {
    expect(mutations.mutations).toHaveLength(9);
    expect(mutations.target_code_may_read_expected_findings).toBe(false);
    for (const mutation of mutations.mutations) {
      const observed = applyFiniteVocabularyMutant(positive, mutation);
      const result = evaluateFiniteVocabulary({
        denominator,
        owner_catalogue: ownerCatalogue,
        observation: observed,
      });
      expect(result.verdict, mutation.mutation_id).toBe("fail");
      expect([...new Set(result.findings.map(({ code }) => code))].sort(),
        mutation.mutation_id).toEqual([...mutation.expected_finding_codes].sort());
      expect(result.positive_decision_accounting.unaccounted,
        mutation.mutation_id).toBe(0);
    }
  });

  it("fails closed on stale owner and fixture digests", () => {
    const staleDenominator = denominatorBytes.replace(
      denominator.denominator_sha256,
      "0".repeat(64),
    );
    expect(() => decodeFiniteVocabularyDenominatorV1(
      staleDenominator,
      ownerBytes,
      ownerPath,
    )).toThrow("FAMILY_ENUM_DENOMINATOR_DIGEST_STALE");

    const observationBytes = JSON.stringify({
      ...positive,
      observation_sha256: "0".repeat(64),
    });
    expect(() => decodeFiniteVocabularyObservationV1(observationBytes))
      .toThrow("FAMILY_ENUM_OBSERVATION_DIGEST_STALE");
  });

  it("keeps fixture expectations outside evaluator and mutation execution", async () => {
    const [evaluatorSource, mutationSource] = await Promise.all([
      readFile(resolve(here, "evaluate-finite-vocabulary.ts"), "utf8"),
      readFile(resolve(here,
        "../mutations/apply-finite-vocabulary-mutant.ts"), "utf8"),
    ]);
    for (const source of [evaluatorSource, mutationSource]) {
      expect(source).not.toContain("fixtures/");
      expect(source).not.toContain("mutants.json");
      expect(source).not.toContain("expected_finding_codes");
      expect(source).not.toContain("targets/python");
      expect(source).not.toContain("targets/rust");
      expect(source).not.toContain("targets/typescript");
    }
  });
});
