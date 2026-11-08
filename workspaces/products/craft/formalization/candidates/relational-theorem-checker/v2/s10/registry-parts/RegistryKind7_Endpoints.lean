import RegistryKind7_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind7_endpoints : ∀ pair ∈ kind7.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind7, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2
  · subst pair; exact ⟨node_member_55, node_member_68⟩
  · subst pair; exact ⟨node_member_55, node_member_97⟩
  · cases h2
end Registry.Snapshot
