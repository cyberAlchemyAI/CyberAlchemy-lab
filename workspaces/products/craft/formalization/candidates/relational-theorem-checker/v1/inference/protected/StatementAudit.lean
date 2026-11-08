import ProtectedLineage

namespace Inference.LineageAudit

theorem required_statement : RequiredProtectedLineage := audited_protected_lineage

#print axioms required_statement
#print axioms lineage_checker_iff
#print axioms justification_is_rooted
#print axioms initial_root_lineage
#print axioms protected_lineage
#print axioms checked_protected_lineage
#print axioms no_unrooted_protected_derivation

end Inference.LineageAudit
