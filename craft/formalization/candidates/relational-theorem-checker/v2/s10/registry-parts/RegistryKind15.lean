import RegistryKind15_Basic
import RegistryKind15_Unique
import RegistryKind15_Endpoints
namespace Registry.Snapshot
theorem kind_valid15 : KindValid nodes kind15 := ⟨kind15_basic.1, kind15_basic.2.1, kind15_unique, kind15_endpoints, kind15_basic.2.2.1, kind15_basic.2.2.2⟩
#print axioms kind_valid15
end Registry.Snapshot
