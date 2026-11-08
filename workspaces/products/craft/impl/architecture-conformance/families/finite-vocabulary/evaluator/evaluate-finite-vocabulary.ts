import { createHash } from "node:crypto";

import {
  FINITE_VOCABULARY_DECISIONS,
  type FiniteVocabularyDecisionId,
  type FiniteVocabularyDenominatorV1,
  type FiniteVocabularyEvaluationV1,
  type FiniteVocabularyFindingCode,
  type FiniteVocabularyFindingV1,
  type FiniteVocabularyObservationV1,
  type OwnerEnumCatalogueV1,
} from "../contracts/finite-vocabulary-contracts.js";
import { canonicalFiniteVocabularyJson } from
  "../providers/decode-finite-vocabulary.js";

export type EvaluateFiniteVocabularyInput = Readonly<{
  denominator: FiniteVocabularyDenominatorV1;
  owner_catalogue: OwnerEnumCatalogueV1;
  observation: FiniteVocabularyObservationV1;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: unknown): string => createHash("sha256")
  .update(canonicalFiniteVocabularyJson(value), "utf8")
  .digest("hex");

const decisionForCode: Readonly<Record<FiniteVocabularyFindingCode,
FiniteVocabularyDecisionId>> = Object.freeze({
  FAMILY_ENUM_PROVENANCE_MISMATCH: "owner-catalogue-provenance",
  FAMILY_ENUM_MEMBER_MISSING: "exact-member-set",
  FAMILY_ENUM_MEMBER_UNEXPECTED: "exact-member-set",
  FAMILY_ENUM_MEMBER_DUPLICATE: "unique-member-observation",
  FAMILY_ENUM_ALIAS_OBSERVED: "one-native-key-per-member",
  FAMILY_ENUM_MEMBER_KEY_MISMATCH: "one-native-key-per-member",
  FAMILY_ENUM_NATIVE_KEY_COLLISION: "unique-native-keys",
  FAMILY_ENUM_WIRE_MISMATCH: "exact-member-wire",
  FAMILY_ENUM_WIRE_COLLISION: "unique-emitted-wires",
  FAMILY_ENUM_ROUND_TRIP_CYCLE: "known-wire-round-trip",
  FAMILY_ENUM_UNKNOWN_WIRE_ACCEPTED: "unknown-wire-structured-failure",
  FAMILY_ENUM_UNKNOWN_PROBE_INVALID: "unknown-wire-structured-failure",
  FAMILY_ENUM_ORDER_BECAME_SEMANTIC: "order-is-non-semantic",
});

const finding = (
  code: FiniteVocabularyFindingCode,
  details: Partial<Pick<FiniteVocabularyFindingV1,
  "member_id" | "expected" | "observed">> = {},
): FiniteVocabularyFindingV1 => Object.freeze({
  code,
  decision_id: decisionForCode[code],
  member_id: details.member_id ?? null,
  expected: details.expected ?? null,
  observed: details.observed ?? null,
});

const addDistinctMemberCollisions = (
  observations: FiniteVocabularyObservationV1["members"],
  values: (member: FiniteVocabularyObservationV1["members"][number]) => readonly string[],
  code: "FAMILY_ENUM_NATIVE_KEY_COLLISION" | "FAMILY_ENUM_WIRE_COLLISION",
  findings: FiniteVocabularyFindingV1[],
): void => {
  const membersByValue = new Map<string, Set<string>>();
  for (const member of observations) {
    for (const value of values(member)) {
      const members = membersByValue.get(value) ?? new Set<string>();
      members.add(member.member_id);
      membersByValue.set(value, members);
    }
  }
  for (const [value, members] of membersByValue) {
    if (members.size > 1) findings.push(finding(code, {
      observed: value,
      member_id: [...members].sort(compareUtf8).join(","),
    }));
  }
};

export const evaluateFiniteVocabulary = (
  input: EvaluateFiniteVocabularyInput,
): FiniteVocabularyEvaluationV1 => {
  const { denominator, owner_catalogue: ownerCatalogue, observation } = input;
  const findings: FiniteVocabularyFindingV1[] = [];
  const expectedRef = denominator.owner_catalogue_ref;
  const observedRef = observation.owner_catalogue_ref;
  if (ownerCatalogue.catalogue_id !== expectedRef.catalogue_id
      || observation.catalogue_origin !== "owner-authored-admission-input"
      || observedRef.catalogue_id !== expectedRef.catalogue_id
      || observedRef.path !== expectedRef.path
      || observedRef.sha256 !== expectedRef.sha256) {
    findings.push(finding("FAMILY_ENUM_PROVENANCE_MISMATCH", {
      expected: `${expectedRef.catalogue_id}@${expectedRef.sha256}`,
      observed: `${String(observation.catalogue_origin)}:${observedRef.catalogue_id}@${observedRef.sha256}`,
    }));
  }

  const observationsByMember = new Map<string,
  FiniteVocabularyObservationV1["members"][number][]>();
  for (const member of observation.members) {
    const entries = observationsByMember.get(member.member_id) ?? [];
    entries.push(member);
    observationsByMember.set(member.member_id, entries);
  }
  const expectedByMember = new Map(ownerCatalogue.members.map((member) =>
    [member.member_id, member] as const));

  for (const observed of observation.members) {
    if (!expectedByMember.has(observed.member_id)) {
      findings.push(finding("FAMILY_ENUM_MEMBER_UNEXPECTED", {
        member_id: observed.member_id,
        observed: observed.emitted_wire,
      }));
    }
  }
  for (const expected of ownerCatalogue.members) {
    const matches = observationsByMember.get(expected.member_id) ?? [];
    if (matches.length === 0) {
      findings.push(finding("FAMILY_ENUM_MEMBER_MISSING", {
        member_id: expected.member_id,
        expected: expected.wire_value,
      }));
      continue;
    }
    if (matches.length > 1) {
      findings.push(finding("FAMILY_ENUM_MEMBER_DUPLICATE", {
        member_id: expected.member_id,
        expected: "1",
        observed: String(matches.length),
      }));
      continue;
    }
    const observed = matches[0]!;
    if (observed.native_keys.length !== 1) {
      findings.push(finding("FAMILY_ENUM_ALIAS_OBSERVED", {
        member_id: expected.member_id,
        expected: expected.member_key,
        observed: observed.native_keys.join(","),
      }));
    } else if (observed.native_keys[0] !== expected.member_key) {
      findings.push(finding("FAMILY_ENUM_MEMBER_KEY_MISMATCH", {
        member_id: expected.member_id,
        expected: expected.member_key,
        observed: observed.native_keys[0] ?? null,
      }));
    }
    if (observed.emitted_wire !== expected.wire_value) {
      findings.push(finding("FAMILY_ENUM_WIRE_MISMATCH", {
        member_id: expected.member_id,
        expected: expected.wire_value,
        observed: observed.emitted_wire,
      }));
    }
    if (observed.parsed_member_id !== expected.member_id) {
      findings.push(finding("FAMILY_ENUM_ROUND_TRIP_CYCLE", {
        member_id: expected.member_id,
        expected: expected.member_id,
        observed: observed.parsed_member_id,
      }));
    }
  }

  addDistinctMemberCollisions(
    observation.members,
    ({ native_keys: nativeKeys }) => nativeKeys,
    "FAMILY_ENUM_NATIVE_KEY_COLLISION",
    findings,
  );
  addDistinctMemberCollisions(
    observation.members,
    ({ emitted_wire: wire }) => [wire],
    "FAMILY_ENUM_WIRE_COLLISION",
    findings,
  );

  const expectedWires = new Set(ownerCatalogue.members.map(({ wire_value: wire }) => wire));
  if (expectedWires.has(observation.unknown_wire.wire_value)) {
    findings.push(finding("FAMILY_ENUM_UNKNOWN_PROBE_INVALID", {
      expected: "wire outside owner catalogue",
      observed: observation.unknown_wire.wire_value,
    }));
  }
  if (observation.unknown_wire.outcome !== "structured-failure"
      || observation.unknown_wire.error_code === null
      || observation.unknown_wire.error_code.length === 0
      || observation.unknown_wire.parsed_member_id !== null) {
    findings.push(finding("FAMILY_ENUM_UNKNOWN_WIRE_ACCEPTED", {
      expected: "structured-failure",
      observed: `${observation.unknown_wire.outcome}:${observation.unknown_wire.parsed_member_id ?? "null"}`,
    }));
  }
  if (observation.member_order_semantics !== "none") {
    findings.push(finding("FAMILY_ENUM_ORDER_BECAME_SEMANTIC", {
      expected: "none",
      observed: observation.member_order_semantics,
    }));
  }

  const normalizedFindings = Object.freeze([...findings].sort((left, right) =>
    compareUtf8(
      `${left.code}\u0000${left.member_id ?? ""}\u0000${left.observed ?? ""}`,
      `${right.code}\u0000${right.member_id ?? ""}\u0000${right.observed ?? ""}`,
    )));
  const failedDecisions = new Set(normalizedFindings.map(({ decision_id: id }) => id));
  const declared = FINITE_VOCABULARY_DECISIONS.length;
  const failed = failedDecisions.size;
  const verdict = normalizedFindings.length === 0 ? "pass" as const : "fail" as const;
  const denominatorRef = Object.freeze({
    denominator_id: denominator.denominator_id,
    denominator_sha256: denominator.denominator_sha256,
  });
  const observationRef = Object.freeze({
    observation_id: observation.observation_id,
    observation_sha256: observation.observation_sha256,
  });
  return Object.freeze({
    schema_version: "FiniteVocabularyEvaluation/v1" as const,
    evaluation_id: `evaluation.finite-vocabulary.${sha256({
      denominatorRef,
      observationRef,
      findings: normalizedFindings,
    })}`,
    denominator_ref: denominatorRef,
    observation_ref: observationRef,
    verdict,
    findings: normalizedFindings,
    positive_decision_accounting: Object.freeze({
      declared,
      passed: declared - failed,
      failed,
      unaccounted: 0 as const,
    }),
    portable_claim: "owner-bound-finite-member-wire-bijection" as const,
    native_identity_diagnostic: observation.native_identity_diagnostic,
    authority_effect: "none" as const,
  });
};
