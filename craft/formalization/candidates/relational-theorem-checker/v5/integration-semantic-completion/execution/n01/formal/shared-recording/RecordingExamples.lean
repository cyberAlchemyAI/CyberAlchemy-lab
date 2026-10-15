import QualifiedRecording

set_option autoImplicit false

namespace RelationalSuccessor.CandidateRecording.Examples
open RelationalSuccessor

def ref (revision digest : String) : RevisionRef :=
  ⟨⟨"fixture", "relation-record", revision⟩, digest⟩
def original : Envelope Nat := ⟨ref "1" "digest-A", 1, []⟩
def changedBody : Envelope Nat := ⟨original.ref, 2, []⟩
def changedDigest : Envelope Nat := ⟨ref "1" "digest-B", 1, []⟩
def changedContent : Envelope Nat := { original with content := [1] }
def nextRevision : Envelope Nat := ⟨ref "2" "digest-C", 2, []⟩
def unqualified : Envelope Nat := ⟨ref "3" "digest-D", 0, []⟩
def protectedState : List Nat := [7, 8, 9]
def emptyStore : State Nat (List Nat) := ⟨protectedState, []⟩
def recorded : State Nat (List Nat) := ⟨protectedState, [original]⟩
def malformed : State Nat (List Nat) := ⟨protectedState, [original, changedBody]⟩
def identicalDuplicates : State Nat (List Nat) := ⟨protectedState, [original, original]⟩
def check (record : Envelope Nat) : Bool := decide (0 < record.body)

theorem fresh_append_example : (submit check emptyStore original).outcome = .appended := by decide

theorem fresh_append_has_exact_one_record :
    (submit check emptyStore original).state.records = [original] := by decide

theorem duplicate_retains_exact_record :
    (submit check recorded original).outcome = .retained ∧
    (submit check recorded original).state.records = [original] := by decide

theorem immediate_retry_is_idempotent :
    (submit check (submit check emptyStore original).state original).outcome = .retained ∧
    (submit check (submit check emptyStore original).state original).state.records = [original] := by decide

theorem different_body_same_revision_refused :
    (submit check recorded changedBody).outcome = .revisionConflict ∧
    (submit check recorded changedBody).state.records = [original] := by decide

theorem different_digest_same_revision_refused :
    (submit check recorded changedDigest).outcome = .revisionConflict ∧
    (submit check recorded changedDigest).state.records = [original] := by decide

theorem different_bytes_same_revision_refused :
    (submit check recorded changedContent).outcome = .revisionConflict ∧
    (submit check recorded changedContent).state.records = [original] := by decide

theorem distinct_revision_appends_without_overwrite :
    (submit check recorded nextRevision).outcome = .appended ∧
    (submit check recorded nextRevision).state.records = [original, nextRevision] := by decide

theorem unqualified_request_refused :
    (submit check recorded unqualified).outcome = .unqualified ∧
    (submit check recorded unqualified).state.records = [original] := by decide

theorem existing_record_does_not_seed_success :
    (submit (fun _ => false) recorded original).outcome = .unqualified ∧
    (submit (fun _ => false) recorded original).state.records = [original] := by decide

theorem conflicting_store_refused_without_repair :
    (submit check malformed nextRevision).outcome = .malformedStore ∧
    (submit check malformed nextRevision).state.records = [original, changedBody] := by decide

theorem identical_duplicate_keys_are_malformed :
    (submit check identicalDuplicates nextRevision).outcome = .malformedStore ∧
    (submit check identicalDuplicates nextRevision).state.records = [original, original] := by decide

#print axioms fresh_append_example
#print axioms fresh_append_has_exact_one_record
#print axioms duplicate_retains_exact_record
#print axioms immediate_retry_is_idempotent
#print axioms different_body_same_revision_refused
#print axioms different_digest_same_revision_refused
#print axioms different_bytes_same_revision_refused
#print axioms distinct_revision_appends_without_overwrite
#print axioms unqualified_request_refused
#print axioms existing_record_does_not_seed_success
#print axioms conflicting_store_refused_without_repair
#print axioms identical_duplicate_keys_are_malformed
end RelationalSuccessor.CandidateRecording.Examples
