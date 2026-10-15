import ProducerPolicy
import ProjectionProofs

namespace Successor.Observation
open Inference
open Successor.Projection
def keys (v : Vocabulary) : List Key := [v.conformance,v.targetKind,v.unary]
def observed (v : Vocabulary) (g : Relational.Graph) : List Atom :=
  ((project g).map (conformanceAtom v) ++
   (projectKinds g).map (fun rk => kindAtom v rk.1 rk.2) ++
   (projectUnary g).map (unaryAtom v)).eraseDups
-- Defined in source meanings, independent of observed/project/checkHeads.
abbrev SourceMeaning (v : Vocabulary) (g : Relational.Graph) (a : Atom) : Prop :=
  (∃ x, MemberConformance g x ∧ conformanceAtom v x = a) ∨
  (∃ r k, MemberKind g r k ∧ kindAtom v r k = a) ∨
  (∃ x, MemberConformance g x ∧ unaryAtom v x.subject = a)
abbrev SeedCoverage (v : Vocabulary) (g : Relational.Graph) (F : List Atom) : Prop :=
  ∀ a, Sealed (keys v) a → (a ∈ F ↔ SourceMeaning v g a)
theorem observation_exact (v : Vocabulary) (g : Relational.Graph) (a : Atom) :
    a ∈ observed v g ↔ SourceMeaning v g a := by
  simp only [observed,List.mem_eraseDups,List.mem_append,List.mem_map]
  constructor
  · intro h
    rcases h with (⟨x,hx,eq⟩ | ⟨rk,hk,eq⟩) | ⟨r,hr,eq⟩
    · exact Or.inl ⟨x,(projection_exact g x).mp hx,eq⟩
    · exact Or.inr (Or.inl ⟨rk.1,rk.2,(kind_projection_exact g rk.1 rk.2).mp hk,eq⟩)
    · rcases (existential_view_exact g r).mp hr with ⟨x,hx,eqr⟩
      exact Or.inr (Or.inr ⟨x,(projection_exact g x).mp hx,by simpa only [eqr] using eq⟩)
  · intro h
    rcases h with ⟨x,hx,eq⟩ | ⟨r,k,hk,eq⟩ | ⟨x,hx,eq⟩
    · exact Or.inl (Or.inl ⟨x,(projection_exact g x).mpr hx,eq⟩)
    · exact Or.inl (Or.inr ⟨(r,k),(kind_projection_exact g r k).mpr hk,eq⟩)
    · exact Or.inr ⟨x.subject,(existential_view_exact g x.subject).mpr ⟨x,(projection_exact g x).mpr hx,rfl⟩,eq⟩
theorem source_derivation_exact {v g T F a} (policy : NoSealedHeads T (keys v))
    (coverage : SeedCoverage v g F) (sealed : Sealed (keys v) a) :
    Derivable T F a ↔ SourceMeaning v g a :=
  (Producer.observation_derivation_exact T F (keys v) a policy sealed).trans (coverage a sealed)
theorem source_faithful_least {v g T F} (policy : NoSealedHeads T (keys v))
    (coverage : SeedCoverage v g F) :
    SourceFaithful (keys v) (observed v g) (Derivable T F) := by
  intro a sealed
  exact (source_derivation_exact policy coverage sealed).trans (observation_exact v g a).symm
#print axioms observation_exact
#print axioms source_derivation_exact
#print axioms source_faithful_least
end Successor.Observation
