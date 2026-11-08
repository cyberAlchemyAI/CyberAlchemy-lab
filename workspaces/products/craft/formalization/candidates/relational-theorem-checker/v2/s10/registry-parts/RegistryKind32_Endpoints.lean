import RegistryKind32_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind32_endpoints : ∀ pair ∈ kind32.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind32, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2
  · subst pair; exact ⟨node_member_42, node_member_41⟩
  · subst pair; exact ⟨node_member_55, node_member_84⟩
  · cases h2
end Registry.Snapshot
