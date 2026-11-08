import RegistryKind8_Basic
import RegistryKind8_Unique
import RegistryKind8_Endpoints
namespace Registry.Snapshot
theorem kind_valid8 : KindValid nodes kind8 := ⟨kind8_basic.1, kind8_basic.2.1, kind8_unique, kind8_endpoints, kind8_basic.2.2.1, kind8_basic.2.2.2⟩
#print axioms kind_valid8
end Registry.Snapshot
