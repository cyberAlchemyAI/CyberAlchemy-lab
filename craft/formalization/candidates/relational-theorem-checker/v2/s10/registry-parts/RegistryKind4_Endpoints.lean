import RegistryKind4_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind4_endpoints : ∀ pair ∈ kind4.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind4, List.mem_cons] at hk
  rcases hk with h0 | h1
  · subst pair; exact ⟨node_member_61, node_member_75⟩
  · cases h1
end Registry.Snapshot
