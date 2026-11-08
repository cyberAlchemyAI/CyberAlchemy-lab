import RegistryChecker

namespace Registry.Evolution

-- Structural assumptions can be checked without assuming preservation itself.
structure FreshExtension (base expanded : Theory) where
  added : List Kind
  nodes_equal : expanded.nodeKinds = base.nodeKinds
  kinds_append : expanded.kinds = base.kinds ++ added
  fresh_ids : ∀ d ∈ added, d.id ∉ base.kinds.map Kind.id
  base_valid : TheoryValid base
  expanded_valid : TheoryValid expanded

def OldLanguage (base : Theory) (g : Graph) : Prop :=
  ∀ e ∈ g.assertions, e.kindId ∈ base.kinds.map Kind.id

theorem lift_instance {base expanded : Theory} (h : FreshExtension base expanded)
    (g : Graph) (e : Assertion) (valid : InstanceValid base g e) :
    InstanceValid expanded g e := by
  rcases valid with ⟨id, source, hs, target, ht, sr, tr, d, hd, kid, ver, pair, qualifiers⟩
  have included : d ∈ expanded.kinds := by
    rw [h.kinds_append]
    exact List.mem_append.mpr (Or.inl hd)
  exact ⟨id, source, hs, target, ht, sr, tr, d, included, kid, ver, pair, qualifiers⟩

theorem reflect_old_instance {base expanded : Theory} (h : FreshExtension base expanded)
    (g : Graph) (e : Assertion) (old : e.kindId ∈ base.kinds.map Kind.id)
    (valid : InstanceValid expanded g e) : InstanceValid base g e := by
  rcases valid with ⟨id, source, hs, target, ht, sr, tr, d, hd, kid, ver, pair, qualifiers⟩
  rw [h.kinds_append] at hd
  rcases List.mem_append.mp hd with hb | ha
  · exact ⟨id, source, hs, target, ht, sr, tr, d, hb, kid, ver, pair, qualifiers⟩
  · have impossible : d.id ∈ base.kinds.map Kind.id := by simpa [kid] using old
    exact False.elim (h.fresh_ids d ha impossible)

theorem lift_model {base expanded : Theory} (h : FreshExtension base expanded)
    (g : Graph) (valid : Inv base g) : Inv expanded g := by
  rcases valid with ⟨_, nodeKeys, nodes, edgeKeys, edges⟩
  refine ⟨h.expanded_valid, nodeKeys, ?_, edgeKeys, ?_⟩
  · intro n hn
    simpa only [h.nodes_equal] using nodes n hn
  · intro e he
    exact lift_instance h g e (edges e he)

theorem reflect_old_model {base expanded : Theory} (h : FreshExtension base expanded)
    (g : Graph) (old : OldLanguage base g) (valid : Inv expanded g) : Inv base g := by
  rcases valid with ⟨_, nodeKeys, nodes, edgeKeys, edges⟩
  refine ⟨h.base_valid, nodeKeys, ?_, edgeKeys, ?_⟩
  · intro n hn
    simpa only [h.nodes_equal] using nodes n hn
  · intro e he
    exact reflect_old_instance h g e (old e he) (edges e he)

theorem preserves_old_language {base expanded : Theory} (h : FreshExtension base expanded)
    (g : Graph) (old : OldLanguage base g) : Inv expanded g ↔ Inv base g :=
  ⟨reflect_old_model h g old, lift_model h g⟩

def RequiredPreservation : Prop := ∀ (base expanded : Theory),
  FreshExtension base expanded → ∀ g, OldLanguage base g → (Inv expanded g ↔ Inv base g)
theorem audited_preservation : RequiredPreservation :=
  fun _ _ h g old => preserves_old_language h g old

-- A real counterexample: sampled compatibility can coexist with weakened meaning.
namespace Witnesses
def baseKind : Kind := { id := "relation.example", version := "v1", pairs := [("subject","contract")], fields := ["scope"] }
def base : Theory := { nodeKinds := ["subject","contract","other"], kinds := [baseKind] }
def widened : Theory := { base with kinds := [{ baseKind with pairs := [("subject","contract"),("subject","other")] }] }
def subject : Node := { ref := ⟨"s","v1"⟩, kind := "subject", contentIdentity := "fixture:s" }
def contract : Node := { ref := ⟨"t","v1"⟩, kind := "contract", contentIdentity := "fixture:t" }
def other : Node := { contract with kind := "other" }
def edge : Assertion := { id := "e", kindId := baseKind.id, kindVersion := "v1", source := subject.ref, target := contract.ref, qualifiers := [("scope","fixture:scope")] }
def sample : Graph := { nodes := [subject,contract], assertions := [edge] }
def counterexample : Graph := { nodes := [subject,other], assertions := [edge] }
theorem sample_still_compatible : Inv base sample ∧ Inv widened sample := by decide
theorem widened_invariant_is_weaker : Inv widened counterexample ∧ ¬ Inv base counterexample := by decide
end Witnesses

#print axioms lift_instance
#print axioms reflect_old_instance
#print axioms lift_model
#print axioms reflect_old_model
#print axioms preserves_old_language
#print axioms audited_preservation
#print axioms Witnesses.sample_still_compatible
#print axioms Witnesses.widened_invariant_is_weaker
end Registry.Evolution
