import RegistryKind14_Basic
import RegistryKind14_Unique
import RegistryKind14_Endpoints
namespace Registry.Snapshot
theorem kind_valid14 : KindValid nodes kind14 := ⟨kind14_basic.1, kind14_basic.2.1, kind14_unique, kind14_endpoints, kind14_basic.2.2.1, kind14_basic.2.2.2⟩
#print axioms kind_valid14
end Registry.Snapshot
