import ChainSemantics
set_option maxRecDepth 4096
open RelationalExtensions.Chain
namespace ChainInstance
def q : Query := ⟨⟨"Alice", "v1"⟩, ⟨"Carol", "v1"⟩, "review", "approve", 5⟩
def edges : List Hop := [⟨⟨"hop0", "v1"⟩, ⟨"Alice", "v1"⟩, ⟨"Bob", "v1"⟩, ["review"], ["approve"], 0, 10, true, .yes, .no⟩, ⟨⟨"hop1", "v1"⟩, ⟨"Bob", "v1"⟩, ⟨"Carol", "v1"⟩, ["review", "administration"], ["approve"], 0, 10, true, .yes, .no⟩]
def depth : Nat := 2
theorem full_count : (pathUniverse edges depth).length = 6 := by decide
theorem all_positive_paths : supported q edges depth = [] := by decide
theorem all_unknown_paths : undecided q edges depth = [] := by decide
theorem complete_verdict : query q edges depth = .no := by decide
theorem each_reported_ancestor : ∀ p ∈ supported q edges depth, ∀ h ∈ p, q.scope ∈ h.scopes ∧ q.action ∈ h.actions ∧ h.start ≤ q.epoch ∧ q.epoch < h.finish := by intro p hp; exact reported_path_non_amplification q edges depth p hp
#print axioms full_count
#print axioms all_positive_paths
#print axioms all_unknown_paths
#print axioms complete_verdict
#print axioms each_reported_ancestor
end ChainInstance
