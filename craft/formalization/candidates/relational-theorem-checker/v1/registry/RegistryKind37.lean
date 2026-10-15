import RegistryNodes
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace Registry.Snapshot
def kind37 : Kind := { id := "relation.tests-hypothesis", version := "sha256:644268137f28414c446968be09b53df39310c696f67b3ec5265d3bf9dac07d80", pairs := [("experiment-design", "hypothesis")], fields := ["hypothesis_version_ref", "test_role"] }
theorem kind_valid37 : KindValid nodes kind37 := by decide
end Registry.Snapshot
