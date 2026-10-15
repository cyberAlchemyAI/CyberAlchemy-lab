import RegistryKind29_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind29_endpoints : ∀ pair ∈ kind29.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind29, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5
  · subst pair; exact ⟨node_member_4, node_member_1⟩
  · subst pair; exact ⟨node_member_4, node_member_42⟩
  · subst pair; exact ⟨node_member_4, node_member_92⟩
  · subst pair; exact ⟨node_member_4, node_member_94⟩
  · subst pair; exact ⟨node_member_4, node_member_106⟩
  · cases h5
end Registry.Snapshot
