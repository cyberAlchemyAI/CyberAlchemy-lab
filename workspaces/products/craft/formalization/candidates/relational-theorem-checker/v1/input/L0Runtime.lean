import ReferenceChecker
import CheckerSoundness
import Lean.Data.Json.FromToJson
import Lean.Data.Json.Printer

namespace Relational.Runtime
open Lean

def diagnostic (g : Graph) (e : Assertion) : Json := Json.mkObj [
  ("assertion_id",toJson e.id), ("endpoint_valid",toJson (decide (EndpointValid g e))),
  ("qualifier_valid",toJson (decide (QualifierValid e))),
  ("version_scope_valid",toJson (decide (VersionScopeValid g e))),
  ("instance_valid",toJson (checkInstance g e))]

def result (base candidate : Graph) : Json := Json.mkObj [
  ("accepted_base",toJson (checkGraph base)),("accepted_result",toJson (checkGraph candidate)),
  ("inventory_valid",toJson (decide (InventoryValid candidate))),
  ("assertion_ids_unique",toJson (decide ((candidate.assertions.map Assertion.id).Nodup))),
  ("assertion_count",toJson candidate.assertions.length),
  ("assertions",Json.arr (candidate.assertions.map (diagnostic candidate)).toArray)]

end Relational.Runtime
