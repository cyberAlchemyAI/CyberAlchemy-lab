import RegistryKind7_Basic
import RegistryKind7_Unique
import RegistryKind7_Endpoints
namespace Registry.Snapshot
theorem kind_valid7 : KindValid nodes kind7 := ⟨kind7_basic.1, kind7_basic.2.1, kind7_unique, kind7_endpoints, kind7_basic.2.2.1, kind7_basic.2.2.2⟩
#print axioms kind_valid7
end Registry.Snapshot
