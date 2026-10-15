import RegistryKind40_Basic
import RegistryKind40_Unique
import RegistryKind40_Endpoints
namespace Registry.Snapshot
theorem kind_valid40 : KindValid nodes kind40 := ⟨kind40_basic.1, kind40_basic.2.1, kind40_unique, kind40_endpoints, kind40_basic.2.2.1, kind40_basic.2.2.2⟩
#print axioms kind_valid40
end Registry.Snapshot
