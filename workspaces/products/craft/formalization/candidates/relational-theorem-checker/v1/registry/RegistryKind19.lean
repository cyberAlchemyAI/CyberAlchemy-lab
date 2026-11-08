import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind19 : Kind := { id := "relation.frames", version := "sha256:f1e3c1b7f3a1bcd3e90544963398c3e5b9f3d40b9824e66692efcbbe87f06885", pairs := [("context", "bounded-context"), ("context", "goal"), ("context", "product"), ("context", "project"), ("context", "review")], fields := ["framing_role"] }
theorem kind_valid19 : KindValid nodes kind19 := by decide
end Registry.Snapshot
