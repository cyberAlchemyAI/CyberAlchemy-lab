import RegistryKind25_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind25_endpoints : ∀ pair ∈ kind25.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind25, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4
  · subst pair; exact ⟨node_member_0, node_member_49⟩
  · subst pair; exact ⟨node_member_0, node_member_87⟩
  · subst pair; exact ⟨node_member_0, node_member_88⟩
  · subst pair; exact ⟨node_member_0, node_member_89⟩
  · cases h4
end Registry.Snapshot
