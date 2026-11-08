import CheckerSoundness
import InhabitedExample
import FormalCheckerControls

namespace Relational.Audit
open Relational

-- These targets are audited separately from the implementation theorem bodies.
def RequiredInstanceSoundness : Prop :=
  ∀ (g : Graph) (e : Assertion), checkInstance g e = true → InstanceValid g e
def RequiredGraphSoundness : Prop :=
  ∀ (g : Graph), checkGraph g = true → Inv g
def RequiredAdditionPreservation : Prop :=
  ∀ (g : Graph) (e : Assertion), checkAddition g e = true → Inv (applyAddition g e)

theorem audited_instance : RequiredInstanceSoundness := instance_check_sound
theorem audited_graph : RequiredGraphSoundness := graph_check_sound
theorem audited_addition : RequiredAdditionPreservation := addition_preserves

end Relational.Audit

#check Relational.instance_check_sound
#check Relational.graph_check_sound
#check Relational.addition_preserves
#check Relational.graph_check_iff
#print axioms Relational.Audit.audited_instance
#print axioms Relational.Audit.audited_graph
#print axioms Relational.Audit.audited_addition
#print axioms Relational.instance_check_iff
#print axioms Relational.graph_check_iff
#print axioms Relational.addition_preserves_admission_roots
#print axioms Relational.Witnesses.inhabited_valid_graph
#print axioms Relational.Witnesses.inhabited_valid_addition
#print axioms Relational.Witnesses.conformance_without_admission
#print axioms Relational.Witnesses.independent_admission_coexistence
#print axioms Relational.Controls.conformsTo_pair_1
#print axioms Relational.Controls.conformsTo_pair_2
#print axioms Relational.Controls.conformsTo_pair_3
#print axioms Relational.Controls.declaresEffectOn_pair_1
#print axioms Relational.Controls.declaresEffectOn_pair_2
#print axioms Relational.Controls.declaresEffectOn_pair_3
#print axioms Relational.Controls.declaresEffectOn_pair_4
#print axioms Relational.Controls.declaresEffectOn_pair_5
#print axioms Relational.Controls.declaresEffectOn_pair_6
#print axioms Relational.Controls.declaresEffectOn_pair_7
#print axioms Relational.Controls.declaresEffectOn_pair_8
#print axioms Relational.Controls.declaresEffectOn_pair_9
#print axioms Relational.Controls.declaresEffectOn_pair_10
#print axioms Relational.Controls.declaresEffectOn_pair_11
#print axioms Relational.Controls.declaresEffectOn_pair_12
#print axioms Relational.Controls.declaresEffectOn_pair_13
#print axioms Relational.Controls.declaresEffectOn_pair_14
#print axioms Relational.Controls.declaresEffectOn_pair_15
#print axioms Relational.Controls.declaresEffectOn_pair_16
#print axioms Relational.Controls.declaresEffectOn_pair_17
#print axioms Relational.Controls.declaresEffectOn_pair_18
#print axioms Relational.Controls.declaresEffectOn_pair_19
#print axioms Relational.Controls.declaresEffectOn_pair_20
#print axioms Relational.Controls.declaresEffectOn_pair_21
#print axioms Relational.Controls.materializesConsequence_pair_1
#print axioms Relational.Controls.materializesConsequence_pair_2
#print axioms Relational.Controls.materializesConsequence_pair_3
#print axioms Relational.Controls.materializesConsequence_pair_4
#print axioms Relational.Controls.all_three_kinds
#print axioms Relational.Controls.valid_addition
#print axioms Relational.Controls.conformance_coexists_with_admission
#print axioms Relational.Controls.distinct_effect_value
#print axioms Relational.Controls.phantom_conformance_pair
#print axioms Relational.Controls.reversed_pair
#print axioms Relational.Controls.phantom_effect_pair
#print axioms Relational.Controls.phantom_materialization_pair
#print axioms Relational.Controls.wrong_qualifier_constructor
#print axioms Relational.Controls.empty_required_qualifier
#print axioms Relational.Controls.wrong_target_version
#print axioms Relational.Controls.wrong_effect_version
#print axioms Relational.Controls.missing_evidence_reference
#print axioms Relational.Controls.stale_endpoint
#print axioms Relational.Controls.wrong_evidence_scope
#print axioms Relational.Controls.unaccepted_evidence
#print axioms Relational.Controls.misbound_receipt
#print axioms Relational.Controls.wrong_receipt_role
#print axioms Relational.Controls.wrong_output_digest
#print axioms Relational.Controls.duplicate_assertion_identity
#print axioms Relational.Controls.duplicate_node_identity
#print axioms Relational.Controls.duplicate_assessment_identity
#print axioms Relational.Controls.invalid_existing_graph
#print axioms Relational.Controls.invalid_unused_assessment
#print axioms Relational.Controls.admission_wrong_decision_kind
#print axioms Relational.Controls.empty_node_identity
