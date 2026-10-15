import RegistryKind5_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind5_endpoints : ∀ pair ∈ kind5.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind5, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4
  · subst pair; exact ⟨node_member_54, node_member_78⟩
  · subst pair; exact ⟨node_member_78, node_member_77⟩
  · subst pair; exact ⟨node_member_78, node_member_78⟩
  · subst pair; exact ⟨node_member_82, node_member_81⟩
  · cases h4
end Registry.Snapshot
