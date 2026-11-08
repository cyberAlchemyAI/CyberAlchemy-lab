import RegistryKind4_Basic
import RegistryKind4_Unique
import RegistryKind4_Endpoints
namespace Registry.Snapshot
theorem kind_valid4 : KindValid nodes kind4 := ⟨kind4_basic.1, kind4_basic.2.1, kind4_unique, kind4_endpoints, kind4_basic.2.2.1, kind4_basic.2.2.2⟩
#print axioms kind_valid4
end Registry.Snapshot
