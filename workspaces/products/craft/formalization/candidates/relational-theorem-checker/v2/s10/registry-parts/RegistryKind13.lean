import RegistryKind13_Basic
import RegistryKind13_Unique
import RegistryKind13_Endpoints
namespace Registry.Snapshot
theorem kind_valid13 : KindValid nodes kind13 := ⟨kind13_basic.1, kind13_basic.2.1, kind13_unique, kind13_endpoints, kind13_basic.2.2.1, kind13_basic.2.2.2⟩
#print axioms kind_valid13
end Registry.Snapshot
