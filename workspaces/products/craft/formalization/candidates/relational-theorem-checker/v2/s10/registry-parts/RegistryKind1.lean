import RegistryKind1_Basic
import RegistryKind1_Unique
import RegistryKind1_Endpoints
namespace Registry.Snapshot
theorem kind_valid1 : KindValid nodes kind1 := ⟨kind1_basic.1, kind1_basic.2.1, kind1_unique, kind1_endpoints, kind1_basic.2.2.1, kind1_basic.2.2.2⟩
#print axioms kind_valid1
end Registry.Snapshot
