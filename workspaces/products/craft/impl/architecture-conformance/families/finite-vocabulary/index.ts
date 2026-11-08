import { evaluateEnumBijection } from "../../realization/evaluator/evaluate-enum-bijection.js";
import { normalizeEnumRealization } from "../../realization/enum/normalize-enum-realization.js";
import { evaluateFiniteVocabulary } from "./evaluator/evaluate-finite-vocabulary.js";
import {
  decodeFiniteVocabularyDenominatorV1,
  decodeFiniteVocabularyMutationCatalogueV1,
  decodeFiniteVocabularyObservationV1,
} from "./providers/decode-finite-vocabulary.js";

export * from "./contracts/finite-vocabulary-contracts.js";
export { evaluateFiniteVocabulary } from "./evaluator/evaluate-finite-vocabulary.js";
export { applyFiniteVocabularyMutant } from
  "./mutations/apply-finite-vocabulary-mutant.js";
export {
  decodeFiniteVocabularyDenominatorV1,
  decodeFiniteVocabularyMutationCatalogueV1,
  decodeFiniteVocabularyObservationV1,
  mintFiniteVocabularyObservationV1,
} from "./providers/decode-finite-vocabulary.js";

export const portableFiniteVocabularyFamilyProvider = Object.freeze({
  schema_version: "PortableFamilyProvider/v1" as const,
  provider_id: "family.finite-vocabulary.portable",
  provider_version: "1.0.0",
  decode: Object.freeze({
    denominator: decodeFiniteVocabularyDenominatorV1,
    observation: decodeFiniteVocabularyObservationV1,
    mutations: decodeFiniteVocabularyMutationCatalogueV1,
  }),
  evaluate: evaluateFiniteVocabulary,
  expected_catalogue_origin: "owner-authored-only" as const,
  native_identity_claim: "diagnostic-not-portable-parity" as const,
  authority_effect: "none" as const,
});

export const finiteVocabularyFamilyProvider = Object.freeze({
  schema_version: "FamilyProvider/v2" as const,
  provider_id: "family.finite-vocabulary",
  provider_version: "1.0.0",
  normalize: normalizeEnumRealization,
  evaluate: evaluateEnumBijection,
  portable: portableFiniteVocabularyFamilyProvider,
  authority_effect: "none" as const,
});
