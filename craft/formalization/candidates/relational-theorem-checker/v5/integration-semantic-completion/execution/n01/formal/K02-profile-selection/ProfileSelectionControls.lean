import ProfileSelectionEvidence
import DigestCaptureControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateProfileSelection.Controls
def frame : Frame := CandidateBindingBytes.Controls.roleExpected.body.frame
def issuer : RevisionRef := ⟨⟨"fixture","principal","1"⟩,"uncomputed-fixture-principal"⟩
def declaration : Declaration := ⟨⟨declarationVersion,⟨"fixture","digest-profile","1"⟩,declarationKind,⟨"declare-profile",⟨"sha256-fips1804-2015","lowerhex64",issuer,.accepted,.clear,100⟩,frame⟩,issuer⟩,⟨[1],1,issuer,"uncomputed-typed-row-digest"⟩⟩
def selection : SelectionRecord := ⟨⟨selectionVersion,⟨"fixture","profile-selection","1"⟩,selectionKind,⟨"select-profile",⟨declaration.entry.ref,issuer,.accepted,.clear,100⟩,frame⟩,issuer⟩,⟨[2],1,issuer,"uncomputed-typed-row-digest"⟩⟩
theorem typed_data_positive : selectProfileRows frame [declaration] [selection]=some (declaredProfile declaration) := by decide
theorem typed_identical_duplicates : selectProfileRows frame [declaration,declaration] [selection,selection]=some (declaredProfile declaration) := by decide
theorem missing_selection : selectProfileRows frame [declaration] []=none := by decide
theorem missing_declaration : selectProfileRows frame [] [selection]=none := by decide
theorem declaration_review_missing : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with target:={declaration.record.body.target with review:=.missing}}}}] [selection]=none := by decide
theorem declaration_review_rejected : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with target:={declaration.record.body.target with review:=.rejected}}}}] [selection]=none := by decide
theorem declaration_revocation_unknown : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with target:={declaration.record.body.target with revocation:=.unknown}}}}] [selection]=none := by decide
theorem declaration_revocation_revoked : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with target:={declaration.record.body.target with revocation:=.revoked}}}}] [selection]=none := by decide
theorem declaration_expiry_42 : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with target:={declaration.record.body.target with expiry:=42}}}}] [selection]=none := by decide
theorem declaration_wrong_frame : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with frame:={frame with epoch:=43}}}}] [selection]=none := by decide
theorem declaration_wrong_token : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with token:="other"}}}] [selection]=none := by decide
theorem selection_review_missing : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with review:=.missing}}}}]=none := by decide
theorem selection_review_rejected : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with review:=.rejected}}}}]=none := by decide
theorem selection_revocation_unknown : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with revocation:=.unknown}}}}]=none := by decide
theorem selection_revocation_revoked : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with revocation:=.revoked}}}}]=none := by decide
theorem selection_expiry_42 : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with expiry:=42}}}}]=none := by decide
theorem selection_wrong_frame : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with frame:={frame with epoch:=43}}}}]=none := by decide
theorem selection_wrong_token : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with token:="other"}}}]=none := by decide
theorem unsupported_algorithm : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with target:={declaration.record.body.target with algorithm:="sha1"}}}}] [selection]=none := by decide
theorem unsupported_encoding : selectProfileRows frame [{declaration with record:={declaration.record with body:={declaration.record.body with target:={declaration.record.body.target with encoding:="upperhex64"}}}}] [selection]=none := by decide
theorem wrong_complete_declaration_ref : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with declaration:=issuer}}}}]=none := by decide
theorem selection_conflict_forward : selectProfileRows frame [declaration] [selection,{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with declaration:=issuer}}}}]=none := by decide
theorem selection_conflict_reverse : selectProfileRows frame [declaration] [{selection with record:={selection.record with body:={selection.record.body with target:={selection.record.body.target with declaration:=issuer}}}},selection]=none := by decide
theorem unused_declaration_key_conflict : selectProfileRows frame [declaration,{declaration with record:={declaration.record with ownerReview:={issuer with digest:="other"}}}] [selection]=none := by decide
#print axioms typed_data_positive
#print axioms typed_identical_duplicates
#print axioms missing_selection
#print axioms missing_declaration
#print axioms declaration_review_missing
#print axioms declaration_review_rejected
#print axioms declaration_revocation_unknown
#print axioms declaration_revocation_revoked
#print axioms declaration_expiry_42
#print axioms declaration_wrong_frame
#print axioms declaration_wrong_token
#print axioms selection_review_missing
#print axioms selection_review_rejected
#print axioms selection_revocation_unknown
#print axioms selection_revocation_revoked
#print axioms selection_expiry_42
#print axioms selection_wrong_frame
#print axioms selection_wrong_token
#print axioms unsupported_algorithm
#print axioms unsupported_encoding
#print axioms wrong_complete_declaration_ref
#print axioms selection_conflict_forward
#print axioms selection_conflict_reverse
#print axioms unused_declaration_key_conflict
end RelationalSuccessor.CandidateProfileSelection.Controls
