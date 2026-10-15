import CanonicalIR
namespace RelationalExtensions.Canonical
-- Import is the only IR boundary: reject noncanonical record order/duplicates,
-- then produce the independently defined typed semantic value.
def importChecked (ir : IR) : Option Meaning :=
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
theorem reference_fields_retained (id version : String) :
    denote (.record (.cons "id" (.text id) (.cons "version" (.text version) .nil))) =
    .record (.cons (scalars "id") (.scalars (scalars id)) (.cons (scalars "version") (.scalars (scalars version)) .nil)) := rfl
theorem boolean_is_not_natural (b : Bool) (n : Nat) : denote (.boolean b) ≠ denote (.natural n) := by
  simp [denote]
#print axioms import_exact
#print axioms imported_denotation
#print axioms rejects_noncanonical
#print axioms reference_fields_retained
#print axioms boolean_is_not_natural
end RelationalExtensions.Canonical
