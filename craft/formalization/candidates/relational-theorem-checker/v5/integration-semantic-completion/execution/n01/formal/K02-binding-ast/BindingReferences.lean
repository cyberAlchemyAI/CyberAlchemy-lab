import BindingAstCombinators
import SharedSemantics

set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingAst
open RelationalSuccessor

def NonemptyMeaning (value : J) (output : String) : Prop := value = .string output ∧ output ≠ ""

def decodeNonempty : J → Option String
  | .string output => if output ≠ "" then some output else none
  | _ => none

theorem nonempty_exact (value : J) (output : String) :
    decodeNonempty value = some output ↔ NonemptyMeaning value output := by
  cases value <;> simp [decodeNonempty,NonemptyMeaning]
  constructor
  · rintro ⟨nonempty,same⟩; exact ⟨same,same ▸ nonempty⟩
  · rintro ⟨same,nonempty⟩; exact ⟨same.symm ▸ nonempty,same⟩

def nonempty : Decoder String := ⟨decodeNonempty, NonemptyMeaning, nonempty_exact⟩

def keyKeys : List String := ["owner","artifact","revision"]
def keyFields : Fields RevisionKey :=
  mapFields (cons nonempty (cons nonempty (cons nonempty empty)))
    (fun output => ⟨output.1,output.2.1,output.2.2.1⟩)
def key : Decoder RevisionKey := object keyKeys keyFields

def KeyMeaning (value : J) (output : RevisionKey) : Prop := ObjectMeaning keyKeys keyFields value output

theorem key_exact (value : J) (output : RevisionKey) : key.decode value = some output ↔ KeyMeaning value output :=
  object_exact keyKeys keyFields value output

def refKeys : List String := ["key","digest"]
def refFields : Fields RevisionRef :=
  mapFields (cons key (cons nonempty empty)) (fun output => ⟨output.1,output.2.1⟩)
def reference : Decoder RevisionRef := object refKeys refFields

def ReferenceMeaning (value : J) (output : RevisionRef) : Prop := ObjectMeaning refKeys refFields value output

theorem reference_exact (value : J) (output : RevisionRef) :
    reference.decode value = some output ↔ ReferenceMeaning value output := object_exact refKeys refFields value output

def ArrayMeaning {α : Type} (item : Decoder α) (value : J) (outputs : List α) : Prop :=
  ∃ values, value = .array values ∧ CandidateJsonSource.ElementsMeaning item.Meaning values outputs

def arrayDecode {α : Type} (item : Decoder α) : J → Option (List α)
  | .array values => CandidateJsonSource.decodeElements item.decode values
  | _ => none

theorem array_exact {α : Type} (item : Decoder α) (value : J) (outputs : List α) :
    arrayDecode item value = some outputs ↔ ArrayMeaning item value outputs := by
  cases value with
  | array values =>
    rw [arrayDecode, CandidateJsonSource.decode_elements_exact item.decode item.Meaning item.exact]
    constructor
    · intro represented; exact ⟨values,rfl,represented⟩
    · rintro ⟨actual,same,represented⟩; cases same; exact represented
  | null => simp [arrayDecode,ArrayMeaning]
  | boolean b => simp [arrayDecode,ArrayMeaning]
  | number t => simp [arrayDecode,ArrayMeaning]
  | string t => simp [arrayDecode,ArrayMeaning]
  | object es => simp [arrayDecode,ArrayMeaning]

def array {α : Type} (item : Decoder α) : Decoder (List α) := ⟨arrayDecode item, ArrayMeaning item, array_exact item⟩

theorem decoded_array_length {α : Type} (item : Decoder α) (values : List J) (outputs : List α)
    (accepted : (array item).decode (.array values) = some outputs) : outputs.length = values.length := by
  have represented := (CandidateJsonSource.decode_elements_exact item.decode item.Meaning item.exact values outputs).mp accepted
  exact CandidateJsonSource.elements_meaning_length item.Meaning values outputs represented

theorem key_fields_nonempty (value : J) (output : RevisionKey) (meaning : KeyMeaning value output) :
    output.owner ≠ "" ∧ output.artifact ≠ "" ∧ output.revision ≠ "" := by
  rcases meaning with ⟨values,_,input,h,same⟩
  rcases h with ⟨a,rest,_,ha,b,rest',_,hb,c,rest'',_,hc,_⟩
  subst output
  exact ⟨ha.2,hb.2,hc.2⟩

theorem reference_fields_nonempty (value : J) (output : RevisionRef) (meaning : ReferenceMeaning value output) :
    output.key.owner ≠ "" ∧ output.key.artifact ≠ "" ∧ output.key.revision ≠ "" ∧ output.digest ≠ "" := by
  rcases meaning with ⟨values,_,input,h,same⟩
  rcases h with ⟨a,rest,_,ha,b,rest',_,hb,_⟩
  subst output
  have keyNonempty := key_fields_nonempty a input.1 ha
  exact ⟨keyNonempty.1,keyNonempty.2.1,keyNonempty.2.2,hb.2⟩

#print axioms nonempty_exact
#print axioms key_exact
#print axioms reference_exact
#print axioms array_exact
#print axioms decoded_array_length
#print axioms key_fields_nonempty
#print axioms reference_fields_nonempty
end RelationalSuccessor.CandidateBindingAst
