import ProfileSources
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileSelection
open CandidateDigest (Profile)

def DeclarationsNonEquivocating (rows : List Declaration) : Prop :=
  ∀ a∈rows,∀ b∈rows,a.entry.ref.key=b.entry.ref.key → a=b

def SelectionAgreement (rows : List SelectionRecord) : Prop := ∀ a∈rows,∀ b∈rows,a=b

def declarationCatalogCheck (rows : List Declaration) : Bool :=
  rows.all fun a=>rows.all fun b=>decide (a.entry.ref.key=b.entry.ref.key → a=b)
def selectionAgreementCheck (rows : List SelectionRecord) : Bool :=
  rows.all fun a=>rows.all fun b=>decide (a=b)

theorem declaration_catalog_exact (rows : List Declaration) :
    declarationCatalogCheck rows=true ↔ DeclarationsNonEquivocating rows := by
  simp only [declarationCatalogCheck,DeclarationsNonEquivocating,List.all_eq_true,decide_eq_true_eq]

theorem selection_agreement_exact (rows : List SelectionRecord) :
    selectionAgreementCheck rows=true ↔ SelectionAgreement rows := by
  simp only [selectionAgreementCheck,SelectionAgreement,List.all_eq_true,decide_eq_true_eq]

def lookupDeclaration : List Declaration → RevisionRef → Option Declaration
  | [],_=>none
  | row::rest,ref=>if row.entry.ref=ref then some row else lookupDeclaration rest ref

theorem declaration_lookup_sound (rows : List Declaration) (ref : RevisionRef) (row : Declaration)
    (found : lookupDeclaration rows ref=some row) : row∈rows ∧ row.entry.ref=ref := by
  induction rows with
  | nil=>simp [lookupDeclaration] at found
  | cons first rest ih=>
    unfold lookupDeclaration at found
    split at found
    · rename_i eq;cases found;exact ⟨by simp,eq⟩
    · have tail:=ih found;exact ⟨by simp [tail.1],tail.2⟩

theorem declaration_lookup_complete (rows : List Declaration) (ref : RevisionRef) (row : Declaration)
    (consistent : DeclarationsNonEquivocating rows) (member : row∈rows) (same : row.entry.ref=ref) :
    lookupDeclaration rows ref=some row := by
  induction rows with
  | nil=>simp at member
  | cons first rest ih=>
    unfold lookupDeclaration
    split
    · rename_i eq
      have full : first.entry.ref=row.entry.ref := eq.trans same.symm
      have identical := consistent first (by simp) row member (congrArg RevisionRef.key full)
      simp only [identical]
    · rename_i ne
      rcases List.mem_cons.mp member with eq | tail
      · subst row;exact False.elim (ne same)
      · exact ih (by intro a ha b hb eq;exact consistent a (by simp [ha]) b (by simp [hb]) eq) tail

def SelectedRowsMeaning (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord)
    (output : Profile) : Prop :=
  DeclarationsNonEquivocating declarations ∧ SelectionAgreement selections ∧
    ∃ choice∈selections,∃ declaration∈declarations,
      SelectionEligible frame choice ∧ declaration.entry.ref=choice.record.body.target.declaration ∧
      DeclarationEligible frame declaration ∧ CandidateDigest.ProfileMeaning (declaredProfile declaration) declaration.entry.ref ∧
      output=declaredProfile declaration

def selectProfileRows (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord) : Option Profile :=
  if declarationCatalogCheck declarations && selectionAgreementCheck selections then
    match selections with
    | []=>none
    | choice::_=>
      if SelectionEligible frame choice then
        match lookupDeclaration declarations choice.record.body.target.declaration with
        | none=>none
        | some declaration=>
          if DeclarationEligible frame declaration ∧ CandidateDigest.ProfileMeaning (declaredProfile declaration) declaration.entry.ref then
            some (declaredProfile declaration)
          else none
      else none
  else none

theorem selected_rows_exact (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord) (output : Profile) :
    selectProfileRows frame declarations selections=some output ↔ SelectedRowsMeaning frame declarations selections output := by
  constructor
  · intro accepted
    unfold selectProfileRows at accepted
    split at accepted
    · rename_i checked
      have parts : declarationCatalogCheck declarations=true ∧ selectionAgreementCheck selections=true := by simpa only [Bool.and_eq_true] using checked
      cases selections with
      | nil=>contradiction
      | cons choice rest=>
        dsimp only at accepted
        split at accepted
        · rename_i eligible
          cases found : lookupDeclaration declarations choice.record.body.target.declaration with
          | none=>simp only [found] at accepted;contradiction
          | some declaration=>
            simp only [found] at accepted
            split at accepted
            · rename_i valid
              cases accepted
              have origin:=declaration_lookup_sound declarations _ declaration found
              exact ⟨(declaration_catalog_exact declarations).mp parts.1,
                (selection_agreement_exact (choice::rest)).mp parts.2,choice,by simp,declaration,origin.1,
                eligible,origin.2,valid.1,valid.2,rfl⟩
            · contradiction
        · contradiction
    · contradiction
  · rintro ⟨consistent,agreement,choice,member,declaration,origin,eligible,refMatch,valid,supported,rfl⟩
    cases selections with
    | nil=>simp at member
    | cons first rest=>
      have same : first=choice := agreement first (by simp) choice member
      subst first
      simp only [selectProfileRows,(declaration_catalog_exact declarations).mpr consistent,
        (selection_agreement_exact (choice::rest)).mpr agreement,Bool.and_true,if_true,if_pos eligible,
        declaration_lookup_complete declarations _ declaration consistent origin refMatch,if_pos (And.intro valid supported)]

theorem selected_rows_none_exact (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord) :
    selectProfileRows frame declarations selections=none ↔ ¬∃output,SelectedRowsMeaning frame declarations selections output := by
  constructor
  · intro refused;rintro ⟨output,meaning⟩
    have accepted:=(selected_rows_exact frame declarations selections output).mpr meaning
    rw [refused] at accepted;contradiction
  · intro absent
    cases eq : selectProfileRows frame declarations selections with
    | none=>rfl
    | some output=>exact False.elim (absent ⟨output,(selected_rows_exact frame declarations selections output).mp eq⟩)

theorem selected_rows_unique (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord) (a b : Profile)
    (ha : SelectedRowsMeaning frame declarations selections a) (hb : SelectedRowsMeaning frame declarations selections b) : a=b :=
  Option.some.inj ((selected_rows_exact frame declarations selections a).mpr ha |>.symm.trans ((selected_rows_exact frame declarations selections b).mpr hb))

theorem selected_source_witnesses (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord) (output : Profile)
    (meaning : SelectedRowsMeaning frame declarations selections output) :
    ∃ choice∈selections,∃ declaration∈declarations,
      output.ref=declaration.entry.ref ∧ choice.record.body.target.declaration=output.ref ∧
      choice.record.body.frame=frame ∧ declaration.record.body.frame=frame := by
  rcases meaning with ⟨_,_,choice,cm,declaration,dm,eligible,refEq,valid,_,rfl⟩
  exact ⟨choice,cm,declaration,dm,rfl,refEq.symm,eligible.1,valid.1⟩

theorem selection_conflict_refuses (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord)
    (bad : ¬SelectionAgreement selections) : selectProfileRows frame declarations selections=none := by
  apply (selected_rows_none_exact frame declarations selections).mpr
  rintro ⟨output,meaning⟩;exact bad meaning.2.1

theorem unused_declaration_conflict_refuses (frame : Frame) (declarations : List Declaration) (selections : List SelectionRecord)
    (bad : ¬DeclarationsNonEquivocating declarations) : selectProfileRows frame declarations selections=none := by
  apply (selected_rows_none_exact frame declarations selections).mpr
  rintro ⟨output,meaning⟩;exact bad meaning.1
#print axioms declaration_catalog_exact
#print axioms selection_agreement_exact
#print axioms declaration_lookup_sound
#print axioms declaration_lookup_complete
#print axioms selected_rows_exact
#print axioms selected_rows_none_exact
#print axioms selected_rows_unique
#print axioms selected_source_witnesses
#print axioms selection_conflict_refuses
#print axioms unused_declaration_conflict_refuses
end RelationalSuccessor.CandidateProfileSelection
