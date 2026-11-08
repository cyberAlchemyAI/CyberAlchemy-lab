import ReferenceChecker

namespace Relational

theorem instance_check_iff (g : Graph) (e : Assertion) :
    checkInstance g e = true ↔ InstanceValid g e := by
  simp only [checkInstance, Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · rintro ⟨⟨⟨hid, hend⟩, hqual⟩, hver⟩
    exact ⟨hid, hend, hqual, hver⟩
  · rintro ⟨hid, hend, hqual, hver⟩
    exact ⟨⟨⟨hid, hend⟩, hqual⟩, hver⟩

theorem instance_check_sound (g : Graph) (e : Assertion) :
    checkInstance g e = true → InstanceValid g e :=
  (instance_check_iff g e).mp

theorem graph_check_iff (g : Graph) : checkGraph g = true ↔ Inv g := by
  simp only [checkGraph, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true]
  constructor
  · rintro ⟨⟨hinv, hall⟩, huniq⟩
    exact ⟨hinv, fun e he => instance_check_sound g e (hall e he), huniq⟩
  · rintro ⟨hinv, hall, huniq⟩
    exact ⟨⟨hinv, fun e he => (instance_check_iff g e).mpr (hall e he)⟩, huniq⟩

theorem graph_check_sound (g : Graph) : checkGraph g = true → Inv g :=
  (graph_check_iff g).mp

theorem addition_preserves (g : Graph) (e : Assertion) :
    checkAddition g e = true → Inv (applyAddition g e) :=
  graph_check_sound (applyAddition g e)

theorem addition_iff (g : Graph) (e : Assertion) :
    checkAddition g e = true ↔ Inv (applyAddition g e) :=
  graph_check_iff (applyAddition g e)

theorem addition_preserves_admission_roots (g : Graph) (e : Assertion) :
    (applyAddition g e).admissionRoots = g.admissionRoots := rfl

end Relational
