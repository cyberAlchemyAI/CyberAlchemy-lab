import RegistryKind6_Data
namespace Registry.Snapshot
theorem kind6_basic : kind6.id ≠ "" ∧ kind6.version ≠ "" ∧ kind6.fields.Nodup ∧ (∀ field ∈ kind6.fields, field ≠ "") := by decide
end Registry.Snapshot
