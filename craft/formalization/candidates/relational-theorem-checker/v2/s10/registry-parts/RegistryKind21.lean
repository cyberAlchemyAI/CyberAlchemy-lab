import RegistryKind21_Basic
import RegistryKind21_Unique
import RegistryKind21_Endpoints
namespace Registry.Snapshot
theorem kind_valid21 : KindValid nodes kind21 := ⟨kind21_basic.1, kind21_basic.2.1, kind21_unique, kind21_endpoints, kind21_basic.2.2.1, kind21_basic.2.2.2⟩
#print axioms kind_valid21
end Registry.Snapshot
