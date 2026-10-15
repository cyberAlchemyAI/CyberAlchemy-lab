import RegistryKind35_Data
namespace Registry.Snapshot
theorem kind35_basic : kind35.id ≠ "" ∧ kind35.version ≠ "" ∧ kind35.fields.Nodup ∧ (∀ field ∈ kind35.fields, field ≠ "") := by decide
end Registry.Snapshot
