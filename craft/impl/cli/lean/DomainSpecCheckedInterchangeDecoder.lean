import Lean.Data.Json
import DomainSpecMetaTypeCompilerRefinement

namespace DomainSpec.CheckedInterchangeDecoder

open Lean
open DomainSpec.MetaTypeKernel
open DomainSpec.MetaTypeCompilerRefinement

def rotateRight32 (value : UInt32) (amount : Nat) : UInt32 :=
  (value >>> UInt32.ofNat amount) ||| (value <<< UInt32.ofNat (32 - amount))

def sha256Constants : Array UInt32 := #[
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

def paddedSha256Bytes (input : ByteArray) : ByteArray := Id.run do
  let mut bytes := input.push 0x80
  while bytes.size % 64 != 56 do bytes := bytes.push 0
  let bitLength := UInt64.ofNat (input.size * 8)
  for shift in [56, 48, 40, 32, 24, 16, 8, 0] do
    bytes := bytes.push (UInt8.ofNat ((bitLength >>> UInt64.ofNat shift).toNat &&& 0xff))
  return bytes

def sha256Word (bytes : ByteArray) (offset : Nat) : UInt32 :=
  (UInt32.ofNat bytes[offset]!.toNat <<< 24) |||
  (UInt32.ofNat bytes[offset + 1]!.toNat <<< 16) |||
  (UInt32.ofNat bytes[offset + 2]!.toNat <<< 8) |||
  UInt32.ofNat bytes[offset + 3]!.toNat

def sha256Words (text : String) : Array UInt32 := Id.run do
  let bytes := paddedSha256Bytes text.toUTF8
  let mut state : Array UInt32 := #[0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
  for chunk in [0:bytes.size / 64] do
    let base := chunk * 64
    let mut words : Array UInt32 := Array.replicate 64 0
    for index in [0:16] do words := words.set! index (sha256Word bytes (base + index * 4))
    for index in [16:64] do
      let x := words[index - 15]!
      let y := words[index - 2]!
      let s0 := rotateRight32 x 7 ^^^ rotateRight32 x 18 ^^^ (x >>> 3)
      let s1 := rotateRight32 y 17 ^^^ rotateRight32 y 19 ^^^ (y >>> 10)
      words := words.set! index (words[index - 16]! + s0 + words[index - 7]! + s1)
    let mut a := state[0]!
    let mut b := state[1]!
    let mut c := state[2]!
    let mut d := state[3]!
    let mut e := state[4]!
    let mut f := state[5]!
    let mut g := state[6]!
    let mut h := state[7]!
    for index in [0:64] do
      let sum1 := rotateRight32 e 6 ^^^ rotateRight32 e 11 ^^^ rotateRight32 e 25
      let choice := (e &&& f) ^^^ ((~~~e) &&& g)
      let temporary1 := h + sum1 + choice + sha256Constants[index]! + words[index]!
      let sum0 := rotateRight32 a 2 ^^^ rotateRight32 a 13 ^^^ rotateRight32 a 22
      let majority := (a &&& b) ^^^ (a &&& c) ^^^ (b &&& c)
      let temporary2 := sum0 + majority
      h := g; g := f; f := e; e := d + temporary1
      d := c; c := b; b := a; a := temporary1 + temporary2
    state := #[state[0]! + a, state[1]! + b, state[2]! + c, state[3]! + d,
      state[4]! + e, state[5]! + f, state[6]! + g, state[7]! + h]
  return state

def hexDigit (value : Nat) : Char :=
  if value < 10 then Char.ofNat (48 + value) else Char.ofNat (87 + value)

def sha256Hex (text : String) : String :=
  String.ofList <| (sha256Words text).toList.flatMap fun word =>
    (List.range 8).map fun index => hexDigit (((word >>> UInt32.ofNat ((7 - index) * 4)).toNat) % 16)

def jsonWithout (value : Json) (field : String) : Except String Json := do
  return Json.obj ((← value.getObj?).erase field)

structure DecodedCheckedProjectionInput where
  graph : Json × Json × Json
  certificate : GraphCertificate
  projectId : String
  sourceManifestSha256 : String
  sourceBytesSha256 : String
  graphSha256 : String
  nodeCount : Nat
  edgeCount : Nat
  obligationCount : Nat
  witnessCount : Nat

def requiredTopLevelKeys : List String :=
  ["schema_version", "project_id", "source_identity", "compiled_graph", "compiled_certificate",
   "formalization_payload", "denominators", "claim_scope", "authority_effect",
   "interchange_sha256"]

def requireExactKeys (value : Json) (keys : List String) (label : String) : Except String Unit := do
  let object ← value.getObj?
  if object.size != keys.length then throw s!"{label}:unexpected-or-missing-member"
  for key in keys do
    if !object.contains key then throw s!"{label}:missing:{key}"

def stringAt (value : Json) (key : String) : Except String String := do
  (← value.getObjVal? key).getStr?

def graphSourceIdentity (graph : Json) : SourceIdentity :=
  match stringAt graph "project_id", stringAt graph "source_manifest_sha256", stringAt graph "source_bytes_sha256" with
  | .ok projectId, .ok manifest, .ok bytes => ⟨projectId, manifest, bytes⟩
  | _, _, _ => ⟨"", "", ""⟩

def natAt (value : Json) (key : String) : Except String Nat := do
  (← value.getObjVal? key).getNat?

def arrayAt (value : Json) (key : String) : Except String (Array Json) := do
  (← value.getObjVal? key).getArr?

def uniqueStringField (values : Array Json) (field label : String) : Except String Unit := do
  let mut identities : Array String := #[]
  for value in values do
    let identity ← stringAt value field
    if identities.contains identity then throw s!"{label}:duplicate:{identity}"
    identities := identities.push identity

def stringFieldArray (values : Array Json) (field : String) : Except String (Array String) := do
  let mut identities : Array String := #[]
  for value in values do identities := identities.push (← stringAt value field)
  return identities

def findByStringField (values : Array Json) (field expected label : String) : Except String Json := do
  for value in values do
    if (← stringAt value field) == expected then return value
  throw s!"{label}:unknown:{expected}"

def requireSha256 (value label : String) : Except String Unit := do
  let valid := value.length == 64 && value.toList.all fun char =>
    ('0' ≤ char && char ≤ '9') || ('a' ≤ char && char ≤ 'f')
  if !valid then throw s!"{label}:invalid-sha256"

def leanMetaTypeName (value : String) : Except String String :=
  match value with
  | "Entity" => .ok "entity" | "Value Object" => .ok "valueObject" | "Enum" => .ok "enumType"
  | "Operation" => .ok "operation" | "Query" => .ok "query" | "Calculation" => .ok "calculation"
  | "Rule" => .ok "rule" | "Policy" => .ok "policy" | "Workflow" => .ok "workflow"
  | "Interface" => .ok "interfaceType" | "Event" => .ok "event" | "Mapping" => .ok "mapping"
  | "State Machine" => .ok "stateMachine" | _ => .error s!"unknown-meta-type:{value}"

def leanScopeName (value : String) : Except String String :=
  match value with
  | "same-feature" => .ok "sameFeature" | "cross-feature" => .ok "crossFeature"
  | "ui" => .ok "ui" | "ui-backend" => .ok "uiBackend"
  | _ => .error s!"unknown-scope:{value}"

def leanMultiplicityName (value : String) : Except String String :=
  match value with
  | "one_to_one" => .ok "oneToOne" | "one_to_many" => .ok "oneToMany"
  | "one_to_many_ordered" => .ok "oneToManyOrdered" | "many_to_one" => .ok "manyToOne"
  | "many_to_many" => .ok "manyToMany" | _ => .error s!"unknown-multiplicity:{value}"

def mappedStrings (values : Array Json) (mapping : String → Except String String) : Except String (Array String) := do
  let mut result := #[]
  for value in values do result := result.push (← mapping (← value.getStr?))
  return result

def stringsAt (value : Json) (field : String) : Except String (Array String) :=
  do mappedStrings (← arrayAt value field) (fun item => .ok item)

def boolAt (value : Json) (field : String) : Except String Bool := do
  (← value.getObjVal? field).getBool?

def optionalStringAt (value : Json) (field : String) : Except String String := do
  match ← value.getObjVal? field with
  | .null => return ""
  | .str text => return text
  | _ => throw s!"{field}:expected-string-or-null"

def expectedTypeRef (field : Json) : Except String String := do
  let typeRef ← field.getObjVal? "type_ref"
  match ← stringAt typeRef "kind" with
  | "primitive" => return s!"primitive:{← stringAt typeRef "name"}"
  | "reference" => return s!"reference:{← stringAt typeRef "selector"}"
  | kind => throw s!"unknown-type-ref:{kind}"

def projectionFields (compiledNode : Json) : Except String (Array Json) := do
  let kind ← stringAt compiledNode "kind"
  let body ← compiledNode.getObjVal? "body"
  if kind == "Entity" || kind == "Value Object" then
    match (body.getObjVal? "typed_contract").toOption with
    | some typed =>
        if (stringAt typed "schema_version").toOption == some "domainspec.typed-record/v1" then
          return ← arrayAt typed "properties"
        else return ← arrayAt body "fields"
    | none => return ← arrayAt body "fields"
  else if kind == "Event" then
    return #[(← body.getObjVal? "occurrence_id")] ++ (← arrayAt body "payload")
  else if kind == "Interface" then
    let mut fields := #[]
    for operation in (← arrayAt body "operations") do
      fields := fields ++ (← arrayAt operation "request") ++ (← arrayAt operation "result")
    return fields
  else return #[]

def typedRecordProperties? (compiledNode : Json) : Option (Array Json) := do
  let body ← (compiledNode.getObjVal? "body").toOption
  let typed ← (body.getObjVal? "typed_contract").toOption
  if (stringAt typed "schema_version").toOption == some "domainspec.typed-record/v1" then
    (arrayAt typed "properties").toOption
  else none

def validateNodeProjection (compiledNode formalNode : Json) : Except String Unit := do
  let selector ← stringAt compiledNode "selector"
  if (← stringAt formalNode "selector") != selector ||
     (← stringAt formalNode "feature_id") != (← stringAt compiledNode "feature_id") ||
     (← stringAt formalNode "node_id") != (← stringAt compiledNode "node_id") ||
     (← stringAt formalNode "meta_type") != (← leanMetaTypeName (← stringAt compiledNode "kind")) then
    throw s!"compiled-projection:node-identity:{selector}"
  let body ← compiledNode.getObjVal? "body"
  let fields ← projectionFields compiledNode
  let expectedIds ← match typedRecordProperties? compiledNode with
    | some properties => stringFieldArray properties "name"
    | none => stringFieldArray fields "field_id"
  let mut expectedTypes := #[]
  match typedRecordProperties? compiledNode with
  | some properties =>
      for property in properties do expectedTypes := expectedTypes.push s!"typed:{(← property.getObjVal? "type").compress}"
  | none =>
      for field in fields do expectedTypes := expectedTypes.push (← expectedTypeRef field)
  if (← stringsAt formalNode "typed_field_ids") != expectedIds then throw s!"compiled-projection:typed-field-ids:{selector}"
  if (← stringsAt formalNode "typed_field_type_refs") != expectedTypes then throw s!"compiled-projection:typed-field-types:{selector}"
  let generated ← compiledNode.getObjVal? "generated_relationship_projections"
  let expectedTargets := match (arrayAt generated "creation_targets").toOption with | some values => values | none => #[]
  if (← formalNode.getObjVal? "generated_creation_targets").compress != (Json.arr expectedTargets).compress then throw s!"compiled-projection:generated-targets:{selector}"
  if (← formalNode.getObjVal? "authored_forbidden_projection_attributes").compress != (← compiledNode.getObjVal? "authored_forbidden_projection_attributes").compress then throw s!"compiled-projection:authored-projection:{selector}"
  let kind ← stringAt compiledNode "kind"
  let expectedIdentity ← if kind == "Entity" then
    match typedRecordProperties? compiledNode with
    | some properties =>
        let mut identityName : Option String := none
        for property in properties do
          if (← boolAt property "identity") then identityName := some (← stringAt property "name")
        match identityName with | some name => .ok name | none => .error "compiled-projection:missing-identity"
    | none => stringAt body "identity_field"
    else .ok ""
  if (← stringAt formalNode "entity_identity_field") != expectedIdentity then throw s!"compiled-projection:entity-identity:{selector}"
  if (← boolAt formalNode "value_object_structural_equality") != (kind == "Value Object") then throw s!"compiled-projection:value-object:{selector}"
  let expectedValues ← if kind == "Enum" then body.getObjVal? "values" else .ok (Json.arr #[])
  if (← formalNode.getObjVal? "enum_values").compress != expectedValues.compress then throw s!"compiled-projection:enum:{selector}"
  let expectedEventType ← if kind == "Event" then stringAt body "event_type" else .ok ""
  let expectedEventVersion ← if kind == "Event" then stringAt body "version" else .ok ""
  let expectedOccurrence ← if kind == "Event" then do stringAt (← body.getObjVal? "occurrence_id") "field_id" else .ok ""
  let expectedOccurredAt ← if kind == "Event" then stringAt body "occurred_at_policy" else .ok ""
  if (← stringAt formalNode "event_type") != expectedEventType || (← stringAt formalNode "event_version") != expectedEventVersion ||
     (← stringAt formalNode "event_occurrence_field") != expectedOccurrence || (← stringAt formalNode "event_occurred_at_policy") != expectedOccurredAt then throw s!"compiled-projection:event:{selector}"
  let expectedBoundary ← if kind == "Interface" then stringAt body "boundary_kind" else .ok ""
  let expectedInterfaceVersion ← if kind == "Interface" then stringAt body "version" else .ok ""
  let expectedCompatibility ← if kind == "Interface" then stringAt body "compatibility" else .ok ""
  let expectedOperationRefs ← if kind == "Interface" then stringFieldArray (← arrayAt body "operations") "operation_ref" else .ok #[]
  if (← stringAt formalNode "interface_boundary_kind") != expectedBoundary || (← stringAt formalNode "interface_version") != expectedInterfaceVersion ||
     (← stringAt formalNode "interface_compatibility") != expectedCompatibility || (← stringsAt formalNode "interface_operation_refs") != expectedOperationRefs then throw s!"compiled-projection:interface:{selector}"
  let expectedStates ← if kind == "State Machine" then body.getObjVal? "states" else .ok (Json.arr #[])
  let expectedInitial ← if kind == "State Machine" then stringAt body "initial" else .ok ""
  if (← formalNode.getObjVal? "state_machine_states").compress != expectedStates.compress || (← stringAt formalNode "state_machine_initial") != expectedInitial then throw s!"compiled-projection:state-machine:{selector}"
  let formalTransitions ← arrayAt formalNode "state_machine_transitions"
  let compiledTransitions ← if kind == "State Machine" then arrayAt body "transitions" else .ok #[]
  if formalTransitions.size != compiledTransitions.size then throw s!"compiled-projection:transitions:{selector}"
  for index in [0:formalTransitions.size] do
    let formal := formalTransitions[index]!
    let compiled := compiledTransitions[index]!
    if (← stringAt formal "transition_id") != (← stringAt compiled "transition_id") ||
       (← stringAt formal "source_state") != (← stringAt compiled "source_state") ||
       (← stringAt formal "target_state") != (← stringAt compiled "target_state") ||
       (← stringAt formal "guard_ref") != (← optionalStringAt compiled "guard_ref") ||
       (← stringAt formal "effect_event_ref") != (← optionalStringAt compiled "effect_event_ref") then throw s!"compiled-projection:transition:{selector}"

def validateEdgeProjection (compiledEdge formalEdge : Json) (formalNodes relations : Array Json) : Except String Unit := do
  let edgeId ← stringAt compiledEdge "edge_id"
  let relationship ← stringAt compiledEdge "relationship"
  let relation ← findByStringField relations "id" relationship "compiled-projection-relation"
  let source ← compiledEdge.getObjVal? "source"
  let target ← compiledEdge.getObjVal? "target"
  let sourceSelector := s!"{← stringAt source "feature_id"}:{← stringAt source "node_id"}"
  let targetSelector := s!"{← stringAt target "feature_id"}:{← stringAt target "node_id"}"
  if (← stringAt formalEdge "edge_id") != edgeId || (← stringAt formalEdge "authored_relationship_id") != relationship ||
     (← stringAt formalEdge "relation") != (← stringAt relation "lean_constructor") ||
     (← stringAt formalEdge "source_selector") != sourceSelector || (← stringAt formalEdge "target_selector") != targetSelector ||
     (← stringAt formalEdge "source_type") != (← leanMetaTypeName (← stringAt source "kind")) ||
     (← stringAt formalEdge "target_type") != (← leanMetaTypeName (← stringAt target "kind")) then throw s!"compiled-projection:edge:{edgeId}"
  let expectedScope ← if (← stringAt compiledEdge "scope") == "project" then .ok "crossFeature" else
    let scopes ← stringsAt relation "scopes"
    if scopes.contains "sameFeature" then .ok "sameFeature" else if scopes.contains "ui" then .ok "ui" else if scopes.contains "uiBackend" then .ok "uiBackend" else .error "compiled-projection:scope"
  if (← stringAt formalEdge "scope") != expectedScope then throw s!"compiled-projection:edge-scope:{edgeId}"
  if (← formalEdge.getObjVal? "obligation_ids").compress != (← relation.getObjVal? "obligation_ids").compress then throw s!"compiled-projection:edge-obligations:{edgeId}"
  let sourceNode ← findByStringField formalNodes "selector" sourceSelector "compiled-projection-source"
  let authoredProjection ← stringsAt sourceNode "authored_forbidden_projection_attributes"
  if (← formalEdge.getObjVal? "source_generated_creation_targets").compress != (← sourceNode.getObjVal? "generated_creation_targets").compress ||
     (← boolAt formalEdge "source_authored_generated_projection") != !authoredProjection.isEmpty then throw s!"compiled-projection:edge-source:{edgeId}"

def validateCompiledProjection (compiledGraph formalGraph payload : Json) : Except String Unit := do
  let compiledNodes ← arrayAt compiledGraph "nodes"
  let formalNodes ← arrayAt formalGraph "nodes"
  if compiledNodes.size != formalNodes.size then throw "compiled-projection:node-count"
  for compiledNode in compiledNodes do
    let formalNode ← findByStringField formalNodes "selector" (← stringAt compiledNode "selector") "compiled-projection-node"
    validateNodeProjection compiledNode formalNode
  let compiledEdges ← arrayAt compiledGraph "relationships"
  let formalEdges ← arrayAt formalGraph "edges"
  if compiledEdges.size != formalEdges.size then throw "compiled-projection:edge-count"
  let relations ← arrayAt payload "relationships"
  for compiledEdge in compiledEdges do
    let formalEdge ← findByStringField formalEdges "edge_id" (← stringAt compiledEdge "edge_id") "compiled-projection-edge"
    validateEdgeProjection compiledEdge formalEdge formalNodes relations

def compiledProjectionCorresponds (compiledGraph formalGraph payload : Json) : Bool :=
  (validateCompiledProjection compiledGraph formalGraph payload).isOk

def decodedTheory : Theory (Json × Json × Json) where
  staticConforms := fun graph => compiledProjectionCorresponds graph.1 graph.2.1 graph.2.2
  graphDigest := fun graph => sha256Hex graph.2.1.compress
  sourceIdentity := fun graph => graphSourceIdentity graph.2.1

def lowerDecodedInterchange (decoded : DecodedCheckedProjectionInput) : CheckedProjectionInput (Json × Json × Json) :=
  ⟨decoded.graph, decoded.certificate⟩

theorem decodedInterchangeRefinesCheckedInput (decoded : DecodedCheckedProjectionInput)
    (compiled : compileChecked decodedTheory (lowerDecodedInterchange decoded) = some decoded.certificate) :
    GraphDigestBound decodedTheory decoded.graph decoded.certificate ∧
    SourceIdentityBound decodedTheory decoded.graph decoded.certificate ∧
    StaticConforms decodedTheory decoded.graph :=
  compile_success_implies_static_conformance decodedTheory (lowerDecodedInterchange decoded) decoded.certificate compiled

def decodeCheckedInterchange (root : Json) : Except String DecodedCheckedProjectionInput := do
  requireExactKeys root requiredTopLevelKeys "root"
  if (← stringAt root "schema_version") != "domainspec.checked-interchange/v1-candidate" then
    throw "schema_version:unsupported"
  if (← stringAt root "claim_scope") != "exact-finite-compiled-project-projection" then
    throw "claim_scope:invalid"
  if (← stringAt root "authority_effect") != "none" then
    throw "authority_effect:invalid"
  let interchangeSha ← stringAt root "interchange_sha256"
  requireSha256 interchangeSha "interchange"
  let interchangeBody ← jsonWithout root "interchange_sha256"
  let projectId ← stringAt root "project_id"
  let source ← root.getObjVal? "source_identity"
  requireExactKeys source ["source_manifest_sha256", "source_bytes_sha256"] "source_identity"
  let sourceManifest ← stringAt source "source_manifest_sha256"
  let sourceBytes ← stringAt source "source_bytes_sha256"
  let payload ← root.getObjVal? "formalization_payload"
  let graph ← payload.getObjVal? "project_graph"
  requireExactKeys graph ["project_id", "source_manifest_sha256", "source_bytes_sha256", "graph_sha256", "nodes", "edges"] "project-graph"
  let nodes ← arrayAt graph "nodes"
  let edges ← arrayAt graph "edges"
  let obligations ← arrayAt payload "obligation_catalog"
  let witnesses ← arrayAt payload "applicable_witnesses"
  uniqueStringField nodes "selector" "nodes"
  uniqueStringField edges "edge_id" "edges"
  uniqueStringField obligations "obligation_id" "obligations"
  uniqueStringField witnesses "witness_id" "witnesses"
  for node in nodes do
    requireExactKeys node ["selector", "feature_id", "node_id", "meta_type", "generated_creation_targets", "authored_forbidden_projection_attributes", "typed_field_ids", "typed_field_type_refs", "entity_identity_field", "value_object_structural_equality", "enum_values", "event_type", "event_version", "event_occurrence_field", "event_occurred_at_policy", "interface_boundary_kind", "interface_version", "interface_compatibility", "interface_operation_refs", "state_machine_states", "state_machine_initial", "state_machine_transitions"] "node"
    for transition in (← arrayAt node "state_machine_transitions") do
      requireExactKeys transition ["transition_id", "source_state", "target_state", "guard_ref", "effect_event_ref"] "state-machine-transition"
    if (← stringAt node "selector") != s!"{← stringAt node "feature_id"}:{← stringAt node "node_id"}" then throw "node:selector-mismatch"
  for edge in edges do
    requireExactKeys edge ["edge_id", "relation", "scope", "source_selector", "target_selector", "source_type", "target_type", "authored_relationship_id", "source_generated_creation_targets", "source_authored_generated_projection", "obligation_ids"] "edge"
    let source ← findByStringField nodes "selector" (← stringAt edge "source_selector") "edge-source"
    let target ← findByStringField nodes "selector" (← stringAt edge "target_selector") "edge-target"
    if (← stringAt source "meta_type") != (← stringAt edge "source_type") then throw "edge:source-type-mismatch"
    if (← stringAt target "meta_type") != (← stringAt edge "target_type") then throw "edge:target-type-mismatch"
  let denominators ← root.getObjVal? "denominators"
  requireExactKeys denominators ["node_count", "edge_count", "obligation_count", "applicable_witness_count"] "denominators"
  let nodeCount ← natAt denominators "node_count"
  let edgeCount ← natAt denominators "edge_count"
  let obligationCount ← natAt denominators "obligation_count"
  let witnessCount ← natAt denominators "applicable_witness_count"
  if nodeCount != nodes.size then throw "denominators:node-count"
  if edgeCount != edges.size then throw "denominators:edge-count"
  if obligationCount != obligations.size then throw "denominators:obligation-count"
  if witnessCount != witnesses.size then throw "denominators:witness-count"
  if obligationCount != 45 then throw "denominators:closed-obligation-count"
  let edgeIds ← stringFieldArray edges "edge_id"
  let obligationIds ← stringFieldArray obligations "obligation_id"
  let projectedWitnessIds ← stringFieldArray witnesses "witness_id"
  for witness in witnesses do
    requireExactKeys witness ["witness_id", "lean_constructor", "edge_id", "obligation_id"] "projected-witness"
    if !edgeIds.contains (← stringAt witness "edge_id") then throw "projected-witness:unknown-edge"
    if !obligationIds.contains (← stringAt witness "obligation_id") then throw "projected-witness:unknown-obligation"
  let compiled ← root.getObjVal? "compiled_certificate"
  requireExactKeys compiled ["schema_version", "project_id", "source_manifest_sha256", "graph_sha256", "node_count", "edge_count", "backend_type_ids", "backend_relationship_ids", "obligation_applicability", "obligation_witnesses", "compiler", "authority_effect", "certificate_sha256"] "compiled-certificate"
  if (← stringAt compiled "schema_version") != "domainspec.compiled-project-certificate/v1" then throw "compiled-certificate:schema"
  if (← stringAt compiled "project_id") != projectId then throw "compiled-certificate:project-mismatch"
  if (← stringAt compiled "source_manifest_sha256") != sourceManifest then throw "compiled-certificate:manifest-mismatch"
  if (← natAt compiled "node_count") != nodeCount then throw "compiled-certificate:node-count"
  if (← natAt compiled "edge_count") != edgeCount then throw "compiled-certificate:edge-count"
  if (← stringAt compiled "authority_effect") != "none" then throw "compiled-certificate:authority"
  let compiledSha ← stringAt compiled "certificate_sha256"
  requireSha256 compiledSha "compiled-certificate"
  let compiledBody ← jsonWithout compiled "certificate_sha256"
  if sha256Hex compiledBody.compress != compiledSha then throw "compiled-certificate:digest-mismatch"
  let compiledGraph ← root.getObjVal? "compiled_graph"
  requireExactKeys compiledGraph ["schema_version", "project_id", "source_manifest", "nodes", "relationships", "obligation_witnesses", "obligation_applicability", "authority_effect"] "compiled-graph"
  if (← stringAt compiledGraph "schema_version") != "domainspec.compiled-project-graph/v1-candidate" ||
     (← stringAt compiledGraph "project_id") != projectId ||
     (← stringAt compiledGraph "authority_effect") != "none" then throw "compiled-graph:identity-mismatch"
  let compiledManifest ← compiledGraph.getObjVal? "source_manifest"
  if (← stringAt compiledManifest "manifest_sha256") != sourceManifest ||
     (← stringAt compiledManifest "aggregate_sha256") != sourceBytes then throw "compiled-graph:source-mismatch"
  let compiledNodes ← arrayAt compiledGraph "nodes"
  let compiledEdges ← arrayAt compiledGraph "relationships"
  if compiledNodes.size != nodeCount || compiledEdges.size != edgeCount then throw "compiled-graph:denominator-mismatch"
  let declaredCompiledGraphSha ← stringAt compiled "graph_sha256"
  requireSha256 declaredCompiledGraphSha "compiled-graph"
  let semanticCompiledGraph ← jsonWithout compiledGraph "project_root"
  let applicability ← arrayAt compiled "obligation_applicability"
  let detailedWitnesses ← arrayAt compiled "obligation_witnesses"
  if (← compiledGraph.getObjVal? "obligation_applicability").compress != (← compiled.getObjVal? "obligation_applicability").compress then throw "compiled-graph:applicability-mismatch"
  if (← compiledGraph.getObjVal? "obligation_witnesses").compress != (← compiled.getObjVal? "obligation_witnesses").compress then throw "compiled-graph:witness-mismatch"
  uniqueStringField applicability "obligation_id" "applicability"
  uniqueStringField detailedWitnesses "witness_id" "detailed-witnesses"
  if applicability.size == 0 then throw "applicability:empty"
  if detailedWitnesses.size != witnessCount then throw "detailed-witnesses:witness-count"
  let detailedWitnessIds ← stringFieldArray detailedWitnesses "witness_id"
  for projectedId in projectedWitnessIds do
    if !detailedWitnessIds.contains projectedId then throw "detailed-witnesses:projection-mismatch"
  for row in applicability do
    requireExactKeys row ["obligation_id", "relationship_ids", "applicable", "source_selectors", "reason"] "applicability"
    if !obligationIds.contains (← stringAt row "obligation_id") then throw "applicability:unknown-obligation"
  for witness in detailedWitnesses do
    requireExactKeys witness ["witness_id", "edge_id", "obligation_id", "family", "predicate", "witness"] "detailed-witness"
    if !edgeIds.contains (← stringAt witness "edge_id") then throw "detailed-witness:unknown-edge"
    if !obligationIds.contains (← stringAt witness "obligation_id") then throw "detailed-witness:unknown-obligation"
    let edge ← findByStringField edges "edge_id" (← stringAt witness "edge_id") "detailed-witness"
    let obligation ← findByStringField obligations "obligation_id" (← stringAt witness "obligation_id") "detailed-witness"
    if (← stringAt witness "family") != (← stringAt obligation "family") then throw "detailed-witness:family-mismatch"
    let expectedWitnessId := s!"{← stringAt witness "edge_id"}:{← stringAt witness "obligation_id"}"
    if (← stringAt witness "witness_id") != expectedWitnessId then throw "detailed-witness:id-mismatch"
    let predicate ← witness.getObjVal? "predicate"
    requireExactKeys predicate ["relationship_id", "allowed_source_types", "allowed_target_types", "allowed_scopes", "multiplicity", "inverse_kind", "generated_projection_attribute"] "detailed-witness:predicate"
    if (← stringAt predicate "relationship_id") != (← stringAt edge "authored_relationship_id") then throw "detailed-witness:relationship-mismatch"
    let relation ← findByStringField (← arrayAt payload "relationships") "id" (← stringAt predicate "relationship_id") "detailed-witness"
    if (← mappedStrings (← arrayAt predicate "allowed_source_types") leanMetaTypeName) != (← mappedStrings (← arrayAt relation "source_types") (fun value => .ok value)) then throw "detailed-witness:source-predicate-mismatch"
    if (← mappedStrings (← arrayAt predicate "allowed_target_types") leanMetaTypeName) != (← mappedStrings (← arrayAt relation "target_types") (fun value => .ok value)) then throw "detailed-witness:target-predicate-mismatch"
    if (← mappedStrings (← arrayAt predicate "allowed_scopes") leanScopeName) != (← mappedStrings (← arrayAt relation "scopes") (fun value => .ok value)) then throw "detailed-witness:scope-predicate-mismatch"
    if (← leanMultiplicityName (← stringAt predicate "multiplicity")) != (← stringAt relation "multiplicity") then throw "detailed-witness:multiplicity-mismatch"
    if (← stringAt predicate "inverse_kind") != (← stringAt relation "inverse_kind") then throw "detailed-witness:inverse-mismatch"
    let endpoint ← witness.getObjVal? "witness"
    requireExactKeys endpoint ["scope", "source_selector", "source_type", "target_selector", "target_type"] "detailed-witness:endpoint"
    if (← stringAt endpoint "source_selector") != (← stringAt edge "source_selector") then throw "detailed-witness:source-selector-mismatch"
    if (← stringAt endpoint "target_selector") != (← stringAt edge "target_selector") then throw "detailed-witness:target-selector-mismatch"
    if (← leanMetaTypeName (← stringAt endpoint "source_type")) != (← stringAt edge "source_type") then throw "detailed-witness:source-type-mismatch"
    if (← leanMetaTypeName (← stringAt endpoint "target_type")) != (← stringAt edge "target_type") then throw "detailed-witness:target-type-mismatch"
  if sha256Hex semanticCompiledGraph.compress != declaredCompiledGraphSha then throw "compiled-graph:digest-mismatch"
  if (← stringAt graph "project_id") != projectId then throw "project_id:graph-mismatch"
  if (← stringAt graph "source_manifest_sha256") != sourceManifest then throw "source_identity:manifest-mismatch"
  if (← stringAt graph "source_bytes_sha256") != sourceBytes then throw "source_identity:bytes-mismatch"
  let graphSha ← stringAt graph "graph_sha256"
  requireSha256 graphSha "project-graph"
  let graphBody ← jsonWithout graph "graph_sha256"
  if sha256Hex graphBody.compress != graphSha then throw "project-graph:digest-mismatch"
  let graphCertificate ← payload.getObjVal? "graph_certificate"
  requireExactKeys graphCertificate ["graph_sha256", "source_identity"] "graph-certificate"
  if (← stringAt graphCertificate "graph_sha256") != graphSha then throw "graph_certificate:digest-mismatch"
  let certificateSource ← graphCertificate.getObjVal? "source_identity"
  requireExactKeys certificateSource ["project_id", "source_manifest_sha256", "source_bytes_sha256"] "graph-certificate-source"
  if (← stringAt certificateSource "project_id") != projectId then throw "graph_certificate:project-mismatch"
  if (← stringAt certificateSource "source_manifest_sha256") != sourceManifest then throw "graph_certificate:manifest-mismatch"
  if (← stringAt certificateSource "source_bytes_sha256") != sourceBytes then throw "graph_certificate:bytes-mismatch"
  let typescriptProjection ← payload.getObjVal? "typescript_projection"
  requireExactKeys typescriptProjection ["project_id", "source_manifest_sha256", "source_bytes_sha256", "graph_sha256"] "typescript-projection"
  if (← stringAt typescriptProjection "project_id") != projectId ||
     (← stringAt typescriptProjection "source_manifest_sha256") != sourceManifest ||
     (← stringAt typescriptProjection "source_bytes_sha256") != sourceBytes ||
     (← stringAt typescriptProjection "graph_sha256") != graphSha then throw "typescript-projection:binding-mismatch"
  validateCompiledProjection compiledGraph graph payload
  if sha256Hex interchangeBody.compress != interchangeSha then throw "interchange:digest-mismatch"
  let certificate : GraphCertificate := ⟨graphSha, ⟨projectId, sourceManifest, sourceBytes⟩⟩
  let decoded : DecodedCheckedProjectionInput := ⟨(compiledGraph, graphBody, payload), certificate, projectId, sourceManifest, sourceBytes, graphSha, nodeCount, edgeCount, obligationCount, witnessCount⟩
  if compileChecked decodedTheory (lowerDecodedInterchange decoded) != some certificate then throw "compiler-refinement:certificate-rejected"
  return decoded

def renderSummary (value : DecodedCheckedProjectionInput) : String :=
  String.intercalate "\t" ["pass", value.projectId, value.sourceManifestSha256,
    value.sourceBytesSha256, value.graphSha256, toString value.nodeCount,
    toString value.edgeCount, toString value.obligationCount, toString value.witnessCount]

def run (args : List String) : IO UInt32 := do
  match args with
  | [filename] =>
      let contents ← IO.FS.readFile filename
      match Json.parse contents >>= decodeCheckedInterchange with
      | .ok decoded =>
          IO.println (renderSummary decoded)
          return 0
      | .error message =>
          IO.eprintln message
          return 22
  | _ =>
      IO.eprintln "expected one checked-interchange JSON path"
      return 22

end DomainSpec.CheckedInterchangeDecoder

def main (args : List String) : IO UInt32 :=
  DomainSpec.CheckedInterchangeDecoder.run args
