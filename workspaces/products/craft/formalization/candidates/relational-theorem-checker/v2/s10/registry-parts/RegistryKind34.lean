import RegistryKind34_Basic
import RegistryKind34_Unique
import RegistryKind34_Endpoints
namespace Registry.Snapshot
theorem kind_valid34 : KindValid nodes kind34 := ⟨kind34_basic.1, kind34_basic.2.1, kind34_unique, kind34_endpoints, kind34_basic.2.2.1, kind34_basic.2.2.2⟩
#print axioms kind_valid34
end Registry.Snapshot
