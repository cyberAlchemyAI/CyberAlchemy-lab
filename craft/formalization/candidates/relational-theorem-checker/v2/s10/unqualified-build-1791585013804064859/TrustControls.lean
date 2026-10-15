import TrustProofs
namespace Successor.Qualification.Controls
open Inference Inference.Extension
def badStress : Stress.Graph := ⟨[],[],[⟨⟨"",""⟩,"","",false,[]⟩],[]⟩
theorem empty_certificate_can_pass_invalid_graph : Stress.checkCertificate badStress [] = true := by decide
theorem invalid_graph_not_qualified : ¬ Stress.GraphValid badStress := by decide
theorem certificate_does_not_imply_graph_qualification :
    ¬ (∀ g steps, Stress.checkCertificate g steps = true → Stress.GraphValid g) := by
  intro upgrade
  exact invalid_graph_not_qualified (upgrade badStress [] empty_certificate_can_pass_invalid_graph)
def sealedKey : Key := ⟨"ConformsTo","v2","sealed"⟩
def T : Theory := ⟨[.reference "subject" "v1",.reference "target" "v1",.scope "scope"],
  [⟨sealedKey,[.reference,.reference,.scope],.ordinary⟩],[],[],0⟩
def fabricated : Atom := ⟨sealedKey,[.reference "subject" "v1",.reference "target" "v1",.scope "scope"]⟩
def M (a : Atom) := a = fabricated
theorem generic_model_with_extra_observation : SemanticModel T [] M := by
  refine ⟨?_,?_,?_⟩
  · intro a ha
    subst a
    exact ⟨by decide,by decide⟩
  · intro a ha; simp at ha
  · intro i hi _
    rcases hi with ⟨rule,hr,_⟩
    simp [T] at hr
theorem extra_observation_not_source_faithful : ¬ SourceFaithful [sealedKey] [] M := by
  intro source
  have sealed : Sealed [sealedKey] fabricated := by decide
  have meaning := (source fabricated sealed).mp rfl
  simp at meaning
#print axioms certificate_does_not_imply_graph_qualification
#print axioms generic_model_with_extra_observation
#print axioms extra_observation_not_source_faithful
end Successor.Qualification.Controls
