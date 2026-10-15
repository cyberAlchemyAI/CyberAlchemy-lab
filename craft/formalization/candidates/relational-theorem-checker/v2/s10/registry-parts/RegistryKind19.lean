import RegistryKind19_Basic
import RegistryKind19_Unique
import RegistryKind19_Endpoints
namespace Registry.Snapshot
theorem kind_valid19 : KindValid nodes kind19 := ⟨kind19_basic.1, kind19_basic.2.1, kind19_unique, kind19_endpoints, kind19_basic.2.2.1, kind19_basic.2.2.2⟩
#print axioms kind_valid19
end Registry.Snapshot
