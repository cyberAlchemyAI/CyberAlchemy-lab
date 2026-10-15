import RegistryKind22_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind22_endpoints : ∀ pair ∈ kind22.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind22, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2
  · subst pair; exact ⟨node_member_4, node_member_3⟩
  · subst pair; exact ⟨node_member_5, node_member_3⟩
  · cases h2
end Registry.Snapshot
