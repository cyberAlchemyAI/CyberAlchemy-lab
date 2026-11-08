import RegistryKind16_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind16_endpoints : ∀ pair ∈ kind16.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind16, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4
  · subst pair; exact ⟨node_member_41, node_member_91⟩
  · subst pair; exact ⟨node_member_42, node_member_91⟩
  · subst pair; exact ⟨node_member_48, node_member_91⟩
  · subst pair; exact ⟨node_member_92, node_member_91⟩
  · cases h4
end Registry.Snapshot
