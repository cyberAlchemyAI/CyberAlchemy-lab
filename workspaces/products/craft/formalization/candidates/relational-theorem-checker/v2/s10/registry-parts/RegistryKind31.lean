import RegistryKind31_Basic
import RegistryKind31_Unique
import RegistryKind31_Endpoints
namespace Registry.Snapshot
theorem kind_valid31 : KindValid nodes kind31 := ⟨kind31_basic.1, kind31_basic.2.1, kind31_unique, kind31_endpoints, kind31_basic.2.2.1, kind31_basic.2.2.2⟩
#print axioms kind_valid31
end Registry.Snapshot
