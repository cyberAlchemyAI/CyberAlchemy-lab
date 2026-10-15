import RegistryKind11_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind11_endpoints : ∀ pair ∈ kind11.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind11, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2
  · subst pair; exact ⟨node_member_7, node_member_29⟩
  · subst pair; exact ⟨node_member_7, node_member_74⟩
  · cases h2
end Registry.Snapshot
