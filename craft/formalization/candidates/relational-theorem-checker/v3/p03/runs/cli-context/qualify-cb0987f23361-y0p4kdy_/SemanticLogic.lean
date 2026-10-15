import RelationalSemantics

namespace Relational.Logic
open Relational

-- These are semantic claims about assertions, not checker results.
abbrev ConformsAt (g : Graph) (e : Assertion) (scope version evidence : String) : Prop :=
  e.kind = .conformsTo ∧ e.qualifiers = .conformance scope version evidence ∧
    InstanceValid g e

abbrev MaterializesAs (g : Graph) (e : Assertion) (receipt role digest : String) : Prop :=
  e.kind = .materializesConsequence ∧ e.qualifiers = .materialization receipt role digest ∧
    InstanceValid g e

-- Presence of separately supplied provenance; this does not authenticate authority.
abbrev HasAdmissionRoot (g : Graph) (subject : NodeRef) : Prop :=
  ∃ root ∈ g.admissionRoots, root.subject = subject

instance (g : Graph) (e : Assertion) (scope version evidence : String) :
    Decidable (ConformsAt g e scope version evidence) := by
  unfold ConformsAt
  infer_instance

instance (g : Graph) (e : Assertion) (receipt role digest : String) :
    Decidable (MaterializesAs g e receipt role digest) := by
  unfold MaterializesAs
  infer_instance

instance (g : Graph) (subject : NodeRef) : Decidable (HasAdmissionRoot g subject) := by
  unfold HasAdmissionRoot
  infer_instance

def withAdmissionRoots (g : Graph) (roots : List AdmissionRoot) : Graph :=
  { g with admissionRoots := roots }

theorem identity_functional_of_nodup_map {α β : Type} (key : α → β) (xs : List α)
    (hunique : (xs.map key).Nodup) (a b : α)
    (ha : a ∈ xs) (hb : b ∈ xs) (hkey : key a = key b) : a = b := by
  induction xs with
  | nil => simp at ha
  | cons head tail ih =>
    rcases List.nodup_cons.mp hunique with ⟨hhead, htail⟩
    rcases List.mem_cons.mp ha with ha | ha
    · rcases List.mem_cons.mp hb with hb | hb
      · exact ha.trans hb.symm
      · subst a
        exact False.elim (hhead (hkey.symm ▸ List.mem_map.mpr ⟨b, hb, rfl⟩))
    · rcases List.mem_cons.mp hb with hb | hb
      · subst b
        exact False.elim (hhead (hkey ▸ List.mem_map.mpr ⟨a, ha, rfl⟩))
      · exact ih htail ha hb

theorem assessment_identity_functional (g : Graph) (hg : Inv g)
    (a b : Assessment) (ha : a ∈ g.assessments) (hb : b ∈ g.assessments)
    (href : a.ref = b.ref) : a = b :=
  identity_functional_of_nodup_map Assessment.ref g.assessments
    hg.1.2.2.2.1 a b ha hb href

theorem conformance_has_bound_assessment (g : Graph) (e : Assertion)
    (scope version evidence : String) (h : ConformsAt g e scope version evidence) :
    version = e.target.version ∧ ∃ a ∈ g.assessments,
      a.ref = evidence ∧ a.mode = .conformance ∧ a.accepted = true ∧
      a.subject = e.source ∧ a.target = e.target ∧ a.scope = scope := by
  rcases h with ⟨hkind, hqual, hvalid⟩
  have hv := hvalid.2.2.2
  simpa only [VersionScopeValid, hkind, hqual] using hv

-- Sharing one assessment token cannot widen scope or substitute exact endpoints.
theorem conformance_evidence_functional (g : Graph) (hg : Inv g)
    (e₁ e₂ : Assertion) (scope₁ scope₂ version₁ version₂ evidence : String)
    (h₁ : ConformsAt g e₁ scope₁ version₁ evidence)
    (h₂ : ConformsAt g e₂ scope₂ version₂ evidence) :
    e₁.source = e₂.source ∧ e₁.target = e₂.target ∧
      scope₁ = scope₂ ∧ version₁ = version₂ := by
  rcases conformance_has_bound_assessment g e₁ scope₁ version₁ evidence h₁ with
    ⟨hv₁, a, ha, href₁, _, _, hsource₁, htarget₁, hscope₁⟩
  rcases conformance_has_bound_assessment g e₂ scope₂ version₂ evidence h₂ with
    ⟨hv₂, b, hb, href₂, _, _, hsource₂, htarget₂, hscope₂⟩
  have hab := assessment_identity_functional g hg a b ha hb (href₁.trans href₂.symm)
  subst b
  have htarget := htarget₁.symm.trans htarget₂
  exact ⟨hsource₁.symm.trans hsource₂, htarget, hscope₁.symm.trans hscope₂,
    hv₁.trans ((congrArg NodeRef.version htarget).trans hv₂.symm)⟩

theorem materialization_has_bound_receipt (g : Graph) (e : Assertion)
    (receipt role digest : String) (h : MaterializesAs g e receipt role digest) :
    (∃ t ∈ g.nodes, t.ref = e.target ∧ t.contentIdentity = digest) ∧
    ∃ a ∈ g.assessments, a.ref = receipt ∧ a.mode = .applicationReceipt ∧
      a.accepted = true ∧ a.subject = e.source ∧ a.target = e.target ∧
      a.role = role ∧ a.outputDigest = digest := by
  rcases h with ⟨hkind, hqual, hvalid⟩
  have hv := hvalid.2.2.2
  simpa only [VersionScopeValid, hkind, hqual] using hv

theorem materialization_receipt_functional (g : Graph) (hg : Inv g)
    (e₁ e₂ : Assertion) (receipt role₁ role₂ digest₁ digest₂ : String)
    (h₁ : MaterializesAs g e₁ receipt role₁ digest₁)
    (h₂ : MaterializesAs g e₂ receipt role₂ digest₂) :
    e₁.source = e₂.source ∧ e₁.target = e₂.target ∧
      role₁ = role₂ ∧ digest₁ = digest₂ := by
  rcases materialization_has_bound_receipt g e₁ receipt role₁ digest₁ h₁ with
    ⟨_, a, ha, href₁, _, _, hsource₁, htarget₁, hrole₁, hdigest₁⟩
  rcases materialization_has_bound_receipt g e₂ receipt role₂ digest₂ h₂ with
    ⟨_, b, hb, href₂, _, _, hsource₂, htarget₂, hrole₂, hdigest₂⟩
  have hab := assessment_identity_functional g hg a b ha hb (href₁.trans href₂.symm)
  subst b
  exact ⟨hsource₁.symm.trans hsource₂, htarget₁.symm.trans htarget₂,
    hrole₁.symm.trans hrole₂, hdigest₁.symm.trans hdigest₂⟩

theorem admission_roots_do_not_change_instance_meaning (g : Graph)
    (roots : List AdmissionRoot) (e : Assertion) :
    InstanceValid (withAdmissionRoots g roots) e ↔ InstanceValid g e := Iff.rfl

theorem well_formed_admission_variation_preserves_inv (g : Graph)
    (roots : List AdmissionRoot) (hg : Inv g)
    (hroots : ∀ root ∈ roots, AdmissionRootValid g root) :
    Inv (withAdmissionRoots g roots) := by
  rcases hg with ⟨⟨hnodes, hnodekeys, hassess, hassesskeys, _⟩, hedges, hedgekeys⟩
  exact ⟨⟨hnodes, hnodekeys, hassess, hassesskeys, hroots⟩, hedges, hedgekeys⟩

end Relational.Logic
