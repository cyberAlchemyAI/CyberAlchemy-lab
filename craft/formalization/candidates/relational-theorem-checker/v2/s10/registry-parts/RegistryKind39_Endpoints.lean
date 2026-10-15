import RegistryKind39_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind39_endpoints : ∀ pair ∈ kind39.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind39, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4
  · subst pair; exact ⟨node_member_1, node_member_55⟩
  · subst pair; exact ⟨node_member_1, node_member_102⟩
  · subst pair; exact ⟨node_member_7, node_member_55⟩
  · subst pair; exact ⟨node_member_7, node_member_102⟩
  · cases h4
end Registry.Snapshot
