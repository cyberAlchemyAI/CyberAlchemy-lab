import QualifiedRecording
import IntentAddressingCheck
import ScopedImpactCheck

set_option autoImplicit false

namespace RelationalSuccessor.CandidateRecording.Bindings
open RelationalSuccessor

-- The issued relation revision is distinct from the primary witness revision.
-- Authenticity and completeness of this independently captured catalog are later
-- provenance/source obligations, not supplied by this typed membership test.
structure IssuedRevision where
  ref : RevisionRef
  kind : String
  frame : Frame
  witness : RevisionRef
  content : List UInt8
  deriving DecidableEq, Repr

def IssuedMeaning (roots : List IssuedRevision) (ref : RevisionRef)
    (kind : String) (frame : Frame) (witness : RevisionRef) (content : List UInt8) : Prop :=
  ∃ issued ∈ roots, issued.ref = ref ∧ issued.kind = kind ∧
    issued.frame = frame ∧ issued.witness = witness ∧ issued.content = content

def issuedCheck (roots : List IssuedRevision) (ref : RevisionRef)
    (kind : String) (frame : Frame) (witness : RevisionRef) (content : List UInt8) : Bool :=
  roots.any (fun issued => decide (issued.ref = ref ∧ issued.kind = kind ∧
    issued.frame = frame ∧ issued.witness = witness ∧ issued.content = content))

theorem issued_check_exact (roots : List IssuedRevision) (ref : RevisionRef)
    (kind : String) (frame : Frame) (witness : RevisionRef) (content : List UInt8) :
    issuedCheck roots ref kind frame witness content = true ↔ IssuedMeaning roots ref kind frame witness content := by
  simp [issuedCheck, IssuedMeaning, List.any_eq_true]

namespace Intent
abbrev Payload := CandidateIntentAddressing.Claim

def Meaning (world : CandidateIntentAddressing.World) (roots : List IssuedRevision)
    (record : Envelope Payload) : Prop :=
  IssuedMeaning roots record.ref "relation.addresses-intent" record.body.selection.frame record.body.selection.ref record.content ∧
  CandidateIntentAddressing.Addresses world record.body

def check (world : CandidateIntentAddressing.World) (roots : List IssuedRevision)
    (record : Envelope Payload) : Bool :=
  issuedCheck roots record.ref "relation.addresses-intent" record.body.selection.frame record.body.selection.ref record.content &&
  CandidateIntentAddressing.Checker.check world record.body

def record {β : Type} (world : CandidateIntentAddressing.World) (roots : List IssuedRevision)
    (before : State Payload β) (proposal : Envelope Payload) : Result Payload β :=
  submit (check world roots) before proposal

theorem check_exact (world : CandidateIntentAddressing.World) (roots : List IssuedRevision)
    (proposal : Envelope Payload) : check world roots proposal = true ↔ Meaning world roots proposal := by
  simp [check, Meaning, issued_check_exact, CandidateIntentAddressing.Checker.check_exact]

theorem successful_recording_has_meaning {β : Type} (world : CandidateIntentAddressing.World)
    (roots : List IssuedRevision) (before : State Payload β) (proposal : Envelope Payload)
    (success : Succeeded (record world roots before proposal).outcome) : Meaning world roots proposal :=
  successful_submission_has_meaning (Meaning world roots) (check world roots)
    (check_exact world roots) before proposal success

theorem recording_preserves_protected_state {β : Type} (world : CandidateIntentAddressing.World)
    (roots : List IssuedRevision) (before : State Payload β) (proposal : Envelope Payload) :
    (record world roots before proposal).state.protectedState = before.protectedState :=
  submit_preserves_protected_state (check world roots) before proposal

theorem unissued_revision_refuses {β : Type} (world : CandidateIntentAddressing.World)
    (roots : List IssuedRevision) (before : State Payload β) (proposal : Envelope Payload)
    (unissued : ¬ IssuedMeaning roots proposal.ref "relation.addresses-intent"
      proposal.body.selection.frame proposal.body.selection.ref proposal.content) :
    record world roots before proposal = ⟨.unqualified, before⟩ := by
  apply unqualified_preserves_state
  have failed : issuedCheck roots proposal.ref "relation.addresses-intent"
      proposal.body.selection.frame proposal.body.selection.ref proposal.content = false := by
    cases result : issuedCheck roots proposal.ref "relation.addresses-intent"
      proposal.body.selection.frame proposal.body.selection.ref proposal.content
    · rfl
    · exact False.elim (unissued ((issued_check_exact _ _ _ _ _ _).mp result))
  simp [check, failed]
end Intent

namespace Impact
abbrev Payload := CandidateScopedImpact.Claim

def Meaning (world : CandidateScopedImpact.World) (roots : List IssuedRevision)
    (record : Envelope Payload) : Prop :=
  IssuedMeaning roots record.ref "relation.affects" record.body.observation.frame record.body.observation.ref record.content ∧
  CandidateScopedImpact.Affects world record.body

def check (world : CandidateScopedImpact.World) (roots : List IssuedRevision)
    (record : Envelope Payload) : Bool :=
  issuedCheck roots record.ref "relation.affects" record.body.observation.frame record.body.observation.ref record.content &&
  CandidateScopedImpact.Checker.check world record.body

def record {β : Type} (world : CandidateScopedImpact.World) (roots : List IssuedRevision)
    (before : State Payload β) (proposal : Envelope Payload) : Result Payload β :=
  submit (check world roots) before proposal

theorem check_exact (world : CandidateScopedImpact.World) (roots : List IssuedRevision)
    (proposal : Envelope Payload) : check world roots proposal = true ↔ Meaning world roots proposal := by
  simp [check, Meaning, issued_check_exact, CandidateScopedImpact.Checker.check_exact]

theorem successful_recording_has_meaning {β : Type} (world : CandidateScopedImpact.World)
    (roots : List IssuedRevision) (before : State Payload β) (proposal : Envelope Payload)
    (success : Succeeded (record world roots before proposal).outcome) : Meaning world roots proposal :=
  successful_submission_has_meaning (Meaning world roots) (check world roots)
    (check_exact world roots) before proposal success

theorem recording_preserves_protected_state {β : Type} (world : CandidateScopedImpact.World)
    (roots : List IssuedRevision) (before : State Payload β) (proposal : Envelope Payload) :
    (record world roots before proposal).state.protectedState = before.protectedState :=
  submit_preserves_protected_state (check world roots) before proposal

theorem unissued_revision_refuses {β : Type} (world : CandidateScopedImpact.World)
    (roots : List IssuedRevision) (before : State Payload β) (proposal : Envelope Payload)
    (unissued : ¬ IssuedMeaning roots proposal.ref "relation.affects"
      proposal.body.observation.frame proposal.body.observation.ref proposal.content) :
    record world roots before proposal = ⟨.unqualified, before⟩ := by
  apply unqualified_preserves_state
  have failed : issuedCheck roots proposal.ref "relation.affects"
      proposal.body.observation.frame proposal.body.observation.ref proposal.content = false := by
    cases result : issuedCheck roots proposal.ref "relation.affects"
      proposal.body.observation.frame proposal.body.observation.ref proposal.content
    · rfl
    · exact False.elim (unissued ((issued_check_exact _ _ _ _ _ _).mp result))
  simp [check, failed]
end Impact

#print axioms issued_check_exact
#print axioms Intent.check_exact
#print axioms Intent.successful_recording_has_meaning
#print axioms Intent.recording_preserves_protected_state
#print axioms Intent.unissued_revision_refuses
#print axioms Impact.check_exact
#print axioms Impact.successful_recording_has_meaning
#print axioms Impact.recording_preserves_protected_state
#print axioms Impact.unissued_revision_refuses
end RelationalSuccessor.CandidateRecording.Bindings
