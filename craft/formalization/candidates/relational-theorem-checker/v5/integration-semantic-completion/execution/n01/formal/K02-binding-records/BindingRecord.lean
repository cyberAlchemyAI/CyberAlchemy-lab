import BindingFrame
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
