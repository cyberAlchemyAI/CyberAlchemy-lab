# AlchLang FormalClaim and sorted first-order logic reference

Status: owner-directed AlchLang authoring reference; `application-v1` consumer
syntax and bounded projections implemented

Scope: this reference describes the retained `application-v1` claim-based
authoring path. Its claim-to-Rule relationship below is specific to that path.
The cumulative generic application path has explicitly executable Rules and
does not require a FormalClaim to generate code; see
[Generic applications](GENERIC-APPLICATIONS.md). Optional formal export joins
that path at C15. Parsing a claim runs no solver, TDE or EVF.

Consult this page before writing or reviewing an AlchLang example containing a
Rule, Policy, Invariant, Query condition, permission condition, or State Machine
guard. It records the selected AlchLang composition model and identifies the
older implementation surface that must not be mistaken for that target.

This page does not redefine DomainSpec formalization semantics. The canonical
contracts remain the DomainSpec JSON and JSON Schema sources named under
[Authority](#authority). AlchLang owns only its authoring and lowering contract.

## Decision

AlchLang uses the DomainSpec FormalClaim model for formal domain truth. Its
logical source is sorted first-order logic under an explicit formal-language
profile and signature. The older AlchLang `sfol-v1` expression dialect is a
bounded compatibility implementation; it is not the target model for new
language examples.

The retained `application-v1` path requires the following composition:

```text
accepted business meaning
  -> exact definition-binding graph
  -> FormalClaim
       - formal-language profile
       - signature: sorts, functions, predicates, constants
       - one canonical proposition
       - assumptions/domain/ceiling that contribute to identity
  -> Rule
  -> Rule consumers
       - Policy case? no: Policy references the Rule
       - State transition guard references the Rule
       - Invariant references the Rule or its FormalClaim
       - Operation enforcement references the Rule
  -> optional preservation-backed provider projection
  -> EVF evidence
```

A FormalClaim is not proof, execution, validation evidence, authorization, or
runtime behavior. A Rule result is not permission to execute an Operation. A
Policy selection returns a declared target identifier and does not execute it.

## Authority

Consult these sources in this order:

1. DomainSpec FormalClaim identity and profile explanation:
   `craft/projects/domainspec-v2/formalization/docs/FORMALCLAIM-AND-PROFILES.md`.
2. Candidate FormalClaim source contract:
   `craft/projects/domainspec-v2/formalization/schemas/formal-claim-source-v4-candidate.schema.json`.
3. Formal-language profile registry:
   `craft/projects/domainspec-v2/formalization/profiles/formal-language-profiles.json`.
4. Definition-binding contract:
   `craft/projects/domainspec-v2/formalization/schemas/formal-claim-definition-binding.schema.json`.
5. Current implemented TDE intake, where compatibility matters:
   `FormalClaimSourcePayload/v2`, as identified by the DomainSpec formalization
   guide and v4 candidate contract.

The first four paths are relative to this repository's selected Craft source.
The v4 contract is a candidate. It requires an exact v2 projection before the
current TDE intake can consume it; an adapter may not add or reinterpret
meaning.

## Opt-in v4 formation check

The core CLI can check one exact-referenced v4 candidate without accepting or
admitting it:

```sh
node scripts/run-toolchain.mjs tsx src/core-cli.ts check-formal-claim < request.json
```

Run this from `language/capabilities/alchlang/plans/general-compiler-v1/implementation`.
`request.json` has this shape (replace the illustrative digest and size with
the actual bytes of the claim file):

```json
{
  "schema_version": "alchlang.formal-claim-formation-request/v1",
  "root_directory": "/absolute/evidence/root",
  "claim_ref": {
    "path": "relative/claim.json",
    "sha256": "<actual lowercase SHA-256>",
    "size_bytes": 123,
    "current": true
  },
  "selected_profile": "fol-core/1-candidate"
}
```

The claim itself must exact-reference its profile registry under the same
root. `checked` exits 0; `rejected` exits 2; `unsupported` exits 3. Every
result has `authority_effect: none` and a formation-only ceiling. A checked
proposition is not a checked definition closure, accepted business meaning,
admitted FormalClaim, TDE case set, F5/EVF result, or runtime guarantee. The
DomainSpec package validator remains a separate structural/package check and
does not invoke this command.

## FormalClaim identity

One FormalClaim contains one canonical proposition and one declared formal
signature. Its identity includes:

- accepted BusinessMeaning identity;
- the explicit definition-binding graph and accepted definition closure;
- formal-language profile semantics;
- sorts, functions, predicates, and constants in the formal signature;
- canonical proposition semantic identity;
- meaning-bearing assumptions, domain, universe, time, and currentness rules;
- the claim ceiling.

Changing any of those creates a different claim identity. Changing a provider,
solver version, native syntax, runtime environment, finite execution bound, or
InterpretationModel invalidates the relevant evaluation/projection evidence but
does not by itself create a different FormalClaim.

## Logical profiles

`fol-core/1-candidate` is the canonical source profile for ordinary AlchLang
domain claims that require sorted first-order logic. It provides typed
predicates, universal and existential quantifiers, equality, and explicit
assumptions under an exact signature.

`smt-sfol/1-candidate` is a solver-oriented canonical source or projection
profile. It preserves native `sat`, `unsat`, `unknown`, and timeout meanings.
It must not turn `unknown`, timeout, a bounded result, or absence of a found
witness into a general truth claim.

Lean/DTT, TLA/TLC, Alloy, and Souffle are separate source or projection
profiles. Provider availability never chooses the canonical source profile.

## AlchLang composition contract

### Rule

A Rule is the named DomainSpec consumer of one formal condition. Its condition
must resolve to one FormalClaim or to a lossless, identity-bound projection of
that FormalClaim. It must not introduce a second expression language.

Current `application-v1` form:

```alch
formal-claim OrderCanBeSubmittedClaim:
  profile fol-core/1-candidate
  sort Order
  predicate HasLine(Order)
  predicate HasNonNegativeTotal(Order)
  proposition forall order: Order:
    HasLine(order) and HasNonNegativeTotal(order)
  ceiling "Formal submission eligibility only; no observed runtime guarantee."

rule OrderCanBeSubmitted:
  ontology "Only a non-empty order with a valid total may be submitted."
  meaning "Submission requires at least one line and a non-negative total."
  claim OrderCanBeSubmittedClaim
```

The sorts and predicate signatures are part of the claim. A bare expression
such as `order.total >= 0` is not equivalent unless its types, definitions,
assumptions, and semantic identity are closed by the same claim contract.

### Policy

A Policy references declared Rules. It does not own inline SFOL formulas.

```alch
policy FulfillmentPolicy:
  inputs order
  case HighValueOrder -> ManualReview
  default StandardFulfillment
  applies ManualReview, StandardFulfillment
```

`HighValueOrder` must already be a declared Rule bound to its FormalClaim.
This older form is forbidden in target examples:

```alch
# LEGACY — do not present as the target language
policy FulfillmentPolicy:
  inputs order
  case order.total.amount > 1000 -> ManualReview
  default StandardFulfillment
```

Policy ordering chooses the first Rule that evaluates true. It neither proves
the Rule nor authorizes or executes the selected target.

### State Machine

A transition guard references a declared Rule. An event selector references a
declared Event. The State Machine must not parse either as an inline formula.

```alch
state-machine OrderLifecycle:
  subject Order
  initial Draft
  state Draft
  state Submitted

  transition Submit:
    from Draft
    to Submitted
    on OrderPlaced
    guard OrderCanBeSubmitted
```

The required graph is:

```text
OrderPlaced --transitions--> OrderLifecycle
OrderCanBeSubmitted --guards--> Submit
Submit --from/to--> Draft, Submitted
OrderLifecycle --subject--> Order
```

The current compatibility syntax
`Draft -> Submitted when OrderCanBeSubmitted emits OrderPlaced` may remain in
implementation-specific documentation, but it must not be used to imply that
the Event is both a trigger and a resulting event.

### Invariant and Operation

An Invariant references a declared Rule/FormalClaim. An Operation can be
enforced by a declared Rule. Neither duplicates the proposition text.

```alch
invariant MoneyIsNonNegative:
  claim NonNegativeMoneyClaim

rule CustomerCanPlaceOrder:
  claim ActiveCustomerClaim
  enforces PlaceOrder
```

### Query and other executable projections

A Query filter or runtime check may consume an executable projection of a
FormalClaim only when the projection declares its domain/bound, losses, result
semantics, and preservation direction. The executable subset is not allowed to
replace the claim or silently narrow its meaning.

## What remains implemented as legacy compatibility

The general compiler retains an explicitly separate compatibility path:

- `logic sfol-v1` selects a quantifier-free comparison/presence expression
  dialect in the base parser;
- the legacy branch in `parser.ts` parses Policy cases as inline formulas;
- `predicate-parser.ts` implements the bounded expression parser;
- `model.ts` names the resulting AST `SfolFormula`;
- `typed-backend.ts` directly evaluates Policy case formulas;
- `definitions/DEFINITIONS.md`, `docs/TUTORIAL.md`, and `docs/LANGUAGE.md`
  still describe that compatibility surface;
- the declarative-function profile has collection quantifiers, but it does not
  by itself implement FormalClaim identity, definition closure, or profile-bound
  preservation.

These facts describe the retained `legacy-sfol-v1` implementation, not
`application-v1`. New examples must select their profile explicitly.

## Proposition parser limits

`parseFormalProposition` exports `FORMAL_PROPOSITION_LIMITS_VERSION`
(`fol-core-proposition-limits/v1`) and the immutable
`FORMAL_PROPOSITION_LIMITS` object. Each invocation has these inclusive bounds:

| Budget key | Maximum | Measurement |
| --- | ---: | --- |
| `source_bytes` | 262144 | UTF-8 bytes of the proposition, checked before tokenization |
| `tokens` | 65536 | Lexical tokens, checked before AST construction |
| `ast_nodes` | 16384 | Proposition and term nodes, including function arguments |
| `ast_depth` | 128 | Longest AST path, with the root at depth 1 |

Grouping parentheses consume tokens but add no AST depth. For example, 10000
pairs around a single zero-argument predicate remain admissible. Negations,
quantifiers, function nesting and connective chains do add depth. All grammar
transitions use an explicit work stack; host recursion is not a fifth budget.

Exhaustion throws `CompilationRejected` with an issue whose code is
`CLAIM_RESOURCE_LIMIT`, whose message includes `kind=<budget> limit=<maximum>`,
and whose path retains the supplied source path/line plus the parser offset.
Malformed syntax, unknown symbols, arity errors and sort errors retain their
specific diagnostics. Inputs within the budgets retain the existing grammar,
precedence, binding and signature-use requirements. A supplied invalid claim
still rejects; these bounds do not make claims mandatory for generic code
generation. They bound this proposition parser, not every document scanner or
future formal backend. Installed-package qualification is tracked separately
by the package repair.

## Review checklist

Before accepting an AlchLang example, verify all of the following:

- [ ] Every formal condition has one identifiable FormalClaim source.
- [ ] The claim binds accepted meaning and an explicit definition graph.
- [ ] Sorts and callable signatures are explicit and type-correct.
- [ ] The canonical proposition and profile are identified.
- [ ] Policies reference declared Rules rather than inline formulas.
- [ ] State-machine guards reference declared Rules.
- [ ] Event triggers and resulting events are not collapsed.
- [ ] Invariants and Operations reuse declared Rules/claims.
- [ ] Executable subsets are labeled as projections with exact limits.
- [ ] Solver or runtime evidence is not described as universal proof,
      authorization, execution, admission, or production correctness.
- [ ] Example syntax is labeled accurately as current compatibility or target.

## Drift ledger

| Surface | Current drift | Required successor behavior |
| --- | --- | --- |
| `definitions/DEFINITIONS.md` `ALCH-TB-D5` | Defines the reduced `sfol-v1` kernel as the shared language | Replace or supersede it with the FormalClaim-bound sorted-FOL model |
| `docs/LANGUAGE.md` | Calls `sfol-v1` the only supported logic profile | Keep this only as implementation compatibility and link here |
| `docs/TUTORIAL.md` | Teaches inline formulas in Policy cases | Teach declared Rule references for target Alch |
| legacy branch in `src/parser.ts` | Parses each compatibility Policy case as `parseSfolFormula(...)` | Kept isolated behind `legacy-sfol-v1`; `application-v1` resolves declared Rules |
| `src/model.ts` | Represents the compatibility formula AST | Does not own the `application-v1` FormalClaim model |
| `src/predicate-parser.ts` | Owns formula meaning locally | Become an explicit bounded projection parser or be superseded |
| `src/typed-backend.ts` | Evaluates inline Policy predicates | Evaluate referenced Rules without granting target execution |
| declarative-function expressions | Support finite collection quantifiers without FormalClaim identity | Bind any formal use to an explicit claim/projection contract |

This ledger now distinguishes retained compatibility debt from the implemented
`application-v1` parser and bounded consumer projections. It does not claim the
later E02 formal-provider or EVF bridge.

## Open Questions

- Which selected DomainSpec v4 validation contract will consume the opt-in
  formation result without treating unsupported historical media as checked?
- How will accepted inline definitions and their complete theory be parsed,
  type-checked, and bound to the current proposition?
- Which independently reviewed preservation and runtime evidence will close
  the remaining Auth no-call and F5/EVF obligations?
