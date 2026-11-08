import RegistryKind38_Basic
import RegistryKind38_Unique
import RegistryKind38_Endpoints
namespace Registry.Snapshot
theorem kind_valid38 : KindValid nodes kind38 := ⟨kind38_basic.1, kind38_basic.2.1, kind38_unique, kind38_endpoints, kind38_basic.2.2.1, kind38_basic.2.2.2⟩
#print axioms kind_valid38
end Registry.Snapshot
