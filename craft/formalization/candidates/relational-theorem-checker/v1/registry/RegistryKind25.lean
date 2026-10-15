import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind25 : Kind := { id := "relation.materializes-consequence", version := "sha256:b47800d5e3d1270fea0e1a6493b8e894da13aa7ced5b986707befdaaad3e1b0c", pairs := [("admission-transaction", "generated-output"), ("admission-transaction", "project-governance-event-history"), ("admission-transaction", "project-semantic-event-history"), ("admission-transaction", "project-state")], fields := ["application_receipt_ref", "consequence_role", "output_digest"] }
theorem kind_valid25 : KindValid nodes kind25 := by decide
end Registry.Snapshot
