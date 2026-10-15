import CapturedMetadata
import JsonRecord

set_option autoImplicit false

namespace RelationalSuccessor.CandidateCapturedMetadata
open RelationalSuccessor

-- AST/body agreement and original-byte equality do not prove that these bytes
-- parsed to this AST. That correlation and authentic context are provider
-- obligations; neither is encoded as a caller-controlled approval flag.
structure SourceMeaning (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (receipt : Receipt) : Prop where
  metadata : ResolvedMeaning context expected ref receipt
  bytes : receipt.artifact.content = bytes
  ast : CandidateJsonSource.SchemaAstMeaning ast receipt.artifact.body

def decodeSource (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) : Option Receipt :=
  match resolve context expected ref, CandidateJsonSource.decodeRecord ast with
  | some receipt, some body =>
      if receipt.artifact.content = bytes ∧ receipt.artifact.body = body then some receipt else none
  | _, _ => none

theorem decode_source_exact (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (receipt : Receipt) :
    decodeSource context expected ref bytes ast = some receipt ↔
      SourceMeaning context expected ref bytes ast receipt := by
  constructor
  · intro decoded
    cases found : resolve context expected ref with
    | none => simp [decodeSource, found] at decoded
    | some actual =>
      cases parsed : CandidateJsonSource.decodeRecord ast with
      | none => simp [decodeSource, found, parsed] at decoded
      | some body =>
        simp only [decodeSource, found, parsed] at decoded
        split at decoded
        · rename_i checked
          cases decoded
          refine ⟨(resolve_exact context expected ref actual).mp found, checked.1, ?_⟩
          simpa only [checked.2] using (CandidateJsonSource.decode_record_exact ast body).mp parsed
        · cases decoded
  · intro represented
    have found := (resolve_exact context expected ref receipt).mpr represented.metadata
    have parsed := (CandidateJsonSource.decode_record_exact ast receipt.artifact.body).mpr represented.ast
    simp [decodeSource, found, parsed, represented.bytes]

theorem source_preserves_full_body (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (receipt : Receipt)
    (decoded : decodeSource context expected ref bytes ast = some receipt) :
    CandidateJsonSource.decodeRecord ast = some receipt.artifact.body :=
  (CandidateJsonSource.decode_record_exact ast receipt.artifact.body).mpr
    ((decode_source_exact context expected ref bytes ast receipt).mp decoded).ast

theorem source_requires_original_bytes (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (receipt : Receipt)
    (decoded : decodeSource context expected ref bytes ast = some receipt) :
    receipt.artifact.content = bytes :=
  ((decode_source_exact context expected ref bytes ast receipt).mp decoded).bytes

theorem source_requires_owner_binding (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (receipt : Receipt)
    (decoded : decodeSource context expected ref bytes ast = some receipt) :
    receipt.owner ∈ context.owners ∧ receipt.owner.token = receipt.artifact.body.owner_ref ∧
      receipt.scope.ownerBinding = receipt.owner.ref := by
  have meaning := ((decode_source_exact context expected ref bytes ast receipt).mp decoded).metadata.receiptMeaning
  exact ⟨meaning.ownerOwned, meaning.ownerToken, meaning.ownerJoin⟩

theorem source_ref_exact (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value) (receipt : Receipt)
    (decoded : decodeSource context expected ref bytes ast = some receipt) : receipt.artifact.ref = ref :=
  ((decode_source_exact context expected ref bytes ast receipt).mp decoded).metadata.source

theorem source_without_metadata_refuses (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value)
    (missing : resolve context expected ref = none) : decodeSource context expected ref bytes ast = none := by
  simp [decodeSource, missing]

theorem malformed_source_refuses (context : Context) (expected : Frame) (ref : RevisionRef)
    (bytes : List UInt8) (ast : CandidateJsonSource.Value)
    (malformed : CandidateJsonSource.decodeRecord ast = none) : decodeSource context expected ref bytes ast = none := by
  simp only [decodeSource, malformed]
  cases resolve context expected ref <;> rfl

#print axioms decode_source_exact
#print axioms source_preserves_full_body
#print axioms source_requires_original_bytes
#print axioms source_requires_owner_binding
#print axioms source_ref_exact
#print axioms source_without_metadata_refuses
#print axioms malformed_source_refuses
end RelationalSuccessor.CandidateCapturedMetadata
