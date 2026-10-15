import RuleConservativity
import ProtectedLineage

namespace Inference.ExtensionAudit
theorem required_statement : Extension.RequiredRuleConservativity := Extension.audited_rule_conservativity
#print axioms required_statement
#print axioms Extension.ground_rule_output_valid
#print axioms Extension.ground_instances_sound
#print axioms Extension.lift_atom
#print axioms Extension.lift_root_policy
#print axioms Extension.old_interpretation_unchanged
#print axioms Extension.every_base_model_expands
#print axioms Extension.checked_list_model_is_semantic
#print axioms audited_derivation_soundness
#print axioms audited_closure_adequacy
#print axioms audited_protected_lineage
#print axioms audited_countermodel_soundness
end Inference.ExtensionAudit
