import RegistryKind10_Basic
import RegistryKind10_Unique
import RegistryKind10_Endpoints
namespace Registry.Snapshot
theorem kind_valid10 : KindValid nodes kind10 := ⟨kind10_basic.1, kind10_basic.2.1, kind10_unique, kind10_endpoints, kind10_basic.2.2.1, kind10_basic.2.2.2⟩
#print axioms kind_valid10
end Registry.Snapshot
