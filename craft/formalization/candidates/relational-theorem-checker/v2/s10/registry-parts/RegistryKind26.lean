import RegistryKind26_Basic
import RegistryKind26_Unique
import RegistryKind26_Endpoints
namespace Registry.Snapshot
theorem kind_valid26 : KindValid nodes kind26 := ⟨kind26_basic.1, kind26_basic.2.1, kind26_unique, kind26_endpoints, kind26_basic.2.2.1, kind26_basic.2.2.2⟩
#print axioms kind_valid26
end Registry.Snapshot
