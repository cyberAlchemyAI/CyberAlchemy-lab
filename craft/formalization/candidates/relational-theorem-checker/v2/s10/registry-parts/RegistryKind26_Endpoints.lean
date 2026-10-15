import RegistryKind26_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind26_endpoints : ∀ pair ∈ kind26.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind26, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22 | h23 | h24
  · subst pair; exact ⟨node_member_1, node_member_7⟩
  · subst pair; exact ⟨node_member_2, node_member_86⟩
  · subst pair; exact ⟨node_member_4, node_member_7⟩
  · subst pair; exact ⟨node_member_15, node_member_86⟩
  · subst pair; exact ⟨node_member_20, node_member_19⟩
  · subst pair; exact ⟨node_member_23, node_member_83⟩
  · subst pair; exact ⟨node_member_23, node_member_86⟩
  · subst pair; exact ⟨node_member_31, node_member_32⟩
  · subst pair; exact ⟨node_member_40, node_member_86⟩
  · subst pair; exact ⟨node_member_41, node_member_86⟩
  · subst pair; exact ⟨node_member_42, node_member_86⟩
  · subst pair; exact ⟨node_member_46, node_member_58⟩
  · subst pair; exact ⟨node_member_50, node_member_86⟩
  · subst pair; exact ⟨node_member_72, node_member_68⟩
  · subst pair; exact ⟨node_member_78, node_member_100⟩
  · subst pair; exact ⟨node_member_83, node_member_83⟩
  · subst pair; exact ⟨node_member_84, node_member_83⟩
  · subst pair; exact ⟨node_member_85, node_member_83⟩
  · subst pair; exact ⟨node_member_89, node_member_86⟩
  · subst pair; exact ⟨node_member_91, node_member_86⟩
  · subst pair; exact ⟨node_member_92, node_member_86⟩
  · subst pair; exact ⟨node_member_93, node_member_95⟩
  · subst pair; exact ⟨node_member_103, node_member_68⟩
  · subst pair; exact ⟨node_member_106, node_member_86⟩
  · cases h24
end Registry.Snapshot
