import RegistryKind0_Basic
import RegistryKind0_Unique
import RegistryKind0_Endpoints
namespace Registry.Snapshot
theorem kind_valid0 : KindValid nodes kind0 := ⟨kind0_basic.1, kind0_basic.2.1, kind0_unique, kind0_endpoints, kind0_basic.2.2.1, kind0_basic.2.2.2⟩
#print axioms kind_valid0
end Registry.Snapshot
