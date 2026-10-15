import RegistryKind34_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind34_endpoints : ∀ pair ∈ kind34.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind34, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2
  · subst pair; exact ⟨node_member_1, node_member_46⟩
  · subst pair; exact ⟨node_member_1, node_member_58⟩
  · cases h2
end Registry.Snapshot
