import AuthorityPreparation
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileEvidence
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateBindingCapture (Envelope)

-- A real provider must establish the admissibility/authenticity of the complete
-- original snapshot. No provider, default True predicate or approval Boolean.
structure RootPolicy where
  authoritativeSnapshot : RevisionRef → Frame → Envelope → Prop

def TrustedAuthorityMeaning (policy : RootPolicy) (bootstrap : Profile) (limits : Limits) (root ref : RevisionRef)
    (capture : Envelope) (authority : CapturedAuthority) (frame : Frame) : Prop :=
  AuthorityDataMeaning bootstrap limits.perCaptureBytes frame root ref capture authority ∧
    policy.authoritativeSnapshot root frame capture

def interpretedRequirements (policy : RootPolicy) (bootstrap : Profile) (limits : Limits) (root ref : RevisionRef)
    (capture : Envelope) (authority : CapturedAuthority) : CandidateProfileSelection.EvidenceRequirements where
  completeAuthenticSnapshot := fun frame declarations selections=>
    TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
      ∃ stage,CandidateProfileSelection.SelectedDataMeaning bootstrap limits frame declarations selections stage ∧
        ManifestMeaning authority.record.body.target stage
  authenticBootstrapSelection := fun frame profile=>
    TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧ authority.record.body.target.bootstrap=profile
  issuedDeclaration := fun frame row=>TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
    Issued authority.record.body.target row row.record.body.target.issuer
  issuedSelection := fun frame row=>TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
    Issued authority.record.body.target row row.record.body.target.issuer
  entitledToDeclare := fun frame principal=>TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
    Entitled authority.record.body.target frame principal "declare"
  entitledToSelect := fun frame principal=>TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
    Entitled authority.record.body.target frame principal "select"
  faithfulDeclarationReviewLifecycle := fun frame row=>TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
    Reviewed authority.record.body.target row row.record.body.target.review row.record.body.target.revocation row.record.body.target.expiry
  faithfulSelectionReviewLifecycle := fun frame row=>TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
    Reviewed authority.record.body.target row row.record.body.target.review row.record.body.target.revocation row.record.body.target.expiry

theorem interpreted_snapshot_requirement_exact (policy : RootPolicy) (bootstrap : Profile) (limits : Limits) (root ref : RevisionRef)
    (capture : Envelope) (authority : CapturedAuthority) (frame : Frame) (declarations selections : List Envelope) :
    (interpretedRequirements policy bootstrap limits root ref capture authority).completeAuthenticSnapshot frame declarations selections ↔
      TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
        ∃ stage,CandidateProfileSelection.SelectedDataMeaning bootstrap limits frame declarations selections stage ∧
          ManifestMeaning authority.record.body.target stage := Iff.rfl

theorem interpreted_issuance_requirement_exact (policy : RootPolicy) (bootstrap : Profile) (limits : Limits) (root ref : RevisionRef)
    (capture : Envelope) (authority : CapturedAuthority) (frame : Frame) (row : CandidateProfileSelection.Declaration) :
    (interpretedRequirements policy bootstrap limits root ref capture authority).issuedDeclaration frame row ↔
      TrustedAuthorityMeaning policy bootstrap limits root ref capture authority frame ∧
        Issued authority.record.body.target row row.record.body.target.issuer := Iff.rfl

theorem prepared_evidence_and_authentic_boundary_construct_ownership (policy : RootPolicy) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (root ref : RevisionRef) (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage)
    (prepared : PreparedEvidenceMeaning bootstrap limits frame root ref capture declarations selections stage)
    (authentic : policy.authoritativeSnapshot root frame capture) :
    CandidateProfileSelection.OwnedSelectionMeaning
      (interpretedRequirements policy bootstrap limits root ref capture stage.authority)
      bootstrap limits frame declarations selections stage.profile := by
  have trusted : TrustedAuthorityMeaning policy bootstrap limits root ref capture stage.authority frame := ⟨prepared.authority,authentic⟩
  refine ⟨prepared.profile,⟨trusted,stage.profile,prepared.profile,prepared.rows.2.2.1⟩,
    ⟨trusted,prepared.authority.2.1.2.2.2.2⟩,?_,?_⟩
  · intro row member
    have evidence:=prepared.rows.2.2.2.1 row member
    exact ⟨⟨trusted,evidence.1⟩,⟨trusted,evidence.2.1⟩,⟨trusted,evidence.2.2⟩⟩
  · intro row member
    have evidence:=prepared.rows.2.2.2.2 row member
    exact ⟨⟨trusted,evidence.1⟩,⟨trusted,evidence.2.1⟩,⟨trusted,evidence.2.2⟩⟩

theorem ownership_requires_actual_snapshot_boundary (policy : RootPolicy) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (root ref : RevisionRef) (capture : Envelope) (authority : CapturedAuthority)
    (declarations selections : List Envelope) (stage : CandidateProfileSelection.Stage)
    (owned : CandidateProfileSelection.OwnedSelectionMeaning
      (interpretedRequirements policy bootstrap limits root ref capture authority) bootstrap limits frame declarations selections stage) :
    policy.authoritativeSnapshot root frame capture := owned.snapshot.1.2

theorem absent_boundary_blocks_owned_profile (policy : RootPolicy) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (root ref : RevisionRef) (capture : Envelope) (authority : CapturedAuthority)
    (declarations selections : List Envelope) (profile : RevisionRef)
    (absent : ¬policy.authoritativeSnapshot root frame capture) :
    ¬CandidateProfileSelection.OwnedProfileMeaning
      (interpretedRequirements policy bootstrap limits root ref capture authority) bootstrap limits declarations selections frame profile := by
  rintro ⟨stage,owned,_⟩
  exact absent (ownership_requires_actual_snapshot_boundary policy bootstrap limits frame root ref capture authority declarations selections stage owned)

theorem owned_evidence_still_requires_checked_sources (policy : RootPolicy) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (root ref : RevisionRef) (capture : Envelope) (authority : CapturedAuthority)
    (declarations selections : List Envelope) (stage : CandidateProfileSelection.Stage)
    (owned : CandidateProfileSelection.OwnedSelectionMeaning
      (interpretedRequirements policy bootstrap limits root ref capture authority) bootstrap limits frame declarations selections stage) :
    CandidateProfileSelection.prepareSelectedProfile bootstrap limits frame declarations selections=some stage :=
  CandidateProfileSelection.owned_selection_implies_preparation _ bootstrap limits frame declarations selections stage owned

theorem complete_capture_from_interpreted_evidence {α : Type} (policy : RootPolicy) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (root ref : RevisionRef) (authorityCapture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage)
    (prepared : PreparedEvidenceMeaning bootstrap limits frame root ref authorityCapture declarations selections stage)
    (authentic : policy.authoritativeSnapshot root frame authorityCapture)
    (policies : CandidateBindingCapture.Policies α) (budget : Nat) (version kind : String) (target : CandidateBindingAst.Decoder α)
    (capture : Envelope) (row : CandidateBindingCapture.Prepared α)
    (data : CandidateDigestCapture.DigestPreparedMeaning stage.profile.profile budget version kind target frame capture row)
    (schema : ∀ ast,CandidateScalarConversion.ScalarByteDocumentMeaning capture.content ast → policies.schema frame version kind ast)
    (reviewed : policies.reviewed frame row.entry) :
    ∃ ast,CandidateBindingCapture.CaptureMeaning
      (CandidateDigestCapture.withDigestPolicy stage.profile.profile
        (CandidateProfileSelection.withSelectedOwnership
          (interpretedRequirements policy bootstrap limits root ref authorityCapture stage.authority)
          bootstrap limits declarations selections policies)) version kind target frame capture ast row :=
  CandidateProfileSelection.complete_capture_from_owned_selection _ bootstrap limits frame declarations selections stage.profile
    (prepared_evidence_and_authentic_boundary_construct_ownership policy bootstrap limits frame root ref authorityCapture declarations selections stage prepared authentic)
    policies budget version kind target capture row data schema reviewed
#print axioms interpreted_snapshot_requirement_exact
#print axioms interpreted_issuance_requirement_exact
#print axioms prepared_evidence_and_authentic_boundary_construct_ownership
#print axioms ownership_requires_actual_snapshot_boundary
#print axioms absent_boundary_blocks_owned_profile
#print axioms owned_evidence_still_requires_checked_sources
#print axioms complete_capture_from_interpreted_evidence
end RelationalSuccessor.CandidateProfileEvidence
