import CanonicalIR
namespace RelationalExtensions.Canonical
-- Import is the only IR boundary: reject noncanonical record order/duplicates,
-- then produce the independently defined typed semantic value.
noncomputable def importChecked (ir : IR) : Option Meaning :=
  if canonical ir then some (denote ir) else none
theorem import_exact (ir : IR) (value : Meaning) :
    importChecked ir = some value ↔ canonical ir = true ∧ value = denote ir := by
  unfold importChecked
  split
  · rename_i h; simp [h, eq_comm]
  · rename_i h; simp [h]
theorem imported_denotation (ir : IR) (value : Meaning) (h : importChecked ir = some value) :
    value = denote ir := ((import_exact ir value).mp h).2
theorem rejects_noncanonical (ir : IR) (h : canonical ir = false) : importChecked ir = none := by
  simp [importChecked,h]
theorem reference_fields_retained (id version : List Nat) :
    denote (.record (.field [105,100] (.text id) (.field [118,101,114,115,105,111,110] (.text version) .nil))) =
    .record (.field [105,100] (.scalars id) (.field [118,101,114,115,105,111,110] (.scalars version) .nil)) := rfl
theorem boolean_is_not_natural (b : Bool) (n : Nat) : denote (.boolean b) ≠ denote (.natural n) := by
  simp [denote]
#print axioms import_exact
#print axioms imported_denotation
#print axioms rejects_noncanonical
#print axioms reference_fields_retained
#print axioms boolean_is_not_natural
end RelationalExtensions.Canonical
