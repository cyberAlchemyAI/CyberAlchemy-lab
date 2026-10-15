import ScopedImpactCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateScopedImpact.Witnesses
open RelationalSuccessor

def ref (name : String) : RevisionRef := ⟨⟨"fixture", name, "1"⟩, name⟩
def sourceName : SourceKind → String
  | .failureOccurrence => "failure-occurrence"
  | .incident => "incident"
  | .other => "other-source"
def targetName : TargetKind → String
  | .agentCapability => "agent-capability"
  | .agentSession => "agent-session"
  | .artifactType => "artifact-type"
  | .generatedOutput => "generated-output"
  | .implementation => "implementation"
  | .ontology => "ontology"
  | .personReference => "person-reference"
  | .product => "product"
  | .productCapability => "product-capability"
  | .project => "project"
  | .work => "work"
  | .other => "other-target"
def source (kind : SourceKind) : Source :=
  ⟨ref ("source:" ++ sourceName kind), kind, ref "accountable-principal"⟩
def target (kind : TargetKind) : Target := ⟨ref ("target:" ++ targetName kind), kind⟩
def scope (s : SourceKind) (t : TargetKind) : Scope :=
  ⟨ref ("scope:" ++ sourceName s ++ ":" ++ targetName t),
    [(source s).ref, (target t).ref], 0, 10, "fixture-time"⟩
def frame (s : SourceKind) (t : TargetKind) : Frame :=
  ⟨ref "profile", (source s).ref, (target t).ref, ref "context", (scope s t).ref,
    ref "snapshot", 5, "fixture-time"⟩
def policy (s : SourceKind) (t : TargetKind) : ImpactPolicy :=
  ⟨ref ("policy:" ++ sourceName s ++ ":" ++ targetName t), "observed-scoped-change",
    s, t, [(scope s t).ref], [ref "observer"], [ref "method"], ref "metric", ref "unit",
    .increase, 2⟩
def measurement (t : TargetKind) : Measurement :=
  ⟨ref ("measurement:" ++ targetName t), (target t).ref, ref "metric", ref "unit",
    0, 1, 4, "fixture-time", ref "observer", ref "method"⟩
def provenance (s : SourceKind) (t : TargetKind) : Provenance :=
  ⟨ref ("provenance:" ++ sourceName s ++ ":" ++ targetName t), (measurement t).ref,
    ref "action", ref "output", ref "source-evidence", frame s t⟩
def observation (s : SourceKind) (t : TargetKind) : Observation :=
  ⟨ref ("observation:" ++ sourceName s ++ ":" ++ targetName t), (source s).ref,
    (target t).ref, (scope s t).ref, (policy s t).ref, .observed, (measurement t).ref,
    (provenance s t).ref, frame s t⟩
def commonModel (s : SourceKind) (t : TargetKind) : CausalModel :=
  ⟨ref ("common-model:" ++ sourceName s ++ ":" ++ targetName t), (source s).ref,
    (target t).ref, .commonCause, true, frame s t⟩
def directModel (s : SourceKind) (t : TargetKind) : CausalModel :=
  { commonModel s t with ref := ref ("direct-model:" ++ sourceName s ++ ":" ++ targetName t),
    equation := .direct }
def world (s : SourceKind) (t : TargetKind) : World := {
  profile := ref "profile", context := ref "context", snapshot := ref "snapshot",
  epoch := 5, timeDomain := "fixture-time", sources := [source s], targets := [target t],
  scopes := [scope s t], policies := [policy s t], observations := [observation s t],
  measurements := [measurement t], provenanceRoots := [provenance s t],
  evidenceRoots := [ref "source-evidence"], actions := [ref "action"], outputs := [ref "output"],
  causalModels := [commonModel s t]
}
def claim (s : SourceKind) (t : TargetKind) : Claim :=
  ⟨source s, target t, scope s t, policy s t, observation s t, measurement t,
    provenance s t, (scope s t).ref, (policy s t).code⟩

theorem legitimate_impact (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) : Affects (world s t) (claim s t) := by
  refine {
    sourceKind := hs
    targetKind := ht
    sourceOwned := by simp [world, claim]
    targetOwned := by simp [world, claim]
    scopeOwned := by simp [world, claim]
    policyOwned := by simp [world, claim]
    observationOwned := by simp [world, claim]
    measurementOwned := by simp [world, claim]
    provenanceOwned := by simp [world, claim]
    scopeQualifier := rfl
    postureQualifier := rfl
    policyNonempty := by change "observed-scoped-change" ≠ ""; decide
    policySource := rfl
    policyTarget := rfl
    permittedScope := by simp [claim, policy]
    scopedSource := by simp [claim, scope]
    scopedTarget := by simp [claim, scope]
    scopeOrdered := by change 0 ≤ 10; decide
    scopeStart := by change 0 ≤ 5; decide
    scopeFinish := by change 5 ≤ 10; decide
    scopeTime := rfl
    observed := rfl
    source := rfl
    target := rfl
    scope := rfl
    policy := rfl
    measurement := rfl
    provenance := rfl
    measuredSubject := rfl
    metric := rfl
    unit := rfl
    observer := by simp [claim, measurement, policy]
    method := by simp [claim, measurement, policy]
    measurementTime := rfl
    notFuture := by change 4 ≤ 5; decide
    fresh := by change 5 ≤ 4 + 2; decide
    impact := by change 0 < 1; decide
    provenanceMeasurement := rfl
    evidenceRoot := by simp [claim, provenance, world]
    actionOwned := by simp [claim, provenance, world]
    outputOwned := by simp [claim, provenance, world]
    provenanceFrame := rfl
    frameSource := rfl
    frameTarget := rfl
    frameScope := rfl
    frameProfile := rfl
    frameContext := rfl
    frameSnapshot := rfl
    frameEpoch := rfl
    frameTime := rfl
  }

theorem impact_does_not_establish_causation (s : SourceKind) (t : TargetKind) :
    ¬ Causes (world s t) (claim s t) := by
  rintro ⟨model, captured, _, _, _, dependence⟩
  have same : model = commonModel s t := by simpa [world] using captured
  subst model
  exact dependence rfl

theorem impact_does_not_assess_severity (s : SourceKind) (t : TargetKind) :
    ¬ AssessedSeverity (world s t) (claim s t) := by
  rintro ⟨assessment, captured, _⟩
  simp [world] at captured

theorem impact_does_not_assign_blame (s : SourceKind) (t : TargetKind) :
    ¬ Blamed (world s t) (claim s t) := by
  rintro ⟨assessment, captured, _⟩
  simp [world] at captured

theorem impact_does_not_assign_ownership (s : SourceKind) (t : TargetKind) :
    ¬ HasOwnership (world s t) (claim s t) := by
  rintro ⟨ownership, captured, _⟩
  simp [world] at captured

theorem causation_non_entailment_all_22 (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    Affects (world s t) (claim s t) ∧ ¬ Causes (world s t) (claim s t) :=
  ⟨legitimate_impact s t hs ht, impact_does_not_establish_causation s t⟩
theorem severity_non_entailment_all_22 (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    Affects (world s t) (claim s t) ∧ ¬ AssessedSeverity (world s t) (claim s t) :=
  ⟨legitimate_impact s t hs ht, impact_does_not_assess_severity s t⟩
theorem blame_non_entailment_all_22 (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    Affects (world s t) (claim s t) ∧ ¬ Blamed (world s t) (claim s t) :=
  ⟨legitimate_impact s t hs ht, impact_does_not_assign_blame s t⟩
theorem ownership_non_entailment_all_22 (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    Affects (world s t) (claim s t) ∧ ¬ HasOwnership (world s t) (claim s t) :=
  ⟨legitimate_impact s t hs ht, impact_does_not_assign_ownership s t⟩

-- Both event occurrence and target delay can be explained by the same common
-- factor; changing the source intervention alone leaves the target unchanged.
theorem common_factor_explains_observed_delay (s : SourceKind) (t : TargetKind) :
    evaluateEquation (commonModel s t).equation true (commonModel s t).common = true ∧
    evaluateEquation (commonModel s t).equation false (commonModel s t).common = true := ⟨rfl, rfl⟩

def causalWorld (s : SourceKind) (t : TargetKind) : World :=
  { world s t with causalModels := [directModel s t] }

theorem causation_can_coexist_with_impact (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    Affects (causalWorld s t) (claim s t) ∧ Causes (causalWorld s t) (claim s t) := by
  constructor
  · cases legitimate_impact s t hs ht
    constructor <;> assumption
  · exact ⟨directModel s t, by simp [causalWorld], rfl, rfl, rfl,
      direct_equation_has_source_intervention_effect true⟩

def severityPolicy : SeverityPolicy := ⟨ref "severity-policy", ref "metric", ref "unit", 1, 5⟩
def severityAssessment (s : SourceKind) (t : TargetKind) : SeverityAssessment :=
  ⟨ref ("severity:" ++ sourceName s ++ ":" ++ targetName t), (source s).ref,
    (target t).ref, (measurement t).ref, severityPolicy.ref, .moderate, frame s t⟩
def severityWorld (s : SourceKind) (t : TargetKind) : World :=
  { world s t with severityPolicies := [severityPolicy], severityAssessments := [severityAssessment s t] }

theorem severity_can_coexist_with_impact (s : SourceKind) (t : TargetKind)
    (hs : s ∈ allowedSources) (ht : t ∈ allowedTargets) :
    Affects (severityWorld s t) (claim s t) ∧ AssessedSeverity (severityWorld s t) (claim s t) := by
  constructor
  · cases legitimate_impact s t hs ht
    constructor <;> assumption
  · exact ⟨severityAssessment s t, by simp [severityWorld], severityPolicy,
      by simp [severityWorld], rfl, rfl, rfl, rfl, rfl, rfl, rfl,
      by change 1 < 5; decide, by change Grade.moderate = classify severityPolicy (measurement t); rfl⟩

theorem predicted_impact_refuses_example :
    ¬ Affects (world .incident .work) { claim .incident .work with observation :=
      { observation .incident .work with posture := .predicted } } :=
  predicted_impact_refuses _ _ rfl

theorem unobserved_label_refuses_example :
    ¬ Affects { world .incident .work with measurements := [] } (claim .incident .work) := by
  apply unowned_measurement_refuses
  simp

theorem scope_widening_refuses_example :
    ¬ Affects (world .incident .work) { claim .incident .work with scope :=
      { scope .incident .work with participants := [(source .incident).ref] } } := by
  apply scope_widening_refuses
  decide

theorem unsupported_provenance_refuses_example :
    ¬ Affects { world .incident .work with provenanceRoots := [] } (claim .incident .work) := by
  apply unsupported_provenance_refuses
  simp

theorem arbitrary_posture_refuses_example :
    ¬ Affects (world .incident .work) { claim .incident .work with postureQualifier := "definitely-observed" } := by
  apply arbitrary_posture_code_refuses
  decide

theorem unchanged_measurement_refuses_example :
    ¬ Affects (world .incident .work) { claim .incident .work with measurement :=
      { measurement .work with observed := 0 } } := by
  apply no_impact_change_refuses
  change ¬ 0 < 0
  decide

theorem stale_measurement_refuses_example :
    ¬ Affects (world .incident .work) { claim .incident .work with measurement :=
      { measurement .work with observedAt := 1 } } := by
  apply stale_measurement_refuses
  change 1 + 2 < 5
  decide

theorem future_measurement_refuses_example :
    ¬ Affects (world .incident .work) { claim .incident .work with measurement :=
      { measurement .work with observedAt := 6 } } := by
  apply future_measurement_refuses
  change 5 < 6
  decide

theorem wrong_snapshot_refuses_example :
    ¬ Affects (world .incident .work) { claim .incident .work with observation :=
      { observation .incident .work with frame := { frame .incident .work with snapshot := ref "stale" } } } := by
  apply wrong_snapshot_refuses
  decide

#print axioms legitimate_impact
#print axioms impact_does_not_establish_causation
#print axioms impact_does_not_assess_severity
#print axioms impact_does_not_assign_blame
#print axioms impact_does_not_assign_ownership
#print axioms causation_non_entailment_all_22
#print axioms severity_non_entailment_all_22
#print axioms blame_non_entailment_all_22
#print axioms ownership_non_entailment_all_22
#print axioms common_factor_explains_observed_delay
#print axioms causation_can_coexist_with_impact
#print axioms severity_can_coexist_with_impact
#print axioms predicted_impact_refuses_example
#print axioms unobserved_label_refuses_example
#print axioms scope_widening_refuses_example
#print axioms unsupported_provenance_refuses_example
#print axioms arbitrary_posture_refuses_example
#print axioms unchanged_measurement_refuses_example
#print axioms stale_measurement_refuses_example
#print axioms future_measurement_refuses_example
#print axioms wrong_snapshot_refuses_example
end RelationalSuccessor.CandidateScopedImpact.Witnesses
