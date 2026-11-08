import RegistryKind2_Data
namespace Registry.Snapshot
theorem kind2_basic : kind2.id ≠ "" ∧ kind2.version ≠ "" ∧ kind2.fields.Nodup ∧ (∀ field ∈ kind2.fields, field ≠ "") := by decide
end Registry.Snapshot
