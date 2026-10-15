-- Generated source data; no source semantic refinement or discharge.
-- K02 source SHA256: 387bc793dd5199d280e5002916b2721af238d0e6f9991d426d8fa7233017ae85
-- member-of source SHA256: e50e790c2f84f9ee3f4673de62b8b7e486ee8c2ae37e75e44ba2fd19b3cf56f4
import IntentAddressingCandidate
set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentAddressing.SourceSignature
def capturedSources : List SubjectKind := [.agentAssignment, .goal, .product, .productCapability, .project, .researchInquiry]
def capturedMembershipPairs : List (SubjectKind × ContainerKind) := [(.agentAssignment, .project), (.goal, .project), (.product, .product), (.productCapability, .product), (.researchInquiry, .project)]
theorem source_signature_equals_model : capturedSources = allowedSources := rfl
theorem membership_signature_equals_model (source : SubjectKind) (target : ContainerKind) :
    (source, target) ∈ capturedMembershipPairs ↔ AllowedMembership source target := by
  cases source <;> cases target <;> simp [capturedMembershipPairs, AllowedMembership]
#print axioms source_signature_equals_model
#print axioms membership_signature_equals_model
end RelationalSuccessor.CandidateIntentAddressing.SourceSignature
