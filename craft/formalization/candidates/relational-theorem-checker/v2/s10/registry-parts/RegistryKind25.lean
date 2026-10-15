import RegistryKind25_Basic
import RegistryKind25_Unique
import RegistryKind25_Endpoints
namespace Registry.Snapshot
theorem kind_valid25 : KindValid nodes kind25 := ⟨kind25_basic.1, kind25_basic.2.1, kind25_unique, kind25_endpoints, kind25_basic.2.2.1, kind25_basic.2.2.2⟩
#print axioms kind_valid25
end Registry.Snapshot
