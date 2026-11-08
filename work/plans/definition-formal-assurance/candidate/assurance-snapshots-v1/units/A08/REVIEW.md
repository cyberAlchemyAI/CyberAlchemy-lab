# A08 candidate review: definitions before solver claims

This unit implements an isolated finite search over the source-backed partial record semantics established by A07. It is a candidate agent self-review. It accepts neither whole-definition fidelity nor actual owner acts. The formalization episode remains active, with all 183 current definitions in scope.

The concrete result is a constructive separation: lineage, granted permissions, assigned duties, and assertions can vary independently. The positive search found models for all eleven required existential queries after 79 generated configurations. That establishes existence within the declared conditional record profile. It does not establish universal validity, natural-language equivalence, or completion of the episode. Independent denotational replay is the next A09 obligation.

## 1. Source, definition form, and unresolved meaning

Seven exact current SourceRefs bind Authority, AuthorityClaim, Responsibility, Provenance, GovernanceAxisIndependenceInvariant, AuthorityBoundary, and AuthoritySurface. A07 accounts for 166 source meaning units without declaring their whole-definition translations complete. The complete current-source snapshot still contains 183 current definitions and 189 admitted source versions. Admission of those source bytes supplies provenance, not acceptance of this translation.

Two source conflicts remain explicit: FID-RESP-001 separates the normative duty reading from an inherited AuthorityClaim-shaped tuple, and FID-PROV-EMPTY-001 distinguishes a zero-or-more lineage notation from a useful-origin requirement. A08 searches the selected A07 candidate interpretation. It supplies evidence that the interpretation is usable for this bounded purpose; it cannot decide owner precedence between alternatives.

This review classifies each relevant aspect rather than treating every definition as a biconditional or every record as a granted right:

| Aspect | Selected interpretation | Claim boundary |
|---|---|---|
| Definition form | Operational record definitions; the axis invariant is a proof obligation | Neither complete real definition nor full executable governance policy |
| Information type | Known, unknown, deferred, and source-local are tagged states | Missing knowledge is not an empty sequence |
| Provenance type | Empty, complete, incomplete with explicit routed gaps, or unavailable | Valid structure does not prove the referenced history occurred |
| Authority position | Tagged permit or assigned responsibility; both may coexist | Duty is not automatically permission |
| Grant | Independent assignment qualified by role, boundary, principal, scope, operation, object, effect, and challenge route | Root legitimacy is a hypothetical external premise |
| Claim | Explicit assertion carrying fields and an assignment reference | Complete fields do not supply a missing grant |
| Responsibility | Independent duty assignment with outcome and owner route | Fulfillment and moral/legal obligation are not evaluated |
| Boundary | Allowed object/effect sets, excluded effects, and owner binding | Exclusion takes priority; no delegation theorem |
| Surface | The exact selected operation/effect context | Authority does not transfer by a shared principal or object label |
| Lineage predicate | Qualified nonempty known/local trace, including routed incomplete traces | Trace does not create a grant or eliminate uncertainty |
| Axis change | Exact subject/context and full before/after state identities | An unrelated subject cannot be substituted |
| Frame | Every actual component change is intended or explicitly recorded | Silent status promotion fails |
| Assignment change | Complete permit/duty delta denominator and an explicit basis | A changed grant cannot hide in an unchanged posture |
| Static identity | Source, version, scope, and local symbol qualify predicate identity | Same spelling or shared carrier does not merge meaning |
| Carrier | Explicit candidate same-object Record identity maps | This does not prove whole-definition equivalence or closure |
| Logical evidence | Models for independently generated T, I, and Q | Search success does not admit source meanings |
| Absence | Complete exhaustion of an exact declared rank interval | Partial search cannot justify absence; no unbounded theorem |
| Readiness | Logical observations and fidelity/currentness/closure gates remain separate | All semantic admission gates remain pending |

## 2. Types and independent denotation

The record signatures are sealed in A07. A08 reuses their closed structural validator, but implements the record predicates separately. It never calls A07 `inspect_state` or `check_move`; tests make those calls fail if attempted. This separation reduces accidental agreement through the same evaluator. It is still one implementation of a denotation, and must receive the independent A09 replay specified in the DAG.

For a record x in the exact selected local-use context, let:

- Right(x) mean that an independent permit assignment satisfies the role, boundary, and exact query qualifications.
- Duty(x) mean that an independent responsibility assignment matches its role, context, and outcome.
- Position(x) mean Right(x) or Duty(x).
- BackedRight(x) mean a complete right assertion refers to and matches a qualified independent permit assignment.
- Traceable(x) mean the selected trace condition holds, with source-local scope checked exactly.

These predicates are deliberately unequal. An ungranted complete assertion is representable and unbacked. An unclaimed grant remains a right. A responsibility remains a position without becoming a right. An incomplete assertion remains incomplete while its independent grant can still exist. Unknown origin does not revoke an otherwise qualified permit. The operation-specific requirement that local use have trace evidence does not become a universal axiom Right implies Traceable.

The static IR contains only unary predicates over Record. Seven source-qualified IR inputs and six explicit carrier maps compose a shared hypothetical object carrier. All whole-source clauses in that projection remain deferred. They have not been lowered to first-order axioms. This is a projection of selected record denotations, not a generic translation theorem from records, deontic language, or temporal behavior into classical first-order logic.

## 3. Theory, required populations, and query targets

The selected static T has exactly two assertions:

```text
forall x:Record. Position(x) iff (Right(x) or Duty(x))
forall x:Record. BackedRight(x) implies Right(x)
```

The record transition must also satisfy the independently implemented subject, snapshot, frame, and assignment-delta checks. Optional named stress constraints are recorded separately in the request and its digest. They are never inserted into the sealed projection theory. A test regenerates a required set around an added counterexample target and confirms the profile still rejects that substituted theory.

I requires an inhabitant for each of the five predicates. A06 independently regenerates the exact required set from T, population policy, endpoint bindings, and relation requests; submitted result lists cannot choose their own denominator. Its eleven logical queries are:

1. Consistency of the selected conditional theory and record frame.
2. Joint satisfiability of all five required populations.
3. Five separate population existence queries, evaluated under the joint population requirements.
4. Two intersection witnesses: Traceable with Position, and Traceable with BackedRight.
5. Two permitted distinction witnesses: Traceable outside Position, and Traceable outside BackedRight.

The direction is explicitly forward. These requirements do not demand converse differences or pairwise disjointness. Overlap and distinction can coexist in one model. Every witness carries its rank, full record/transition model and digest, and the source-qualified static projection model and digest. Eleven administrative/semantic gates accompany the eleven logical queries; they are not discharged by finding models.

Inconsistent stress constraints produce no candidate T model. A satisfiable theory with an empty required Right population is a different outcome: it has T models but no joint I model. A trace-implies-position stress constraint can retain overlap while eliminating the requested Traceable-outside-Position witness. These are three distinct diagnoses, preventing classical vacuity from masquerading as useful assurance.

## 4. Exact finite domain and algorithm

Two hypothetical objects form the carrier. Neither refers to an actual grant or actual completed review. The search enumerates the mixed-radix product:

```text
(6 provenance choices for object 0)
* (6 provenance choices for object 1)
* (2 independent grant bits for each object)
* (2 independent duty bits for each object)
* (5 selected claim scenarios)
* (3 selected transition forms)
= 8640 configurations
```

The radix vector is `(6,6,2,2,2,2,5,3)`. Grant and duty assignments vary independently of lineage and assertions. Claims are one global selected scenario applied to both records; the incomplete-right scenario leaves the first claim partial and the second complete. This is an explicit profile restriction: arbitrary independent combinations of claim sets, arbitrary subjects, arbitrary owners, different contexts, and arbitrary transition sequences are outside this product.

Transition forms are a provenance-only move, a move with silent status change, and a move that explicitly records the extra status change. The silent variant remains in the enumerated universe and fails the frame condition; it is not quietly removed before search. Assignment-delta controls exercise additional well-typed transitions beyond these three generator forms.

The algorithm constructs each requested configuration rank, computes record predicates and the frame, projects the finite model, and evaluates T, I, and required Q through the static denotation. It records the first actual witness for each required query. Default first-evidence mode stops only after all eleven queries have witnesses. It never selects the A07 example list as its search universe.

An explicitly requested interval `[start, stop)` may be exhausted. Its exact scope and request hash travel with the result. Exhaustion is complete only if every rank in that interval was examined without interruption or binding failure. It does not certify all 8640 configurations unless the interval is the full product and the complete-search flag survives every check.

## 5. Budgets, currentness, and failures

The existing P01 caps apply: 30 seconds, 10000 configurations, 100000 evaluation steps, at most three domain elements, and one megabyte of output. Callers may tighten them. A08 has no functions, so the function-tuple-space cap does not create a new obligation here. The fixed two-object carrier is rejected if the requested domain budget is smaller than two; it is not silently shrunk.

Evaluation-step accounting covers predicate/record comparisons and logical AST operations, not every Python instruction, structural validation instruction, digest operation, or OS call. Time cancellation is cooperative: it is checked at bounded operation boundaries. Startup input validation and final byte checks can take longer than a tiny requested deadline. This is not a hard process-level CPU or memory sandbox. Native hard process isolation remains later work.

Sources, the selected A07 signatures, upstream context bytes, all captured projection inputs, the candidate implementation, and the P01 selected runtime are checked. The current-source snapshot is rechecked through A07 binding. Final reads also occur on an interrupted search before any partial witnesses are returned. Stale input/runtime/checker bindings invalidate witnesses and complete-exhaustion claims. The verifier must still check externally selected exact receipt/input bindings; an emitted digest alone does not establish that a caller selected those bytes.

An early timeout or cancellation before input preparation is explicitly labeled `unresolved-no-evidence-emitted` for the query denominator. It cannot be read as an empty successfully verified manifest. Once preparation succeeds, all eleven logical identities remain present even on interruption. An output limit drops witness payloads and strengths while preserving all required logical identities, pending gate identities, and input digests. A malformed or unsupported request fails without truth evidence.

Retained actual searches cover positive existence, bounded collapse, contradiction, missing population, the full-range budget stop, configuration/step/output limits, real clock expiry, and a real cancellation callback. Additional tests cover ungranted claims, incomplete claims, unrelated subjects, assignment deltas, stale bindings at closeout, malformed containers/nonfinite values/Unicode, missing projection inputs, nominal predicate substitution, and substituted theories/required sets.

The first invocation failed because Markdown byte bindings were incorrectly parsed as JSON. Its code and failure are retained in attempt-001. The next test run had 38 passing checks and one expectation failure over the stale-input outcome label; code, tests, output, and diagnosis are retained in attempt-002. The corrected and extended final suite passes 42 tests. Neither failed attempt is represented as final acceptance evidence.

## 6. Disposition and next obligations

A08 is accepted by this agent as a bounded implementation of the declared partial record search, subject to its exact receipt and preserved byte manifest. Candidate acceptance does not discharge any source-owner, dependency-closure, semantic-admission, or unbounded-proof gate.

A09 must independently evaluate the retained record models against the mathematical denotation, regenerate the projection and all required queries, and audit the complete declared finite product or retain explicit incomplete outcomes. Exhaustive rank sharding must bind disjoint intervals and their complete union; combining partial or overlapping runs cannot manufacture exhaustion. A10 must expose the exact meanings, source alternatives, root assumptions, and independent-check results for review; pending owner acceptance must remain explicit.

Full definition-family translations, semantic dependency closure, carrier decisions, solver/kernel and extension profiles, revision/regression handling, combined global theory consistency and non-vacuity, owner acceptance, and the complete end-of-episode explanation remain outstanding. Current counts of owner-accepted whole-definition translations and whole-definition proofs remain zero.
