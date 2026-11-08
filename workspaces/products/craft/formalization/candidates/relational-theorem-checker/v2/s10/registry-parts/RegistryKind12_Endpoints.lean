import RegistryKind12_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind12_endpoints : ∀ pair ∈ kind12.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind12, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8
  · subst pair; exact ⟨node_member_1, node_member_50⟩
  · subst pair; exact ⟨node_member_1, node_member_83⟩
  · subst pair; exact ⟨node_member_41, node_member_50⟩
  · subst pair; exact ⟨node_member_42, node_member_50⟩
  · subst pair; exact ⟨node_member_86, node_member_50⟩
  · subst pair; exact ⟨node_member_86, node_member_83⟩
  · subst pair; exact ⟨node_member_91, node_member_50⟩
  · subst pair; exact ⟨node_member_92, node_member_50⟩
  · cases h8
end Registry.Snapshot
