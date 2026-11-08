import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind29 : Kind := { id := "relation.performs", version := "sha256:eed979c4a84b0ba04655a371805464a9d8c1b0e3edc1e630f843475721dfd5da", pairs := [("agent-instance", "agent-action"), ("agent-instance", "experiment-run"), ("agent-instance", "research-run"), ("agent-instance", "review"), ("agent-instance", "work")], fields := ["session_ref", "participation_role", "action_posture"] }
theorem kind_valid29 : KindValid nodes kind29 := by decide
end Registry.Snapshot
