import RegistryKind17_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind17_endpoints : ∀ pair ∈ kind17.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind17, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16
  · subst pair; exact ⟨node_member_39, node_member_15⟩
  · subst pair; exact ⟨node_member_39, node_member_84⟩
  · subst pair; exact ⟨node_member_39, node_member_85⟩
  · subst pair; exact ⟨node_member_41, node_member_15⟩
  · subst pair; exact ⟨node_member_41, node_member_83⟩
  · subst pair; exact ⟨node_member_41, node_member_84⟩
  · subst pair; exact ⟨node_member_41, node_member_85⟩
  · subst pair; exact ⟨node_member_42, node_member_15⟩
  · subst pair; exact ⟨node_member_42, node_member_83⟩
  · subst pair; exact ⟨node_member_42, node_member_84⟩
  · subst pair; exact ⟨node_member_42, node_member_85⟩
  · subst pair; exact ⟨node_member_43, node_member_46⟩
  · subst pair; exact ⟨node_member_62, node_member_61⟩
  · subst pair; exact ⟨node_member_80, node_member_21⟩
  · subst pair; exact ⟨node_member_107, node_member_1⟩
  · subst pair; exact ⟨node_member_107, node_member_106⟩
  · cases h16
end Registry.Snapshot
