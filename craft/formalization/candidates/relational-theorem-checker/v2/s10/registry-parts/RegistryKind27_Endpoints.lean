import RegistryKind27_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind27_endpoints : ∀ pair ∈ kind27.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind27, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5
  · subst pair; exact ⟨node_member_46, node_member_1⟩
  · subst pair; exact ⟨node_member_46, node_member_7⟩
  · subst pair; exact ⟨node_member_46, node_member_42⟩
  · subst pair; exact ⟨node_member_46, node_member_92⟩
  · subst pair; exact ⟨node_member_46, node_member_106⟩
  · cases h5
end Registry.Snapshot
