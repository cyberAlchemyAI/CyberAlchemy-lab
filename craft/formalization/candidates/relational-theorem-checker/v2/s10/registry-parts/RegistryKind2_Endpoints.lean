import RegistryKind2_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind2_endpoints : ∀ pair ∈ kind2.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind2, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6
  · subst pair; exact ⟨node_member_2, node_member_59⟩
  · subst pair; exact ⟨node_member_50, node_member_59⟩
  · subst pair; exact ⟨node_member_83, node_member_59⟩
  · subst pair; exact ⟨node_member_84, node_member_59⟩
  · subst pair; exact ⟨node_member_86, node_member_59⟩
  · subst pair; exact ⟨node_member_91, node_member_59⟩
  · cases h6
end Registry.Snapshot
