import FiniteSourceCatalog
import RawIntentPayload

set_option autoImplicit false

namespace RelationalSuccessor.CandidateFiniteSourceCatalog.IntentPayload
open RelationalSuccessor
abbrev RawPayload := _root_.RelationalSuccessor.CandidateIntentSource.RawPayload
abbrev Payload := _root_.RelationalSuccessor.CandidateIntentSource.Payload
abbrev PayloadMeaning := _root_.RelationalSuccessor.CandidateIntentSource.PayloadMeaning

def targets {α : Type} (capture : Capture α) (role : Role) (token : String) : List RevisionRef :=
  (capture.bindings.filter (fun binding => decide (binding.role = role ∧ binding.token = token))).map Binding.ref

def approvedRefs {α : Type} (capture : Capture α) (role : Role) : List RevisionRef :=
  (capture.roots.filter (fun root => decide (root.role = role ∧ root.frame = capture.frame))).map
    (fun root => root.artifact.ref)

theorem targets_member_exact {α : Type} (capture : Capture α) (role : Role)
    (token : String) (ref : RevisionRef) :
    ref ∈ targets capture role token ↔
      ∃ binding ∈ capture.bindings, binding.role = role ∧ binding.token = token ∧ binding.ref = ref := by
  simp only [targets, List.mem_map, List.mem_filter, decide_eq_true_eq]
  constructor
  · rintro ⟨binding, ⟨member, correctRole, exactToken⟩, exactRef⟩
    exact ⟨binding, member, correctRole, exactToken, exactRef⟩
  · rintro ⟨binding, member, correctRole, exactToken, exactRef⟩
    exact ⟨binding, ⟨member, correctRole, exactToken⟩, exactRef⟩

theorem approvals_member_exact {α : Type} (capture : Capture α) (role : Role) (ref : RevisionRef) :
    ref ∈ approvedRefs capture role ↔ ∃ root ∈ capture.roots,
      root.role = role ∧ root.frame = capture.frame ∧ root.artifact.ref = ref := by
  simp only [approvedRefs, List.mem_map, List.mem_filter, decide_eq_true_eq]
  constructor
  · rintro ⟨root, ⟨member, correctRole, exactFrame⟩, exactRef⟩
    exact ⟨root, member, correctRole, exactFrame, exactRef⟩
  · rintro ⟨root, member, correctRole, exactFrame, exactRef⟩
    exact ⟨root, ⟨member, correctRole, exactFrame⟩, exactRef⟩

theorem projected_token_meaning_exact {α : Type} (capture : Capture α) (valid : CaptureMeaning capture)
    (role : Role) (token : String) (ref : RevisionRef) :
    CandidateSourceResolution.TokenMeaning (targets capture) (approvedRefs capture) role token ref ↔
      ∃ binding ∈ capture.bindings, binding.role = role ∧ binding.token = token ∧ binding.ref = ref := by
  constructor
  · intro meaning
    exact (targets_member_exact capture role token ref).mp meaning.2.1
  · rintro ⟨binding, member, correctRole, exactToken, exactRef⟩
    have qualifies := valid.bindingsApproved binding member
    rcases qualifies with ⟨nonempty, artifact, owned, boundRef, approval⟩
    refine ⟨by simpa [exactToken] using nonempty,
      (targets_member_exact capture role token ref).mpr ⟨binding, member, correctRole, exactToken, exactRef⟩, ?_, ?_⟩
    · intro other otherMember
      rcases (targets_member_exact capture role token other).mp otherMember with
        ⟨otherBinding, otherOwned, otherRole, otherToken, otherRef⟩
      have keys : binding.key = otherBinding.key := by simp [Binding.key, correctRole, exactToken, otherRole, otherToken]
      have equal := valid.bindings binding member otherBinding otherOwned keys
      subst otherBinding
      exact otherRef.symm.trans exactRef
    · rcases approval with ⟨root, rootOwned, rootRole, rootRecord, rootFrame⟩
      refine (approvals_member_exact capture role ref).mpr ⟨root, rootOwned, rootRole.trans correctRole, rootFrame, ?_⟩
      rw [rootRecord]
      exact boundRef.trans exactRef

def Meaning {α : Type} (capture : Capture α) (expected : Frame) (raw : RawPayload) (payload : Payload) : Prop :=
  CaptureMeaning capture ∧ capture.frame = expected ∧
    PayloadMeaning (targets capture) (approvedRefs capture) raw payload

def decode {α : Type} [DecidableEq α] (capture : Capture α) (expected : Frame)
    (raw : RawPayload) : Option Payload :=
  if captureCheck capture then
    if capture.frame = expected then
      CandidateIntentSource.decodePayload (targets capture) (approvedRefs capture) raw
    else none
  else none

theorem guarded_decode_exact {α : Type} [DecidableEq α] (capture : Capture α)
    (expected : Frame) (raw : RawPayload) (payload : Payload) :
    decode capture expected raw = some payload ↔ Meaning capture expected raw payload := by
  by_cases valid : CaptureMeaning capture
  · have checked := (capture_check_exact capture).mpr valid
    by_cases frame : capture.frame = expected
    · simp [decode, Meaning, checked, frame, valid, CandidateIntentSource.decode_payload_exact]
    · simp [decode, Meaning, checked, frame]
  · have failed : captureCheck capture = false := by
      cases checked : captureCheck capture with
      | false => rfl
      | true => exact False.elim (valid ((capture_check_exact capture).mp checked))
    simp [decode, Meaning, failed, valid]

theorem successful_decode_has_consistent_capture {α : Type} [DecidableEq α]
    (capture : Capture α) (expected : Frame) (raw : RawPayload) (payload : Payload)
    (decoded : decode capture expected raw = some payload) :
    CaptureMeaning capture ∧ capture.frame = expected := by
  have meaning := (guarded_decode_exact capture expected raw payload).mp decoded
  exact ⟨meaning.1, meaning.2.1⟩

theorem invalid_capture_refuses {α : Type} [DecidableEq α] (capture : Capture α)
    (expected : Frame) (raw : RawPayload) (invalid : captureCheck capture = false) :
    decode capture expected raw = none := by simp [decode, invalid]

theorem wrong_frame_refuses_payload {α : Type} [DecidableEq α] (capture : Capture α)
    (expected : Frame) (raw : RawPayload) (wrong : capture.frame ≠ expected) :
    decode capture expected raw = none := by
  simp only [decode, if_neg wrong]
  split <;> rfl

theorem conflicting_artifacts_refuse_payload {α : Type} [DecidableEq α]
    (capture : Capture α) (expected : Frame) (raw : RawPayload) (a b : Artifact α)
    (ha : a ∈ allArtifacts capture) (hb : b ∈ allArtifacts capture)
    (same : a.ref.key = b.ref.key) (different : a ≠ b) : decode capture expected raw = none :=
  invalid_capture_refuses capture expected raw (conflicting_artifacts_refuse capture a b ha hb same different)

theorem unapproved_record_refuses_payload {α : Type} [DecidableEq α]
    (capture : Capture α) (expected : Frame) (raw : RawPayload) (artifact : Artifact α)
    (member : artifact ∈ capture.records) (missing : ¬ RecordApproved capture artifact) :
    decode capture expected raw = none :=
  invalid_capture_refuses capture expected raw (unapproved_record_refuses capture artifact member missing)

theorem stale_root_frame_refuses_payload {α : Type} [DecidableEq α]
    (capture : Capture α) (expected : Frame) (raw : RawPayload) (root : Approval α)
    (member : root ∈ capture.roots) (wrong : root.frame ≠ capture.frame) :
    decode capture expected raw = none :=
  invalid_capture_refuses capture expected raw (stale_root_frame_refuses capture root member wrong)

theorem extension_preserves_token_meaning {α : Type} (old next : Capture α)
    (extension : LegalExtension old next) (role : Role) (token : String) (ref : RevisionRef)
    (meaning : CandidateSourceResolution.TokenMeaning (targets old) (approvedRefs old) role token ref) :
    CandidateSourceResolution.TokenMeaning (targets next) (approvedRefs next) role token ref := by
  rcases (projected_token_meaning_exact old extension.1 role token ref).mp meaning with
    ⟨binding, member, correctRole, exactToken, exactRef⟩
  exact (projected_token_meaning_exact next extension.2.1 role token ref).mpr
    ⟨binding, extension.2.2.2.2.1 binding member, correctRole, exactToken, exactRef⟩

theorem extension_preserves_list_meaning {α : Type} (old next : Capture α)
    (extension : LegalExtension old next) (role : Role) (tokens : List String) (refs : List RevisionRef)
    (meaning : CandidateSourceResolution.ListMeaning (targets old) (approvedRefs old) role tokens refs) :
    CandidateSourceResolution.ListMeaning (targets next) (approvedRefs next) role tokens refs := by
  induction tokens generalizing refs with
  | nil => cases refs <;> simp_all [CandidateSourceResolution.ListMeaning]
  | cons token rest ih =>
    cases refs with
    | nil => simp [CandidateSourceResolution.ListMeaning] at meaning
    | cons ref refs =>
      exact ⟨extension_preserves_token_meaning old next extension role token ref meaning.1, ih refs meaning.2⟩

theorem extension_preserves_payload_decoding {α : Type} [DecidableEq α]
    (old next : Capture α) (extension : LegalExtension old next) (expected : Frame)
    (raw : RawPayload) (payload : Payload) (decoded : decode old expected raw = some payload) :
    decode next expected raw = some payload := by
  have meaning := (guarded_decode_exact old expected raw payload).mp decoded
  refine (guarded_decode_exact next expected raw payload).mpr
    ⟨extension.2.1, extension.2.2.1.symm.trans meaning.2.1, ?_⟩
  exact ⟨extension_preserves_token_meaning old next extension _ _ _ meaning.2.2.intent,
    extension_preserves_token_meaning old next extension _ _ _ meaning.2.2.decision,
    extension_preserves_list_meaning old next extension _ _ _ meaning.2.2.selected,
    extension_preserves_list_meaning old next extension _ _ _ meaning.2.2.tests,
    extension_preserves_list_meaning old next extension _ _ _ meaning.2.2.excluded⟩

#print axioms targets_member_exact
#print axioms approvals_member_exact
#print axioms projected_token_meaning_exact
#print axioms guarded_decode_exact
#print axioms successful_decode_has_consistent_capture
#print axioms invalid_capture_refuses
#print axioms wrong_frame_refuses_payload
#print axioms conflicting_artifacts_refuse_payload
#print axioms unapproved_record_refuses_payload
#print axioms stale_root_frame_refuses_payload
#print axioms extension_preserves_token_meaning
#print axioms extension_preserves_list_meaning
#print axioms extension_preserves_payload_decoding
end RelationalSuccessor.CandidateFiniteSourceCatalog.IntentPayload
