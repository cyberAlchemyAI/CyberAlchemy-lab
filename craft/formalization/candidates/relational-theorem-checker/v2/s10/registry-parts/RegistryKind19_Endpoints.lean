import RegistryKind19_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind19_endpoints : ∀ pair ∈ kind19.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind19, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5
  · subst pair; exact ⟨node_member_23, node_member_12⟩
  · subst pair; exact ⟨node_member_23, node_member_50⟩
  · subst pair; exact ⟨node_member_23, node_member_83⟩
  · subst pair; exact ⟨node_member_23, node_member_86⟩
  · subst pair; exact ⟨node_member_23, node_member_94⟩
  · cases h5
end Registry.Snapshot
