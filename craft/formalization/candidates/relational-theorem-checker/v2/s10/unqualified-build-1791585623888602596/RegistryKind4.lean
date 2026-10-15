import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind4 : Kind := { id := "relation.applies-lesson", version := "sha256:c0bf14d9aeae6fecea8ea32eeae07d7b885b28d0fd9ef85d2db6112ff2990738", pairs := [("lesson-application", "operational-lesson")], fields := ["lesson_revision_ref", "application_posture", "applicability_assessment_ref", "instruction_precedence"] }
theorem kind_valid4 : KindValid nodes kind4 := by decide
end Registry.Snapshot
