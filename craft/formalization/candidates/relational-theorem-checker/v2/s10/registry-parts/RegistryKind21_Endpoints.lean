import RegistryKind21_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind21_endpoints : ∀ pair ∈ kind21.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind21, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22 | h23 | h24 | h25 | h26 | h27 | h28 | h29
  · subst pair; exact ⟨node_member_0, node_member_79⟩
  · subst pair; exact ⟨node_member_1, node_member_79⟩
  · subst pair; exact ⟨node_member_4, node_member_79⟩
  · subst pair; exact ⟨node_member_5, node_member_79⟩
  · subst pair; exact ⟨node_member_7, node_member_79⟩
  · subst pair; exact ⟨node_member_8, node_member_22⟩
  · subst pair; exact ⟨node_member_10, node_member_79⟩
  · subst pair; exact ⟨node_member_16, node_member_79⟩
  · subst pair; exact ⟨node_member_17, node_member_16⟩
  · subst pair; exact ⟨node_member_18, node_member_19⟩
  · subst pair; exact ⟨node_member_18, node_member_79⟩
  · subst pair; exact ⟨node_member_21, node_member_79⟩
  · subst pair; exact ⟨node_member_23, node_member_79⟩
  · subst pair; exact ⟨node_member_32, node_member_79⟩
  · subst pair; exact ⟨node_member_33, node_member_79⟩
  · subst pair; exact ⟨node_member_35, node_member_22⟩
  · subst pair; exact ⟨node_member_43, node_member_79⟩
  · subst pair; exact ⟨node_member_44, node_member_79⟩
  · subst pair; exact ⟨node_member_45, node_member_79⟩
  · subst pair; exact ⟨node_member_46, node_member_79⟩
  · subst pair; exact ⟨node_member_47, node_member_79⟩
  · subst pair; exact ⟨node_member_58, node_member_79⟩
  · subst pair; exact ⟨node_member_68, node_member_79⟩
  · subst pair; exact ⟨node_member_70, node_member_79⟩
  · subst pair; exact ⟨node_member_72, node_member_79⟩
  · subst pair; exact ⟨node_member_75, node_member_79⟩
  · subst pair; exact ⟨node_member_90, node_member_22⟩
  · subst pair; exact ⟨node_member_105, node_member_79⟩
  · subst pair; exact ⟨node_member_108, node_member_79⟩
  · cases h29
end Registry.Snapshot
