import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind5 : Kind := { id := "relation.asserts-identity-of", version := "sha256:8aac274b24af42de5dd6848292b1ee4e96f25d11224279ebb7b3f20efbd943e9", pairs := [("identity-claim", "person-reference"), ("person-reference", "person"), ("person-reference", "person-reference"), ("principal-reference", "principal")], fields := ["assertion_kind", "claim_scope"] }
theorem kind_valid5 : KindValid nodes kind5 := by decide
end Registry.Snapshot
