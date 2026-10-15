import RegistryKind29_Basic
import RegistryKind29_Unique
import RegistryKind29_Endpoints
namespace Registry.Snapshot
theorem kind_valid29 : KindValid nodes kind29 := ⟨kind29_basic.1, kind29_basic.2.1, kind29_unique, kind29_endpoints, kind29_basic.2.2.1, kind29_basic.2.2.2⟩
#print axioms kind_valid29
end Registry.Snapshot
