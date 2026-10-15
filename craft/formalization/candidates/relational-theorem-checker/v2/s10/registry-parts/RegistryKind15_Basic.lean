import RegistryKind15_Data
namespace Registry.Snapshot
theorem kind15_basic : kind15.id ≠ "" ∧ kind15.version ≠ "" ∧ kind15.fields.Nodup ∧ (∀ field ∈ kind15.fields, field ≠ "") := by decide
end Registry.Snapshot
