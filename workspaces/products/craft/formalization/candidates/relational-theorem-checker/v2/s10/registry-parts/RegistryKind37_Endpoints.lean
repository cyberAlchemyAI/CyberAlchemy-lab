import RegistryKind37_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind37_endpoints : ∀ pair ∈ kind37.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind37, List.mem_cons] at hk
  rcases hk with h0 | h1
  · subst pair; exact ⟨node_member_41, node_member_53⟩
  · cases h1
end Registry.Snapshot
