import MetadataControls1
import JsonEncoding

set_option autoImplicit false
namespace RelationalSuccessor.CandidateCapturedMetadata.MoreControls
open RelationalSuccessor
open RelationalSuccessor.CandidateCapturedMetadata
open RelationalSuccessor.CandidateCapturedMetadata.Examples

theorem wrong_expected_profile :
    resolve context { frame with profile := revision "wrong-profile" } sourceRef = none := by
  apply wrong_frame_refuses
  decide

theorem wrong_expected_subject :
    resolve context { frame with subject := revision "wrong-subject" } sourceRef = none := by
  apply wrong_frame_refuses
  decide

theorem wrong_expected_target :
    resolve context { frame with target := revision "wrong-target" } sourceRef = none := by
  apply wrong_frame_refuses
  decide

theorem wrong_expected_context :
    resolve context { frame with context := revision "wrong-context" } sourceRef = none := by
  apply wrong_frame_refuses
  decide

theorem wrong_expected_scope :
    resolve context { frame with scope := revision "wrong-scope" } sourceRef = none := by
  apply wrong_frame_refuses
  decide

theorem wrong_expected_snapshot :
    resolve context { frame with snapshot := revision "wrong-snapshot" } sourceRef = none := by
  apply wrong_frame_refuses
  decide

theorem wrong_expected_epoch :
    resolve context { frame with epoch := 43 } sourceRef = none := by
  apply wrong_frame_refuses
  decide

theorem wrong_expected_timeDomain :
    resolve context { frame with timeDomain := "wrong-time-domain" } sourceRef = none := by
  apply wrong_frame_refuses
  decide

def wrongDigest : RevisionRef := { sourceRef with digest := "wrong-digest" }
theorem wrong_requested_digest_refuses : resolve context frame wrongDigest = none := by
  apply absent_ref_refuses
  intro r member
  have same : r = receipt := by simpa [context] using member
  rw [same]
  decide

def emptyContext : Context :=
  { context with records := [], roots := [], identities := [], owners := [], scopes := [] }
theorem empty_context_cannot_seed : resolve emptyContext frame sourceRef = none := by
  apply absent_ref_refuses
  simp [emptyContext]

theorem changed_bytes_refuse : decodeSource context frame sourceRef [0] ast = none := by
  apply different_bytes_refuse context frame sourceRef [0] ast receipt fixture_metadata_resolves
  intro equal
  have headEqual := congrArg (fun xs : List UInt8 => xs.head?) equal
  have different : receipt.artifact.content.head? ≠ ([0] : List UInt8).head? := by decide
  exact different headEqual

def renamedOwnerBody : RawRecord := { raw with owner_ref := "owner:unbound-replacement" }
theorem renamed_owner_shape : CandidateIntentRecordShape.RecordShape renamedOwnerBody := by
  have checked : CandidateIntentRecordShape.checkCarrier renamedOwnerBody = some renamedOwnerBody := by decide
  exact ((CandidateIntentRecordShape.check_carrier_exact renamedOwnerBody renamedOwnerBody).mp checked).1

theorem shape_valid_body_substitution_refuses :
    decodeSource context frame sourceRef originalBytes
      (CandidateJsonSource.encodeRecord renamedOwnerBody) = none := by
  apply different_body_refuses context frame sourceRef originalBytes
    (CandidateJsonSource.encodeRecord renamedOwnerBody) receipt renamedOwnerBody fixture_metadata_resolves
    (CandidateJsonSource.decode_schema_record_encoding renamedOwnerBody renamed_owner_shape)
  intro equal
  have names := congrArg (fun body : RawRecord => body.owner_ref) equal
  have different : receipt.artifact.body.owner_ref ≠ renamedOwnerBody.owner_ref := by decide
  exact different names

theorem malformed_AST_projection_refuses :
    decodeResolution context payloads frame sourceRef originalBytes (.null) = none := by
  apply projection_without_source_refuses
  apply malformed_source_refuses
  rfl

theorem missing_root_projection_refuses :
    decodeResolution Controls.missing_root payloads frame sourceRef originalBytes ast = none := by
  apply projection_without_source_refuses
  exact source_without_metadata_refuses _ _ _ _ _ Controls.missing_root_refuses

def conflictingReceipt : Receipt :=
  { receipt with owner := { owner with holder := revision "another-holder" } }
def receiptConflict : Context :=
  { context with roots := [receipt, conflictingReceipt] }
theorem conflicting_owner_receipts_refuse : resolve receiptConflict frame sourceRef = none := by
  apply invalid_context_refuses
  intro valid
  have same := valid.receipts receipt (by simp [allReceipts, receiptConflict, context])
    conflictingReceipt (by simp [allReceipts, receiptConflict, context]) (by rfl)
  have holders := congrArg (fun r : Receipt => r.owner.holder) same
  have different : receipt.owner.holder ≠ conflictingReceipt.owner.holder := by decide
  exact different holders

def byteConflictReceipt : Receipt :=
  { receipt with artifact := { artifact with content := [0] } }
def byteConflict : Context := { context with roots := [receipt, byteConflictReceipt] }
theorem conflicting_captured_bytes_refuse : resolve byteConflict frame sourceRef = none := by
  apply invalid_context_refuses
  intro valid
  have same := valid.artifacts receipt.artifact (by simp [allArtifacts, allReceipts, byteConflict, context])
    byteConflictReceipt.artifact (by simp [allArtifacts, allReceipts, byteConflict, context]) (by rfl)
  have heads := congrArg (fun a : Artifact RawRecord => a.content.head?) same
  have different : receipt.artifact.content.head? ≠ byteConflictReceipt.artifact.content.head? := by decide
  exact different heads

theorem projected_reference_and_scope :
    (⟨receipt, payload⟩ : Projected).resolution.ref = sourceRef ∧
    (⟨receipt, payload⟩ : Projected).resolution.scope = frame.scope :=
  projected_identity_and_scope context payloads frame sourceRef originalBytes ast
    ⟨receipt, payload⟩ complete_structural_projection

#print axioms wrong_expected_profile
#print axioms wrong_expected_subject
#print axioms wrong_expected_target
#print axioms wrong_expected_context
#print axioms wrong_expected_scope
#print axioms wrong_expected_snapshot
#print axioms wrong_expected_epoch
#print axioms wrong_expected_timeDomain
#print axioms wrong_requested_digest_refuses
#print axioms empty_context_cannot_seed
#print axioms changed_bytes_refuse
#print axioms renamed_owner_shape
#print axioms shape_valid_body_substitution_refuses
#print axioms malformed_AST_projection_refuses
#print axioms missing_root_projection_refuses
#print axioms conflicting_owner_receipts_refuse
#print axioms conflicting_captured_bytes_refuse
#print axioms projected_reference_and_scope
end RelationalSuccessor.CandidateCapturedMetadata.MoreControls
