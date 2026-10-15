import LifecycleSemantics
open RelationalExtensions.Lifecycle
namespace LifecycleInstance
def before : State := ⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"initial", "v1"⟩, 0, [⟨"initial", "v1"⟩], []⟩
def requested : Change := ⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"initial", "v1"⟩, ⟨"successor-B", "v1"⟩, 0, true, .yes, ⟨"initial", "v1"⟩, ⟨"successor-B", "v1"⟩, 0, ⟨"ctx", "v1"⟩, 5, true, "f9a2107566f29c755458b78cc6130707523f78322d5f0401ac3852afa84288ef"⟩
theorem exact_transition : transition before requested = some (⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"successor-B", "v1"⟩, 1, [⟨"initial", "v1"⟩, ⟨"successor-B", "v1"⟩], ["f9a2107566f29c755458b78cc6130707523f78322d5f0401ac3852afa84288ef"]⟩) := by decide
theorem exact_policy : decide (Policy before requested) = true := by decide
#print axioms exact_transition
#print axioms exact_policy
end LifecycleInstance
