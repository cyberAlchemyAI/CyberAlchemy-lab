import RegistryKind38_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind38_endpoints : ∀ pair ∈ kind38.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind38, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7
  · subst pair; exact ⟨node_member_1, node_member_65⟩
  · subst pair; exact ⟨node_member_42, node_member_65⟩
  · subst pair; exact ⟨node_member_64, node_member_65⟩
  · subst pair; exact ⟨node_member_67, node_member_65⟩
  · subst pair; exact ⟨node_member_83, node_member_65⟩
  · subst pair; exact ⟨node_member_86, node_member_65⟩
  · subst pair; exact ⟨node_member_92, node_member_65⟩
  · cases h7
end Registry.Snapshot
