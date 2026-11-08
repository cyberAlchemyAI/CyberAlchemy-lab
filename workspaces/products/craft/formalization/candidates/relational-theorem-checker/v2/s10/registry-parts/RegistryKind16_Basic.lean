import RegistryKind16_Data
namespace Registry.Snapshot
theorem kind16_basic : kind16.id ≠ "" ∧ kind16.version ≠ "" ∧ kind16.fields.Nodup ∧ (∀ field ∈ kind16.fields, field ≠ "") := by decide
end Registry.Snapshot
