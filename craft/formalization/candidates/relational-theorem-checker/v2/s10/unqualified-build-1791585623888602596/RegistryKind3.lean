import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind3 : Kind := { id := "relation.affects", version := "sha256:279f185d1d70e04737747a26c3605c95a570d1cbda77049aa2c8c3a23b0c8850", pairs := [("failure-occurrence", "agent-capability"), ("failure-occurrence", "agent-session"), ("failure-occurrence", "artifact-type"), ("failure-occurrence", "generated-output"), ("failure-occurrence", "implementation"), ("failure-occurrence", "ontology"), ("failure-occurrence", "person-reference"), ("failure-occurrence", "product"), ("failure-occurrence", "product-capability"), ("failure-occurrence", "project"), ("failure-occurrence", "work"), ("incident", "agent-capability"), ("incident", "agent-session"), ("incident", "artifact-type"), ("incident", "generated-output"), ("incident", "implementation"), ("incident", "ontology"), ("incident", "person-reference"), ("incident", "product"), ("incident", "product-capability"), ("incident", "project"), ("incident", "work")], fields := ["impact_scope", "evidence_posture"] }
theorem kind_valid3 : KindValid nodes kind3 := by decide
end Registry.Snapshot
