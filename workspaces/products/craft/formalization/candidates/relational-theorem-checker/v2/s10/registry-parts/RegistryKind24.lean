import RegistryKind24_Basic
import RegistryKind24_Unique
import RegistryKind24_Endpoints
namespace Registry.Snapshot
theorem kind_valid24 : KindValid nodes kind24 := ⟨kind24_basic.1, kind24_basic.2.1, kind24_unique, kind24_endpoints, kind24_basic.2.2.1, kind24_basic.2.2.2⟩
#print axioms kind_valid24
end Registry.Snapshot
