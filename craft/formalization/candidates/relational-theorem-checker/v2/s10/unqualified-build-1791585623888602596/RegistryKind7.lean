import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind7 : Kind := { id := "relation.binds-implementation", version := "sha256:eece4ecf3e801ca5e53b8675dcda4ed024d93f766fbb1cc09167ffcb59292b2d", pairs := [("implementation", "ontology"), ("implementation", "schema")], fields := ["binding_role"] }
theorem kind_valid7 : KindValid nodes kind7 := by decide
end Registry.Snapshot
