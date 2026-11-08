import RegistryKind3_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind3_endpoints : ∀ pair ∈ kind3.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind3, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22
  · subst pair; exact ⟨node_member_46, node_member_3⟩
  · subst pair; exact ⟨node_member_46, node_member_7⟩
  · subst pair; exact ⟨node_member_46, node_member_8⟩
  · subst pair; exact ⟨node_member_46, node_member_49⟩
  · subst pair; exact ⟨node_member_46, node_member_55⟩
  · subst pair; exact ⟨node_member_46, node_member_68⟩
  · subst pair; exact ⟨node_member_46, node_member_78⟩
  · subst pair; exact ⟨node_member_46, node_member_83⟩
  · subst pair; exact ⟨node_member_46, node_member_84⟩
  · subst pair; exact ⟨node_member_46, node_member_86⟩
  · subst pair; exact ⟨node_member_46, node_member_106⟩
  · subst pair; exact ⟨node_member_58, node_member_3⟩
  · subst pair; exact ⟨node_member_58, node_member_7⟩
  · subst pair; exact ⟨node_member_58, node_member_8⟩
  · subst pair; exact ⟨node_member_58, node_member_49⟩
  · subst pair; exact ⟨node_member_58, node_member_55⟩
  · subst pair; exact ⟨node_member_58, node_member_68⟩
  · subst pair; exact ⟨node_member_58, node_member_78⟩
  · subst pair; exact ⟨node_member_58, node_member_83⟩
  · subst pair; exact ⟨node_member_58, node_member_84⟩
  · subst pair; exact ⟨node_member_58, node_member_86⟩
  · subst pair; exact ⟨node_member_58, node_member_106⟩
  · cases h22
end Registry.Snapshot
