import RegistryKind18_Data
namespace Registry.Snapshot
theorem kind18_basic : kind18.id ≠ "" ∧ kind18.version ≠ "" ∧ kind18.fields.Nodup ∧ (∀ field ∈ kind18.fields, field ≠ "") := by decide
end Registry.Snapshot
