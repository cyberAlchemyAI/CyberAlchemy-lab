import RegistryKind39_Basic
import RegistryKind39_Unique
import RegistryKind39_Endpoints
namespace Registry.Snapshot
theorem kind_valid39 : KindValid nodes kind39 := ⟨kind39_basic.1, kind39_basic.2.1, kind39_unique, kind39_endpoints, kind39_basic.2.2.1, kind39_basic.2.2.2⟩
#print axioms kind_valid39
end Registry.Snapshot
