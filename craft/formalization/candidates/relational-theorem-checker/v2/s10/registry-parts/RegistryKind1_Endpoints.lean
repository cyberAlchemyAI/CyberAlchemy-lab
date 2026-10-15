import RegistryKind1_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind1_endpoints : ∀ pair ∈ kind1.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind1, List.mem_cons] at hk
  rcases hk with h0 | h1
  · subst pair; exact ⟨node_member_91, node_member_57⟩
  · cases h1
end Registry.Snapshot
