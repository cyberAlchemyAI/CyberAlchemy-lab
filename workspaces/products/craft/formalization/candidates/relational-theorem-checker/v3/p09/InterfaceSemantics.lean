import QuerySemantics
import EvidenceSemantics

namespace RelationalV3.Interface
open Inference

-- Universal properties over typed atoms. The correspondence between raw JSON
-- numeral spellings and these atoms remains a checked parser/domain boundary.
theorem equal_atoms_preserve_diagnosis (T : Theory) (C : List Atom)
    (complete : Bool) (requested canonical : Atom) (same : requested = canonical) :
    Query.diagnose T C complete requested = Query.diagnose T C complete canonical := by
  rw [same]

theorem canonicalization_does_not_create_derivation (T : Theory) (F : List Atom)
    (requested canonical : Atom) (same : requested = canonical) :
    Derivable T F requested ↔ Derivable T F canonical := by
  rw [same]

-- A deadline signal is not an assertion that the user asked to cancel.
def refusalCause (deadlineElapsed userCancelled : Bool) : Outcome :=
  if deadlineElapsed then .unknownResource
  else if userCancelled then .cancelled
  else .invalid

theorem elapsed_budget_has_resource_cause (userCancelled : Bool) :
    refusalCause true userCancelled = .unknownResource := by
  rfl

theorem explicit_cancel_before_deadline_has_cancel_cause :
    refusalCause false true = .cancelled := by
  rfl

theorem refusal_never_permits_a_claim (d u : Bool) (claim : Claim) :
    ¬ ClaimPermitted (refusalCause d u) claim := by
  cases d <;> cases u <;> simp [refusalCause, ClaimPermitted]

#print axioms equal_atoms_preserve_diagnosis
#print axioms canonicalization_does_not_create_derivation
#print axioms elapsed_budget_has_resource_cause
#print axioms explicit_cancel_before_deadline_has_cancel_cause
#print axioms refusal_never_permits_a_claim
end RelationalV3.Interface
