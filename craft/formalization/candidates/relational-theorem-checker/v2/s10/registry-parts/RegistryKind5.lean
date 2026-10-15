import RegistryKind5_Basic
import RegistryKind5_Unique
import RegistryKind5_Endpoints
namespace Registry.Snapshot
theorem kind_valid5 : KindValid nodes kind5 := ⟨kind5_basic.1, kind5_basic.2.1, kind5_unique, kind5_endpoints, kind5_basic.2.2.1, kind5_basic.2.2.2⟩
#print axioms kind_valid5
end Registry.Snapshot
