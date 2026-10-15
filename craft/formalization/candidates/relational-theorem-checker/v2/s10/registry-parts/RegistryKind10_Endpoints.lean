import RegistryKind10_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind10_endpoints : ∀ pair ∈ kind10.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind10, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3
  · subst pair; exact ⟨node_member_14, node_member_30⟩
  · subst pair; exact ⟨node_member_14, node_member_52⟩
  · subst pair; exact ⟨node_member_23, node_member_27⟩
  · cases h3
end Registry.Snapshot
