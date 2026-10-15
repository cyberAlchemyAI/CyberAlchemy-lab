import RegistryKind20_Basic
import RegistryKind20_Unique
import RegistryKind20_Endpoints
namespace Registry.Snapshot
theorem kind_valid20 : KindValid nodes kind20 := ⟨kind20_basic.1, kind20_basic.2.1, kind20_unique, kind20_endpoints, kind20_basic.2.2.1, kind20_basic.2.2.2⟩
#print axioms kind_valid20
end Registry.Snapshot
