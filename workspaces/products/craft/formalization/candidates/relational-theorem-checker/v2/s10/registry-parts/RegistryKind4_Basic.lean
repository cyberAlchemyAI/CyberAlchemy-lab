import RegistryKind4_Data
namespace Registry.Snapshot
theorem kind4_basic : kind4.id ≠ "" ∧ kind4.version ≠ "" ∧ kind4.fields.Nodup ∧ (∀ field ∈ kind4.fields, field ≠ "") := by decide
end Registry.Snapshot
