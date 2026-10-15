import SemanticWitnesses

namespace Relational.Logic.Audit
open Relational Relational.Logic Relational.Logic.Witnesses

def RequiredConformanceFunctionality : Prop :=
  ∀ (g : Graph), Inv g → ∀ (e₁ e₂ : Assertion)
    (scope₁ scope₂ version₁ version₂ evidence : String),
    ConformsAt g e₁ scope₁ version₁ evidence →
    ConformsAt g e₂ scope₂ version₂ evidence →
    e₁.source = e₂.source ∧ e₁.target = e₂.target ∧
      scope₁ = scope₂ ∧ version₁ = version₂

def RequiredReceiptFunctionality : Prop :=
  ∀ (g : Graph), Inv g → ∀ (e₁ e₂ : Assertion)
    (receipt role₁ role₂ digest₁ digest₂ : String),
    MaterializesAs g e₁ receipt role₁ digest₁ →
    MaterializesAs g e₂ receipt role₂ digest₂ →
    e₁.source = e₂.source ∧ e₁.target = e₂.target ∧
      role₁ = role₂ ∧ digest₁ = digest₂

def RequiredAdmissionNonEntailment : Prop :=
  ¬ (∀ (g : Graph) (e : Assertion) (scope version evidence : String),
    Inv g → e ∈ g.assertions → ConformsAt g e scope version evidence →
    HasAdmissionRoot g e.source)

def RequiredRootVariation : Prop :=
  ∀ (g : Graph) (roots : List AdmissionRoot), Inv g →
    (∀ root ∈ roots, AdmissionRootValid g root) →
    Inv (withAdmissionRoots g roots)

theorem audited_conformance : RequiredConformanceFunctionality := conformance_evidence_functional
theorem audited_receipt : RequiredReceiptFunctionality := materialization_receipt_functional
theorem audited_non_entailment : RequiredAdmissionNonEntailment := conformance_does_not_entail_admission_root
theorem audited_root_variation : RequiredRootVariation := well_formed_admission_variation_preserves_inv

end Relational.Logic.Audit

#check Relational.Logic.conformance_evidence_functional
#check Relational.Logic.materialization_receipt_functional
#check Relational.Logic.well_formed_admission_variation_preserves_inv
#check Relational.Logic.Witnesses.conformance_does_not_entail_admission_root

#print axioms Relational.Logic.identity_functional_of_nodup_map
#print axioms Relational.Logic.assessment_identity_functional
#print axioms Relational.Logic.conformance_has_bound_assessment
#print axioms Relational.Logic.conformance_evidence_functional
#print axioms Relational.Logic.materialization_has_bound_receipt
#print axioms Relational.Logic.materialization_receipt_functional
#print axioms Relational.Logic.admission_roots_do_not_change_instance_meaning
#print axioms Relational.Logic.well_formed_admission_variation_preserves_inv
#print axioms Relational.Logic.Witnesses.inhabited_semantic_model
#print axioms Relational.Logic.Witnesses.conformance_without_root
#print axioms Relational.Logic.Witnesses.conformance_does_not_entail_admission_root
#print axioms Relational.Logic.Witnesses.admission_independence_models
#print axioms Relational.Logic.Witnesses.no_automatic_scope_upgrade
#print axioms Relational.Logic.Witnesses.same_bound_evidence_reuse_is_allowed
#print axioms Relational.Logic.Witnesses.separate_scope_assessment_is_allowed
#print axioms Relational.Logic.Witnesses.unique_identity_premise_is_needed
#print axioms Relational.Logic.Witnesses.functionality_without_invariant_is_false
#print axioms Relational.Logic.Audit.audited_conformance
#print axioms Relational.Logic.Audit.audited_receipt
#print axioms Relational.Logic.Audit.audited_non_entailment
#print axioms Relational.Logic.Audit.audited_root_variation
