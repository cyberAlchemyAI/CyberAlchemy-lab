import RegistryKind6_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind6_endpoints : ∀ pair ∈ kind6.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind6, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6
  · subst pair; exact ⟨node_member_4, node_member_93⟩
  · subst pair; exact ⟨node_member_4, node_member_95⟩
  · subst pair; exact ⟨node_member_78, node_member_93⟩
  · subst pair; exact ⟨node_member_78, node_member_95⟩
  · subst pair; exact ⟨node_member_100, node_member_93⟩
  · subst pair; exact ⟨node_member_100, node_member_95⟩
  · cases h6
end Registry.Snapshot
