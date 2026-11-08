import type {CompiledProjectGraph} from '../input/project-model.js';
import {isReconciledPythonProject, isReconciledRustProject, type SelectedReconciledProject} from '../generation/selected-reconciled-project.js';
import {createReconciledVerificationProjection} from '../verification/reconciled-projection.js';
import {createReconciledPythonVerificationProjection} from '../verification/reconciled-python-projection.js';
import {createReconciledRustVerificationProjection} from '../verification/reconciled-rust-projection.js';
import {FROZEN_RELATIONSHIP_AUTHORITY_V1} from '../relationships/frozen-authority.generated.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';

export const RECONCILED_FORMALIZATION_DEFINITION_SHA256='d4f81940a3562bd57259e31ac963a9b29b064af07e40737418e5db5affc90e29';
const registered=new WeakSet<object>();
export class ReconciledFormalizationError extends Error {
  readonly code='DS_RECONCILED_FORMALIZATION'; readonly exitCode=22;
  constructor(message:string){super('DS_RECONCILED_FORMALIZATION:'+message);this.name='ReconciledFormalizationError';}
}
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
// UTF-16 units are data, not Lean string literals. This also preserves lone surrogates.
function units(s:string):string{
  // Lean and JSON share escapes for tab/LF/CR. Keep multiline ASCII compact;
  // other controls, non-ASCII units and lone surrogates remain explicit data.
  if(/^[\t\n\r\x20-\x7e]*$/.test(s))return '(key '+JSON.stringify(s)+')';
  return '['+s.split('').map(c=>c.charCodeAt(0)).join(', ')+']';
}
function term(v:unknown):string{
  if(v===null)return '.nil';
  if(typeof v==='boolean')return '.bool '+v;
  if(typeof v==='number')return '.num '+JSON.stringify(JSON.stringify(v));
  if(typeof v==='string')return '.str '+units(v);
  if(Array.isArray(v))return '.arr ['+v.map(term).join(', ')+']';
  if(v&&typeof v==='object')return '.obj ['+Object.keys(v).sort().map(k=>'('+units(k)+', '+term((v as Record<string,unknown>)[k])+')').join(', ')+']';
  throw new ReconciledFormalizationError('non-JSON projection value');
}

const kernel=String.raw`import Lean
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
namespace DomainSpec.Reconciled

inductive Data where
  | nil
  | bool (value : Bool)
  | num (canonical : String)
  | str (units : List Nat)
  | arr (items : List Data)
  | obj (entries : List (List Nat × Data))
  deriving Repr

-- Explicit decreasing fuel keeps nested equality reducible by the kernel.
-- Exhaustion rejects equality; it can never establish a false equality.
def dataEq : Nat → Data → Data → Bool
  | 0, _, _ => false
  | _ + 1, .nil, .nil => true
  | _ + 1, .bool a, .bool b => a == b
  | _ + 1, .num a, .num b => a == b
  | _ + 1, .str a, .str b => a == b
  | fuel + 1, .arr a, .arr b => a.length == b.length && (a.zip b).all (fun (x,y) => dataEq fuel x y)
  | fuel + 1, .obj a, .obj b => a.length == b.length && (a.zip b).all (fun (x,y) => x.1 == y.1 && dataEq fuel x.2 y.2)
  | _ + 1, _, _ => false
instance : BEq Data := ⟨dataEq 1024⟩

def key (s : String) : List Nat := s.toList.map Char.toNat
def field (v : Data) (name : String) : Data :=
  match v with
  | .obj entries => (entries.find? (fun e => e.1 == key name)).map Prod.snd |>.getD .nil
  | _ => .nil
def items : Data → List Data
  | .arr xs => xs
  | _ => []
def text : Data → List Nat
  | .str xs => xs
  | _ => []
def named (v : Data) (name expected : String) : Bool := field v name == .str (key expected)
def unique (xs : List Data) : Bool := xs.eraseDups.length == xs.length
def sameIdentities (a b : List Data) : Bool := unique a && unique b && a.length == b.length && a.all b.contains
def nodeFor (nodes : List Data) (selector : Data) : Data :=
  (nodes.find? (fun n => field n "selector" == selector)).getD .nil
def hasKind (nodes : List Data) (selector : Data) (kind : String) : Bool :=
  selector != .nil && named (nodeFor nodes selector) "kind" kind
def endpointSelector (e : Data) : Data :=
  .str (text (field e "feature_id") ++ [58] ++ text (field e "node_id"))
def endpointHolds (nodes : List Data) (e : Data) : Bool :=
  let n := nodeFor nodes (endpointSelector e)
  n != .nil && field n "kind" == field e "kind" &&
  field n "feature_id" == field e "feature_id" && field n "node_id" == field e "node_id"
def edgeHolds (nodes signatures : List Data) (e : Data) : Bool :=
  let signature := (signatures.find? (fun s => field s "id" == field e "relationship")).getD .nil
  signature != .nil && endpointHolds nodes (field e "source") && endpointHolds nodes (field e "target") &&
  (items (field signature "source_types")).contains (field (field e "source") "kind") &&
  (items (field signature "target_types")).contains (field (field e "target") "kind")
def workflowHolds (nodes : List Data) (selection n c : Data) : Bool :=
  let steps := items (field c "steps")
  let compensations := items (field c "compensations")
  let bindings := (items (field selection "workflows")).filter (fun w => field w "selector" == field n "selector")
  let binding := bindings.headD .nil
  !steps.isEmpty && unique (steps.map (fun s => field s "step_id")) &&
  unique (compensations.map (fun s => field s "compensation_id")) &&
  (steps ++ compensations).all (fun s => hasKind nodes (field s "operation_ref") "Operation") &&
  compensations.all (fun s => (steps.map (fun step => field step "step_id")).contains (field s "for_step") &&
    (items (field s "depends_on")).all (fun id => (compensations.map (fun other => field other "compensation_id")).contains id)) &&
  bindings.length == 1 &&
  sameIdentities (steps.map (fun s => field s "step_id")) ((items (field binding "steps")).map (fun s => field s "step_id")) &&
  sameIdentities (compensations.map (fun s => field s "compensation_id")) ((items (field binding "compensations")).map (fun s => field s "compensation_id"))
def interfaceHolds (nodes : List Data) (c : Data) : Bool :=
  let contracts := items (field c "contracts")
  let operations := items (field c "operations")
  unique (contracts.map (fun x => field x "contract_id")) &&
  unique (operations.map (fun x => field x "operation_id")) && !operations.isEmpty &&
  operations.all (fun o => hasKind nodes (field o "operation_ref") "Operation" || hasKind nodes (field o "operation_ref") "Query")
def mappingHolds (nodes : List Data) (c : Data) : Bool :=
  let target := field c "target"
  let owner := nodeFor nodes (field target "interface_selector")
  named owner "kind" "Interface" &&
  (items (field (field (field owner "body") "typed_contract") "contracts")).any (fun contract => field contract "contract_id" == field target "contract_id")
def stateMachineHolds (nodes : List Data) (c : Data) : Bool :=
  let states := items (field c "states")
  let transitions := items (field c "transitions")
  !states.isEmpty && unique states && states.contains (field c "initial") && !transitions.isEmpty &&
  unique (transitions.map (fun t => field t "transition_id")) &&
  transitions.all (fun t => states.contains (field t "source_state") && states.contains (field t "target_state") &&
    hasKind nodes (field t "trigger_event_ref") "Event" &&
    (field t "guard" == .nil || hasKind nodes (field (field t "guard") "selector") "Rule") &&
    (items (field t "output_intents")).all (fun o => hasKind nodes (field o "event_ref") "Event"))
def typedReferencesHold (nodes : List Data) (selection n : Data) : Bool :=
  let c := field (field n "body") "typed_contract"
  if c == .nil then true
  else if named n "kind" "Workflow" then workflowHolds nodes selection n c
  else if named n "kind" "Interface" then interfaceHolds nodes c
  else if named n "kind" "Mapping" && named c "schema_version" "domainspec.typed-mapping/v3" then mappingHolds nodes c
  else if named n "kind" "State Machine" then stateMachineHolds nodes c
  else true
def structureHolds (graph selection : Data) (signatures : List Data) : Bool :=
  let nodes := items (field graph "nodes")
  let selectors := nodes.map (fun n => field n "selector")
  unique selectors &&
  nodes.all (fun n => field n "selector" == endpointSelector n && typedReferencesHold nodes selection n) &&
  (items (field graph "relationships")).all (edgeHolds nodes signatures)

-- The evaluator below is a round-trip observation, not a proof oracle.
def hexDigit (n : Nat) : String := String.singleton (Char.ofNat (if n < 10 then 48 + n else 87 + n))
def escapeUnit (n : Nat) : String := "\\u" ++ hexDigit (n / 4096 % 16) ++ hexDigit (n / 256 % 16) ++ hexDigit (n / 16 % 16) ++ hexDigit (n % 16)
def jsonString (s : List Nat) : String := "\"" ++ String.join (s.map escapeUnit) ++ "\""
partial def toJson : Data → String
  | .nil => "null"
  | .bool true => "true"
  | .bool false => "false"
  | .num value => value
  | .str value => jsonString value
  | .arr values => "[" ++ String.intercalate "," (values.map toJson) ++ "]"
  | .obj entries => "{" ++ String.intercalate "," (entries.map (fun (k,v) => jsonString k ++ ":" ++ toJson v)) ++ "}"
`;

const predicates=Object.freeze(['qualified-node-and-endpoint-identity','frozen-relationship-endpoint-kinds','workflow-occurrence-reference-and-binding-coverage','named-interface-and-public-mapping-target-references','typed-state-machine-state-event-and-guard-references'] as const);

/** Pure construction. The resulting source still requires actual Lean execution. */
export function createReconciledFormalization(graph:CompiledProjectGraph,plan:SelectedReconciledProject){
  const input=isReconciledPythonProject(plan)
    ? createReconciledPythonVerificationProjection(graph,plan)
    : isReconciledRustProject(plan)
      ? createReconciledRustVerificationProjection(graph,plan)
      : createReconciledVerificationProjection(graph,plan);
  const sourceData={graph:input.semantic_graph,selection:input.compilation_selection};
  const signatures=FROZEN_RELATIONSHIP_AUTHORITY_V1.signatures.map(s=>({id:s.id,source_types:s.source_types,target_types:s.target_types}));
  const content=kernel+'\ndef verificationInputSha256 : String := '+JSON.stringify(input.projection_sha256)+'\ndef definitionSha256 : String := '+JSON.stringify(RECONCILED_FORMALIZATION_DEFINITION_SHA256)+'\ndef sourceData : Data := '+term(sourceData)+'\n\ndef signatures : List Data := ['+signatures.map(term).join(', ')+']\n\ntheorem currentStructuralReferencesHold : structureHolds (field sourceData "graph") (field sourceData "selection") signatures = true := by decide +kernel\n\nend DomainSpec.Reconciled\n';
  const body={schema_version:'domainspec.reconciled-formalization/v1-candidate' as const,definition_sha256:RECONCILED_FORMALIZATION_DEFINITION_SHA256,input,checked_predicates:predicates,artifact:{relative_path:'Reconciled.lean',content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)},claim_scope:'finite-structural-references-only' as const,formal_verification:'not-performed' as const,authority_effect:'none' as const};
  const result=freeze({...body,bundle_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type ReconciledFormalization=ReturnType<typeof createReconciledFormalization>;
export function validateReconciledFormalization(value:unknown,graph:CompiledProjectGraph,plan:SelectedReconciledProject):ReconciledFormalization{
  assertInterfaceData(value);const expected=createReconciledFormalization(graph,plan);
  if(canonicalJson(value)!==canonicalJson(expected))throw new ReconciledFormalizationError('changed or incomplete bundle');return expected;
}
export function renderReconciledFormalization(value:ReconciledFormalization):string{
  if(!value||typeof value!=='object'||!registered.has(value))throw new ReconciledFormalizationError('registered bundle required');return value.artifact.content;
}
