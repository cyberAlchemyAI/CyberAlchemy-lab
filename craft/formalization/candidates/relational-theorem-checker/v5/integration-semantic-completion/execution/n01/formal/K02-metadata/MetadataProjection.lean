import MetadataSource
import GuardedIntentPayload

set_option autoImplicit false

namespace RelationalSuccessor.CandidateCapturedMetadata
open RelationalSuccessor

structure Projected where
  receipt : Receipt
  payload : CandidateIntentSource.Payload
  deriving DecidableEq, Repr

def Projected.resolution (projected : Projected) : CandidateIntentAddressing.Resolution :=
  CandidateIntentSource.attach projected.receipt.artifact.ref projected.receipt.scope.scope projected.payload

def ProjectionMeaning {α : Type} (metadata : Context)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (projected : Projected) : Prop :=
  SourceMeaning metadata expected ref bytes ast projected.receipt ∧
    CandidateFiniteSourceCatalog.IntentPayload.Meaning payloads expected
      projected.receipt.artifact.body.payload projected.payload

def decodeResolution {α : Type} [DecidableEq α] (metadata : Context)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) : Option Projected :=
  match decodeSource metadata expected ref bytes ast with
  | none => none
  | some receipt =>
      match CandidateFiniteSourceCatalog.IntentPayload.decode payloads expected receipt.artifact.body.payload with
      | none => none
      | some payload => some ⟨receipt, payload⟩

theorem decode_resolution_exact {α : Type} [DecidableEq α] (metadata : Context)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (projected : Projected) :
    decodeResolution metadata payloads expected ref bytes ast = some projected ↔
      ProjectionMeaning metadata payloads expected ref bytes ast projected := by
  constructor
  · intro decoded
    cases source : decodeSource metadata expected ref bytes ast with
    | none => simp [decodeResolution, source] at decoded
    | some receipt =>
      cases payload : CandidateFiniteSourceCatalog.IntentPayload.decode payloads expected receipt.artifact.body.payload with
      | none => simp [decodeResolution, source, payload] at decoded
      | some body =>
        have same : (⟨receipt, body⟩ : Projected) = projected := by
          simpa [decodeResolution, source, payload] using decoded
        cases same
        exact ⟨(decode_source_exact metadata expected ref bytes ast receipt).mp source,
          (CandidateFiniteSourceCatalog.IntentPayload.guarded_decode_exact
            payloads expected receipt.artifact.body.payload body).mp payload⟩
  · intro represented
    have source := (decode_source_exact metadata expected ref bytes ast projected.receipt).mpr represented.1
    have payload := (CandidateFiniteSourceCatalog.IntentPayload.guarded_decode_exact
      payloads expected projected.receipt.artifact.body.payload projected.payload).mpr represented.2
    simp [decodeResolution, source, payload]

theorem projected_identity_and_scope {α : Type} [DecidableEq α] (metadata : Context)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (projected : Projected)
    (decoded : decodeResolution metadata payloads expected ref bytes ast = some projected) :
    projected.resolution.ref = ref ∧ projected.resolution.scope = expected.scope := by
  have represented := (decode_resolution_exact metadata payloads expected ref bytes ast projected).mp decoded
  have scope := resolved_scope_exact metadata expected ref projected.receipt
    ((resolve_exact metadata expected ref projected.receipt).mpr represented.1.metadata)
  exact ⟨represented.1.metadata.source, scope.1⟩

theorem projected_frame_agreement {α : Type} [DecidableEq α] (metadata : Context)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (projected : Projected)
    (decoded : decodeResolution metadata payloads expected ref bytes ast = some projected) :
    metadata.frame = expected ∧ payloads.frame = expected := by
  have represented := (decode_resolution_exact metadata payloads expected ref bytes ast projected).mp decoded
  exact ⟨represented.1.metadata.frame, represented.2.2.1⟩

theorem projection_without_source_refuses {α : Type} [DecidableEq α] (metadata : Context)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value)
    (refused : decodeSource metadata expected ref bytes ast = none) :
    decodeResolution metadata payloads expected ref bytes ast = none := by
  simp [decodeResolution, refused]

theorem projection_without_payload_refuses {α : Type} [DecidableEq α] (metadata : Context)
    (payloads : CandidateFiniteSourceCatalog.Capture α) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (receipt : Receipt)
    (source : decodeSource metadata expected ref bytes ast = some receipt)
    (refused : CandidateFiniteSourceCatalog.IntentPayload.decode payloads expected receipt.artifact.body.payload = none) :
    decodeResolution metadata payloads expected ref bytes ast = none := by
  simp [decodeResolution, source, refused]

#print axioms decode_resolution_exact
#print axioms projected_identity_and_scope
#print axioms projected_frame_agreement
#print axioms projection_without_source_refuses
#print axioms projection_without_payload_refuses
end RelationalSuccessor.CandidateCapturedMetadata
