import RegistryKind22_Basic
import RegistryKind22_Unique
import RegistryKind22_Endpoints
namespace Registry.Snapshot
theorem kind_valid22 : KindValid nodes kind22 := ⟨kind22_basic.1, kind22_basic.2.1, kind22_unique, kind22_endpoints, kind22_basic.2.2.1, kind22_basic.2.2.2⟩
#print axioms kind_valid22
end Registry.Snapshot
