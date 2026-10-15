import BindingReferences
import NumberEpochAst
set_option autoImplicit false
namespace RelationalSuccessor.CandidateBindingRecords
open RelationalSuccessor
open RelationalSuccessor.CandidateBindingAst

def frameKeys : List String := ["profile","subject","target","context","scope","snapshot","epoch","timeDomain"]
def frameFields : Fields Frame :=
  mapFields (cons reference (cons reference (cons reference (cons reference (cons reference (cons reference (cons RelationalSuccessor.CandidateNumberParser.epochAdapter (cons nonempty (empty)))))))))
    (fun output => ⟨output.1,output.2.1,output.2.2.1,output.2.2.2.1,output.2.2.2.2.1,output.2.2.2.2.2.1,output.2.2.2.2.2.2.1,output.2.2.2.2.2.2.2.1⟩)
def frame : Decoder Frame := object frameKeys frameFields
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
  rcases h with ⟨a,rest0,eq0,ha,h⟩
  rcases h with ⟨b,rest1,eq1,hb,h⟩
  rcases h with ⟨c,rest2,eq2,hc,h⟩
  rcases h with ⟨d,rest3,eq3,hd,h⟩
  rcases h with ⟨e,rest4,eq4,he,h⟩
  rcases h with ⟨f,rest5,eq5,hf,h⟩
  rcases h with ⟨g,rest6,eq6,hg,h⟩
  rcases h with ⟨h,rest7,eq7,hh,htail⟩
  change rest7 = [] at htail
  subst output
  exact ⟨a,b,c,d,e,f,g,h,by simpa only [eq0,eq1,eq2,eq3,eq4,eq5,eq6,eq7,htail] using obj,ha,hb,hc,hd,he,hf,hg,hh⟩

#print axioms frame_exact
#print axioms frame_field_meanings
end RelationalSuccessor.CandidateBindingRecords
