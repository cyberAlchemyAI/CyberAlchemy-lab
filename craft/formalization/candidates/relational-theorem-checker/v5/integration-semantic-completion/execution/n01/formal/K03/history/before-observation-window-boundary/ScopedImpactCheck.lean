import ScopedImpactCandidate

set_option autoImplicit false

namespace RelationalSuccessor.CandidateScopedImpact.Checker
open RelationalSuccessor

instance (p : ImpactPolicy) (m : Measurement) : Decidable (ImpactChange p m) := by
  unfold ImpactChange
  cases p.direction <;> infer_instance

-- A false result means unqualified under this resolved fragment; public
-- unsupported/unknown classification and raw/source refinement are pending.
inductive Diagnostic where
  | sourceKind
  | targetKind
  | sourceOwned
  | targetOwned
  | scopeOwned
  | policyOwned
  | observationOwned
  | measurementOwned
  | provenanceOwned
  | scopeQualifier
  | postureQualifier
  | policyNonempty
  | policySource
  | policyTarget
  | permittedScope
  | scopedSource
  | scopedTarget
  | scopeOrdered
  | scopeStart
  | scopeFinish
  | scopeTime
  | observed
  | source
  | target
  | scope
  | policy
  | measurement
  | provenance
  | measuredSubject
  | metric
  | unit
  | observer
  | method
  | measurementTime
  | notFuture
  | fresh
  | impact
  | provenanceMeasurement
  | evidenceRoot
  | actionOwned
  | outputOwned
  | provenanceFrame
  | frameSource
  | frameTarget
  | frameScope
  | frameProfile
  | frameContext
  | frameSnapshot
  | frameEpoch
  | frameTime
  deriving DecidableEq, Repr

def checks (w : World) (c : Claim) : List (Diagnostic × Bool) :=
  [
    (.sourceKind, decide (c.source.kind ∈ allowedSources)),
    (.targetKind, decide (c.target.kind ∈ allowedTargets)),
    (.sourceOwned, decide (c.source ∈ w.sources)),
    (.targetOwned, decide (c.target ∈ w.targets)),
    (.scopeOwned, decide (c.scope ∈ w.scopes)),
    (.policyOwned, decide (c.policy ∈ w.policies)),
    (.observationOwned, decide (c.observation ∈ w.observations)),
    (.measurementOwned, decide (c.measurement ∈ w.measurements)),
    (.provenanceOwned, decide (c.provenance ∈ w.provenanceRoots)),
    (.scopeQualifier, decide (c.scopeQualifier = c.scope.ref)),
    (.postureQualifier, decide (c.postureQualifier = c.policy.code)),
    (.policyNonempty, decide (c.policy.code ≠ "")),
    (.policySource, decide (c.policy.sourceKind = c.source.kind)),
    (.policyTarget, decide (c.policy.targetKind = c.target.kind)),
    (.permittedScope, decide (c.scope.ref ∈ c.policy.scopes)),
    (.scopedSource, decide (c.source.ref ∈ c.scope.participants)),
    (.scopedTarget, decide (c.target.ref ∈ c.scope.participants)),
    (.scopeOrdered, decide (c.scope.start ≤ c.scope.finish)),
    (.scopeStart, decide (c.scope.start ≤ c.observation.frame.epoch)),
    (.scopeFinish, decide (c.observation.frame.epoch ≤ c.scope.finish)),
    (.scopeTime, decide (c.scope.timeDomain = w.timeDomain)),
    (.observed, decide (c.observation.posture = .observed)),
    (.source, decide (c.observation.source = c.source.ref)),
    (.target, decide (c.observation.affectedSubject = c.target.ref)),
    (.scope, decide (c.observation.scope = c.scope.ref)),
    (.policy, decide (c.observation.policy = c.policy.ref)),
    (.measurement, decide (c.observation.measurement = c.measurement.ref)),
    (.provenance, decide (c.observation.provenance = c.provenance.ref)),
    (.measuredSubject, decide (c.measurement.subject = c.target.ref)),
    (.metric, decide (c.measurement.metric = c.policy.metric)),
    (.unit, decide (c.measurement.unit = c.policy.unit)),
    (.observer, decide (c.measurement.observer ∈ c.policy.observers)),
    (.method, decide (c.measurement.method ∈ c.policy.methods)),
    (.measurementTime, decide (c.measurement.timeDomain = w.timeDomain)),
    (.notFuture, decide (c.measurement.observedAt ≤ c.observation.frame.epoch)),
    (.fresh, decide (c.observation.frame.epoch ≤ c.measurement.observedAt + c.policy.maxAge)),
    (.impact, decide (ImpactChange c.policy c.measurement)),
    (.provenanceMeasurement, decide (c.provenance.measurement = c.measurement.ref)),
    (.evidenceRoot, decide (c.provenance.sourceEvidence ∈ w.evidenceRoots)),
    (.actionOwned, decide (c.provenance.action ∈ w.actions)),
    (.outputOwned, decide (c.provenance.output ∈ w.outputs)),
    (.provenanceFrame, decide (c.provenance.frame = c.observation.frame)),
    (.frameSource, decide (c.observation.frame.subject = c.source.ref)),
    (.frameTarget, decide (c.observation.frame.target = c.target.ref)),
    (.frameScope, decide (c.observation.frame.scope = c.scope.ref)),
    (.frameProfile, decide (c.observation.frame.profile = w.profile)),
    (.frameContext, decide (c.observation.frame.context = w.context)),
    (.frameSnapshot, decide (c.observation.frame.snapshot = w.snapshot)),
    (.frameEpoch, decide (c.observation.frame.epoch = w.epoch)),
    (.frameTime, decide (c.observation.frame.timeDomain = w.timeDomain))
  ]

def check (w : World) (c : Claim) : Bool := (checks w c).all (fun item => item.2)
def failed : List (Diagnostic × Bool) → List Diagnostic
  | [] => []
  | (code, passed) :: rest => if passed then failed rest else code :: failed rest

def diagnostics (w : World) (c : Claim) : List Diagnostic := failed (checks w c)

theorem check_exact (w : World) (c : Claim) : check w c = true ↔ Affects w c := by
  have parts : check w c = true ↔
    (c.source.kind ∈ allowedSources) ∧
    (c.target.kind ∈ allowedTargets) ∧
    (c.source ∈ w.sources) ∧
    (c.target ∈ w.targets) ∧
    (c.scope ∈ w.scopes) ∧
    (c.policy ∈ w.policies) ∧
    (c.observation ∈ w.observations) ∧
    (c.measurement ∈ w.measurements) ∧
    (c.provenance ∈ w.provenanceRoots) ∧
    (c.scopeQualifier = c.scope.ref) ∧
    (c.postureQualifier = c.policy.code) ∧
    (c.policy.code ≠ "") ∧
    (c.policy.sourceKind = c.source.kind) ∧
    (c.policy.targetKind = c.target.kind) ∧
    (c.scope.ref ∈ c.policy.scopes) ∧
    (c.source.ref ∈ c.scope.participants) ∧
    (c.target.ref ∈ c.scope.participants) ∧
    (c.scope.start ≤ c.scope.finish) ∧
    (c.scope.start ≤ c.observation.frame.epoch) ∧
    (c.observation.frame.epoch ≤ c.scope.finish) ∧
    (c.scope.timeDomain = w.timeDomain) ∧
    (c.observation.posture = .observed) ∧
    (c.observation.source = c.source.ref) ∧
    (c.observation.affectedSubject = c.target.ref) ∧
    (c.observation.scope = c.scope.ref) ∧
    (c.observation.policy = c.policy.ref) ∧
    (c.observation.measurement = c.measurement.ref) ∧
    (c.observation.provenance = c.provenance.ref) ∧
    (c.measurement.subject = c.target.ref) ∧
    (c.measurement.metric = c.policy.metric) ∧
    (c.measurement.unit = c.policy.unit) ∧
    (c.measurement.observer ∈ c.policy.observers) ∧
    (c.measurement.method ∈ c.policy.methods) ∧
    (c.measurement.timeDomain = w.timeDomain) ∧
    (c.measurement.observedAt ≤ c.observation.frame.epoch) ∧
    (c.observation.frame.epoch ≤ c.measurement.observedAt + c.policy.maxAge) ∧
    (ImpactChange c.policy c.measurement) ∧
    (c.provenance.measurement = c.measurement.ref) ∧
    (c.provenance.sourceEvidence ∈ w.evidenceRoots) ∧
    (c.provenance.action ∈ w.actions) ∧
    (c.provenance.output ∈ w.outputs) ∧
    (c.provenance.frame = c.observation.frame) ∧
    (c.observation.frame.subject = c.source.ref) ∧
    (c.observation.frame.target = c.target.ref) ∧
    (c.observation.frame.scope = c.scope.ref) ∧
    (c.observation.frame.profile = w.profile) ∧
    (c.observation.frame.context = w.context) ∧
    (c.observation.frame.snapshot = w.snapshot) ∧
    (c.observation.frame.epoch = w.epoch) ∧
    (c.observation.frame.timeDomain = w.timeDomain) := by
    simp [check, checks]
  constructor
  · intro h
    rcases parts.mp h with ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18, h19, h20, h21, h22, h23, h24, h25, h26, h27, h28, h29, h30, h31, h32, h33, h34, h35, h36, h37, h38, h39, h40, h41, h42, h43, h44, h45, h46, h47, h48, h49⟩
    exact ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18, h19, h20, h21, h22, h23, h24, h25, h26, h27, h28, h29, h30, h31, h32, h33, h34, h35, h36, h37, h38, h39, h40, h41, h42, h43, h44, h45, h46, h47, h48, h49⟩
  · intro h
    exact parts.mpr ⟨h.sourceKind, h.targetKind, h.sourceOwned, h.targetOwned, h.scopeOwned, h.policyOwned, h.observationOwned, h.measurementOwned, h.provenanceOwned, h.scopeQualifier, h.postureQualifier, h.policyNonempty, h.policySource, h.policyTarget, h.permittedScope, h.scopedSource, h.scopedTarget, h.scopeOrdered, h.scopeStart, h.scopeFinish, h.scopeTime, h.observed, h.source, h.target, h.scope, h.policy, h.measurement, h.provenance, h.measuredSubject, h.metric, h.unit, h.observer, h.method, h.measurementTime, h.notFuture, h.fresh, h.impact, h.provenanceMeasurement, h.evidenceRoot, h.actionOwned, h.outputOwned, h.provenanceFrame, h.frameSource, h.frameTarget, h.frameScope, h.frameProfile, h.frameContext, h.frameSnapshot, h.frameEpoch, h.frameTime⟩

theorem failed_empty_exact (items : List (Diagnostic × Bool)) :
    failed items = [] ↔ items.all (fun item => item.2) = true := by
  induction items with
  | nil => simp [failed]
  | cons item rest ih =>
    rcases item with ⟨code, passed⟩
    cases passed <;> simp [failed, ih]

theorem diagnostics_empty_exact (w : World) (c : Claim) :
    diagnostics w c = [] ↔ Affects w c :=
  (failed_empty_exact (checks w c)).trans (check_exact w c)

theorem refusal_has_diagnostic (w : World) (c : Claim) (refused : ¬ Affects w c) :
    diagnostics w c ≠ [] := by
  intro empty
  exact refused ((diagnostics_empty_exact w c).mp empty)

#print axioms check_exact
#print axioms failed_empty_exact
#print axioms diagnostics_empty_exact
#print axioms refusal_has_diagnostic
end RelationalSuccessor.CandidateScopedImpact.Checker
