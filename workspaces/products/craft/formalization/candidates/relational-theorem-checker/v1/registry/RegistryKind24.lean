import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind24 : Kind := { id := "relation.instance-of", version := "sha256:02af44a7bb4693b04148dc168cd336749b711da4001dbaf2ea4bcc6047747cf4", pairs := [("agent-action", "classification-value"), ("agent-instance", "classification-value"), ("capability-instance", "governed-model"), ("capability-instance", "product-capability"), ("failure-mode", "classification-value"), ("failure-occurrence", "classification-value"), ("failure-occurrence", "failure-mode"), ("implementation", "governed-model"), ("implementation", "product-capability"), ("improvement-target", "classification-value"), ("operational-lesson", "classification-value"), ("product-capability", "product")], fields := ["parent_version_ref", "binding_ref"] }
theorem kind_valid24 : KindValid nodes kind24 := by decide
end Registry.Snapshot
