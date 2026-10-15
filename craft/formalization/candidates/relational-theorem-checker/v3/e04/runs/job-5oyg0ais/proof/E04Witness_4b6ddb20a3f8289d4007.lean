import LifecycleSemantics
open RelationalExtensions.Lifecycle
namespace LifecycleInstance
def before : State := ⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"initial", "v1"⟩, 0, [⟨"initial", "v1"⟩], []⟩
def requested : Change := ⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"initial", "v1"⟩, ⟨"successor-C", "v1"⟩, 0, true, .yes, ⟨"initial", "v1"⟩, ⟨"successor-C", "v1"⟩, 0, ⟨"ctx", "v1"⟩, 5, true, "09dabcbef81d04a8b384d90e53c241d4952adca6154e31d6ba4723c34aeaacfa"⟩
theorem exact_transition : transition before requested = some (⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"successor-C", "v1"⟩, 1, [⟨"initial", "v1"⟩, ⟨"successor-C", "v1"⟩], ["09dabcbef81d04a8b384d90e53c241d4952adca6154e31d6ba4723c34aeaacfa"]⟩) := by decide
theorem exact_policy : decide (Policy before requested) = true := by decide
#print axioms exact_transition
#print axioms exact_policy
end LifecycleInstance
