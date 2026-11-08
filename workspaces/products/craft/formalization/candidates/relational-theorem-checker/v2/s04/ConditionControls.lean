import MappingStatements

namespace Successor.ConditionControls
open Successor Successor.Conditions
instance (r : Stress.Ref) (s : Relational.NodeRef) : Decidable (StressRefEquals r s) := by unfold StressRefEquals; infer_instance
instance (g : Stress.Graph) (f : Stress.Fact) (es : List Evaluation) (k : EvaluationKey) : Decidable (ActiveNorm g f es k) := by unfold ActiveNorm PotentialNorm; infer_instance
instance (g : Stress.Graph) (f h : Stress.Fact) (es : List Evaluation) (kf kh : EvaluationKey) : Decidable (ActiveConflict g f h es kf kh) := by unfold ActiveConflict; infer_instance

def key : EvaluationKey := ⟨"interpreted-conditions/v2",⟨"approved","v1"⟩,⟨"snapshot","v1"⟩,
  ⟨"subject","v1"⟩,⟨"contract","v1"⟩,"repo",some 5⟩
def positive : Evaluation := ⟨"positive",key,.holds,"evidence:positive"⟩
def negative : Evaluation := ⟨"negative",key,.doesNotHold,"evidence:negative"⟩
def uncertain : Evaluation := ⟨"uncertain",key,.unknown,"evidence:unknown"⟩
def otherEpoch : Evaluation := {negative with key := {key with epoch := some 6}}
def otherContext : Evaluation := {negative with key := {key with context := ⟨"other","v1"⟩}}
def otherVersion : Evaluation := {negative with key := {key with condition := ⟨"approved","v2"⟩}}

theorem holds_is_yes : checkCondition [positive] key = .yes := by decide
theorem explicit_negative_is_no : checkCondition [negative] key = .no := by decide
theorem missing_is_unknown : checkCondition [] key = .unknown := by decide
theorem unknown_is_unknown : checkCondition [uncertain] key = .unknown := by decide
theorem conflicting_status_is_invalid : checkCondition [positive,negative] key = .invalid := by decide
theorem unknown_plus_holds_is_invalid : checkCondition [positive,uncertain] key = .invalid := by decide
theorem different_epoch_not_conflict : checkCondition [positive,otherEpoch] key = .yes := by decide
theorem different_context_not_conflict : checkCondition [positive,otherContext] key = .yes := by decide
theorem different_revision_not_conflict : checkCondition [positive,otherVersion] key = .yes := by decide
theorem agreeing_distinct_supports : checkCondition [positive,{positive with id := "another",evidence := "other-support"}] key = .yes := by decide
theorem duplicate_identity_invalid : checkCondition [positive,positive] key = .invalid := by decide
theorem empty_evidence_invalid : checkCondition [{positive with evidence := ""}] key = .invalid := by decide
theorem timeless_explicit_context : checkCondition [{positive with key := {key with epoch := none}}] {key with epoch := none} = .yes := by decide

def contract : Stress.Contract := ⟨⟨"contract","v1"⟩,"repo","approved",true,[⟨.require,"ship"⟩,⟨.forbid,"ship"⟩,⟨.permit,"ship"⟩]⟩
def binding : Stress.Binding := ⟨⟨"binding","v1"⟩,⟨"subject","v1"⟩,[contract.ref],"repo",true,[]⟩
def edge : Stress.Inheritance := ⟨"inherits",binding.subject,contract.ref,binding.ref,"repo","approved"⟩
def graph : Stress.Graph := ⟨[edge],[binding],[contract],[]⟩
def required : Stress.Fact := ⟨edge,⟨.require,"ship"⟩⟩
def forbidden : Stress.Fact := ⟨edge,⟨.forbid,"ship"⟩⟩
def unrelated : Stress.Fact := ⟨edge,⟨.require,"erase-everything"⟩⟩
theorem potential_without_activation : Stress.Origin graph required ∧ ¬ ActiveNorm graph required [] key := by decide
theorem false_condition_not_active : ¬ ActiveNorm graph required [negative] key := by decide
theorem unknown_condition_not_active : ¬ ActiveNorm graph required [uncertain] key := by decide
theorem inconsistent_not_active : ¬ ActiveNorm graph required [positive,negative] key := by decide
theorem exact_condition_activates : ActiveNorm graph required [positive] key := by decide
theorem wrong_subject_not_active : ¬ ActiveNorm graph required [{positive with key := {key with subject := ⟨"other","v1"⟩}}] {key with subject := ⟨"other","v1"⟩} := by decide
theorem exact_active_conflict : ActiveConflict graph required forbidden [positive] key key := by decide
theorem potential_conflict_not_active_when_false : Stress.ConflictPair required forbidden ∧ ¬ ActiveConflict graph required forbidden [negative] key key := by decide
theorem active_conflict_no_explosion : ¬ Stress.Derives graph unrelated := by
  intro derived
  have absent : ¬ Stress.Origin graph unrelated := by decide
  exact absent (Stress.derivation_preserves_origin _ _ derived)

open Successor.Interpretation

def store : Store := ⟨[(("binding","binding-token"),binding.ref),(("contract-version","contract-version-token"),contract.ref)],[],[],[]⟩
def source : LegacyInheritance := ⟨edge.id,edge.subject,edge.contract,"binding-token","contract-version-token"⟩
theorem inheritance_mapping_inhabited : MapsInheritance store source edge ∧ LegacyNorm store source graph required.norm := by
  constructor
  · decide
  · exact (inheritance_mapping_exact store source graph edge required.norm (by decide) (by decide) (by decide)).mp (by decide)
theorem wrong_binding_token_rejected : ¬ MapsInheritance store {source with bindingToken := "absent"} edge := by decide
theorem wrong_contract_version_rejected : ¬ MapsInheritance store {source with contractVersionToken := "absent"} edge := by decide

#print axioms conflicting_status_is_invalid
#print axioms potential_without_activation
#print axioms exact_active_conflict
#print axioms active_conflict_no_explosion
#print axioms inheritance_mapping_inhabited
end Successor.ConditionControls
