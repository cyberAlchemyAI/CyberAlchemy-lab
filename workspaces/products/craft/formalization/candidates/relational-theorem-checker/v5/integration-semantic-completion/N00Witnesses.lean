import CoverageSemantics

namespace RelationalSuccessor.Witnesses
open RelationalSuccessor

-- These are synthetic model instances, not authenticated owner approvals.
def ref (name : String) : RevisionRef := ⟨⟨"fixture", name, "1"⟩, name⟩
def frame : Frame := ⟨ref "profile", ref "subject", ref "target", ref "context",
  ref "scope", ref "snapshot", 1, "fixture-time"⟩
def condition : Definition := ⟨ref "condition", .condition (.atom (ref "leaf")), [], ref "review"⟩
def substituted : Definition := { condition with body := .condition (.neg (.atom (ref "leaf"))) }
def criteria : List RevisionRef := [ref "C1", ref "C2"]
def requirement : Definition := ⟨ref "requirement", .requirement criteria, [], ref "review"⟩
def roots : List Definition := [condition, requirement]
def supports : List Assessment := criteria.map fun c =>
  ⟨c, ref "requirement", frame, ref "action", ref "output", .yes⟩
def challenge : Challenge := ⟨"fixture-obligation", ref "kind", ref "meaning", "fixture proposition",
  [ref "condition"], frame, [], ["synthetic instance"]⟩
def obligation : Obligation := ⟨challenge, [.kernel]⟩
def evidence : Evidence := ⟨challenge, .kernel, ref "proof", ref "snapshot"⟩

theorem legitimate_owned_condition :
    ownedValue roots roots (ref "condition") frame (fun _ _ => .yes) = .yes := by decide
theorem legitimate_two_criterion_fulfillment :
    fulfilled roots roots (ref "requirement") frame supports criteria = true := by decide
theorem changed_ast_without_approval_refuses :
    resolve roots [substituted, requirement] (ref "condition") = none := by decide
theorem contradictory_catalog_refuses :
    checkedCatalog [condition, substituted] = false := by decide
theorem no_owner_basis_refuses :
    ownedValue [] roots (ref "condition") frame (fun _ _ => .yes) = .unknown := by decide
theorem omitted_criterion_refuses :
    fulfilled roots roots (ref "requirement") frame supports [ref "C1"] = false := by decide
theorem missing_support_refuses :
    fulfilled roots roots (ref "requirement") frame [] criteria = false := by decide
theorem legitimate_complete_qualification :
    qualify [obligation] [obligation] [evidence] (ref "snapshot") false = true := by decide
theorem claimed_yes_without_evidence_refuses :
    qualify [obligation] [obligation] [] (ref "snapshot") true = false := by decide
theorem wrong_snapshot_refuses :
    checkMatch obligation evidence (ref "another-snapshot") = false := by decide
theorem target_substitution_refuses :
    checkMatch obligation { evidence with challenge := { challenge with frame :=
      { frame with target := ref "another-target" } } } (ref "snapshot") = false := by decide
theorem cycle_has_no_seed : ¬ Derivable [] .ready := cyclic_rules_require_seed .ready

#print axioms legitimate_owned_condition
#print axioms legitimate_two_criterion_fulfillment
#print axioms changed_ast_without_approval_refuses
#print axioms contradictory_catalog_refuses
#print axioms no_owner_basis_refuses
#print axioms omitted_criterion_refuses
#print axioms missing_support_refuses
#print axioms legitimate_complete_qualification
#print axioms claimed_yes_without_evidence_refuses
#print axioms wrong_snapshot_refuses
#print axioms target_substitution_refuses
#print axioms cycle_has_no_seed
end RelationalSuccessor.Witnesses
