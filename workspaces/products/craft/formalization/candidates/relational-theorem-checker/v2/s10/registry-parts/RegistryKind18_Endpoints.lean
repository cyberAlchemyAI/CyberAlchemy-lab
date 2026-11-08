import RegistryKind18_Data
import RegistryNodeMembership
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
theorem kind18_endpoints : ∀ pair ∈ kind18.pairs, pair.1 ∈ nodes ∧ pair.2 ∈ nodes := by
  intro pair hk
  simp only [kind18, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22 | h23 | h24 | h25 | h26 | h27 | h28 | h29 | h30 | h31 | h32 | h33 | h34 | h35 | h36 | h37 | h38 | h39 | h40 | h41 | h42 | h43 | h44 | h45 | h46 | h47 | h48 | h49 | h50 | h51 | h52 | h53 | h54 | h55 | h56 | h57 | h58 | h59 | h60 | h61 | h62 | h63 | h64 | h65 | h66 | h67 | h68 | h69 | h70 | h71 | h72
  · subst pair; exact ⟨node_member_40, node_member_11⟩
  · subst pair; exact ⟨node_member_40, node_member_17⟩
  · subst pair; exact ⟨node_member_40, node_member_18⟩
  · subst pair; exact ⟨node_member_40, node_member_37⟩
  · subst pair; exact ⟨node_member_40, node_member_43⟩
  · subst pair; exact ⟨node_member_40, node_member_46⟩
  · subst pair; exact ⟨node_member_40, node_member_48⟩
  · subst pair; exact ⟨node_member_40, node_member_53⟩
  · subst pair; exact ⟨node_member_40, node_member_54⟩
  · subst pair; exact ⟨node_member_40, node_member_56⟩
  · subst pair; exact ⟨node_member_40, node_member_62⟩
  · subst pair; exact ⟨node_member_40, node_member_75⟩
  · subst pair; exact ⟨node_member_40, node_member_80⟩
  · subst pair; exact ⟨node_member_40, node_member_107⟩
  · subst pair; exact ⟨node_member_47, node_member_17⟩
  · subst pair; exact ⟨node_member_47, node_member_18⟩
  · subst pair; exact ⟨node_member_47, node_member_37⟩
  · subst pair; exact ⟨node_member_47, node_member_43⟩
  · subst pair; exact ⟨node_member_47, node_member_46⟩
  · subst pair; exact ⟨node_member_47, node_member_56⟩
  · subst pair; exact ⟨node_member_47, node_member_62⟩
  · subst pair; exact ⟨node_member_47, node_member_75⟩
  · subst pair; exact ⟨node_member_47, node_member_80⟩
  · subst pair; exact ⟨node_member_47, node_member_107⟩
  · subst pair; exact ⟨node_member_48, node_member_17⟩
  · subst pair; exact ⟨node_member_48, node_member_18⟩
  · subst pair; exact ⟨node_member_48, node_member_37⟩
  · subst pair; exact ⟨node_member_48, node_member_43⟩
  · subst pair; exact ⟨node_member_48, node_member_46⟩
  · subst pair; exact ⟨node_member_48, node_member_56⟩
  · subst pair; exact ⟨node_member_48, node_member_62⟩
  · subst pair; exact ⟨node_member_48, node_member_75⟩
  · subst pair; exact ⟨node_member_48, node_member_80⟩
  · subst pair; exact ⟨node_member_48, node_member_107⟩
  · subst pair; exact ⟨node_member_64, node_member_11⟩
  · subst pair; exact ⟨node_member_64, node_member_17⟩
  · subst pair; exact ⟨node_member_64, node_member_18⟩
  · subst pair; exact ⟨node_member_64, node_member_37⟩
  · subst pair; exact ⟨node_member_64, node_member_43⟩
  · subst pair; exact ⟨node_member_64, node_member_46⟩
  · subst pair; exact ⟨node_member_64, node_member_48⟩
  · subst pair; exact ⟨node_member_64, node_member_53⟩
  · subst pair; exact ⟨node_member_64, node_member_54⟩
  · subst pair; exact ⟨node_member_64, node_member_56⟩
  · subst pair; exact ⟨node_member_64, node_member_62⟩
  · subst pair; exact ⟨node_member_64, node_member_75⟩
  · subst pair; exact ⟨node_member_64, node_member_80⟩
  · subst pair; exact ⟨node_member_64, node_member_107⟩
  · subst pair; exact ⟨node_member_67, node_member_11⟩
  · subst pair; exact ⟨node_member_67, node_member_17⟩
  · subst pair; exact ⟨node_member_67, node_member_18⟩
  · subst pair; exact ⟨node_member_67, node_member_37⟩
  · subst pair; exact ⟨node_member_67, node_member_43⟩
  · subst pair; exact ⟨node_member_67, node_member_46⟩
  · subst pair; exact ⟨node_member_67, node_member_48⟩
  · subst pair; exact ⟨node_member_67, node_member_53⟩
  · subst pair; exact ⟨node_member_67, node_member_54⟩
  · subst pair; exact ⟨node_member_67, node_member_56⟩
  · subst pair; exact ⟨node_member_67, node_member_62⟩
  · subst pair; exact ⟨node_member_67, node_member_75⟩
  · subst pair; exact ⟨node_member_67, node_member_80⟩
  · subst pair; exact ⟨node_member_67, node_member_107⟩
  · subst pair; exact ⟨node_member_76, node_member_17⟩
  · subst pair; exact ⟨node_member_76, node_member_18⟩
  · subst pair; exact ⟨node_member_76, node_member_37⟩
  · subst pair; exact ⟨node_member_76, node_member_43⟩
  · subst pair; exact ⟨node_member_76, node_member_46⟩
  · subst pair; exact ⟨node_member_76, node_member_56⟩
  · subst pair; exact ⟨node_member_76, node_member_62⟩
  · subst pair; exact ⟨node_member_76, node_member_75⟩
  · subst pair; exact ⟨node_member_76, node_member_80⟩
  · subst pair; exact ⟨node_member_76, node_member_107⟩
  · cases h72
end Registry.Snapshot
