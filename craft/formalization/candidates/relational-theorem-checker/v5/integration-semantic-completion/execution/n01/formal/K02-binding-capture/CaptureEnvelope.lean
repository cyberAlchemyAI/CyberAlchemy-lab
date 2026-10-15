import BindingRecord
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingCapture
open RelationalSuccessor
abbrev J := RelationalSuccessor.CandidateJsonSource.Value

-- This is submitted capture data, not proof that the bytes parse or are authentic.
structure Envelope where
  content : List UInt8
  byteLength : Nat
  digestProfile : RevisionRef
  digest : String
  deriving DecidableEq, Repr

structure EnvelopeMeaning (capture : Envelope) : Prop where
  length : capture.byteLength = capture.content.length
  digest : capture.digest ≠ ""
  profileOwner : capture.digestProfile.key.owner ≠ ""
  profileArtifact : capture.digestProfile.key.artifact ≠ ""
  profileRevision : capture.digestProfile.key.revision ≠ ""
  profileDigest : capture.digestProfile.digest ≠ ""

def envelopeCheck (capture : Envelope) : Bool :=
  decide (capture.byteLength = capture.content.length) && decide (capture.digest ≠ "") &&
  decide (capture.digestProfile.key.owner ≠ "") && decide (capture.digestProfile.key.artifact ≠ "") &&
  decide (capture.digestProfile.key.revision ≠ "") && decide (capture.digestProfile.digest ≠ "")

theorem envelope_check_exact (capture : Envelope) : envelopeCheck capture = true ↔ EnvelopeMeaning capture := by
  simp only [envelopeCheck, Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · rintro ⟨⟨⟨⟨⟨a,b⟩,c⟩,d⟩,e⟩,f⟩; exact ⟨a,b,c,d,e,f⟩
  · intro h; exact ⟨⟨⟨⟨⟨h.length,h.digest⟩,h.profileOwner⟩,h.profileArtifact⟩,h.profileRevision⟩,h.profileDigest⟩

structure Prepared (α : Type) where
  record : CandidateBindingRecords.Record α
  envelope : Envelope
  deriving DecidableEq, Repr

-- A data projection, with no authentication or admission effect.
def Prepared.entry {α : Type} (prepared : Prepared α) : CandidateOwnedBindings.Entry α :=
  ⟨⟨prepared.record.bindingKey,prepared.envelope.digest⟩,prepared.record.kind,
    prepared.record.body,prepared.envelope.content,prepared.record.ownerReview⟩

structure EntryProjectionMeaning {α : Type} (prepared : Prepared α) (entry : CandidateOwnedBindings.Entry α) : Prop where
  key : entry.ref.key = prepared.record.bindingKey
  digest : entry.ref.digest = prepared.envelope.digest
  kind : entry.sourceKind = prepared.record.kind
  body : entry.body = prepared.record.body
  bytes : entry.content = prepared.envelope.content
  review : entry.ownerReview = prepared.record.ownerReview

theorem entry_projection_exact {α : Type} (prepared : Prepared α) (entry : CandidateOwnedBindings.Entry α) :
    prepared.entry = entry ↔ EntryProjectionMeaning prepared entry := by
  constructor
  · intro same; subst entry; exact ⟨rfl,rfl,rfl,rfl,rfl,rfl⟩
  · intro meaning
    cases entry with
    | mk ref kind body bytes review =>
      cases ref with
      | mk key digest =>
        rcases meaning with ⟨hk,hd,hkind,hbody,hbytes,hreview⟩
        simp only at hk hd hkind hbody hbytes hreview
        subst key; subst digest; subst kind; subst body; subst bytes; subst review
        rfl

structure PreparedMeaning {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : J) (prepared : Prepared α) : Prop where
  envelope : EnvelopeMeaning capture
  decoded : CandidateBindingRecords.RecordMeaning version kind target ast prepared.record
  frame : prepared.record.body.frame = frame
  capture : prepared.envelope = capture

def prepare {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : J) : Option (Prepared α) :=
  if envelopeCheck capture then
    match (CandidateBindingRecords.record version kind target).decode ast with
    | none => none
    | some record => if record.body.frame = frame then some ⟨record,capture⟩ else none
  else none

theorem prepare_exact {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : J) (prepared : Prepared α) :
    prepare version kind target frame capture ast = some prepared ↔
      PreparedMeaning version kind target frame capture ast prepared := by
  constructor
  · intro accepted
    unfold prepare at accepted
    split at accepted
    · rename_i adequate
      cases decoded : (CandidateBindingRecords.record version kind target).decode ast with
      | none => simp [decoded] at accepted
      | some record =>
        simp only [decoded] at accepted
        split at accepted
        · rename_i sameFrame
          cases accepted
          exact ⟨(envelope_check_exact capture).mp adequate,
            (CandidateBindingRecords.record_exact version kind target ast record).mp decoded,sameFrame,rfl⟩
        · simp at accepted
    · simp at accepted
  · intro meaning
    have decoded := (CandidateBindingRecords.record_exact version kind target ast prepared.record).mpr meaning.decoded
    have checked := (envelope_check_exact capture).mpr meaning.envelope
    have same : Prepared.mk prepared.record capture = prepared := by
      cases prepared with
      | mk record envelope =>
        have sameEnvelope : envelope = capture := meaning.capture
        cases sameEnvelope
        rfl
    simp only [prepare, checked, if_true, decoded, meaning.frame]
    exact congrArg some same

def prepareResolution (frame : Frame) (capture : Envelope) (ast : J) : Option (Prepared CandidateIntentAddressing.Resolution) :=
  prepare CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution frame capture ast
def prepareRole (frame : Frame) (capture : Envelope) (ast : J) : Option (Prepared CandidateIntentAddressing.Role) :=
  prepare CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role frame capture ast

theorem prepare_resolution_exact (frame : Frame) (capture : Envelope) (ast : J) (prepared : Prepared CandidateIntentAddressing.Resolution) :
    prepareResolution frame capture ast = some prepared ↔ PreparedMeaning CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution frame capture ast prepared :=
  prepare_exact CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution frame capture ast prepared

theorem prepare_role_exact (frame : Frame) (capture : Envelope) (ast : J) (prepared : Prepared CandidateIntentAddressing.Role) :
    prepareRole frame capture ast = some prepared ↔ PreparedMeaning CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role frame capture ast prepared :=
  prepare_exact CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role frame capture ast prepared

theorem prepared_entry_field_bridge {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : J) (prepared : Prepared α)
    (accepted : prepare version kind target frame capture ast = some prepared) :
    prepared.entry.ref.key = prepared.record.bindingKey ∧
    prepared.entry.ref.digest = capture.digest ∧ prepared.entry.sourceKind = kind ∧
    prepared.entry.body = prepared.record.body ∧ prepared.entry.content = capture.content ∧
    prepared.entry.ownerReview = prepared.record.ownerReview ∧ prepared.entry.body.frame = frame := by
  have meaning := (prepare_exact version kind target frame capture ast prepared).mp accepted
  have constants := CandidateBindingRecords.accepted_record_constants version kind target ast prepared.record
    ((CandidateBindingRecords.record_exact version kind target ast prepared.record).mpr meaning.decoded)
  exact ⟨rfl,by simp only [Prepared.entry,meaning.capture],constants.2,rfl,
    by simp only [Prepared.entry,meaning.capture],rfl,meaning.frame⟩

theorem inadequate_envelope_refuses {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : J) (invalid : ¬ EnvelopeMeaning capture) :
    prepare version kind target frame capture ast = none := by
  have bad : envelopeCheck capture = false := by
    cases h : envelopeCheck capture with
    | false => rfl
    | true => exact False.elim (invalid ((envelope_check_exact capture).mp h))
  simp [prepare,bad]

theorem stale_decoded_frame_refuses {α : Type} (version kind : String) (target : CandidateBindingAst.Decoder α)
    (frame : Frame) (capture : Envelope) (ast : J) (record : CandidateBindingRecords.Record α)
    (decoded : (CandidateBindingRecords.record version kind target).decode ast = some record)
    (stale : record.body.frame ≠ frame) : prepare version kind target frame capture ast = none := by
  simp only [prepare,decoded,if_neg stale]
  split <;> rfl

-- Deterministic recomputation exposes conflicting byte captures at one identity.
-- It does not assert injectivity of a cryptographic digest.
theorem different_bytes_preserve_distinct_entries {α : Type} (a b : Prepared α)
    (different : a.envelope.content ≠ b.envelope.content) : a.entry ≠ b.entry := by
  intro equal
  exact different (congrArg (fun entry : CandidateOwnedBindings.Entry α => entry.content) equal)

#print axioms envelope_check_exact
#print axioms entry_projection_exact
#print axioms prepare_exact
#print axioms prepare_resolution_exact
#print axioms prepare_role_exact
#print axioms prepared_entry_field_bridge
#print axioms inadequate_envelope_refuses
#print axioms stale_decoded_frame_refuses
#print axioms different_bytes_preserve_distinct_entries
end RelationalSuccessor.CandidateBindingCapture
