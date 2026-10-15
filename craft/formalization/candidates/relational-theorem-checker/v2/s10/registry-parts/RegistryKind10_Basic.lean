import RegistryKind10_Data
namespace Registry.Snapshot
theorem kind10_basic : kind10.id ≠ "" ∧ kind10.version ≠ "" ∧ kind10.fields.Nodup ∧ (∀ field ∈ kind10.fields, field ≠ "") := by decide
end Registry.Snapshot
