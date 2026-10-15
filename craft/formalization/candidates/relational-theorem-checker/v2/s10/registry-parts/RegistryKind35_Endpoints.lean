import RegistryKind35_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind35_endpoints : ∀ pair ∈ kind35.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind35, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3
  · subst pair; exact ⟨node_member_10, node_member_34⟩
  · subst pair; exact ⟨node_member_11, node_member_34⟩
  · subst pair; exact ⟨node_member_11, node_member_96⟩
  · cases h3
end Registry.Snapshot
