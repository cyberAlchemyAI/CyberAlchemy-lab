# Commerce source obligations and service ownership

Craft independently reconstructs the `.alch` closure and checks source semantics.
`createCoreCommerceObligationOwner(originalSources, originalSemantics)` joins
those two original owners. Its `prepare(source, semantic)` accepts the exact
original capture used by the semantic owner. Display JSON, a matching hash,
a copied object or a second same-byte capture cannot replace either parent.

The inventory answers three questions: which service owns a declaration,
which original source constraints were statically checked, and which later
implementation tasks still need evidence beyond source checking. It does not
execute an application or establish a theorem.

```typescript
const source = sources.prepare(applicationDirectory);
const semantic = semantics.check(source);
const obligations = createCoreCommerceObligationOwner(sources, semantics);
const inventory = obligations.prepare(source, semantic);
const report = obligations.inspect(inventory);
// report is frozen display data. Retain inventory for original-owner checks.
obligations.assertCurrent(inventory);
```

This is an internal source-stage API. The selected installed SDK/application
path requires its own profile, native, selection and application owners.

## What a checked source row means

Each row identifies the original declaration, grammar rule, file and exact
source span. There must be one original syntax node and one checked declaration
for that row. The owner accounts for the complete reconstruction inventory;
it cannot accept a user-provided list of successful rows.

Pure and value declarations correspond to independent Core pure/value checks.
Query, Operation, Workflow and Entry declarations correspond to their separate
checked producer contracts. These checks cover the typed declaration's source
subtree. The report calls this `typed-declaration-check-covers-source-subtree`;
the number of source nodes is not a count of executions or separately proved
theorems. Interface clauses additionally correspond to exact eagerly checked
clause spans, named `exact-interface-clause-source-check`.

The Interface checker checks unused native signatures as well as used ones.
It rejects unknown parameter/result types, invalid captured source namespaces,
ambiguous singleton clauses, clauses from another Interface kind, wrong
service-private ownership, invalid validation associations and unsupported
primitive ranges. A narrower unsigned business domain belongs in a declared
Rule/refinement/invariant; `UInt64` retains its full primitive domain.

An Interface binding is a captured requirement. Valid method types and matching
ABI text do not provide a native implementation, private context, authorization
decision, transport connection or peer observation. Provider protocol, adapter,
profile-family and application wiring need their assigned later owners/checks.

## Separate implementation requirements

`source_checks` always use `source-statically-checked` and
`runtime_qualified: false`. `implementation_requirements` independently name
original plan tasks and source declarations. Their status is
`required-not-witnessed-by-source-accounting`. This says the source inventory
does not witness their implementation; it is not a second task status registry.
Some named tasks may already have separate component evidence elsewhere.

Pure generation and evaluation belong to EC08/EC13. Bounded codecs and source
identity producers belong to EC09. Role planning/storage/transactions belong to
EC15–EC18 and their service qualification tasks. Private authorization and
entry/application assembly belong to EC11/EC21–EC23. Workflow/event durability
belongs to EC28–EC30. Technical families, SDK build/capture and whole-project
generation retain EC10/EC12/EC31/EC33/EC34 requirements. The rows are causal
assignments, not proof that every task is discharged.

Service ownership comes from the original application service/module declarations.
Shared, technical and coordination declarations keep their actual categories;
an unowned declaration is never assigned an invented service. Optional formal
claims remain separate assurance data and introduce no executable obligations.
Code generation does not require a claim.

`assertProposal(inventory, inertJson)` compares every field with the original
report. Missing or duplicate rows, changed spans/ownership, omitted native
requirements and stronger runtime statuses reject. Successful comparison does
not restore the original handle. Accessors and proxies reject without running
user code. Source/code replacement or parent disposal invalidates later use.

## Integration boundaries

| EC07 output | Original source-stage implementation | Later executable join |
| --- | --- | --- |
| Independent source-to-role reconstruction | Core grammar, pure/value/Interface checks and separate Read/Effect/Workflow/Entry producers | Native role planning and generation in EC08–EC23/EC28–EC33 |
| Wider explicit review/decision/input contracts | Original Source/Semantic/Review/AcceptedReview and SourceAuthoringInput owners | Selected profile/native/early-request/application assembly; source-authoring input is not a selected CommerceInputHandle |
| Service ownership and obligations | Original obligation owner, original syntax spans, separate implementation requirements | Actual native/runtime witnesses and whole-project qualification |

The real candidate's business decision must remain explicit. Fixture decisions
test a protocol and do not accept the real business requirements. Source
inspection, hashes and typed contracts alone cannot mint an accepted review,
selected native basis or checked/generated application.

## Open Questions

The original integrated DAG owns the remaining native, profile, selection,
early-request, application and independent qualification joins. EC07 closure
also requires current wider/U0 regressions and preservation reconciliation.
Local hosting, TDE, EVF, publication/deployment and live identity/provider/
database/broker activation remain deferred.
