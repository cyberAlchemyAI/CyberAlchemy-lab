import RegistryKind37_Basic
import RegistryKind37_Unique
import RegistryKind37_Endpoints
namespace Registry.Snapshot
theorem kind_valid37 : KindValid nodes kind37 := ⟨kind37_basic.1, kind37_basic.2.1, kind37_unique, kind37_endpoints, kind37_basic.2.2.1, kind37_basic.2.2.2⟩
#print axioms kind_valid37
end Registry.Snapshot
