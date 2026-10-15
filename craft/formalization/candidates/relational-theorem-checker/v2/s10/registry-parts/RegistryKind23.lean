import RegistryKind23_Basic
import RegistryKind23_Unique
import RegistryKind23_Endpoints
namespace Registry.Snapshot
theorem kind_valid23 : KindValid nodes kind23 := ⟨kind23_basic.1, kind23_basic.2.1, kind23_unique, kind23_endpoints, kind23_basic.2.2.1, kind23_basic.2.2.2⟩
#print axioms kind_valid23
end Registry.Snapshot
