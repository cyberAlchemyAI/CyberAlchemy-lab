# Test derivation from meta types and relationships

Status: general derivation contract with a candidate compiled-graph construction path. Runnable behavior coverage is not complete.

This document specifies what a complete, source-traceable test derivation *would require* for DomainSpec's current node and edge vocabulary. The authority for node meaning is [DS-D1](../../ontology/definitions/meta-types/meta-types.md) and its per-type criteria. The authority for edge signatures, scope, and multiplicity is [relationships.yml](../../ontology/definitions/relationships/relationships.yml). This document does not change either registry. The older [TEST-PIPELINE.md](TEST-PIPELINE.md) describes a feature-document pipeline; its examples are not a complete DS-D1/DS-D8 contract.

## Construction chain and current boundary

| Stage | Owner and output | Current result |
| --- | --- | --- |
| Meaning | DS-D1 criteria, DS-D8 signatures, D2 validation governance and D21 derivation consequence | Canonical definitions already exist. |
| Authorship | Project-local machine sources and exact source manifest | Current compiler input. |
| Formation | Compiled, checked graph with typed nodes, edges, scope and relationship witnesses | Current compiler path. |
| Derivation | `derive-tests` maps the checked graph to source-bound cases and explicit unresolved dispositions | Implemented as a read-only candidate construction plan for backend nodes and edges. |
| Binding and oracle | Select a target, input witness and independent expected observation for each case | Only selected older TDE paths have this; the general construction plan has no binding adapter yet. |
| Execution and evidence | Run the selected test/profile, retain exact inputs and observed results, then join through EVF | General plan-to-runner and plan-to-EVF joins remain open. |
| Lifecycle decision | The D28 obligation owner decides whether exact evidence discharges an obligation | No generated plan or passing test changes lifecycle state. |

This ordering matters: a checked graph makes a declaration eligible for derivation, while a generated case still needs a separate implementation and oracle before it can say anything about runtime conformance.

## The derivation rule

Given an admitted source graph `G`, a pinned definition/relationship registry `D`, and a versioned derivation rule set `Δ`, derive an ordered set of obligations `δ(G,D,Δ)`. Each obligation records its source anchor and exact source fingerprint, subject type or edge signature, condition and expected observation, required fixture or witness, oracle/binding requirement, and disposition. Its stable key includes the rule version and local source semantics. A changed key must be reconciled with the previous obligation, not silently accepted as an unrelated new test.

1. **Validate formation first.** Reject an undeclared type, malformed type criterion, unresolved endpoint, wrong direction, disallowed scope or multiplicity, or deprecated authored verb. A malformed declaration cannot produce a passing behavior test.
2. **Derive node obligations.** For every well-formed concept, derive the applicable criterion and declared behavior below. A type label alone yields only a formation/structural obligation.
3. **Derive edge obligations.** For every admitted authored edge, derive one relation-conformance obligation and its typed consequence below. Composition of multiple edges may add a path obligation only when the composition rule and expected result are explicit.
4. **Choose cases from authored meaning.** For each finite decision, branch, transition, mapping, status or error declaration, create a distinct case. Add boundary and rejection cases where the source defines the boundary. Do not invent an open-world complement, a business policy, or an expected value from the implementation under test.
5. **Bind and execute separately.** A runnable test requires a selected implementation target, inputs, independent expected result or oracle, and an execution profile. Without these, retain a counted obligation with `needs-binding`, `needs-oracle`, `needs-formal`, `unsupported`, or `candidate-only` disposition. A generated `todo`/`skip` is not a passing test.

The minimum auditable record is `{source_ref, source_digest, definition_ref, subject_ref, rule_id, rule_version, case_id, input_or_witness, expected_observation, oracle_ref, binding_ref, disposition, obligation_key}`. Coverage is reported by **declared obligation and disposition**, not merely by emitted or passing test count. Source conformance, generated-test execution, runtime behavior, and provider evidence are separate results.

For example, if `PositiveAmount --enforces--> CreatePayment` and `CreatePayment --produces--> PaymentCreated`, the source must supply a checkable amount condition and the Event's payload/producer condition. Derivation yields a Rule allow witness, a Rule deny witness, a check that the Operation applies the Rule before mutation, and an Event emission case for successful execution. A no-emission case follows only from an explicit failure contract. Until `CreatePayment` and the Event output are bound to an observable implementation, these remain obligations rather than passing tests. The two edges do not themselves supply an amount threshold, payload value, or transaction guarantee.

## Active backend meta types (DS-D1)

Each row adds to the common formation check against that type's canonical criterion. The listed cases are derived only from authored fields, clauses, tables, or equations. A missing semantic clause is reported as residue.

| Meta type | Derived cases from a well-formed declaration |
| --- | --- |
| **Entity** | Identity field presence and type; distinct identities remain distinct even when other values match; each declared field/constraint and lifecycle invariant. Persistence and lifecycle behavior require a bound implementation. |
| **Value Object** | No designated identity field; typed fields and declared equality; equal field tuples compare equal, and a differing relevant field compares unequal. Immutability needs an observable binding. |
| **Enum** | Every declared value is accepted, and values outside the closed declared set are rejected. Do not treat an Enum as a transition system. |
| **Operation** | Each declared precondition, success postcondition, state change, error branch, and effect boundary. Assert the specified before/after difference and no unauthorized effect on a rejected path; require an explicit state/effect oracle. |
| **Query** | Declared input, filter, projection, ordering, empty/error cases, and the no-state-change claim. Generate only cases the query contract makes decidable; authorization is a separate declared rule/policy. |
| **Calculation** | Exact result cases from a closed formula, branch and boundary cases from its conditions, and declared algebraic properties. A bare call or prose formula remains `needs-formal` or `needs-oracle`; never use the implementation output as expected value. |
| **Rule** | One allow and one deny witness for each checkable Boolean clause, plus declared boundaries and combinations needed to distinguish the clause. The deny case identifies the blocked behavior; a Rule does not select a strategy. |
| **Policy** | One case per declared decision-table row or branch, including ordered precedence, default, and an input reaching each later branch after earlier guards fail. Assert the selected strategy and its declared consequence, not merely that some branch ran. |
| **Workflow** | Each declared step and order/dependency, successful continuation, failure exit, and explicitly declared recovery/compensation path. Test no later step after a blocking failure. Do not infer durable retries or recovery from the Workflow label. |
| **Interface** | Each declared callable entry and response variant: request/response shape, status, error mapping, and dispatch to the exposed Operation or Query. Transport and authentication cases require their own declared contracts. |
| **Event** | Declared past-fact name, payload fields, producer condition, and each declared consumer outcome. Distinguish event emission from consumer handling and from an Event-to-State-Machine transition. |
| **Mapping** | Each authored source-to-target field transform, missing/invalid field rule, direction, default, and collision/round-trip property if explicitly promised. Assert values, not just matching field names. |
| **State Machine** | Each declared valid `(state,event,guard) → state/effect` transition, guard denial, invariant, and terminal behavior. Derive invalid pairs from the finite state/event product only when the source declares a closed event vocabulary and rejection semantics. |

## Active backend relationship signatures (DS-D8)

Every row first requires correct source/target types, direction, scope and multiplicity from the registry. The second column is the *additional* consequence to test when the relevant behavior and observation are declared. The edge alone is not a runnable oracle.

| Authored edge | Derived consequence |
| --- | --- |
| `Entity --performs--> Operation` | The named actor can initiate the bound Operation under its declared conditions; another actor's eligibility is not inferred. |
| `Operation --produces--> Event` | The successful Operation emits the specified Event with its declared payload; failed/rejected execution follows the declared no-emission rule. |
| `Operation --produces-for--> Entity` | The declared cross-feature write/projection reaches the target Entity through the authorized boundary; assert the named resulting data/effect and failure behavior. |
| `Operation --creates--> Entity` | Successful execution creates a fresh target identity and the generated `creation_targets` projection agrees with the edge; enforce partial one-to-one participation and same-feature scope. |
| `Event --triggers-cross--> Operation` | A qualifying cross-feature Event activates the named Operation once under the declared delivery/idempotency contract; that contract must be explicit. |
| `Rule --enforces--> Operation` | The Operation checks the Rule before mutation/effect: allow permits continuation and deny blocks it. Preserve same- or cross-feature placement. |
| `Calculation --calculates--> Operation` | The Operation uses the Calculation's specified value at the declared input/output point; the Calculation remains pure. |
| `Event --transitions--> State Machine` | The Event is a declared transition input; check each matching transition and guard rather than assuming every occurrence advances state. |
| `Interface --exposes--> Operation` or `Query` | The declared entry routes to the exact target with the specified input/output/error translation. |
| `Workflow --orchestrates--> Operation` | The target participates at its declared step and order, in the admitted same- or cross-feature scope; failure/recovery follows the Workflow contract. |
| `Policy --applies--> Operation` or `Calculation` | The target uses the Policy's selected strategy for the stated conditions; an unattached policy decision does not prove application. |
| `Mapping --maps--> Entity` or `Interface` | The target boundary uses the declared transform and preserves each stated field/value rule. |
| `Entity --contains--> Value Object` | The Entity embeds the declared value, whose equality remains by value and whose parent identity remains separate. |
| `Query --reads--> Entity` or `Operation --reads--> Entity` | The behavior's declared result/decision depends on the named Entity data; read permission and mutation absence need their own contracts. Calculation is not a `reads` source. |
| `Entity --emits--> Event` | The Event names the Entity as domain subject/source; do not collapse this into the Operation producer edge. |
| `Entity --owns--> Entity` | Test the declared ownership dimension (`lifecycle`, `custody`, or `write-responsibility`) and its uniqueness/conflict constraints; do not infer all three from one edge. |
| `Entity --belongs-to--> Entity` | Test the declared membership, classification, or home-assignment kind and its uniqueness/conflict constraints; do not infer ownership. |

## UI and cross-layer signatures

These are active **relationship signatures** in the registry, but their UI endpoint meta types remain candidate or deferred. The following are specification targets for a later admitted source/profile. They are `candidate-only` for general TDE derivation today. A particular `UI-SPEC.md` may have its own bounded test path without promoting DS-D1 UI types.

| Authored edge | Proposed observable case after endpoint admission |
| --- | --- |
| `Page --renders--> Component` | The declared component appears on the page in the specified route/context. |
| `Layout --wraps--> Page` | The page renders in the declared layout slots and shared chrome. |
| `Component --composes--> Component` | The child receives its declared input and contributes the declared output/interaction. |
| `Component --consumes--> Hook` | The component reflects the hook's declared state, return and effect lifecycle. |
| `Form --submits--> Action` | Valid input invokes the named action; invalid input follows the declared validation/error path. |
| `Adapter --shapes--> View Model` | Deferred Adapter must first be resolved against Mapping; no separate Adapter test family is admitted. |
| `Guard --protects--> Page` | Allowed access renders the page; denied access follows the declared fallback. The client guard is not authoritative authorization. |
| `Component --displays--> View Model` | The rendered fields match the declared display projection for a selected input. |
| `Binding --fetches--> Query` | The selected UI trigger invokes the exact Query with mapped parameters and handles result/cache behavior as declared. |
| `Binding --mutates--> Operation` | The selected UI trigger invokes the exact Operation, maps the result/error, and applies declared invalidation behavior. |
| `State Indicator --reflects--> State Machine` | Defer until the State Indicator split is resolved; a domain-state visual mapping must cover each declared state. |
| `View Model --derives--> Entity` | Display fields follow the declared Entity-source projection without claiming domain authority. |
| `Form --contracts--> Interface` | Form fields, submission payload and error mapping match the selected Interface entry. |
| `Guard --mirrors--> Rule` | Client feedback agrees with the selected backend Rule on the same witnesses; the Rule remains authoritative. |

The nine UI candidates are **Page, Layout, Component, View Model, Hook, Form, Action, Guard, Binding**. Their candidate formation checks and edge observations may guide experiments; they do not become active DS-D1 test families. **Adapter** is a deferred merge candidate toward Mapping; **State Indicator** is a deferred split candidate. **Saga** is superseded by Workflow and yields no current derivation. Generated `owned-by` is a view of `owns`, not a second authored edge. Deferred `depends-on`, Operation-returned Value Object, and Event payload/publisher composite, and deprecated `enforces-cross` and `queries`, yield no new authored-edge test family.

## Current TDE boundary and qualification

The compiled-project construction path now exposes `domainspec-v2 derive-tests <absolute-source-project-root>`.
It validates the current source graph, then emits a digest-bound plan from the 13 active backend type families
and all authored backend edges. Each node has a source-checked formation case; authored body clauses yield
separate cases, and each admitted edge yields a named relationship-consequence case. The plan inventories all
31 active signatures: 17 backend kinds are available to current projects and 14 UI/cross-layer kinds are
candidate-only because their endpoint types are not admitted backend types. `needs-binding` and `needs-oracle`
cases are obligations, not passing tests. The implementation lives in
[`cli/src/verification/test-derivation-plan.ts`](../cli/src/verification/test-derivation-plan.ts).
The current plan pins the implemented meta-type baseline digest and frozen relationship-authority source
digest. It does not yet carry each DS-D1 criterion file's exact source digest; that definition-byte join is
an additional construction requirement before treating the plan as a fully pinned general test derivation.

The present engine parses legacy aspect documents or a normalized `SPEC.md` when no aspects are present. The normalized adapter currently derives one structural obligation per concept, relationship, field and attribute. Legacy aspect parsing also derives selected transitions, invariants, rules, calculations, contracts, events, workflows, queries, mappings, domain fields/enums and policy rows. This is a **subset** of the contract above; the normalized adapter does not infer the behavior of every DS-D1 type or DS-D8 edge.

Current emission without a binding creates `it.todo` scaffolds. With a supported binding it can emit selected assertions/properties and explicit `coverage_gap` skips; it does not manufacture an oracle. The imported package still has stale fixture identities and legacy source/binding paths, and the recorded unrestricted TDE verification has failures and pending cases. The compiled-graph plan is not yet a bridge to the old TDE emitter, a generated native test, or EVF evidence. Those stages require explicit binding and qualification.

## Acceptance checks for an implementation of this contract

- Inventory comparison proves all 13 active backend types and all 31 active signatures are accounted for; UI candidates, deferred labels and generated/deprecated verbs have explicit dispositions.
- Every rule has a positive witness, a distinguishing negative or boundary witness where meaningful, and an exact source-to-obligation trace. Type/edge formation checks use the owning registry, not a copied spelling table.
- A source mutation retires or changes only the affected obligations unless the declared composition depends on it; changed source/rule fingerprints fail stale replay.
- Every executable assertion has an independent expected result and exact binding. Unsupported formulas, absent oracles, unadmitted UI endpoints and unqualified paths remain counted non-pass residue.
- Focused fixtures pass under the relocated Craft path; saved ID maps/spec regions are reconciled, and the full TDE suite is reported with failures and pending cases rather than a rollup inferred from focused checks.
