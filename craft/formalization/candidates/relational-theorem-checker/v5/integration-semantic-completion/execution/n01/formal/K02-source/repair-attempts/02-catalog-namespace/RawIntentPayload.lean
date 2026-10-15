import TokenResolution
import IntentAddressingCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentSource
open RelationalSuccessor
open CandidateSourceResolution

-- Exact projection of the five required Intent Resolution payload fields.
-- This is a JSON-AST projection, not proof of the byte parser or outer schema.
structure RawPayload where
  intent_ref : String
  owner_decision_ref : String
  selected_subject_refs : List String
  satisfaction_test_refs : List String
  excluded_subject_refs : List String
  deriving DecidableEq, Repr

structure Payload where
  intent : RevisionRef
  ownerDecision : RevisionRef
  selectedSubjects : List RevisionRef
  satisfactionTests : List RevisionRef
  excludedSubjects : List RevisionRef
  deriving DecidableEq, Repr

-- The denotation is independently fieldwise and order-preserving; it does not
-- call decodePayload or equate "meaning" with a successful decoder return.
structure PayloadMeaning (catalog : Catalog) (roots : Roots)
    (raw : RawPayload) (payload : Payload) : Prop where
  intent : TokenMeaning catalog roots .intent raw.intent_ref payload.intent
  decision : TokenMeaning catalog roots .decision raw.owner_decision_ref payload.ownerDecision
  selected : ListMeaning catalog roots .subject raw.selected_subject_refs payload.selectedSubjects
  tests : ListMeaning catalog roots .satisfactionTest raw.satisfaction_test_refs payload.satisfactionTests
  excluded : ListMeaning catalog roots .subject raw.excluded_subject_refs payload.excludedSubjects

def decodePayload (catalog : Catalog) (roots : Roots) (raw : RawPayload) : Option Payload :=
  match resolve catalog roots .intent raw.intent_ref,
        resolve catalog roots .decision raw.owner_decision_ref,
        decodeList catalog roots .subject raw.selected_subject_refs,
        decodeList catalog roots .satisfactionTest raw.satisfaction_test_refs,
        decodeList catalog roots .subject raw.excluded_subject_refs with
  | some intent, some decision, some selected, some tests, some excluded =>
      some ⟨intent, decision, selected, tests, excluded⟩
  | _, _, _, _, _ => none

theorem decode_payload_exact (catalog : Catalog) (roots : Roots)
    (raw : RawPayload) (payload : Payload) :
    decodePayload catalog roots raw = some payload ↔ PayloadMeaning catalog roots raw payload := by
  cases payload with
  | mk intent decision selected tests excluded =>
    have meaning : PayloadMeaning catalog roots raw ⟨intent, decision, selected, tests, excluded⟩ ↔
        TokenMeaning catalog roots .intent raw.intent_ref intent ∧
        TokenMeaning catalog roots .decision raw.owner_decision_ref decision ∧
        ListMeaning catalog roots .subject raw.selected_subject_refs selected ∧
        ListMeaning catalog roots .satisfactionTest raw.satisfaction_test_refs tests ∧
        ListMeaning catalog roots .subject raw.excluded_subject_refs excluded := by
      constructor
      · intro h; exact ⟨h.intent, h.decision, h.selected, h.tests, h.excluded⟩
      · rintro ⟨a, b, c, d, e⟩; exact ⟨a, b, c, d, e⟩
    rw [meaning, ← resolve_exact, ← resolve_exact, ← decode_list_exact,
      ← decode_list_exact, ← decode_list_exact]
    cases hi : resolve catalog roots .intent raw.intent_ref <;>
      cases hd : resolve catalog roots .decision raw.owner_decision_ref <;>
      cases hs : decodeList catalog roots .subject raw.selected_subject_refs <;>
      cases ht : decodeList catalog roots .satisfactionTest raw.satisfaction_test_refs <;>
      cases he : decodeList catalog roots .subject raw.excluded_subject_refs <;>
      simp [decodePayload, hi, hd, hs, ht, he]

theorem decoded_selected_count (catalog : Catalog) (roots : Roots)
    (raw : RawPayload) (payload : Payload)
    (decoded : decodePayload catalog roots raw = some payload) :
    payload.selectedSubjects.length = raw.selected_subject_refs.length :=
  list_meaning_length catalog roots .subject raw.selected_subject_refs payload.selectedSubjects
    ((decode_payload_exact catalog roots raw payload).mp decoded).selected

theorem decoded_test_count (catalog : Catalog) (roots : Roots)
    (raw : RawPayload) (payload : Payload)
    (decoded : decodePayload catalog roots raw = some payload) :
    payload.satisfactionTests.length = raw.satisfaction_test_refs.length :=
  list_meaning_length catalog roots .satisfactionTest raw.satisfaction_test_refs payload.satisfactionTests
    ((decode_payload_exact catalog roots raw payload).mp decoded).tests

theorem decoded_excluded_count (catalog : Catalog) (roots : Roots)
    (raw : RawPayload) (payload : Payload)
    (decoded : decodePayload catalog roots raw = some payload) :
    payload.excludedSubjects.length = raw.excluded_subject_refs.length :=
  list_meaning_length catalog roots .subject raw.excluded_subject_refs payload.excludedSubjects
    ((decode_payload_exact catalog roots raw payload).mp decoded).excluded

def attach (ref scope : RevisionRef) (payload : Payload) : CandidateIntentAddressing.Resolution :=
  ⟨ref, scope, payload.intent, payload.ownerDecision, payload.selectedSubjects,
    payload.excludedSubjects, payload.satisfactionTests⟩

theorem attachment_preserves_payload (ref scope : RevisionRef) (payload : Payload) :
    (attach ref scope payload).intent = payload.intent ∧
    (attach ref scope payload).ownerDecision = payload.ownerDecision ∧
    (attach ref scope payload).selectedSubjects = payload.selectedSubjects ∧
    (attach ref scope payload).excludedSubjects = payload.excludedSubjects ∧
    (attach ref scope payload).satisfactionTests = payload.satisfactionTests := by
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

theorem attached_exclusion_refuses (w : CandidateIntentAddressing.World)
    (c : CandidateIntentAddressing.Claim) (ref scope : RevisionRef) (payload : Payload)
    (attached : c.resolution = attach ref scope payload)
    (excluded : c.subject.ref ∈ payload.excludedSubjects) :
    ¬ CandidateIntentAddressing.Addresses w c := by
  intro addressed
  exact addressed.notExcluded (by simpa [attached, attach] using excluded)

theorem attached_empty_tests_do_not_prove_satisfaction (w : CandidateIntentAddressing.World)
    (c : CandidateIntentAddressing.Claim) (ref scope : RevisionRef) (payload : Payload)
    (attached : c.resolution = attach ref scope payload)
    (empty : payload.satisfactionTests = []) :
    ¬ CandidateIntentAddressing.Satisfied w c := by
  intro satisfied
  exact satisfied.1 (by simpa [attached, attach] using empty)

theorem attached_selected_duplicates_refuse (w : CandidateIntentAddressing.World)
    (c : CandidateIntentAddressing.Claim) (ref scope : RevisionRef) (payload : Payload)
    (attached : c.resolution = attach ref scope payload)
    (duplicates : ¬ payload.selectedSubjects.Nodup) :
    ¬ CandidateIntentAddressing.Addresses w c := by
  intro addressed
  exact duplicates (by simpa [attached, attach] using addressed.selectedDistinct)

#print axioms decode_payload_exact
#print axioms decoded_selected_count
#print axioms decoded_test_count
#print axioms decoded_excluded_count
#print axioms attachment_preserves_payload
#print axioms attached_exclusion_refuses
#print axioms attached_empty_tests_do_not_prove_satisfaction
#print axioms attached_selected_duplicates_refuse
end RelationalSuccessor.CandidateIntentSource
