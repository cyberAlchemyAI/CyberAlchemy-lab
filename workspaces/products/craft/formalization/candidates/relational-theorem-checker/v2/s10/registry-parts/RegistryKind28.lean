import RegistryKind28_Basic
import RegistryKind28_Unique
import RegistryKind28_Endpoints
namespace Registry.Snapshot
theorem kind_valid28 : KindValid nodes kind28 := ⟨kind28_basic.1, kind28_basic.2.1, kind28_unique, kind28_endpoints, kind28_basic.2.2.1, kind28_basic.2.2.2⟩
#print axioms kind_valid28
end Registry.Snapshot
