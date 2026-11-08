import RegistryKind16_Basic
import RegistryKind16_Unique
import RegistryKind16_Endpoints
namespace Registry.Snapshot
theorem kind_valid16 : KindValid nodes kind16 := ⟨kind16_basic.1, kind16_basic.2.1, kind16_unique, kind16_endpoints, kind16_basic.2.2.1, kind16_basic.2.2.2⟩
#print axioms kind_valid16
end Registry.Snapshot
