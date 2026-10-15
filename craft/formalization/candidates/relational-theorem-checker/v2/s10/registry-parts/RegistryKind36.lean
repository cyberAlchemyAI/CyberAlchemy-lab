import RegistryKind36_Basic
import RegistryKind36_Unique
import RegistryKind36_Endpoints
namespace Registry.Snapshot
theorem kind_valid36 : KindValid nodes kind36 := ⟨kind36_basic.1, kind36_basic.2.1, kind36_unique, kind36_endpoints, kind36_basic.2.2.1, kind36_basic.2.2.2⟩
#print axioms kind_valid36
end Registry.Snapshot
