import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind40 : Kind := { id := "relation.violates", version := "sha256:7ada5e225d79db87376b8cf34c6afc5734a11c1298979e7b05ceb86db6102dfc", pairs := [("failure-occurrence", "challenge-contract"), ("failure-occurrence", "contract"), ("failure-occurrence", "policy"), ("failure-occurrence", "schema")], fields := ["boundary_version_ref", "evidence_posture"] }
theorem kind_valid40 : KindValid nodes kind40 := by decide
end Registry.Snapshot
