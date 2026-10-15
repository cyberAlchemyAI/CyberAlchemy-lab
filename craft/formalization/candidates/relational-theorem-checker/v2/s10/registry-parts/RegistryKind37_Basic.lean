import RegistryKind37_Data
namespace Registry.Snapshot
theorem kind37_basic : kind37.id ≠ "" ∧ kind37.version ≠ "" ∧ kind37.fields.Nodup ∧ (∀ field ∈ kind37.fields, field ≠ "") := by decide
end Registry.Snapshot
