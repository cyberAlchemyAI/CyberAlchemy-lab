import RegistryKind33_Basic
import RegistryKind33_Unique
import RegistryKind33_Endpoints
namespace Registry.Snapshot
theorem kind_valid33 : KindValid nodes kind33 := ⟨kind33_basic.1, kind33_basic.2.1, kind33_unique, kind33_endpoints, kind33_basic.2.2.1, kind33_basic.2.2.2⟩
#print axioms kind_valid33
end Registry.Snapshot
