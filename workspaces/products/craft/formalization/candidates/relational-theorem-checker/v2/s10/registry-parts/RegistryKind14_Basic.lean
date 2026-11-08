import RegistryKind14_Data
namespace Registry.Snapshot
theorem kind14_basic : kind14.id ≠ "" ∧ kind14.version ≠ "" ∧ kind14.fields.Nodup ∧ (∀ field ∈ kind14.fields, field ≠ "") := by decide
end Registry.Snapshot
