import RegistryKind2_Basic
import RegistryKind2_Unique
import RegistryKind2_Endpoints
namespace Registry.Snapshot
theorem kind_valid2 : KindValid nodes kind2 := ⟨kind2_basic.1, kind2_basic.2.1, kind2_unique, kind2_endpoints, kind2_basic.2.2.1, kind2_basic.2.2.2⟩
#print axioms kind_valid2
end Registry.Snapshot
