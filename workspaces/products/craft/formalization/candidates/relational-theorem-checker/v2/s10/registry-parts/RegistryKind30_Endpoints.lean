import RegistryKind30_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind30_endpoints : ∀ pair ∈ kind30.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind30, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19
  · subst pair; exact ⟨node_member_1, node_member_6⟩
  · subst pair; exact ⟨node_member_1, node_member_17⟩
  · subst pair; exact ⟨node_member_1, node_member_18⟩
  · subst pair; exact ⟨node_member_1, node_member_35⟩
  · subst pair; exact ⟨node_member_1, node_member_37⟩
  · subst pair; exact ⟨node_member_1, node_member_40⟩
  · subst pair; exact ⟨node_member_1, node_member_43⟩
  · subst pair; exact ⟨node_member_1, node_member_46⟩
  · subst pair; exact ⟨node_member_1, node_member_47⟩
  · subst pair; exact ⟨node_member_1, node_member_48⟩
  · subst pair; exact ⟨node_member_1, node_member_49⟩
  · subst pair; exact ⟨node_member_1, node_member_56⟩
  · subst pair; exact ⟨node_member_1, node_member_61⟩
  · subst pair; exact ⟨node_member_1, node_member_64⟩
  · subst pair; exact ⟨node_member_1, node_member_67⟩
  · subst pair; exact ⟨node_member_1, node_member_75⟩
  · subst pair; exact ⟨node_member_1, node_member_76⟩
  · subst pair; exact ⟨node_member_1, node_member_103⟩
  · subst pair; exact ⟨node_member_1, node_member_107⟩
  · cases h19
end Registry.Snapshot
