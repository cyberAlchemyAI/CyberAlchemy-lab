import ModelSemantics

namespace Inference.ModelAudit
theorem required_statement : RequiredCountermodelSoundness := audited_countermodel_soundness
#print axioms required_statement
#print axioms model_checker_iff
#print axioms checked_model_is_closed
#print axioms countermodel_checker_iff
#print axioms checked_countermodel_non_entailment
end Inference.ModelAudit
