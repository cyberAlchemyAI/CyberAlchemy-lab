import RegistryKind40_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind40_endpoints : ∀ pair ∈ kind40.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind40, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4
  · subst pair; exact ⟨node_member_46, node_member_16⟩
  · subst pair; exact ⟨node_member_46, node_member_30⟩
  · subst pair; exact ⟨node_member_46, node_member_79⟩
  · subst pair; exact ⟨node_member_46, node_member_97⟩
  · cases h4
end Registry.Snapshot
