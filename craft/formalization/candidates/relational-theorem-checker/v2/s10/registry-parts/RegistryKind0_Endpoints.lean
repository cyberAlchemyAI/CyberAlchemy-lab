import RegistryKind0_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind0_endpoints : ∀ pair ∈ kind0.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind0, List.mem_cons] at hk
  rcases hk with h0 | h1
  · subst pair; exact ⟨node_member_4, node_member_81⟩
  · cases h1
end Registry.Snapshot
