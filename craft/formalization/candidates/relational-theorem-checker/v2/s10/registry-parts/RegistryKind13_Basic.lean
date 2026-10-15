import RegistryKind13_Data
namespace Registry.Snapshot
theorem kind13_basic : kind13.id ≠ "" ∧ kind13.version ≠ "" ∧ kind13.fields.Nodup ∧ (∀ field ∈ kind13.fields, field ≠ "") := by decide
end Registry.Snapshot
