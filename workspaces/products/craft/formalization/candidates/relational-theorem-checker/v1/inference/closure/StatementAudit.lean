import ClosureAdequacy

namespace Inference.ClosureAudit

theorem required_statement : RequiredClosureAdequacy := audited_closure_adequacy

#print axioms required_statement
#print axioms choices_complete
#print axioms ground_rule_captures_instance
#print axioms ground_instances_complete
#print axioms closure_checker_iff
#print axioms checked_closure_is_closed
#print axioms checked_closure_has_no_extra
#print axioms checked_closure_exact
#print axioms checked_closure_is_least
#print axioms absent_from_checked_closure_not_derivable
#print axioms saturation_measure_decreases
#print axioms saturation_sufficient_fuel
#print axioms saturation_never_exhausts
#print axioms saturate

end Inference.ClosureAudit
