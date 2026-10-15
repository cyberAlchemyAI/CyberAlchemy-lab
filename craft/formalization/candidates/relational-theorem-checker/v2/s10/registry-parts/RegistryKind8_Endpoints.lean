import RegistryKind8_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind8_endpoints : ∀ pair ∈ kind8.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind8, List.mem_cons] at hk
  rcases hk with h0 | h1
  · subst pair; exact ⟨node_member_8, node_member_35⟩
  · cases h1
end Registry.Snapshot
