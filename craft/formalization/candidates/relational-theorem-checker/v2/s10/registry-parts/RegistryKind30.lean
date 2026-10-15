import RegistryKind30_Basic
import RegistryKind30_Unique
import RegistryKind30_Endpoints
namespace Registry.Snapshot
theorem kind_valid30 : KindValid nodes kind30 := ⟨kind30_basic.1, kind30_basic.2.1, kind30_unique, kind30_endpoints, kind30_basic.2.2.1, kind30_basic.2.2.2⟩
#print axioms kind_valid30
end Registry.Snapshot
