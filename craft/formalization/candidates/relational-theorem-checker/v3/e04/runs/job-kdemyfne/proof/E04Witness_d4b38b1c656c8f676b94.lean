import LifecycleSemantics
open RelationalExtensions.Lifecycle
namespace LifecycleInstance
def before : State := ⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"initial", "v1"⟩, 0, [⟨"initial", "v1"⟩], []⟩
def requested : Change := ⟨"a61526197f4a405eb8ba35c84fdb979f", ⟨"ctx", "v1"⟩, 5, ⟨"initial", "v1"⟩, ⟨"ineligible", "v1"⟩, 0, true, .unknown, ⟨"initial", "v1"⟩, ⟨"ineligible", "v1"⟩, 0, ⟨"ctx", "v1"⟩, 5, true, "fff8bd0575f9645ac0d9901a338aacda0fd0aeb87215d212c4b139b0e77440aa"⟩
theorem exact_transition : transition before requested = none := by decide
theorem exact_policy : decide (Policy before requested) = false := by decide
#print axioms exact_transition
#print axioms exact_policy
end LifecycleInstance
