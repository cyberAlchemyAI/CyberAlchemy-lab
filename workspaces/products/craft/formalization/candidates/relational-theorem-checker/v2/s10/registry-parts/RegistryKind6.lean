import RegistryKind6_Basic
import RegistryKind6_Unique
import RegistryKind6_Endpoints
namespace Registry.Snapshot
theorem kind_valid6 : KindValid nodes kind6 := ⟨kind6_basic.1, kind6_basic.2.1, kind6_unique, kind6_endpoints, kind6_basic.2.2.1, kind6_basic.2.2.2⟩
#print axioms kind_valid6
end Registry.Snapshot
