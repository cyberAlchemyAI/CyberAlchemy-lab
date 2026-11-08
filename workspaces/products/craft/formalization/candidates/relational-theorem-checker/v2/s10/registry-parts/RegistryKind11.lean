import RegistryKind11_Basic
import RegistryKind11_Unique
import RegistryKind11_Endpoints
namespace Registry.Snapshot
theorem kind_valid11 : KindValid nodes kind11 := ⟨kind11_basic.1, kind11_basic.2.1, kind11_unique, kind11_endpoints, kind11_basic.2.2.1, kind11_basic.2.2.2⟩
#print axioms kind_valid11
end Registry.Snapshot
