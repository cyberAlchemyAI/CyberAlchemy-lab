import AuthoritySources
set_option autoImplicit false
namespace RelationalSuccessor.CandidateProfileEvidence
open CandidateProfileSelection (Stage Declaration SelectionRecord ReviewPosture RevocationPosture)

def CoherentAuthority (authority : Authority) : Prop :=
  (∀ a∈authority.issues,∀ b∈authority.issues,a.source.key=b.source.key → a=b) ∧
  (∀ a∈authority.grants,∀ b∈authority.grants,a.ref.key=b.ref.key → a=b) ∧
  (∀ a∈authority.reviews,∀ b∈authority.reviews,a.ref.key=b.ref.key → a.ref=b.ref) ∧
  (∀ a∈authority.reviews,∀ b∈authority.reviews,a.ref.key=b.ref.key ∧ a.source.key=b.source.key → a=b) ∧
  (∀ a∈authority.issues,∀ byte∈a.bytes,byte<256) ∧
  (∀ a∈authority.grants,∀ action∈a.actions,action="declare" ∨ action="select")
def coherenceCheck (authority : Authority) : Bool :=
  (authority.issues.all fun a=>authority.issues.all fun b=>decide (a.source.key=b.source.key → a=b)) &&
  (authority.grants.all fun a=>authority.grants.all fun b=>decide (a.ref.key=b.ref.key → a=b)) &&
  (authority.reviews.all fun a=>authority.reviews.all fun b=>decide (a.ref.key=b.ref.key → a.ref=b.ref)) &&
  (authority.reviews.all fun a=>authority.reviews.all fun b=>decide (a.ref.key=b.ref.key ∧ a.source.key=b.source.key → a=b)) &&
  (authority.issues.all fun a=>a.bytes.all fun byte=>decide (byte<256)) &&
  (authority.grants.all fun a=>a.actions.all fun action=>decide (action="declare" ∨ action="select"))

theorem coherence_exact (authority : Authority) : coherenceCheck authority=true ↔ CoherentAuthority authority := by
  simp only [coherenceCheck,CoherentAuthority,Bool.and_eq_true,List.all_eq_true,decide_eq_true_eq]
  simp only [and_assoc]

def IssuanceMeaning {α : Type} (row : CandidateBindingCapture.Prepared α) (issuer : RevisionRef) (fact : Issue) : Prop :=
  fact.source=row.entry.ref ∧ fact.kind=row.entry.sourceKind ∧ fact.issuer=issuer ∧
    fact.ownerReview=row.entry.ownerReview ∧ fact.bytes=row.entry.content.map UInt8.toNat
instance {α : Type} (row : CandidateBindingCapture.Prepared α) (issuer : RevisionRef) (fact : Issue) :
    Decidable (IssuanceMeaning row issuer fact) := by unfold IssuanceMeaning;infer_instance
def Issued {α : Type} (authority : Authority) (row : CandidateBindingCapture.Prepared α) (issuer : RevisionRef) : Prop :=
  ∃ fact∈authority.issues,IssuanceMeaning row issuer fact
def issuanceCheck {α : Type} (authority : Authority) (row : CandidateBindingCapture.Prepared α) (issuer : RevisionRef) : Bool :=
  authority.issues.any fun fact=>decide (IssuanceMeaning row issuer fact)
theorem issuance_exact {α : Type} (authority : Authority) (row : CandidateBindingCapture.Prepared α) (issuer : RevisionRef) :
    issuanceCheck authority row issuer=true ↔ Issued authority row issuer := by
  simp only [issuanceCheck,Issued,List.any_eq_true,decide_eq_true_eq]

def GrantMeaning (frame : Frame) (principal : RevisionRef) (action : String) (grant : Grant) : Prop :=
  grant.principal=principal ∧ action∈grant.actions ∧ grant.scope=frame.scope
instance (frame : Frame) (principal : RevisionRef) (action : String) (grant : Grant) :
    Decidable (GrantMeaning frame principal action grant) := by unfold GrantMeaning;infer_instance
def Entitled (authority : Authority) (frame : Frame) (principal : RevisionRef) (action : String) : Prop :=
  ∃ grant∈authority.grants,GrantMeaning frame principal action grant
def entitlementCheck (authority : Authority) (frame : Frame) (principal : RevisionRef) (action : String) : Bool :=
  authority.grants.any fun grant=>decide (GrantMeaning frame principal action grant)
theorem entitlement_exact (authority : Authority) (frame : Frame) (principal : RevisionRef) (action : String) :
    entitlementCheck authority frame principal action=true ↔ Entitled authority frame principal action := by
  simp only [entitlementCheck,Entitled,List.any_eq_true,decide_eq_true_eq]

def ReviewMeaning {α : Type} (row : CandidateBindingCapture.Prepared α) (decision : ReviewPosture)
    (revocation : RevocationPosture) (expiry : Nat) (review : Review) : Prop :=
  review.ref=row.entry.ownerReview ∧ review.source=row.entry.ref ∧ review.decision=decision ∧
    review.revocation=revocation ∧ review.expiry=expiry
instance {α : Type} (row : CandidateBindingCapture.Prepared α) (decision : ReviewPosture)
    (revocation : RevocationPosture) (expiry : Nat) (review : Review) :
    Decidable (ReviewMeaning row decision revocation expiry review) := by unfold ReviewMeaning;infer_instance
def Reviewed {α : Type} (authority : Authority) (row : CandidateBindingCapture.Prepared α) (decision : ReviewPosture)
    (revocation : RevocationPosture) (expiry : Nat) : Prop :=
  ∃ review∈authority.reviews,ReviewMeaning row decision revocation expiry review
def reviewCheck {α : Type} (authority : Authority) (row : CandidateBindingCapture.Prepared α) (decision : ReviewPosture)
    (revocation : RevocationPosture) (expiry : Nat) : Bool :=
  authority.reviews.any fun review=>decide (ReviewMeaning row decision revocation expiry review)
theorem review_check_exact {α : Type} (authority : Authority) (row : CandidateBindingCapture.Prepared α) (decision : ReviewPosture)
    (revocation : RevocationPosture) (expiry : Nat) :
    reviewCheck authority row decision revocation expiry=true ↔ Reviewed authority row decision revocation expiry := by
  simp only [reviewCheck,Reviewed,List.any_eq_true,decide_eq_true_eq]

def DeclarationEvidence (authority : Authority) (frame : Frame) (row : Declaration) : Prop :=
  Issued authority row row.record.body.target.issuer ∧ Entitled authority frame row.record.body.target.issuer "declare" ∧
    Reviewed authority row row.record.body.target.review row.record.body.target.revocation row.record.body.target.expiry
def SelectionEvidence (authority : Authority) (frame : Frame) (row : SelectionRecord) : Prop :=
  Issued authority row row.record.body.target.issuer ∧ Entitled authority frame row.record.body.target.issuer "select" ∧
    Reviewed authority row row.record.body.target.review row.record.body.target.revocation row.record.body.target.expiry
def declarationEvidenceCheck (authority : Authority) (frame : Frame) (row : Declaration) : Bool :=
  issuanceCheck authority row row.record.body.target.issuer && entitlementCheck authority frame row.record.body.target.issuer "declare" &&
    reviewCheck authority row row.record.body.target.review row.record.body.target.revocation row.record.body.target.expiry
def selectionEvidenceCheck (authority : Authority) (frame : Frame) (row : SelectionRecord) : Bool :=
  issuanceCheck authority row row.record.body.target.issuer && entitlementCheck authority frame row.record.body.target.issuer "select" &&
    reviewCheck authority row row.record.body.target.review row.record.body.target.revocation row.record.body.target.expiry
theorem declaration_evidence_exact (authority : Authority) (frame : Frame) (row : Declaration) :
    declarationEvidenceCheck authority frame row=true ↔ DeclarationEvidence authority frame row := by
  simp only [declarationEvidenceCheck,DeclarationEvidence,Bool.and_eq_true,issuance_exact,entitlement_exact,review_check_exact]
  simp only [and_assoc]
theorem selection_evidence_exact (authority : Authority) (frame : Frame) (row : SelectionRecord) :
    selectionEvidenceCheck authority frame row=true ↔ SelectionEvidence authority frame row := by
  simp only [selectionEvidenceCheck,SelectionEvidence,Bool.and_eq_true,issuance_exact,entitlement_exact,review_check_exact]
  simp only [and_assoc]

def ManifestMeaning (authority : Authority) (stage : Stage) : Prop :=
  authority.declarations=stage.declarations.map (fun row=>row.entry.ref) ∧
    authority.selections=stage.selections.map (fun row=>row.entry.ref)
def EvidenceRowsMeaning (frame : Frame) (stage : Stage) (authority : CapturedAuthority) : Prop :=
  authority.record.body.frame=frame ∧ stage.frame=frame ∧ ManifestMeaning authority.record.body.target stage ∧
    (∀ row∈stage.declarations,DeclarationEvidence authority.record.body.target frame row) ∧
    (∀ row∈stage.selections,SelectionEvidence authority.record.body.target frame row)
def evidenceRowsCheck (frame : Frame) (stage : Stage) (authority : CapturedAuthority) : Bool :=
  decide (authority.record.body.frame=frame) && decide (stage.frame=frame) &&
    decide (authority.record.body.target.declarations=stage.declarations.map (fun row=>row.entry.ref)) &&
    decide (authority.record.body.target.selections=stage.selections.map (fun row=>row.entry.ref)) &&
    (stage.declarations.all fun row=>declarationEvidenceCheck authority.record.body.target frame row) &&
    (stage.selections.all fun row=>selectionEvidenceCheck authority.record.body.target frame row)
theorem evidence_rows_exact (frame : Frame) (stage : Stage) (authority : CapturedAuthority) :
    evidenceRowsCheck frame stage authority=true ↔ EvidenceRowsMeaning frame stage authority := by
  simp only [evidenceRowsCheck,EvidenceRowsMeaning,ManifestMeaning,Bool.and_eq_true,decide_eq_true_eq,
    List.all_eq_true,declaration_evidence_exact,selection_evidence_exact]
  simp only [and_assoc]

theorem exact_issuance_preserves_original_bytes {α : Type} (authority : Authority) (row : CandidateBindingCapture.Prepared α)
    (issuer : RevisionRef) (issued : Issued authority row issuer) :
    ∃ fact∈authority.issues,fact.source=row.entry.ref ∧ fact.bytes=row.entry.content.map UInt8.toNat := by
  rcases issued with ⟨fact,member,meaning⟩
  exact ⟨fact,member,meaning.1,meaning.2.2.2.2⟩
#print axioms coherence_exact
#print axioms issuance_exact
#print axioms entitlement_exact
#print axioms review_check_exact
#print axioms declaration_evidence_exact
#print axioms selection_evidence_exact
#print axioms evidence_rows_exact
#print axioms exact_issuance_preserves_original_bytes
end RelationalSuccessor.CandidateProfileEvidence
