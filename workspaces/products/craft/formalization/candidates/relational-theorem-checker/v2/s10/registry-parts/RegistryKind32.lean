import RegistryKind32_Basic
import RegistryKind32_Unique
import RegistryKind32_Endpoints
namespace Registry.Snapshot
theorem kind_valid32 : KindValid nodes kind32 := ⟨kind32_basic.1, kind32_basic.2.1, kind32_unique, kind32_endpoints, kind32_basic.2.2.1, kind32_basic.2.2.2⟩
#print axioms kind_valid32
end Registry.Snapshot
