"""Generate explicit field-preserving candidate AST definitions; inspect/compile them separately."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
N=HERE.parents[1]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def product(specs):
    result='empty'
    for spec in reversed(specs):result=f'cons {spec} ({result})'
    return result

def projection(index):return 'output.'+'.'.join(['2']*index+['1'])

def run():
    prior=json.loads((HERE.parent/'K02-number-parser/context-pack.json').read_text())
    context={'task':'N01','unit':'K02-binding-records','mode':'candidate-formalization','scope':'All eight Frame fields, complete typed binding bodies and enclosing resolution/role records: independent AST meanings and exact field-preserving decoders. Full JSON Schema interpreter, original bytes/capture/authentic/independent closure remain required.','selected_sources':prior['selected_sources']+[binding(HERE.parent/'K02-number-parser/verification.json'),binding(HERE.parent/'K02-number-parser/NEXT-IMPLEMENTATION.md'),binding(HERE.parent/'K02-owned-qualifiers/OwnedBindingCatalog.lean')],'decision':'Reuse the existing typed owned Body and exact number adapter. Fix version/kind/target schemas in the two public record decoders, preserving all input fields. Keep original binding bytes/digest external; a syntactic review reference is not authentication.','write_scope':'New N01 candidate package and exact evidence/index/progress bindings only.','gate_verdict':'Reversible preparation authorized by existing complete-plan instruction; K04/global review and full N01/N02/N03 acceptance remain pending.','validation':'Fresh pinned compiler/replay/axiom/import audits; quantified independent exactness and field characterizations; draft-schema comparison and malformed-field/correspondence controls.','inherited_discharges':0}
    (HERE/'context-pack.json').write_text(json.dumps(context,indent=2)+'\n')
    specs=['reference']*6+['RelationalSuccessor.CandidateNumberParser.epochAdapter','nonempty']
    text='''import BindingReferences
import NumberEpochAst
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingRecords
open RelationalSuccessor
open RelationalSuccessor.CandidateBindingAst

'''
    text+='def frameKeys : List String := ["profile","subject","target","context","scope","snapshot","epoch","timeDomain"]\n'
    text+=f'def frameFields : Fields Frame :=\n  mapFields ({product(specs)})\n    (fun output => ⟨'+','.join(projection(i) for i in range(8))+'⟩)\n'
    text+='''def frame : Decoder Frame := object frameKeys frameFields
def FrameMeaning (value : J) (output : Frame) : Prop := ObjectMeaning frameKeys frameFields value output

theorem frame_exact (value : J) (output : Frame) : frame.decode value = some output ↔ FrameMeaning value output :=
  object_exact frameKeys frameFields value output

theorem frame_field_meanings (value : J) (output : Frame) (meaning : FrameMeaning value output) :
    ∃ a b c d e f g h, CandidateJsonSource.ObjectValueMeaning frameKeys value [a,b,c,d,e,f,g,h] ∧
      ReferenceMeaning a output.profile ∧ ReferenceMeaning b output.subject ∧
      ReferenceMeaning c output.target ∧ ReferenceMeaning d output.context ∧
      ReferenceMeaning e output.scope ∧ ReferenceMeaning f output.snapshot ∧
      RelationalSuccessor.CandidateNumberParser.AstEpochMeaning g output.epoch ∧
      NonemptyMeaning h output.timeDomain := by
  rcases meaning with ⟨values,obj,input,h,same⟩
'''
    names=list('abcdefgh')
    for i,name in enumerate(names):text+=f'  rcases h with ⟨{name},rest{i},eq{i},h{name},'+('htail' if i==7 else 'h')+'⟩\n'
    text+='  change rest7 = [] at htail\n  subst output\n  exact ⟨'+','.join(names)+',by simpa only ['+','.join('eq'+str(i) for i in range(8))+',htail] using obj,'+','.join('h'+v for v in names)+'⟩\n'
    text+='\n#print axioms frame_exact\n#print axioms frame_field_meanings\nend RelationalSuccessor.CandidateBindingRecords\n'
    (HERE/'BindingFrame.lean').write_text(text)
    text='''import BindingFrame
import BindingTargets
import OwnedBindingCatalog
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingRecords
open RelationalSuccessor
open RelationalSuccessor.CandidateBindingAst
abbrev RawBody (α : Type) := RelationalSuccessor.CandidateOwnedBindings.Body α

structure Record (α : Type) where
  schemaVersion : String
  bindingKey : RevisionKey
  kind : String
  body : RawBody α
  ownerReview : RevisionRef
  deriving DecidableEq, Repr

def ConstantMeaning (expected : String) (value : J) (output : String) : Prop :=
  value = .string expected ∧ output = expected

def decodeConstant (expected : String) : J → Option String
  | .string input => if input = expected then some expected else none
  | _ => none

theorem constant_exact (expected : String) (value : J) (output : String) :
    decodeConstant expected value = some output ↔ ConstantMeaning expected value output := by
  cases value <;> simp [decodeConstant,ConstantMeaning]
  intro _
  exact eq_comm

def constant (expected : String) : Decoder String := ⟨decodeConstant expected,ConstantMeaning expected,constant_exact expected⟩

def bodyKeys : List String := ["token","target","frame"]
def bodyFields {α : Type} (target : Decoder α) : Fields (RawBody α) :=
  mapFields (cons nonempty (cons target (cons frame empty)))
    (fun output => ⟨output.1,output.2.1,output.2.2.1⟩)
def body {α : Type} (target : Decoder α) : Decoder (RawBody α) := object bodyKeys (bodyFields target)
def BodyMeaning {α : Type} (target : Decoder α) (value : J) (output : RawBody α) : Prop :=
  ObjectMeaning bodyKeys (bodyFields target) value output

theorem body_exact {α : Type} (target : Decoder α) (value : J) (output : RawBody α) :
    (body target).decode value = some output ↔ BodyMeaning target value output := object_exact bodyKeys (bodyFields target) value output

theorem body_field_meanings {α : Type} (target : Decoder α) (value : J) (output : RawBody α)
    (meaning : BodyMeaning target value output) :
    ∃ a b c, CandidateJsonSource.ObjectValueMeaning bodyKeys value [a,b,c] ∧
      NonemptyMeaning a output.token ∧ target.Meaning b output.target ∧ FrameMeaning c output.frame := by
  rcases meaning with ⟨values,obj,input,h,same⟩
  rcases h with ⟨a,rest0,eq0,ha,h⟩
  rcases h with ⟨b,rest1,eq1,hb,h⟩
  rcases h with ⟨c,rest2,eq2,hc,htail⟩
  change rest2 = [] at htail
  subst output
  exact ⟨a,b,c,by simpa only [eq0,eq1,eq2,htail] using obj,ha,hb,hc⟩

def recordKeys : List String := ["schema_version","binding_revision_key","kind","body","owner_review_ref"]
def recordFields {α : Type} (version kind : String) (target : Decoder α) : Fields (Record α) :=
  mapFields (cons (constant version) (cons key (cons (constant kind) (cons (body target) (cons reference empty)))))
    (fun output => ⟨output.1,output.2.1,output.2.2.1,output.2.2.2.1,output.2.2.2.2.1⟩)
def record {α : Type} (version kind : String) (target : Decoder α) : Decoder (Record α) := object recordKeys (recordFields version kind target)
def RecordMeaning {α : Type} (version kind : String) (target : Decoder α) (value : J) (output : Record α) : Prop :=
  ObjectMeaning recordKeys (recordFields version kind target) value output

theorem record_exact {α : Type} (version kind : String) (target : Decoder α) (value : J) (output : Record α) :
    (record version kind target).decode value = some output ↔ RecordMeaning version kind target value output :=
  object_exact recordKeys (recordFields version kind target) value output

theorem record_field_meanings {α : Type} (version kind : String) (target : Decoder α) (value : J) (output : Record α)
    (meaning : RecordMeaning version kind target value output) :
    ∃ a b c d e, CandidateJsonSource.ObjectValueMeaning recordKeys value [a,b,c,d,e] ∧
      ConstantMeaning version a output.schemaVersion ∧ KeyMeaning b output.bindingKey ∧
      ConstantMeaning kind c output.kind ∧ BodyMeaning target d output.body ∧ ReferenceMeaning e output.ownerReview := by
  rcases meaning with ⟨values,obj,input,h,same⟩
  rcases h with ⟨a,rest0,eq0,ha,h⟩
  rcases h with ⟨b,rest1,eq1,hb,h⟩
  rcases h with ⟨c,rest2,eq2,hc,h⟩
  rcases h with ⟨d,rest3,eq3,hd,h⟩
  rcases h with ⟨e,rest4,eq4,he,htail⟩
  change rest4 = [] at htail
  subst output
  exact ⟨a,b,c,d,e,by simpa only [eq0,eq1,eq2,eq3,eq4,htail] using obj,ha,hb,hc,hd,he⟩

def resolutionVersion : String := "cyberalchemy-lab-intent-resolution-qualifier-binding/candidate-v1"
def resolutionKind : String := "intent-resolution-qualifier-binding"
def roleVersion : String := "cyberalchemy-lab-intent-addressing-role-binding/candidate-v1"
def roleKind : String := "intent-addressing-role-binding"

def resolutionRecord : Decoder (Record RelationalSuccessor.CandidateIntentAddressing.Resolution) :=
  record resolutionVersion resolutionKind resolution
def roleRecord : Decoder (Record RelationalSuccessor.CandidateIntentAddressing.Role) :=
  record roleVersion roleKind role

theorem resolution_record_exact (value : J) (output : Record RelationalSuccessor.CandidateIntentAddressing.Resolution) :
    resolutionRecord.decode value = some output ↔ RecordMeaning resolutionVersion resolutionKind resolution value output :=
  record_exact resolutionVersion resolutionKind resolution value output

theorem role_record_exact (value : J) (output : Record RelationalSuccessor.CandidateIntentAddressing.Role) :
    roleRecord.decode value = some output ↔ RecordMeaning roleVersion roleKind role value output :=
  record_exact roleVersion roleKind role value output

theorem accepted_record_constants {α : Type} (version kind : String) (target : Decoder α) (value : J) (output : Record α)
    (accepted : (record version kind target).decode value = some output) : output.schemaVersion = version ∧ output.kind = kind := by
  rcases record_field_meanings version kind target value output ((record_exact version kind target value output).mp accepted)
    with ⟨_,_,_,_,_,_,hv,_,hk,_,_⟩
  exact ⟨hv.2,hk.2⟩

#print axioms constant_exact
#print axioms body_exact
#print axioms body_field_meanings
#print axioms record_exact
#print axioms record_field_meanings
#print axioms resolution_record_exact
#print axioms role_record_exact
#print axioms accepted_record_constants
end RelationalSuccessor.CandidateBindingRecords
'''
    (HERE/'BindingRecord.lean').write_text(text)
    print('Wrote explicit frame and complete record definitions; no acceptance inferred.')
if __name__=='__main__':run()
