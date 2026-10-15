import RegistryKind7_Data
namespace Registry.Snapshot
theorem kind7_basic : kind7.id ≠ "" ∧ kind7.version ≠ "" ∧ kind7.fields.Nodup ∧ (∀ field ∈ kind7.fields, field ≠ "") := by decide
end Registry.Snapshot
