import RegistryKind9_Basic
import RegistryKind9_Unique
import RegistryKind9_Endpoints
namespace Registry.Snapshot
theorem kind_valid9 : KindValid nodes kind9 := ⟨kind9_basic.1, kind9_basic.2.1, kind9_unique, kind9_endpoints, kind9_basic.2.2.1, kind9_basic.2.2.2⟩
#print axioms kind_valid9
end Registry.Snapshot
