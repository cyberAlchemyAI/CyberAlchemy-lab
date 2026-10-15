import RegistryKind18_Basic
import RegistryKind18_Unique
import RegistryKind18_Endpoints
namespace Registry.Snapshot
theorem kind_valid18 : KindValid nodes kind18 := ⟨kind18_basic.1, kind18_basic.2.1, kind18_unique, kind18_endpoints, kind18_basic.2.2.1, kind18_basic.2.2.2⟩
#print axioms kind_valid18
end Registry.Snapshot
