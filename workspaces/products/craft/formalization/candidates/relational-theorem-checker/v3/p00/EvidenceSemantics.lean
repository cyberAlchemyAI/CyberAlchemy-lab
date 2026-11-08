import RequirementSemantics
import RecursiveConservativity
import ConditionSemantics
import BaselineContract

namespace RelationalV3

inductive ChangeClass where
  | register | ruleOnly | richerMigration
  deriving DecidableEq, Repr

inductive Obligation where
  | snapshotShape | sourceCurrent | profileCatalogCurrent | referenceImmutability
  | producerPolicy | projectionExact | kindProjectionExact | unaryViewExact
  | sealedDerivationExact | sourceSupportExact | typedTheory | protectedLineage
  | derivationSoundness | closureAdequacy | completeClosure | sourceInterpretation
  | conditionConsistency | oldFrameIdentical | recursiveExtensionHypotheses
  | everyOldModelExpansion | transitionView
  deriving DecidableEq, Repr

-- Normative inventory fixed independently of any submitted result or checker.
def registrationObligations : List Obligation :=
  [.snapshotShape, .sourceCurrent, .profileCatalogCurrent, .referenceImmutability,
   .producerPolicy, .projectionExact, .kindProjectionExact, .unaryViewExact,
   .sealedDerivationExact, .sourceSupportExact, .typedTheory, .protectedLineage,
   .derivationSoundness, .closureAdequacy, .completeClosure, .sourceInterpretation,
   .conditionConsistency]

def requiredObligations : ChangeClass → List Obligation
  | .register => registrationObligations
  | .ruleOnly => registrationObligations ++
      [.oldFrameIdentical, .recursiveExtensionHypotheses, .everyOldModelExpansion]
  | .richerMigration => registrationObligations ++ [.transitionView]

inductive Layout where
  | combined | staged
  deriving DecidableEq, Repr

inductive ModuleRole where
  | combined | data | typed | closure | expansion
  deriving DecidableEq, Repr

def requiredModules : Layout → List ModuleRole
  | .combined => [.combined]
  | .staged => [.data, .typed, .closure, .expansion]

structure Identity where
  proposal : String
  baseline : String
  profile : String
  catalog : String
  toolchain : String
  sourceProfile : String
  deriving DecidableEq, Repr

abbrev IdentityValid (i : Identity) : Prop :=
  i.proposal ≠ "" ∧ i.baseline ≠ "" ∧ i.profile ≠ "" ∧
  i.catalog ≠ "" ∧ i.toolchain ≠ "" ∧ i.sourceProfile ≠ ""

structure Artifact where
  path : String
  digest : String
  deriving DecidableEq, Repr

abbrev ArtifactValid (a : Artifact) : Prop := a.path ≠ "" ∧ a.digest ≠ ""

structure ModuleEvidence where
  role : ModuleRole
  source : Artifact
  compiled : Artifact
  deriving DecidableEq, Repr

structure Request where
  identity : Identity
  changeClass : ChangeClass
  layout : Layout
  deriving DecidableEq, Repr

structure Manifest where
  identity : Identity
  changeClass : ChangeClass
  layout : Layout
  obligations : List Obligation
  modules : List ModuleEvidence
  general : Artifact
  projection : Artifact
  dependencies : Artifact
  deriving DecidableEq, Repr

def artifacts (m : Manifest) : List Artifact :=
  m.modules.flatMap (fun e => [e.source, e.compiled]) ++
    [m.general, m.projection, m.dependencies]

abbrev EvidenceComplete (r : Request) (m : Manifest) : Prop :=
  IdentityValid r.identity ∧ m.identity = r.identity ∧
  m.changeClass = r.changeClass ∧ m.layout = r.layout ∧
  m.obligations = requiredObligations r.changeClass ∧
  m.modules.map ModuleEvidence.role = requiredModules r.layout ∧
  ∀ a ∈ artifacts m, ArtifactValid a

-- Byte-currentness is an explicit host/hash assumption, not issuer truth.
abbrev RecordedCurrent (r : Request) (m : Manifest) (current : Artifact → Prop) : Prop :=
  EvidenceComplete r m ∧ ∀ a ∈ artifacts m, current a

structure ReplayEvent where
  identity : Identity
  session : String
  deriving DecidableEq, Repr

structure Invocation where
  session : String
  events : List ReplayEvent
  deriving DecidableEq, Repr

-- Accepted replay events belong to a live verifier invocation, never caller JSON.
-- The meaning of replayAccepted is fixed by the verifier boundary, not a flag.
abbrev FreshQualified (r : Request) (m : Manifest) (current : Artifact → Prop)
    (invocation : Invocation) (replayAccepted : ReplayEvent → Prop) : Prop :=
  RecordedCurrent r m current ∧ invocation.session ≠ "" ∧
  ∃ e ∈ invocation.events, e.identity = r.identity ∧
    e.session = invocation.session ∧ replayAccepted e

inductive Outcome where
  | qualified | invalid | unsupported | unknownResource | cancelled | unsupportedPolicy
  deriving DecidableEq, Repr

inductive Claim where
  | derivation | completeClosure | absence | shadowReady
  deriving DecidableEq, Repr

-- Necessary permission, not sufficient proof of an individual logical claim.
def ClaimPermitted (outcome : Outcome) (_claim : Claim) : Prop := outcome = .qualified

inductive PublicationPhase where
  | prepared | committed | reconciliationRequired
  deriving DecidableEq, Repr

structure Publication where
  phase : PublicationPhase
  mediatedWriters : Bool
  reviewedGeneration : Nat
  observedGeneration : Nat
  successor : Identity
  deriving DecidableEq, Repr

-- Abstract contract only; filesystem durability/atomicity require host evidence.
abbrev PublicationQualified (r : Request) (m : Manifest) (current : Artifact → Prop)
    (invocation : Invocation) (accepted : ReplayEvent → Prop) (p : Publication) : Prop :=
  p.phase = .committed ∧ p.mediatedWriters = true ∧
  p.reviewedGeneration = p.observedGeneration ∧ p.successor = r.identity ∧
  FreshQualified r m current invocation accepted

-- Existing meanings are referenced without strengthening or replacing them.
abbrev MemberConformance := Successor.MemberConformance
abbrev SourceFaithful := Successor.SourceFaithful
abbrev EvaluationKey := Successor.EvaluationKey
abbrev ActiveNorm := Successor.ActiveNorm
abbrev PotentialNorm := Successor.PotentialNorm
abbrev RuleOnlyFrame := Successor.Baseline.RuleOnlyFrame

end RelationalV3
