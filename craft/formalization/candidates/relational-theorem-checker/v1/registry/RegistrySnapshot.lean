import RegistryKind0
import RegistryKind1
import RegistryKind2
import RegistryKind3
import RegistryKind4
import RegistryKind5
import RegistryKind6
import RegistryKind7
import RegistryKind8
import RegistryKind9
import RegistryKind10
import RegistryKind11
import RegistryKind12
import RegistryKind13
import RegistryKind14
import RegistryKind15
import RegistryKind16
import RegistryKind17
import RegistryKind18
import RegistryKind19
import RegistryKind20
import RegistryKind21
import RegistryKind22
import RegistryKind23
import RegistryKind24
import RegistryKind25
import RegistryKind26
import RegistryKind27
import RegistryKind28
import RegistryKind29
import RegistryKind30
import RegistryKind31
import RegistryKind32
import RegistryKind33
import RegistryKind34
import RegistryKind35
import RegistryKind36
import RegistryKind37
import RegistryKind38
import RegistryKind39
import RegistryKind40
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def captured : Theory := { nodeKinds := nodes, kinds := [kind0, kind1, kind2, kind3, kind4, kind5, kind6, kind7, kind8, kind9, kind10, kind11, kind12, kind13, kind14, kind15, kind16, kind17, kind18, kind19, kind20, kind21, kind22, kind23, kind24, kind25, kind26, kind27, kind28, kind29, kind30, kind31, kind32, kind33, kind34, kind35, kind36, kind37, kind38, kind39, kind40] }
theorem kinds_unique : (captured.kinds.map Kind.id).Nodup := by decide
theorem kinds_valid : ∀ k ∈ captured.kinds, KindValid captured.nodeKinds k := by
  intro k hk
  simp only [captured, List.mem_cons] at hk
  rcases hk with h0 | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | h17 | h18 | h19 | h20 | h21 | h22 | h23 | h24 | h25 | h26 | h27 | h28 | h29 | h30 | h31 | h32 | h33 | h34 | h35 | h36 | h37 | h38 | h39 | h40 | h41
  · subst k; exact kind_valid0
  · subst k; exact kind_valid1
  · subst k; exact kind_valid2
  · subst k; exact kind_valid3
  · subst k; exact kind_valid4
  · subst k; exact kind_valid5
  · subst k; exact kind_valid6
  · subst k; exact kind_valid7
  · subst k; exact kind_valid8
  · subst k; exact kind_valid9
  · subst k; exact kind_valid10
  · subst k; exact kind_valid11
  · subst k; exact kind_valid12
  · subst k; exact kind_valid13
  · subst k; exact kind_valid14
  · subst k; exact kind_valid15
  · subst k; exact kind_valid16
  · subst k; exact kind_valid17
  · subst k; exact kind_valid18
  · subst k; exact kind_valid19
  · subst k; exact kind_valid20
  · subst k; exact kind_valid21
  · subst k; exact kind_valid22
  · subst k; exact kind_valid23
  · subst k; exact kind_valid24
  · subst k; exact kind_valid25
  · subst k; exact kind_valid26
  · subst k; exact kind_valid27
  · subst k; exact kind_valid28
  · subst k; exact kind_valid29
  · subst k; exact kind_valid30
  · subst k; exact kind_valid31
  · subst k; exact kind_valid32
  · subst k; exact kind_valid33
  · subst k; exact kind_valid34
  · subst k; exact kind_valid35
  · subst k; exact kind_valid36
  · subst k; exact kind_valid37
  · subst k; exact kind_valid38
  · subst k; exact kind_valid39
  · subst k; exact kind_valid40
  · cases h41
theorem valid_snapshot : TheoryValid captured := ⟨nodes_unique, nodes_named, kinds_unique, kinds_valid⟩
def RequiredPairOrigin : Prop := ∀ (r : Theory) (g : Graph) (e : Assertion), checkInstance r g e = true → ∃ source ∈ g.nodes, ∃ target ∈ g.nodes, ∃ kind ∈ r.kinds, source.ref = e.source ∧ target.ref = e.target ∧ kind.id = e.kindId ∧ kind.version = e.kindVersion ∧ (source.kind,target.kind) ∈ kind.pairs
theorem audited_pair_origin : RequiredPairOrigin := accepted_pair_has_origin
#print axioms instance_checker_iff
#print axioms graph_checker_iff
#print axioms accepted_pair_has_origin
#print axioms valid_snapshot
#print axioms audited_pair_origin
end Registry.Snapshot
