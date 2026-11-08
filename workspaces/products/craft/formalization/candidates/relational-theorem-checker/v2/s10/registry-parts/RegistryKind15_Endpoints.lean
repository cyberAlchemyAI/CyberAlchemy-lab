import RegistryKind15_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind15_endpoints : ∀ pair ∈ kind15.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind15, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22 | h23 | h24 | h25 | h26 | h27 | h28 | h29 | h30 | h31 | h32 | h33 | h34 | h35 | h36 | h37 | h38 | h39 | h40
  · subst pair; exact ⟨node_member_6, node_member_1⟩
  · subst pair; exact ⟨node_member_6, node_member_7⟩
  · subst pair; exact ⟨node_member_6, node_member_40⟩
  · subst pair; exact ⟨node_member_6, node_member_43⟩
  · subst pair; exact ⟨node_member_6, node_member_47⟩
  · subst pair; exact ⟨node_member_6, node_member_48⟩
  · subst pair; exact ⟨node_member_6, node_member_67⟩
  · subst pair; exact ⟨node_member_6, node_member_76⟩
  · subst pair; exact ⟨node_member_6, node_member_107⟩
  · subst pair; exact ⟨node_member_18, node_member_40⟩
  · subst pair; exact ⟨node_member_18, node_member_47⟩
  · subst pair; exact ⟨node_member_18, node_member_48⟩
  · subst pair; exact ⟨node_member_18, node_member_64⟩
  · subst pair; exact ⟨node_member_18, node_member_67⟩
  · subst pair; exact ⟨node_member_18, node_member_76⟩
  · subst pair; exact ⟨node_member_18, node_member_99⟩
  · subst pair; exact ⟨node_member_29, node_member_23⟩
  · subst pair; exact ⟨node_member_40, node_member_42⟩
  · subst pair; exact ⟨node_member_40, node_member_92⟩
  · subst pair; exact ⟨node_member_48, node_member_40⟩
  · subst pair; exact ⟨node_member_48, node_member_92⟩
  · subst pair; exact ⟨node_member_49, node_member_99⟩
  · subst pair; exact ⟨node_member_56, node_member_37⟩
  · subst pair; exact ⟨node_member_56, node_member_43⟩
  · subst pair; exact ⟨node_member_56, node_member_76⟩
  · subst pair; exact ⟨node_member_56, node_member_107⟩
  · subst pair; exact ⟨node_member_57, node_member_56⟩
  · subst pair; exact ⟨node_member_57, node_member_62⟩
  · subst pair; exact ⟨node_member_57, node_member_75⟩
  · subst pair; exact ⟨node_member_64, node_member_42⟩
  · subst pair; exact ⟨node_member_64, node_member_92⟩
  · subst pair; exact ⟨node_member_67, node_member_42⟩
  · subst pair; exact ⟨node_member_67, node_member_92⟩
  · subst pair; exact ⟨node_member_75, node_member_6⟩
  · subst pair; exact ⟨node_member_75, node_member_40⟩
  · subst pair; exact ⟨node_member_75, node_member_43⟩
  · subst pair; exact ⟨node_member_75, node_member_47⟩
  · subst pair; exact ⟨node_member_75, node_member_48⟩
  · subst pair; exact ⟨node_member_75, node_member_62⟩
  · subst pair; exact ⟨node_member_84, node_member_85⟩
  · cases h40
end Registry.Snapshot
