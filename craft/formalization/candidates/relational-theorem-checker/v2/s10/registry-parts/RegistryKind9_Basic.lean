import RegistryKind9_Data
namespace Registry.Snapshot
theorem kind9_basic : kind9.id ≠ "" ∧ kind9.version ≠ "" ∧ kind9.fields.Nodup ∧ (∀ field ∈ kind9.fields, field ≠ "") := by decide
end Registry.Snapshot
