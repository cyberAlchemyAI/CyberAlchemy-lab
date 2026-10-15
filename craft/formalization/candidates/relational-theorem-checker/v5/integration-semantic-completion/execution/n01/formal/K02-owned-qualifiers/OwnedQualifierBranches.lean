import OwnedQualifierFixture

set_option autoImplicit false
namespace RelationalSuccessor.CandidateOwnedIntentQualifiers.Branches
open RelationalSuccessor
open RelationalSuccessor.CandidateOwnedIntentQualifiers
open RelationalSuccessor.CandidateOwnedIntentQualifiers.Fixture

-- These are synthetic typed branches. Reusing the fixture reference does not
-- prove real entity kinds or authentic World/Selection/catalog capture.
def branchClaim (kind : CandidateIntentAddressing.SubjectKind) : Claim :=
  { Eclaim with subject := { Eclaim.subject with kind := kind }, role := { Erole with subjectKind := kind } }
def branchWorld (kind : CandidateIntentAddressing.SubjectKind) : FramedWorld :=
  { Eworld with world := { Eworld.world with subjects := [(branchClaim kind).subject], roles := [(branchClaim kind).role] } }
def branchContext (kind : CandidateIntentAddressing.SubjectKind) : Context :=
  { context with roles := ⟨Eframe,
    [{ roleEntry with body := { roleEntry.body with target := (branchClaim kind).role } }],
    [{ roleEntry with body := { roleEntry.body with target := (branchClaim kind).role } }]⟩ }

theorem agent_assignment_accepts : check (branchContext .agentAssignment) (branchWorld .agentAssignment)
    Eprojected raw (branchClaim .agentAssignment) = true := by decide

theorem goal_accepts : check (branchContext .goal) (branchWorld .goal)
    Eprojected raw (branchClaim .goal) = true := by decide

theorem product_accepts : check (branchContext .product) (branchWorld .product)
    Eprojected raw (branchClaim .product) = true := by decide

theorem product_capability_accepts : check (branchContext .productCapability) (branchWorld .productCapability)
    Eprojected raw (branchClaim .productCapability) = true := by decide

theorem project_accepts : check (branchContext .project) (branchWorld .project)
    Eprojected raw (branchClaim .project) = true := by decide

theorem inquiry_accepts : check (branchContext .researchInquiry) (branchWorld .researchInquiry)
    Eprojected raw (branchClaim .researchInquiry) = true := by decide

theorem other_kind_refuses : check (branchContext .other) (branchWorld .other)
    Eprojected raw (branchClaim .other) = false := by decide

#print axioms agent_assignment_accepts
#print axioms goal_accepts
#print axioms product_accepts
#print axioms product_capability_accepts
#print axioms project_accepts
#print axioms inquiry_accepts
#print axioms other_kind_refuses
end RelationalSuccessor.CandidateOwnedIntentQualifiers.Branches
