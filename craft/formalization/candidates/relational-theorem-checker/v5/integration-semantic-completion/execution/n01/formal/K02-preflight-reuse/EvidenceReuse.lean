import TypedReuse
set_option autoImplicit false
namespace RelationalSuccessor.CandidatePreflightReuse
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)
open CandidateEvidenceResources (NumericLimits DataOutcome)
open CandidateProfileSelection (declarationVersion declarationKind settingsDecoder selectionVersion selectionKind selectionDecoder)

def prepareProfile (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame)
    (declarations selections : List (CertifiedInput bootstrap limits.perCaptureBytes numbers)) : Option CandidateProfileSelection.Stage :=
  if decide (CandidateDigest.ProfileMeaning bootstrap bootstrap.ref) then
    if CandidateDigestCapture.catalogBudgetCheck limits (declarations.map fun input=>input.val.capture) (selections.map fun input=>input.val.capture) then
      match prepareMany declarationVersion declarationKind settingsDecoder frame declarations,
          prepareMany selectionVersion selectionKind selectionDecoder frame selections with
      | some declarationRows,some selectionRows=>
        (CandidateProfileSelection.selectProfileRows frame declarationRows selectionRows).map fun profile=>⟨frame,bootstrap,declarationRows,selectionRows,profile⟩
      | _,_=>none
    else none
  else none

theorem reused_profile_equal_legacy (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame)
    (declarations selections : List (CertifiedInput bootstrap limits.perCaptureBytes numbers)) :
    prepareProfile bootstrap limits numbers frame declarations selections=
      CandidateProfileSelection.prepareSelectedProfile bootstrap limits frame
        (declarations.map fun input=>input.val.capture) (selections.map fun input=>input.val.capture) := by
  simp only [prepareProfile,CandidateProfileSelection.prepareSelectedProfile,cached_many_equal_legacy]
  rfl

def prepareAuthority (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (input : CertifiedInput bootstrap limits.perCaptureBytes numbers) : Option CandidateProfileEvidence.CapturedAuthority :=
  match prepareInput CandidateProfileEvidence.authorityVersion CandidateProfileEvidence.authorityKind CandidateProfileEvidence.authorityDecoder frame input with
  | none=>none
  | some authority=>if CandidateProfileEvidence.authorityCheck bootstrap frame root ref authority then some authority else none

theorem reused_authority_equal_legacy (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (input : CertifiedInput bootstrap limits.perCaptureBytes numbers) :
    prepareAuthority bootstrap limits numbers frame root ref input=
      CandidateProfileEvidence.prepareAuthority bootstrap limits.perCaptureBytes frame root ref input.val.capture := by
  simp only [prepareAuthority,CandidateProfileEvidence.prepareAuthority,cached_preparation_equal_legacy]
  rfl

def classifyData (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (authority : CertifiedInput bootstrap limits.perCaptureBytes numbers)
    (declarations selections : List (CertifiedInput bootstrap limits.perCaptureBytes numbers)) : DataOutcome :=
  match prepareProfile bootstrap limits numbers frame declarations selections with
  | none=>.profileDataRefused
  | some profile=>match prepareAuthority bootstrap limits numbers frame root ref authority with
    | none=>.authorityDataRefused
    | some authority=>if CandidateProfileEvidence.evidenceRowsCheck frame profile authority then .prepared ⟨profile,authority⟩ else .evidenceJoinRefused

theorem reused_data_equal_legacy (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (authority : CertifiedInput bootstrap limits.perCaptureBytes numbers)
    (declarations selections : List (CertifiedInput bootstrap limits.perCaptureBytes numbers)) :
    classifyData bootstrap limits numbers frame root ref authority declarations selections=
      CandidateEvidenceResources.classifyData bootstrap limits frame root ref authority.val.capture
        (declarations.map fun input=>input.val.capture) (selections.map fun input=>input.val.capture) := by
  simp only [classifyData,CandidateEvidenceResources.classifyData,reused_profile_equal_legacy,reused_authority_equal_legacy]
  rfl

theorem reused_data_exact (bootstrap : Profile) (limits : Limits) (numbers : NumericLimits) (frame : Frame) (root ref : RevisionRef)
    (authority : CertifiedInput bootstrap limits.perCaptureBytes numbers)
    (declarations selections : List (CertifiedInput bootstrap limits.perCaptureBytes numbers)) (outcome : DataOutcome) :
    classifyData bootstrap limits numbers frame root ref authority declarations selections=outcome ↔
      CandidateEvidenceResources.DataOutcomeMeaning bootstrap limits frame root ref authority.val.capture
        (declarations.map fun input=>input.val.capture) (selections.map fun input=>input.val.capture) outcome := by
  rw [reused_data_equal_legacy]
  exact CandidateEvidenceResources.data_outcome_meaning_exact bootstrap limits frame root ref _ _ _ outcome
#print axioms reused_profile_equal_legacy
#print axioms reused_authority_equal_legacy
#print axioms reused_data_equal_legacy
#print axioms reused_data_exact
end RelationalSuccessor.CandidatePreflightReuse
