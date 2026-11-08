import RegistryKind24_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind24_endpoints : ∀ pair ∈ kind24.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind24, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12
  · subst pair; exact ⟨node_member_1, node_member_20⟩
  · subst pair; exact ⟨node_member_4, node_member_20⟩
  · subst pair; exact ⟨node_member_14, node_member_52⟩
  · subst pair; exact ⟨node_member_14, node_member_84⟩
  · subst pair; exact ⟨node_member_45, node_member_20⟩
  · subst pair; exact ⟨node_member_46, node_member_20⟩
  · subst pair; exact ⟨node_member_46, node_member_45⟩
  · subst pair; exact ⟨node_member_55, node_member_52⟩
  · subst pair; exact ⟨node_member_55, node_member_84⟩
  · subst pair; exact ⟨node_member_57, node_member_20⟩
  · subst pair; exact ⟨node_member_75, node_member_20⟩
  · subst pair; exact ⟨node_member_84, node_member_83⟩
  · cases h12
end Registry.Snapshot
