import RegistryKind27_Basic
import RegistryKind27_Unique
import RegistryKind27_Endpoints
namespace Registry.Snapshot
theorem kind_valid27 : KindValid nodes kind27 := ⟨kind27_basic.1, kind27_basic.2.1, kind27_unique, kind27_endpoints, kind27_basic.2.2.1, kind27_basic.2.2.2⟩
#print axioms kind_valid27
end Registry.Snapshot
