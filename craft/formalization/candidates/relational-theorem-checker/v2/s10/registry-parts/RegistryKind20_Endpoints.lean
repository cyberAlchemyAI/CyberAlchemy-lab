import RegistryKind20_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind20_endpoints : ∀ pair ∈ kind20.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind20, List.mem_cons] at hk
  rcases hk with h0 | h1
  · subst pair; exact ⟨node_member_29, node_member_28⟩
  · cases h1
end Registry.Snapshot
