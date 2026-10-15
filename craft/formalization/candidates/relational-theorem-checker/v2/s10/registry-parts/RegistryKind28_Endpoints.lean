import RegistryKind28_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind28_endpoints : ∀ pair ∈ kind28.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind28, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7
  · subst pair; exact ⟨node_member_8, node_member_99⟩
  · subst pair; exact ⟨node_member_35, node_member_99⟩
  · subst pair; exact ⟨node_member_37, node_member_99⟩
  · subst pair; exact ⟨node_member_47, node_member_99⟩
  · subst pair; exact ⟨node_member_48, node_member_99⟩
  · subst pair; exact ⟨node_member_76, node_member_99⟩
  · subst pair; exact ⟨node_member_90, node_member_99⟩
  · cases h7
end Registry.Snapshot
