import RegistryKind14_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind14_endpoints : ∀ pair ∈ kind14.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind14, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21
  · subst pair; exact ⟨node_member_31, node_member_3⟩
  · subst pair; exact ⟨node_member_31, node_member_5⟩
  · subst pair; exact ⟨node_member_31, node_member_8⟩
  · subst pair; exact ⟨node_member_31, node_member_15⟩
  · subst pair; exact ⟨node_member_31, node_member_17⟩
  · subst pair; exact ⟨node_member_31, node_member_18⟩
  · subst pair; exact ⟨node_member_31, node_member_21⟩
  · subst pair; exact ⟨node_member_31, node_member_35⟩
  · subst pair; exact ⟨node_member_31, node_member_36⟩
  · subst pair; exact ⟨node_member_31, node_member_38⟩
  · subst pair; exact ⟨node_member_31, node_member_43⟩
  · subst pair; exact ⟨node_member_31, node_member_44⟩
  · subst pair; exact ⟨node_member_31, node_member_45⟩
  · subst pair; exact ⟨node_member_31, node_member_46⟩
  · subst pair; exact ⟨node_member_31, node_member_52⟩
  · subst pair; exact ⟨node_member_31, node_member_57⟩
  · subst pair; exact ⟨node_member_31, node_member_58⟩
  · subst pair; exact ⟨node_member_31, node_member_60⟩
  · subst pair; exact ⟨node_member_31, node_member_75⟩
  · subst pair; exact ⟨node_member_31, node_member_84⟩
  · subst pair; exact ⟨node_member_31, node_member_90⟩
  · cases h21
end Registry.Snapshot
