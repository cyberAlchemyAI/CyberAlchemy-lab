import RegistryKind19_Data
namespace Registry.Snapshot
theorem kind19_basic : kind19.id ≠ "" ∧ kind19.version ≠ "" ∧ kind19.fields.Nodup ∧ (∀ field ∈ kind19.fields, field ≠ "") := by decide
end Registry.Snapshot
