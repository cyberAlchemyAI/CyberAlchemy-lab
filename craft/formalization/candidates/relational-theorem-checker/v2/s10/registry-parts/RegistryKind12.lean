import RegistryKind12_Basic
import RegistryKind12_Unique
import RegistryKind12_Endpoints
namespace Registry.Snapshot
theorem kind_valid12 : KindValid nodes kind12 := ⟨kind12_basic.1, kind12_basic.2.1, kind12_unique, kind12_endpoints, kind12_basic.2.2.1, kind12_basic.2.2.2⟩
#print axioms kind_valid12
end Registry.Snapshot
