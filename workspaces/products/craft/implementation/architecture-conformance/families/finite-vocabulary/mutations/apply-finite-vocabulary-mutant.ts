import type {
  FiniteVocabularyMutationKind,
  FiniteVocabularyObservationV1,
  FiniteVocabularyObservedMemberV1,
} from "../contracts/finite-vocabulary-contracts.js";
import { mintFiniteVocabularyObservationV1 } from
  "../providers/decode-finite-vocabulary.js";

export type FiniteVocabularyMutationSelector = Readonly<{
  mutation_id: string;
  mutation_kind: FiniteVocabularyMutationKind;
}>;

const replaceMember = (
  members: readonly FiniteVocabularyObservedMemberV1[],
  memberId: string,
  replace: (member: FiniteVocabularyObservedMemberV1) => FiniteVocabularyObservedMemberV1,
): readonly FiniteVocabularyObservedMemberV1[] => members.map((member) =>
  member.member_id === memberId ? replace(member) : member);

export const applyFiniteVocabularyMutant = (
  positive: FiniteVocabularyObservationV1,
  mutation: FiniteVocabularyMutationSelector,
): FiniteVocabularyObservationV1 => {
  let members: readonly FiniteVocabularyObservedMemberV1[] = positive.members;
  let catalogueOrigin = positive.catalogue_origin;
  let memberOrderSemantics = positive.member_order_semantics;
  let unknownWire = positive.unknown_wire;

  switch (mutation.mutation_kind) {
    case "missing-member":
      members = members.filter(({ member_id: id }) => id !== "priority.normal");
      break;
    case "extra-member":
      members = [...members, Object.freeze({
        member_id: "priority.foreign",
        native_keys: Object.freeze(["Foreign"]),
        emitted_wire: "foreign",
        parsed_member_id: "priority.foreign",
      })];
      break;
    case "duplicate-member": {
      const duplicate = members.find(({ member_id: id }) => id === "priority.deferred");
      if (duplicate === undefined) throw new Error("FAMILY_ENUM_MUTATION_FIXTURE_INVALID");
      members = [...members, duplicate];
      break;
    }
    case "alias":
      members = replaceMember(members, "priority.deferred", (member) => Object.freeze({
        ...member,
        native_keys: Object.freeze(["Deferred", "DeferredAlias"]),
      }));
      break;
    case "round-trip-cycle":
      members = members.map((member) => {
        if (member.member_id === "priority.deferred") {
          return Object.freeze({ ...member, parsed_member_id: "priority.normal" });
        }
        if (member.member_id === "priority.normal") {
          return Object.freeze({ ...member, parsed_member_id: "priority.deferred" });
        }
        return member;
      });
      break;
    case "wire-collision":
      members = replaceMember(members, "priority.normal", (member) => Object.freeze({
        ...member,
        emitted_wire: "deferred",
      }));
      break;
    case "order-authority":
      memberOrderSemantics = "declaration";
      break;
    case "implementation-provenance":
      catalogueOrigin = "implementation-observed";
      break;
    case "unknown-wire-accepted":
      unknownWire = Object.freeze({
        wire_value: positive.unknown_wire.wire_value,
        outcome: "member" as const,
        error_code: null,
        parsed_member_id: "priority.deferred",
      });
      break;
    default: {
      const exhaustive: never = mutation.mutation_kind;
      throw new Error(`FAMILY_ENUM_MUTATION_KIND_UNSUPPORTED:${String(exhaustive)}`);
    }
  }

  return mintFiniteVocabularyObservationV1({
    schema_version: "FiniteVocabularyObservation/v1",
    observation_id: `${positive.observation_id}.mutant.${mutation.mutation_id}`,
    source_kind: "mutated-family-observation",
    target: positive.target,
    owner_catalogue_ref: positive.owner_catalogue_ref,
    catalogue_origin: catalogueOrigin,
    member_order_semantics: memberOrderSemantics,
    members,
    unknown_wire: unknownWire,
    native_identity_diagnostic: positive.native_identity_diagnostic,
    authority_effect: "none",
  });
};
