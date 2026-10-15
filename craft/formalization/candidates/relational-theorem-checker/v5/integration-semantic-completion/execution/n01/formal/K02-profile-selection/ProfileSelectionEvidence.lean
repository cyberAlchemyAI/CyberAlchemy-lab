import ProfileSelectionPreparation
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileSelection
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateBindingCapture (Envelope Policies)

-- Independent external evidence requirements: no booleans, default providers or
-- assertions that membership/labels establish authentic principal ownership.
structure EvidenceRequirements where
  completeAuthenticSnapshot : Frame → List Envelope → List Envelope → Prop
  authenticBootstrapSelection : Frame → Profile → Prop
  issuedDeclaration : Frame → Declaration → Prop
  issuedSelection : Frame → SelectionRecord → Prop
  entitledToDeclare : Frame → RevisionRef → Prop
  entitledToSelect : Frame → RevisionRef → Prop
  faithfulDeclarationReviewLifecycle : Frame → Declaration → Prop
  faithfulSelectionReviewLifecycle : Frame → SelectionRecord → Prop

structure OwnedSelectionMeaning (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (declarations selections : List Envelope) (stage : Stage) : Prop where
  data : SelectedDataMeaning bootstrap limits frame declarations selections stage
  snapshot : requirements.completeAuthenticSnapshot frame declarations selections
  bootstrap : requirements.authenticBootstrapSelection frame bootstrap
  declarations : ∀ row∈stage.declarations,
    requirements.issuedDeclaration frame row ∧ requirements.entitledToDeclare frame row.record.body.target.issuer ∧
      requirements.faithfulDeclarationReviewLifecycle frame row
  selections : ∀ row∈stage.selections,
    requirements.issuedSelection frame row ∧ requirements.entitledToSelect frame row.record.body.target.issuer ∧
      requirements.faithfulSelectionReviewLifecycle frame row

def OwnedProfileMeaning (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (declarations selections : List Envelope) (frame : Frame) (ref : RevisionRef) : Prop :=
  ∃ stage, OwnedSelectionMeaning requirements bootstrap limits frame declarations selections stage ∧ stage.profile.ref=ref

def withSelectedOwnership {α : Type} (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (declarations selections : List Envelope) (policies : Policies α) : Policies α :=
  {policies with ownedDigestProfile:=OwnedProfileMeaning requirements bootstrap limits declarations selections}

theorem installed_ownership_policy {α : Type} (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (declarations selections : List Envelope) (policies : Policies α) (frame : Frame) (ref : RevisionRef) :
    (withSelectedOwnership requirements bootstrap limits declarations selections policies).ownedDigestProfile frame ref ↔
      OwnedProfileMeaning requirements bootstrap limits declarations selections frame ref := Iff.rfl

theorem other_capture_policies_unchanged {α : Type} (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (declarations selections : List Envelope) (policies : Policies α) :
    (withSelectedOwnership requirements bootstrap limits declarations selections policies).parses=policies.parses ∧
    (withSelectedOwnership requirements bootstrap limits declarations selections policies).digest=policies.digest ∧
    (withSelectedOwnership requirements bootstrap limits declarations selections policies).schema=policies.schema ∧
    (withSelectedOwnership requirements bootstrap limits declarations selections policies).reviewed=policies.reviewed := ⟨rfl,rfl,rfl,rfl⟩

theorem owned_selection_implies_preparation (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (declarations selections : List Envelope) (stage : Stage)
    (meaning : OwnedSelectionMeaning requirements bootstrap limits frame declarations selections stage) :
    prepareSelectedProfile bootstrap limits frame declarations selections=some stage :=
  (selected_preparation_exact bootstrap limits frame declarations selections stage).mpr meaning.data

theorem owned_selection_profile_unique (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (declarations selections : List Envelope) (a b : RevisionRef)
    (ha : OwnedProfileMeaning requirements bootstrap limits declarations selections frame a)
    (hb : OwnedProfileMeaning requirements bootstrap limits declarations selections frame b) : a=b := by
  rcases ha with ⟨sa,ma,ea⟩
  rcases hb with ⟨sb,mb,eb⟩
  have same:=prepared_profile_unique bootstrap limits frame declarations selections sa sb ma.data mb.data
  subst sb;exact ea.symm.trans eb

theorem absent_authentic_snapshot_blocks_ownership (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (declarations selections : List Envelope) (ref : RevisionRef)
    (absent : ¬requirements.completeAuthenticSnapshot frame declarations selections) :
    ¬OwnedProfileMeaning requirements bootstrap limits declarations selections frame ref := by
  rintro ⟨stage,meaning,_⟩;exact absent meaning.snapshot

theorem absent_bootstrap_ownership_blocks_ownership (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (declarations selections : List Envelope) (ref : RevisionRef)
    (absent : ¬requirements.authenticBootstrapSelection frame bootstrap) :
    ¬OwnedProfileMeaning requirements bootstrap limits declarations selections frame ref := by
  rintro ⟨stage,meaning,_⟩;exact absent meaning.bootstrap

theorem owned_selected_participant_evidence (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (declarations selections : List Envelope) (stage : Stage)
    (meaning : OwnedSelectionMeaning requirements bootstrap limits frame declarations selections stage) :
    ∃ choice∈stage.selections,∃ declaration∈stage.declarations,
      stage.profile.ref=declaration.entry.ref ∧ choice.record.body.target.declaration=stage.profile.ref ∧
      requirements.issuedDeclaration frame declaration ∧ requirements.entitledToDeclare frame declaration.record.body.target.issuer ∧
      requirements.faithfulDeclarationReviewLifecycle frame declaration ∧ requirements.issuedSelection frame choice ∧
      requirements.entitledToSelect frame choice.record.body.target.issuer ∧ requirements.faithfulSelectionReviewLifecycle frame choice := by
  rcases selected_source_witnesses frame stage.declarations stage.selections stage.profile meaning.data.selected with
    ⟨choice,cm,declaration,dm,refEq,selectedRef,_,_⟩
  have de:=meaning.declarations declaration dm
  have se:=meaning.selections choice cm
  exact ⟨choice,cm,declaration,dm,refEq,selectedRef,de.1,de.2.1,de.2.2,se.1,se.2.1,se.2.2⟩

theorem complete_capture_from_owned_selection {α : Type} (requirements : EvidenceRequirements) (bootstrap : Profile) (limits : Limits)
    (frame : Frame) (declarations selections : List Envelope) (stage : Stage)
    (owned : OwnedSelectionMeaning requirements bootstrap limits frame declarations selections stage)
    (policies : Policies α) (budget : Nat) (version kind : String) (target : CandidateBindingAst.Decoder α)
    (capture : Envelope) (prepared : CandidateBindingCapture.Prepared α)
    (data : CandidateDigestCapture.DigestPreparedMeaning stage.profile budget version kind target frame capture prepared)
    (schema : ∀ ast,CandidateScalarConversion.ScalarByteDocumentMeaning capture.content ast → policies.schema frame version kind ast)
    (reviewed : policies.reviewed frame prepared.entry) :
    ∃ ast,CandidateBindingCapture.CaptureMeaning
      (CandidateDigestCapture.withDigestPolicy stage.profile
        (withSelectedOwnership requirements bootstrap limits declarations selections policies)) version kind target frame capture ast prepared := by
  apply CandidateDigestCapture.checked_capture_construction stage.profile
    (withSelectedOwnership requirements bootstrap limits declarations selections policies) budget version kind target frame capture prepared data
  · exact ⟨stage,owned,data.2.1.1⟩
  · exact schema
  · exact reviewed
#print axioms installed_ownership_policy
#print axioms other_capture_policies_unchanged
#print axioms owned_selection_implies_preparation
#print axioms owned_selection_profile_unique
#print axioms absent_authentic_snapshot_blocks_ownership
#print axioms absent_bootstrap_ownership_blocks_ownership
#print axioms owned_selected_participant_evidence
#print axioms complete_capture_from_owned_selection
end RelationalSuccessor.CandidateProfileSelection
