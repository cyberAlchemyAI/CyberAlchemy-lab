import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind1 : Kind := { id := "relation.addresses-improvement-target", version := "sha256:85bb6746337f42e9be2a2ee93b9971e775692592151857e542cb9e965f10228a", pairs := [("research-inquiry", "improvement-target")], fields := ["target_version_ref", "addressing_role"] }
theorem kind_valid1 : KindValid nodes kind1 := by decide
end Registry.Snapshot
