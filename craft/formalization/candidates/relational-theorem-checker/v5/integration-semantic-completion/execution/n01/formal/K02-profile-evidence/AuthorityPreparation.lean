import AuthorityChecks
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileEvidence
open CandidateBindingCapture (Envelope)
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits)

def AuthorityHeaderMeaning (bootstrap : Profile) (frame : Frame) (root ref : RevisionRef) (authority : CapturedAuthority) : Prop :=
  authority.record.body.frame=frame ∧ authority.entry.ref=ref ∧ authority.record.body.token="profile-authority-snapshot" ∧
    authority.record.body.target.trustRoot=root ∧ authority.record.body.target.bootstrap=bootstrap
instance (bootstrap : Profile) (frame : Frame) (root ref : RevisionRef) (authority : CapturedAuthority) :
    Decidable (AuthorityHeaderMeaning bootstrap frame root ref authority) := by unfold AuthorityHeaderMeaning;infer_instance
def authorityCheck (bootstrap : Profile) (frame : Frame) (root ref : RevisionRef) (authority : CapturedAuthority) : Bool :=
  decide (AuthorityHeaderMeaning bootstrap frame root ref authority) && coherenceCheck authority.record.body.target
theorem authority_check_exact (bootstrap : Profile) (frame : Frame) (root ref : RevisionRef) (authority : CapturedAuthority) :
    authorityCheck bootstrap frame root ref authority=true ↔
      AuthorityHeaderMeaning bootstrap frame root ref authority ∧ CoherentAuthority authority.record.body.target := by
  simp only [authorityCheck,Bool.and_eq_true,decide_eq_true_eq,coherence_exact]

def AuthorityDataMeaning (bootstrap : Profile) (budget : Nat) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (authority : CapturedAuthority) : Prop :=
  CandidateDigestCapture.DigestPreparedMeaning bootstrap budget authorityVersion authorityKind authorityDecoder frame capture authority ∧
    AuthorityHeaderMeaning bootstrap frame root ref authority ∧ CoherentAuthority authority.record.body.target
def prepareAuthority (bootstrap : Profile) (budget : Nat) (frame : Frame) (root ref : RevisionRef) (capture : Envelope) : Option CapturedAuthority :=
  match CandidateDigestCapture.prepareDigestBytes bootstrap budget authorityVersion authorityKind authorityDecoder frame capture with
  | none=>none
  | some authority=>if authorityCheck bootstrap frame root ref authority then some authority else none

theorem authority_preparation_exact (bootstrap : Profile) (budget : Nat) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (authority : CapturedAuthority) :
    prepareAuthority bootstrap budget frame root ref capture=some authority ↔ AuthorityDataMeaning bootstrap budget frame root ref capture authority := by
  constructor
  · intro accepted
    unfold prepareAuthority at accepted
    cases checked : CandidateDigestCapture.prepareDigestBytes bootstrap budget authorityVersion authorityKind authorityDecoder frame capture with
    | none=>simp only [checked] at accepted;contradiction
    | some actual=>
      simp only [checked] at accepted
      split at accepted
      · rename_i guard
        cases accepted
        exact ⟨(CandidateDigestCapture.digest_capture_exact bootstrap budget authorityVersion authorityKind authorityDecoder frame capture authority).mp checked,
          (authority_check_exact bootstrap frame root ref authority).mp guard⟩
      · contradiction
  · rintro ⟨prepared,header,coherent⟩
    simp only [prepareAuthority,
      (CandidateDigestCapture.digest_capture_exact bootstrap budget authorityVersion authorityKind authorityDecoder frame capture authority).mpr prepared,
      (authority_check_exact bootstrap frame root ref authority).mpr ⟨header,coherent⟩,if_true]

structure EvidenceStage where
  profile : CandidateProfileSelection.Stage
  authority : CapturedAuthority
  deriving DecidableEq, Repr
structure PreparedEvidenceMeaning (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage) : Prop where
  profile : CandidateProfileSelection.SelectedDataMeaning bootstrap limits frame declarations selections stage.profile
  authority : AuthorityDataMeaning bootstrap limits.perCaptureBytes frame root ref capture stage.authority
  rows : EvidenceRowsMeaning frame stage.profile stage.authority

def prepareProfileEvidence (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) : Option EvidenceStage :=
  match CandidateProfileSelection.prepareSelectedProfile bootstrap limits frame declarations selections,
      prepareAuthority bootstrap limits.perCaptureBytes frame root ref capture with
  | some profile,some authority=>if evidenceRowsCheck frame profile authority then some ⟨profile,authority⟩ else none
  | _,_=>none

theorem profile_evidence_preparation_exact (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage) :
    prepareProfileEvidence bootstrap limits frame root ref capture declarations selections=some stage ↔
      PreparedEvidenceMeaning bootstrap limits frame root ref capture declarations selections stage := by
  constructor
  · intro accepted
    unfold prepareProfileEvidence at accepted
    cases p : CandidateProfileSelection.prepareSelectedProfile bootstrap limits frame declarations selections with
    | none=>simp only [p] at accepted;contradiction
    | some profile=>
      cases a : prepareAuthority bootstrap limits.perCaptureBytes frame root ref capture with
      | none=>simp only [p,a] at accepted;contradiction
      | some authority=>
        simp only [p,a] at accepted
        split at accepted
        · rename_i guard
          cases accepted
          exact ⟨(CandidateProfileSelection.selected_preparation_exact bootstrap limits frame declarations selections profile).mp p,
            (authority_preparation_exact bootstrap limits.perCaptureBytes frame root ref capture authority).mp a,
            (evidence_rows_exact frame profile authority).mp guard⟩
        · contradiction
  · intro meaning
    have p:=(CandidateProfileSelection.selected_preparation_exact bootstrap limits frame declarations selections stage.profile).mpr meaning.profile
    have a:=(authority_preparation_exact bootstrap limits.perCaptureBytes frame root ref capture stage.authority).mpr meaning.authority
    have r:=(evidence_rows_exact frame stage.profile stage.authority).mpr meaning.rows
    cases stage
    simp only [prepareProfileEvidence,p,a,r,if_true]

theorem profile_evidence_none_exact (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) :
    prepareProfileEvidence bootstrap limits frame root ref capture declarations selections=none ↔
      ¬∃stage,PreparedEvidenceMeaning bootstrap limits frame root ref capture declarations selections stage := by
  constructor
  · intro absent;rintro ⟨stage,meaning⟩
    have found:=(profile_evidence_preparation_exact bootstrap limits frame root ref capture declarations selections stage).mpr meaning
    rw [absent] at found;contradiction
  · intro absent
    cases found : prepareProfileEvidence bootstrap limits frame root ref capture declarations selections with
    | none=>rfl
    | some stage=>exact False.elim (absent ⟨stage,(profile_evidence_preparation_exact bootstrap limits frame root ref capture declarations selections stage).mp found⟩)

theorem prepared_evidence_retains_inputs (bootstrap : Profile) (limits : Limits) (frame : Frame) (root ref : RevisionRef)
    (capture : Envelope) (declarations selections : List Envelope) (stage : EvidenceStage)
    (meaning : PreparedEvidenceMeaning bootstrap limits frame root ref capture declarations selections stage) :
    stage.profile.declarations.map CandidateBindingCapture.Prepared.envelope=declarations ∧
      stage.profile.selections.map CandidateBindingCapture.Prepared.envelope=selections ∧ stage.authority.envelope=capture := by
  have retained:=CandidateProfileSelection.prepared_selection_retains_inputs bootstrap limits frame declarations selections stage.profile meaning.profile
  rcases meaning.authority.1.1 with ⟨ast,parsed,data⟩
  exact ⟨retained.1,retained.2,data.capture⟩
#print axioms authority_check_exact
#print axioms authority_preparation_exact
#print axioms profile_evidence_preparation_exact
#print axioms profile_evidence_none_exact
#print axioms prepared_evidence_retains_inputs
end RelationalSuccessor.CandidateProfileEvidence
