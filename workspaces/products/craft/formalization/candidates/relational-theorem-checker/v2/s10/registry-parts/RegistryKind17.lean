import RegistryKind17_Basic
import RegistryKind17_Unique
import RegistryKind17_Endpoints
namespace Registry.Snapshot
theorem kind_valid17 : KindValid nodes kind17 := ⟨kind17_basic.1, kind17_basic.2.1, kind17_unique, kind17_endpoints, kind17_basic.2.2.1, kind17_basic.2.2.2⟩
#print axioms kind_valid17
end Registry.Snapshot
