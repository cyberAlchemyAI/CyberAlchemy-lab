import BindingReferences
import IntentAddressingCandidate

set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingAst
open RelationalSuccessor
open RelationalSuccessor.CandidateIntentAddressing (Resolution Role SubjectKind)

def subjectName : SubjectKind → String
  | .agentAssignment => "agent-assignment"
  | .goal => "goal"
  | .product => "product"
  | .productCapability => "product-capability"
  | .project => "project"
  | .researchInquiry => "research-inquiry"
  | .other => "other"

def SubjectMeaning (value : J) (output : SubjectKind) : Prop := value = .string (subjectName output)
def decodeSubject : J → Option SubjectKind
  | .string "agent-assignment" => some .agentAssignment
  | .string "goal" => some .goal
  | .string "product" => some .product
  | .string "product-capability" => some .productCapability
  | .string "project" => some .project
  | .string "research-inquiry" => some .researchInquiry
  | .string "other" => some .other
  | _ => none

theorem subject_exact (value : J) (output : SubjectKind) :
    decodeSubject value = some output ↔ SubjectMeaning value output := by
  cases output <;> cases value <;> simp [decodeSubject,SubjectMeaning,subjectName]
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all
  all_goals split <;> simp_all

def subject : Decoder SubjectKind := ⟨decodeSubject,SubjectMeaning,subject_exact⟩

def roleKeys : List String := ["ref","code","subjectKind"]
def roleFields : Fields Role :=
  mapFields (cons reference (cons nonempty (cons subject empty)))
    (fun output => ⟨output.1,output.2.1,output.2.2.1⟩)
def role : Decoder Role := object roleKeys roleFields

def RoleMeaning (value : J) (output : Role) : Prop := ObjectMeaning roleKeys roleFields value output

theorem role_exact (value : J) (output : Role) : role.decode value = some output ↔ RoleMeaning value output :=
  object_exact roleKeys roleFields value output

def resolutionKeys : List String :=
  ["ref","scope","intent","ownerDecision","selectedSubjects","excludedSubjects","satisfactionTests"]
def resolutionFields : Fields Resolution :=
  mapFields
    (cons reference (cons reference (cons reference (cons reference
      (cons (array reference) (cons (array reference) (cons (array reference) empty)))))))
    (fun output => ⟨output.1,output.2.1,output.2.2.1,output.2.2.2.1,
      output.2.2.2.2.1,output.2.2.2.2.2.1,output.2.2.2.2.2.2.1⟩)
def resolution : Decoder Resolution := object resolutionKeys resolutionFields

def ResolutionMeaning (value : J) (output : Resolution) : Prop := ObjectMeaning resolutionKeys resolutionFields value output

theorem resolution_exact (value : J) (output : Resolution) :
    resolution.decode value = some output ↔ ResolutionMeaning value output := object_exact resolutionKeys resolutionFields value output

theorem role_code_nonempty (value : J) (output : Role) (meaning : RoleMeaning value output) : output.code ≠ "" := by
  rcases meaning with ⟨values,_,input,h,same⟩
  rcases h with ⟨a,rest,_,_,b,rest',_,hb,_⟩
  subst output
  exact hb.2


theorem role_field_meanings (value : J) (output : Role) (meaning : RoleMeaning value output) :
    ∃ a b c, CandidateJsonSource.ObjectValueMeaning roleKeys value [a,b,c] ∧
      ReferenceMeaning a output.ref ∧ NonemptyMeaning b output.code ∧ SubjectMeaning c output.subjectKind := by
  rcases meaning with ⟨values,obj,input,h,same⟩
  rcases h with ⟨a,rest,eqA,ha,h⟩
  rcases h with ⟨b,rest',eqB,hb,h⟩
  rcases h with ⟨c,rest'',eqC,hc,htail⟩
  change rest'' = [] at htail
  subst output
  exact ⟨a,b,c,by simpa only [eqA,eqB,eqC,htail] using obj,ha,hb,hc⟩

theorem resolution_field_meanings (value : J) (output : Resolution) (meaning : ResolutionMeaning value output) :
    ∃ a b c d e f g, CandidateJsonSource.ObjectValueMeaning resolutionKeys value [a,b,c,d,e,f,g] ∧
      ReferenceMeaning a output.ref ∧ ReferenceMeaning b output.scope ∧
      ReferenceMeaning c output.intent ∧ ReferenceMeaning d output.ownerDecision ∧
      ArrayMeaning reference e output.selectedSubjects ∧
      ArrayMeaning reference f output.excludedSubjects ∧
      ArrayMeaning reference g output.satisfactionTests := by
  rcases meaning with ⟨values,obj,input,h,same⟩
  rcases h with ⟨a,rest,eqA,ha,h⟩
  rcases h with ⟨b,rest',eqB,hb,h⟩
  rcases h with ⟨c,rest'',eqC,hc,h⟩
  rcases h with ⟨d,rest''',eqD,hd,h⟩
  rcases h with ⟨e,rest'''',eqE,he,h⟩
  rcases h with ⟨f,rest''''',eqF,hf,h⟩
  rcases h with ⟨g,rest'''''',eqG,hg,htail⟩
  change rest'''''' = [] at htail
  subst output
  exact ⟨a,b,c,d,e,f,g,by simpa only [eqA,eqB,eqC,eqD,eqE,eqF,eqG,htail] using obj,
    ha,hb,hc,hd,he,hf,hg⟩

#print axioms subject_exact
#print axioms role_exact
#print axioms resolution_exact
#print axioms role_code_nonempty
#print axioms role_field_meanings
#print axioms resolution_field_meanings
end RelationalSuccessor.CandidateBindingAst
