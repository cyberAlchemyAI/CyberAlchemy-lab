import SupportedObservations
import ProtectedLineage

namespace Successor.Support
open Inference
open Successor.Projection
-- Every retained conformance observation has an actual member assertion and assessment
-- support. Ordinary supplied truths and root receipts remain separately named assumptions.
theorem conformance_support {g x} (source : MemberConformance g x) :
    ∃ witness, Supports g x witness := by
  exact (support_exact g x).mp ((projection_exact g x).mpr source)
abbrev VocabularyDistinct (v : Vocabulary) : Prop :=
  v.conformance ≠ v.targetKind ∧ v.conformance ≠ v.unary ∧ v.targetKind ≠ v.unary
theorem conformance_encoding_injective {v : Vocabulary} {x y : ConformanceTuple}
    (eq : conformanceAtom v x = conformanceAtom v y) : x = y := by
  rcases x with ⟨⟨_,_⟩,⟨_,_⟩,_⟩
  rcases y with ⟨⟨_,_⟩,⟨_,_⟩,_⟩
  simp_all [conformanceAtom,referenceValue]
theorem conformance_decodes {v g x} (distinct : VocabularyDistinct v)
    (meaning : Observation.SourceMeaning v g (conformanceAtom v x)) : MemberConformance g x := by
  rcases meaning with ⟨y,hy,eq⟩ | ⟨r,k,_,eq⟩ | ⟨y,_,eq⟩
  · have same := conformance_encoding_injective eq
    simpa only [same] using hy
  · have key := congrArg Atom.predicate eq
    exact False.elim (distinct.1 key.symm)
  · have key := congrArg Atom.predicate eq
    exact False.elim (distinct.2.1 key.symm)
theorem sealed_conformance_support {T F g v x}
    (policy : NoSealedHeads T (Observation.keys v))
    (coverage : Observation.SeedCoverage v g F)
    (distinct : VocabularyDistinct v)
    (derived : Derivable T F (conformanceAtom v x)) :
    ∃ witness, Supports g x witness := by
  have sealed : Sealed (Observation.keys v) (conformanceAtom v x) := by simp [Sealed,Observation.keys,conformanceAtom]
  exact conformance_support (conformance_decodes distinct ((Observation.source_derivation_exact policy coverage sealed).mp derived))
#print axioms conformance_encoding_injective
#print axioms conformance_decodes
#print axioms conformance_support
#print axioms sealed_conformance_support
end Successor.Support
