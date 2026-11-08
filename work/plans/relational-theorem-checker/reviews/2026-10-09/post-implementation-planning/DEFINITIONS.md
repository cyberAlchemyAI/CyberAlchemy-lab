# Concept-by-concept implementation review

The 17 successor concepts below are reviewed individually against the accepted v2 boundaries. The retained production selection contains 176 explicit declarations in 18 modules; that detailed existing declaration review is reused, not silently expanded into an inventory of every generated witness or Python helper.

Retained declaration evidence: [DEFINITION-REVIEW.md](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/DEFINITION-REVIEW.md) and [definition-inventory.json](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/definition-inventory.json). New APIs do not alter those accepted definitions.

## MemberConformance

**Meaning retained:** Inv(G), assertion membership and independent ConformsAt.

**Boundary to preserve:** A valid but unrecorded edge cannot support an observed fact.

**Implementation plan:** P00, P09. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ConformsTo

**Meaning retained:** reference × reference × scope; exact assessment-backed member conformance.

**Boundary to preserve:** Sealed initial observation; no caller facts or rule heads.

**Implementation plan:** P00, P02, P09, E01. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## TargetKind

**Meaning retained:** reference × text; exact node kind through a checked vocabulary map.

**Boundary to preserve:** Independent sound/complete projection; kind text literal must be in captured domain.

**Implementation plan:** P00, P01, P09. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ExistentialConformanceView

**Meaning retained:** Unary Conforms matches rich observations in projected initial inventory.

**Boundary to preserve:** No new rule writing old Conforms; not equality for arbitrary old models.

**Implementation plan:** P00, P04, P09. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## SupportSet

**Meaning retained:** Exact graph/assertion/assessment/profile witnesses for a deduplicated observation.

**Boundary to preserve:** Retain multiple supports; prove validity and source-support completeness.

**Implementation plan:** P02, P04, E01. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ProducerPolicy

**Meaning retained:** Sealed observations versus derived ordinary information, orthogonal to root Role.

**Boundary to preserve:** Every initial source and rule head authorized by exact selected profile.

**Implementation plan:** P00, P03, P09. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## RegisteredBaseline

**Meaning retained:** Bound graph/registry/theory/source/interpretation/epoch/policy/toolchain/catalog snapshot.

**Boundary to preserve:** Independently qualify before use; displayed version is not readiness.

**Implementation plan:** P01, P03, P08. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## BaselineTransition

**Meaning retained:** Named richer-snapshot change with explicit fact/domain/assessment differences.

**Boundary to preserve:** Distinct from fixed-domain rule-only expansion; no reused incompatible receipts.

**Implementation plan:** P00, P08, E04. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## RecursiveFreshExtension

**Meaning retained:** Fixed domain/roots/old rules/facts with positive fresh derived ordinary heads.

**Boundary to preserve:** Every-old-model expansion, finite stabilization, no unseeded facts.

**Implementation plan:** P00, P03, P09. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## EvaluationKey

**Meaning retained:** Profile, condition revision, exact context/snapshot, relevant endpoints and epoch.

**Boundary to preserve:** Consistent selected status; evaluator/interpretation identity bound.

**Implementation plan:** P00, P04, E00. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ConditionStatus

**Meaning retained:** holds, does-not-hold, unknown; inconsistent selection gives conflict diagnostic.

**Boundary to preserve:** No absence-as-false; no contradictory evidence projects holds.

**Implementation plan:** P04, P06, E00. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## PotentialNorm

**Meaning retained:** Inherited interpreted norm with exact Origin support.

**Boundary to preserve:** No claim of true condition, subject conformance or fulfillment.

**Implementation plan:** P00, P04, E03. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ActiveNorm

**Meaning retained:** PotentialNorm plus exact checked ConditionHolds in its context.

**Boundary to preserve:** False, unknown or mismatched context cannot activate; supplied truth explicit.

**Implementation plan:** P00, P04, E00. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ActiveConflict

**Meaning retained:** Active require and active forbid at same subject/action/scope/evaluation context.

**Boundary to preserve:** Separate potential conflict; permit neither erases conflict nor grants authority.

**Implementation plan:** P04, P09, E00. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ClaimScope

**Meaning retained:** Observed/candidate; query derivation/complete closure/model counterexample.

**Boundary to preserve:** No advertised guarantee beyond actually satisfied obligations.

**Implementation plan:** P00, P01, P04, P11. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## ResourceEnvelope

**Meaning retained:** Early conservative bounds and measured stage work/time/allocation ceilings.

**Boundary to preserve:** Exhaustion is unknown and blocks closure, absence and readiness.

**Implementation plan:** P06, P07, P10. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

## SourceInterpretation

**Meaning retained:** Exact qualifier/source/context-to-typed witness for a selected fragment.

**Boundary to preserve:** No guessed strings; extra fields mapped, assumed or explicitly unsupported.

**Implementation plan:** P01, P05, E01, E02, E03, E04, E05. **Review decision:** preserve accepted v2 meaning; extend only through named independent successor contracts.

ConditionStatus diagnostics currently include yes/no/unknown/invalid; operational unknown-resource and cancelled are separate incomplete outcomes. BaselineTransition covers the selected initial-view relation, not a general conservative domain migration. ResourceEnvelope currently gives conservative work and stage-time ceilings; P06 is needed before claiming enforced aggregate memory. Neither named theorem proofs nor byte binding checks establish the truth/authenticity of external assessments.

See [the one-by-one retained declaration dispositions](/home/vlad_/projects/CyberAlchemy-lab/docs/plans/relational-theorem-checker/reviews/2026-10-09/post-implementation-planning/DECLARATIONS.md) for all 176 declarations.
