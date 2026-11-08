import RegistryKind5_Data
namespace Registry.Snapshot
theorem kind5_basic : kind5.id ≠ "" ∧ kind5.version ≠ "" ∧ kind5.fields.Nodup ∧ (∀ field ∈ kind5.fields, field ≠ "") := by decide
end Registry.Snapshot
