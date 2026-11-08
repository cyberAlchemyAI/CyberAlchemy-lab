import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind35 : Kind := { id := "relation.scopes-authority-over", version := "sha256:d1b444063b414b3573b7da829303cde5b884bfafa57086ac1818ce0cdffd59f9", pairs := [("authority-boundary", "decision-scope"), ("authority-claim", "decision-scope"), ("authority-claim", "role-assignment")], fields := ["authority_role", "scope_ref"] }
theorem kind_valid35 : KindValid nodes kind35 := by decide
end Registry.Snapshot
