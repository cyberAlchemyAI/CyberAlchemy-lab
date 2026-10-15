import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind21 : Kind := { id := "relation.governed-by", version := "sha256:2e63e56783a856d2eaa7f755dc67cb7a02188656c1b410daf8aa54e50bcd37f7", pairs := [("admission-transaction", "policy"), ("agent-action", "policy"), ("agent-instance", "policy"), ("agent-profile", "policy"), ("agent-session", "policy"), ("artifact-type", "constitution"), ("authority-boundary", "policy"), ("challenge-contract", "policy"), ("challenge-event", "challenge-contract"), ("classification-assignment", "classification-scheme"), ("classification-assignment", "policy"), ("communication-preference", "policy"), ("context", "policy"), ("decision-bundle", "policy"), ("decision-checkpoint", "policy"), ("definition", "constitution"), ("failure-assessment", "policy"), ("failure-control-binding", "policy"), ("failure-mode", "policy"), ("failure-occurrence", "policy"), ("feedback-record", "policy"), ("incident", "policy"), ("ontology", "policy"), ("ontology-edge", "policy"), ("ontology-node", "policy"), ("operational-lesson", "policy"), ("relation-kind", "constitution"), ("user-decision-preference", "policy"), ("workflow-decision-profile", "policy")], fields := ["governance_role"] }
theorem kind_valid21 : KindValid nodes kind21 := by decide
end Registry.Snapshot
