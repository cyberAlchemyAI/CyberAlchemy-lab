import RegistryKind35_Basic
import RegistryKind35_Unique
import RegistryKind35_Endpoints
namespace Registry.Snapshot
theorem kind_valid35 : KindValid nodes kind35 := ⟨kind35_basic.1, kind35_basic.2.1, kind35_unique, kind35_endpoints, kind35_basic.2.2.1, kind35_basic.2.2.2⟩
#print axioms kind_valid35
end Registry.Snapshot
