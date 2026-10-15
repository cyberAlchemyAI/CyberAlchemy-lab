import InferenceCore

namespace RelationalV3.Query
open Inference

inductive Outcome where
  | present | absentInCompleteProfile | outsideProfile | invalidQuery | incomplete
  deriving DecidableEq, Repr

abbrev Known (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate
abbrev ShapeCompatible (T : Theory) (a : Atom) : Prop :=
  ∃ p ∈ T.predicates, p.key = a.predicate ∧ a.values.map Value.sort = p.sorts
abbrev WithinDomain (T : Theory) (a : Atom) : Prop :=
  ∀ v ∈ a.values, v ∈ T.domain
instance (T : Theory) (a : Atom) : Decidable (Known T a) := by
  unfold Known; infer_instance
instance (T : Theory) (a : Atom) : Decidable (ShapeCompatible T a) := by
  unfold ShapeCompatible; infer_instance
instance (T : Theory) (a : Atom) : Decidable (WithinDomain T a) := by
  unfold WithinDomain; infer_instance

def diagnose (T : Theory) (C : List Atom) (complete : Bool) (a : Atom) : Outcome :=
  if ¬ a.predicate.Valid then .invalidQuery
  else if ¬ Known T a then .outsideProfile
  else if ¬ ShapeCompatible T a then .invalidQuery
  else if ¬ WithinDomain T a then .outsideProfile
  else if complete = false then .incomplete
  else if a ∈ C then .present
  else .absentInCompleteProfile

theorem absence_requires_typed_complete_nonmembership
    (T : Theory) (C : List Atom) (complete : Bool) (a : Atom)
    (h : diagnose T C complete a = .absentInCompleteProfile) :
    AtomValid T a ∧ complete = true ∧ a ∉ C := by
  by_cases hk : a.predicate.Valid
  · by_cases hn : Known T a
    · by_cases hs : ShapeCompatible T a
      · by_cases hv : WithinDomain T a
        · have noOutside : ¬ ∃ v ∈ a.values, v ∉ T.domain := by
            rintro ⟨v, member, missing⟩
            exact missing (hv v member)
          cases complete with
          | false => simp [diagnose, hk, hn, hs, noOutside] at h
          | true =>
            by_cases hm : a ∈ C
            · simp [diagnose, hk, hn, hs, noOutside, hm] at h
            · obtain ⟨p, hp, he, ht⟩ := hs
              exact ⟨⟨p, hp, he, ht, hv⟩, rfl, hm⟩
        · simp [diagnose, hk, hn, hs, hv] at h
      · simp [diagnose, hk, hn, hs] at h
    · simp [diagnose, hk, hn] at h
  · simp [diagnose, hk] at h

theorem absence_excludes_selected_derivation
    (T : Theory) (F C : List Atom) (complete : Bool) (a : Atom)
    (adequacy : ∀ q, q ∈ C ↔ Derivable T F q)
    (h : diagnose T C complete a = .absentInCompleteProfile) :
    ¬ Derivable T F a := by
  have safety := absence_requires_typed_complete_nonmembership T C complete a h
  exact fun derived => safety.2.2 ((adequacy a).mpr derived)

theorem incomplete_cannot_diagnose_absence
    (T : Theory) (C : List Atom) (a : Atom) :
    diagnose T C false a ≠ .absentInCompleteProfile := by
  intro h
  have safety := absence_requires_typed_complete_nonmembership T C false a h
  cases safety.2.1

#print axioms absence_requires_typed_complete_nonmembership
#print axioms absence_excludes_selected_derivation
#print axioms incomplete_cannot_diagnose_absence
end RelationalV3.Query
