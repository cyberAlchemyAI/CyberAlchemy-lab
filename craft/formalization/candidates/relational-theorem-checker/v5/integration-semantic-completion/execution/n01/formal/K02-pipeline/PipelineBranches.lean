import PipelineFixture
set_option autoImplicit false
namespace RelationalSuccessor.CandidateIntentSourcePipeline.BranchControls
open RelationalSuccessor.CandidateIntentSourcePipeline
open RelationalSuccessor.CandidateIntentSourcePipeline.Fixture
open RelationalSuccessor.CandidateOwnedIntentQualifiers.Branches

theorem agent_assignment_pipeline_accepts :
    run metadata payloads (branchContext .agentAssignment) (branchWorld .agentAssignment) bytes sourceAst qualifierAst
      (branchClaim .agentAssignment) = some output :=
  (run_exact _ _ _ _ _ _ _ _ _).mpr (branch_pipeline_meaning .agentAssignment agent_assignment_accepts)

theorem goal_pipeline_accepts :
    run metadata payloads (branchContext .goal) (branchWorld .goal) bytes sourceAst qualifierAst
      (branchClaim .goal) = some output :=
  (run_exact _ _ _ _ _ _ _ _ _).mpr (branch_pipeline_meaning .goal goal_accepts)

theorem product_pipeline_accepts :
    run metadata payloads (branchContext .product) (branchWorld .product) bytes sourceAst qualifierAst
      (branchClaim .product) = some output :=
  (run_exact _ _ _ _ _ _ _ _ _).mpr (branch_pipeline_meaning .product product_accepts)

theorem capability_pipeline_accepts :
    run metadata payloads (branchContext .productCapability) (branchWorld .productCapability) bytes sourceAst qualifierAst
      (branchClaim .productCapability) = some output :=
  (run_exact _ _ _ _ _ _ _ _ _).mpr (branch_pipeline_meaning .productCapability product_capability_accepts)

theorem project_pipeline_accepts :
    run metadata payloads (branchContext .project) (branchWorld .project) bytes sourceAst qualifierAst
      (branchClaim .project) = some output :=
  (run_exact _ _ _ _ _ _ _ _ _).mpr (branch_pipeline_meaning .project project_accepts)

theorem inquiry_pipeline_accepts :
    run metadata payloads (branchContext .researchInquiry) (branchWorld .researchInquiry) bytes sourceAst qualifierAst
      (branchClaim .researchInquiry) = some output :=
  (run_exact _ _ _ _ _ _ _ _ _).mpr (branch_pipeline_meaning .researchInquiry inquiry_accepts)
#print axioms agent_assignment_pipeline_accepts
#print axioms goal_pipeline_accepts
#print axioms product_pipeline_accepts
#print axioms capability_pipeline_accepts
#print axioms project_pipeline_accepts
#print axioms inquiry_pipeline_accepts
end RelationalSuccessor.CandidateIntentSourcePipeline.BranchControls
