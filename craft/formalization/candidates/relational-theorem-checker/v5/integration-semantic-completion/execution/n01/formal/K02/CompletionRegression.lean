import IntentAddressingWitnesses

set_option autoImplicit false

namespace RelationalSuccessor.CandidateIntentAddressing.CompletionRegression
open RelationalSuccessor
open Witnesses

def requirementOne : Definition :=
  ⟨ref "R1", .requirement [ref "criterion-1"], [], ref "review-R1"⟩
def requirementTwo : Definition :=
  ⟨ref "R2", .requirement [ref "criterion-2"], [], ref "review-R2"⟩
def requirements : Catalog := [requirementOne, requirementTwo]
def supportOne : Assessment :=
  ⟨ref "criterion-1", ref "R1", frame .project, ref "action-1", ref "output-1", .yes⟩
def supportTwo : Assessment :=
  ⟨ref "criterion-2", ref "R2", frame .project, ref "action-2", ref "output-2", .yes⟩
def easier : WorkContract :=
  ⟨ref "contract-easier", (subject .project).ref, [ref "R1"], frame .project⟩
def stricter : WorkContract :=
  ⟨ref "contract-stricter", (subject .project).ref, [ref "R1", ref "R2"], frame .project⟩
def partialWorld : World := { world .project with
  workContracts := [easier, stricter], requirementRoots := requirements,
  requirementCatalog := requirements, fulfillmentAssessments := [supportOne] }
def completeWorld : World := { partialWorld with fulfillmentAssessments := [supportOne, supportTwo] }

theorem easier_requirement_fulfilled :
    FulfillmentMeaning partialWorld.requirementRoots partialWorld.requirementCatalog
      (ref "R1") (frame .project) partialWorld.fulfillmentAssessments [ref "criterion-1"] :=
  (fulfillment_exact _ _ _ _ _ _).mp (by decide)

theorem easier_contract_fulfilled : ContractFulfilled partialWorld (claim .project) easier := by
  refine ⟨by decide, by decide, ?_⟩
  intro required member
  have same : required = ref "R1" := by simpa [easier] using member
  subst required
  exact ⟨[ref "criterion-1"], easier_requirement_fulfilled⟩

theorem stricter_contract_unfinished : ¬ ContractFulfilled partialWorld (claim .project) stricter := by
  intro full
  rcases full.2.2 (ref "R2") (by decide) with ⟨submitted, criteria, meaning, _, allSupported⟩
  rcases meaning with ⟨definition, _, _, nonempty, _⟩
  cases criteria with
  | nil => exact nonempty rfl
  | cons first rest =>
    rcases allSupported first (by simp) with ⟨observed, captured, _, required, _, _⟩
    have same : observed = supportOne := by simpa [partialWorld] using captured
    subst observed
    have distinct : supportOne.requirement ≠ ref "R2" := by decide
    exact distinct required

-- Regression: the old existential contract rule accepted this exact world.
theorem existential_contract_choice_accepts_example :
    ∃ contract ∈ partialWorld.workContracts,
      ApplicableContract (claim .project) contract ∧ ContractFulfilled partialWorld (claim .project) contract :=
  ⟨easier, by decide, by unfold ApplicableContract; decide, easier_contract_fulfilled⟩

theorem all_contracts_rule_refuses_example : ¬ Completed partialWorld (claim .project) :=
  easier_contract_cannot_hide_unfinished_contract _ _ easier stricter
    (by decide) (by unfold ApplicableContract; decide) easier_contract_fulfilled
    (by decide) (by unfold ApplicableContract; decide) stricter_contract_unfinished

theorem complete_requirement_one_fulfilled :
    FulfillmentMeaning completeWorld.requirementRoots completeWorld.requirementCatalog
      (ref "R1") (frame .project) completeWorld.fulfillmentAssessments [ref "criterion-1"] :=
  (fulfillment_exact _ _ _ _ _ _).mp (by decide)

theorem complete_requirement_two_fulfilled :
    FulfillmentMeaning completeWorld.requirementRoots completeWorld.requirementCatalog
      (ref "R2") (frame .project) completeWorld.fulfillmentAssessments [ref "criterion-2"] :=
  (fulfillment_exact _ _ _ _ _ _).mp (by decide)

theorem all_contracts_rule_accepts_complete_example : Completed completeWorld (claim .project) := by
  constructor
  · exact ⟨easier, by decide, by unfold ApplicableContract; decide⟩
  · intro contract captured _
    have cases : contract = easier ∨ contract = stricter := by simpa [completeWorld, partialWorld] using captured
    rcases cases with easy | strict
    · subst contract
      refine ⟨by decide, by decide, ?_⟩
      intro required member
      have same : required = ref "R1" := by simpa [easier] using member
      subst required
      exact ⟨[ref "criterion-1"], complete_requirement_one_fulfilled⟩
    · subst contract
      refine ⟨by decide, by decide, ?_⟩
      intro required member
      have cases : required = ref "R1" ∨ required = ref "R2" := by simpa [stricter] using member
      rcases cases with one | two
      · subst required; exact ⟨[ref "criterion-1"], complete_requirement_one_fulfilled⟩
      · subst required; exact ⟨[ref "criterion-2"], complete_requirement_two_fulfilled⟩

#print axioms easier_requirement_fulfilled
#print axioms easier_contract_fulfilled
#print axioms stricter_contract_unfinished
#print axioms existential_contract_choice_accepts_example
#print axioms all_contracts_rule_refuses_example
#print axioms complete_requirement_one_fulfilled
#print axioms complete_requirement_two_fulfilled
#print axioms all_contracts_rule_accepts_complete_example
end RelationalSuccessor.CandidateIntentAddressing.CompletionRegression
