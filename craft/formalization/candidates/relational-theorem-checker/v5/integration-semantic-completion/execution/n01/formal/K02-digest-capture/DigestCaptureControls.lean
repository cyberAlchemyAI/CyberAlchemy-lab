import DigestCaptureCatalog
import ByteCaptureControls
import DigestControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateDigestCapture.Controls
open CandidateBindingBytes.Controls (resolutionBytes resolutionExpected roleBytes roleExpected)
def profile : CandidateDigest.Profile := ⟨resolutionExpected.ownerReview,"sha256-fips1804-2015","lowerhex64"⟩
def resolutionCapture : CandidateBindingCapture.Envelope := ⟨resolutionBytes,2621,profile.ref,"5988b60362dec1e9d97d491ad48c72a9219924803fc4332f17446274b7a00698"⟩
def resolutionFrame : Frame := resolutionExpected.body.frame
def roleCapture : CandidateBindingCapture.Envelope := ⟨roleBytes,1848,profile.ref,"f2d77cf9d080a540b6e19199e174d644cec0556887b5971b07d79890f9c1cd43"⟩
def roleFrame : Frame := roleExpected.body.frame
theorem resolution_wrong_count_refused : classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with byteLength:=2622}=.invalidEnvelope := by
  apply (checked_invalid_envelope_exact profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with byteLength:=2622}).mpr
  rw [←CandidateBindingCapture.envelope_check_exact]
  decide
theorem resolution_wrong_profile_refused : classifyCheckedCapture profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with digestProfile:={profile.ref with digest:="other"}}=.digestRefused .unsupportedProfile := by
  apply (checked_profile_refusal_exact profile 2621 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame {resolutionCapture with digestProfile:={profile.ref with digest:="other"}}).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact _).mp (by decide),by decide⟩
theorem resolution_budget_refused : classifyCheckedCapture profile 2620 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame resolutionCapture=.digestRefused .byteBudgetExceeded := by
  apply (checked_budget_refusal_exact profile 2620 CandidateBindingRecords.resolutionVersion CandidateBindingRecords.resolutionKind CandidateBindingAst.resolution resolutionFrame resolutionCapture).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact _).mp (by decide),by decide,by decide,by decide⟩
theorem resolution_aggregate_budget_refused : prepareResolutionCatalogDigest profile ⟨2621,5241,2⟩ resolutionFrame [resolutionCapture] [resolutionCapture]=none := by decide
theorem resolution_count_budget_refused : prepareResolutionCatalogDigest profile ⟨2621,5242,1⟩ resolutionFrame [resolutionCapture] [resolutionCapture]=none := by decide
theorem role_wrong_count_refused : classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with byteLength:=1849}=.invalidEnvelope := by
  apply (checked_invalid_envelope_exact profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with byteLength:=1849}).mpr
  rw [←CandidateBindingCapture.envelope_check_exact]
  decide
theorem role_wrong_profile_refused : classifyCheckedCapture profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with digestProfile:={profile.ref with digest:="other"}}=.digestRefused .unsupportedProfile := by
  apply (checked_profile_refusal_exact profile 1848 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame {roleCapture with digestProfile:={profile.ref with digest:="other"}}).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact _).mp (by decide),by decide⟩
theorem role_budget_refused : classifyCheckedCapture profile 1847 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame roleCapture=.digestRefused .byteBudgetExceeded := by
  apply (checked_budget_refusal_exact profile 1847 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind CandidateBindingAst.role roleFrame roleCapture).mpr
  exact ⟨(CandidateBindingCapture.envelope_check_exact _).mp (by decide),by decide,by decide,by decide⟩
theorem role_aggregate_budget_refused : prepareRoleCatalogDigest profile ⟨1848,3695,2⟩ roleFrame [roleCapture] [roleCapture]=none := by decide
theorem role_count_budget_refused : prepareRoleCatalogDigest profile ⟨1848,3696,1⟩ roleFrame [roleCapture] [roleCapture]=none := by decide
theorem unsupported_empty_catalog_refused : prepareRoleCatalogDigest {profile with algorithm:="sha1"} ⟨0,0,0⟩ roleFrame [] []=none := by decide
def emptyCapture : CandidateBindingCapture.Envelope := ⟨[],0,profile.ref,CandidateDigest.Controls.emptyDigest⟩
theorem valid_digest_does_not_make_empty_bytes_a_record :
    classifyCheckedCapture profile 0 CandidateBindingRecords.roleVersion CandidateBindingRecords.roleKind
      CandidateBindingAst.role roleFrame emptyCapture=.byteStage (.recordRefused .invalidSyntax) := by
  apply (checked_syntax_exact profile 0 _ _ _ roleFrame emptyCapture).mpr
  refine ⟨(CandidateBindingCapture.envelope_check_exact emptyCapture).mp (by decide),?_,?_⟩
  · exact ⟨by decide,by decide,by decide,CandidateDigest.Controls.empty_vector_meaning⟩
  · exact (CandidateJsonCompleteness.byte_document_none_iff_no_meaning []).mp rfl
#print axioms resolution_wrong_count_refused
#print axioms resolution_wrong_profile_refused
#print axioms resolution_budget_refused
#print axioms resolution_aggregate_budget_refused
#print axioms resolution_count_budget_refused
#print axioms role_wrong_count_refused
#print axioms role_wrong_profile_refused
#print axioms role_budget_refused
#print axioms role_aggregate_budget_refused
#print axioms role_count_budget_refused
#print axioms unsupported_empty_catalog_refused
#print axioms valid_digest_does_not_make_empty_bytes_a_record
end RelationalSuccessor.CandidateDigestCapture.Controls
