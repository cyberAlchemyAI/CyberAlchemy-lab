import RegistryKind3_Basic
import RegistryKind3_Unique
import RegistryKind3_Endpoints
namespace Registry.Snapshot
theorem kind_valid3 : KindValid nodes kind3 := ⟨kind3_basic.1, kind3_basic.2.1, kind3_unique, kind3_endpoints, kind3_basic.2.2.1, kind3_basic.2.2.2⟩
#print axioms kind_valid3
end Registry.Snapshot
