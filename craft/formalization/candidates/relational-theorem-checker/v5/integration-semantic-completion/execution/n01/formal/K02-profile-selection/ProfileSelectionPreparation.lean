import ProfileSelectionData
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileSelection
open CandidateDigest (Profile)
open CandidateDigestCapture (Limits DigestManyMeaning prepareManyDigest digest_many_exact)
open CandidateBindingCapture (Envelope)

structure Stage where
  frame : Frame
  bootstrap : Profile
  declarations : List Declaration
  selections : List SelectionRecord
  profile : Profile
  deriving DecidableEq, Repr

structure SelectedDataMeaning (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) (stage : Stage) : Prop where
  bootstrapSupported : CandidateDigest.ProfileMeaning bootstrap bootstrap.ref
  budget : CandidateDigestCapture.CatalogBudgetMeaning limits declarations selections
  declarationSources : DigestManyMeaning bootstrap limits.perCaptureBytes declarationVersion declarationKind settingsDecoder frame declarations stage.declarations
  selectionSources : DigestManyMeaning bootstrap limits.perCaptureBytes selectionVersion selectionKind selectionDecoder frame selections stage.selections
  selected : SelectedRowsMeaning frame stage.declarations stage.selections stage.profile
  frame : stage.frame=frame
  bootstrap : stage.bootstrap=bootstrap

def prepareSelectedProfile (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) : Option Stage :=
  if decide (CandidateDigest.ProfileMeaning bootstrap bootstrap.ref) then
    if CandidateDigestCapture.catalogBudgetCheck limits declarations selections then
      match prepareManyDigest bootstrap limits.perCaptureBytes declarationVersion declarationKind settingsDecoder frame declarations,
          prepareManyDigest bootstrap limits.perCaptureBytes selectionVersion selectionKind selectionDecoder frame selections with
      | some declarationRows,some selectionRows=>
        (selectProfileRows frame declarationRows selectionRows).map fun profile=>⟨frame,bootstrap,declarationRows,selectionRows,profile⟩
      | _,_=>none
    else none
  else none

theorem selected_preparation_exact (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) (stage : Stage) :
    prepareSelectedProfile bootstrap limits frame declarations selections=some stage ↔
      SelectedDataMeaning bootstrap limits frame declarations selections stage := by
  constructor
  · intro accepted
    unfold prepareSelectedProfile at accepted
    split at accepted
    · rename_i bs
      split at accepted
      · rename_i budget
        cases dr : prepareManyDigest bootstrap limits.perCaptureBytes declarationVersion declarationKind settingsDecoder frame declarations with
        | none=>simp only [dr] at accepted;contradiction
        | some declarationRows=>
          cases sr : prepareManyDigest bootstrap limits.perCaptureBytes selectionVersion selectionKind selectionDecoder frame selections with
          | none=>simp only [dr,sr] at accepted;contradiction
          | some selectionRows=>
            simp only [dr,sr] at accepted
            cases sp : selectProfileRows frame declarationRows selectionRows with
            | none=>simp only [sp,Option.map_none] at accepted;contradiction
            | some profile=>
              simp only [sp,Option.map_some,Option.some.injEq] at accepted
              subst stage
              exact ⟨of_decide_eq_true bs,(CandidateDigestCapture.catalog_budget_exact limits declarations selections).mp budget,
                (digest_many_exact bootstrap _ declarationVersion declarationKind settingsDecoder frame declarations declarationRows).mp dr,
                (digest_many_exact bootstrap _ selectionVersion selectionKind selectionDecoder frame selections selectionRows).mp sr,
                (selected_rows_exact frame declarationRows selectionRows profile).mp sp,rfl,rfl⟩
      · contradiction
    · contradiction
  · intro meaning
    have dr:=(digest_many_exact bootstrap _ declarationVersion declarationKind settingsDecoder frame declarations stage.declarations).mpr meaning.declarationSources
    have sr:=(digest_many_exact bootstrap _ selectionVersion selectionKind selectionDecoder frame selections stage.selections).mpr meaning.selectionSources
    have sp:=(selected_rows_exact frame stage.declarations stage.selections stage.profile).mpr meaning.selected
    have same : Stage.mk frame bootstrap stage.declarations stage.selections stage.profile=stage := by
      cases stage with
      | mk f b d s p=>
        have fe:f=frame:=meaning.frame
        have be:b=bootstrap:=meaning.bootstrap
        cases fe;cases be;rfl
    simp only [prepareSelectedProfile,decide_eq_true meaning.bootstrapSupported,if_true,
      (CandidateDigestCapture.catalog_budget_exact limits declarations selections).mpr meaning.budget,dr,sr,sp,Option.map_some,same]

theorem selected_preparation_none_exact (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) :
    prepareSelectedProfile bootstrap limits frame declarations selections=none ↔
      ¬∃stage,SelectedDataMeaning bootstrap limits frame declarations selections stage := by
  constructor
  · intro refused;rintro ⟨stage,meaning⟩
    have pass:=(selected_preparation_exact bootstrap limits frame declarations selections stage).mpr meaning
    rw [refused] at pass;contradiction
  · intro absent
    cases eq:prepareSelectedProfile bootstrap limits frame declarations selections with
    | none=>rfl
    | some stage=>exact False.elim (absent ⟨stage,(selected_preparation_exact bootstrap limits frame declarations selections stage).mp eq⟩)

theorem prepared_profile_unique (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) (a b : Stage)
    (ha : SelectedDataMeaning bootstrap limits frame declarations selections a)
    (hb : SelectedDataMeaning bootstrap limits frame declarations selections b) : a=b :=
  Option.some.inj (((selected_preparation_exact bootstrap limits frame declarations selections a).mpr ha).symm.trans
    ((selected_preparation_exact bootstrap limits frame declarations selections b).mpr hb))

theorem prepared_selection_retains_inputs (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) (stage : Stage)
    (meaning : SelectedDataMeaning bootstrap limits frame declarations selections stage) :
    stage.declarations.map CandidateBindingCapture.Prepared.envelope=declarations ∧
      stage.selections.map CandidateBindingCapture.Prepared.envelope=selections :=
  ⟨CandidateDigestCapture.digest_many_retains_envelopes meaning.declarationSources,
    CandidateDigestCapture.digest_many_retains_envelopes meaning.selectionSources⟩

theorem selected_profile_source_provenance (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) (stage : Stage)
    (meaning : SelectedDataMeaning bootstrap limits frame declarations selections stage) :
    ∃ row∈stage.declarations,∃ source∈declarations,
      CandidateDigestCapture.DigestPreparedMeaning bootstrap limits.perCaptureBytes declarationVersion declarationKind settingsDecoder frame source row ∧
      stage.profile.ref.key=row.record.bindingKey ∧ stage.profile.ref.digest=source.digest ∧ row.entry.content=source.content := by
  rcases selected_source_witnesses frame stage.declarations stage.selections stage.profile meaning.selected with
    ⟨_,_,row,member,refEq,_,_,_⟩
  rcases CandidateDigestCapture.digest_many_provenance meaning.declarationSources row member with ⟨source,origin,prepared⟩
  have fields:=CandidateBindingBytes.prepared_bytes_entry_fields declarationVersion declarationKind settingsDecoder frame source row prepared.1
  exact ⟨row,member,source,origin,prepared,by rw [refEq];exact fields.1,
    by rw [refEq];exact fields.2.1,fields.2.2.2.2.1⟩

theorem source_budget_refuses (bootstrap : Profile) (limits : Limits) (frame : Frame)
    (declarations selections : List Envelope) (bad : ¬CandidateDigestCapture.CatalogBudgetMeaning limits declarations selections) :
    prepareSelectedProfile bootstrap limits frame declarations selections=none := by
  apply (selected_preparation_none_exact bootstrap limits frame declarations selections).mpr
  rintro ⟨stage,meaning⟩;exact bad meaning.budget
#print axioms selected_preparation_exact
#print axioms selected_preparation_none_exact
#print axioms prepared_profile_unique
#print axioms prepared_selection_retains_inputs
#print axioms selected_profile_source_provenance
#print axioms source_budget_refuses
end RelationalSuccessor.CandidateProfileSelection
