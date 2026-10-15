# L0 relational semantics, version 1

This is the normative **candidate** contract for P01/P03/P04/P05, scoped to three relation kinds and 28 ordered endpoint pairs. Author and semantic reviewer: Codex in this task, with a recorded self-review; no independent human review or authority admission is claimed. Existing JSON schemas and APIs remain draft projections until P02.

## Separate concepts

A relation kind declares allowed ordered endpoint pairs and qualifier meanings. An assertion is an identified claim of that kind between two exact node versions. An assessment is a separately supplied, scoped result bound to exact endpoints. An inference rule is a proposed transformation of premises to conclusions; F0 executes no rule engine. An admission root is separately supplied authority provenance. Asserting conformance or a declared effect creates no admission root.

## Finite input and identity

`Graph` contains finite lists of nodes, assessments, assertions and independent admission roots. Node references are `(id, version)` pairs. Both strings and each node's content identity must be nonempty. Node reference keys, assessment reference tokens and assertion IDs must be unique within their respective inventories. Node revisions may coexist. There is no universal acyclicity, single-edge cardinality or cross-relation constraint.

All references resolve against the same supplied input. Resolution requires exact version equality. Unresolved or ambiguous references fail. Kind and qualifier constructors are closed; no unknown-kind fallback exists. An assertion's qualifier constructor must match its kind. Typed constructors enforce field presence and exclude extra fields; JSON parsing and malformed-object rejection are P02 obligations.

## Exact signatures

| Relation | Source kind | Target kind |
|---|---|---|
| conforms-to | capability-instance | contract |
| conforms-to | capability-instance | governed-model |
| conforms-to | context | context-profile |
| declares-effect-on | decision | agent-capability |
| declares-effect-on | decision | agent-profile |
| declares-effect-on | decision | artifact-type |
| declares-effect-on | decision | capability-realization-binding |
| declares-effect-on | decision | challenge-event |
| declares-effect-on | decision | classification-assignment |
| declares-effect-on | decision | communication-preference |
| declares-effect-on | decision | definition |
| declares-effect-on | decision | delegation |
| declares-effect-on | decision | effect |
| declares-effect-on | decision | failure-assessment |
| declares-effect-on | decision | failure-control-binding |
| declares-effect-on | decision | failure-mode |
| declares-effect-on | decision | failure-occurrence |
| declares-effect-on | decision | governed-model |
| declares-effect-on | decision | improvement-target |
| declares-effect-on | decision | incident |
| declares-effect-on | decision | intent-resolution |
| declares-effect-on | decision | operational-lesson |
| declares-effect-on | decision | product-capability |
| declares-effect-on | decision | relation-kind |
| materializes-consequence | admission-transaction | generated-output |
| materializes-consequence | admission-transaction | project-governance-event-history |
| materializes-consequence | admission-transaction | project-semantic-event-history |
| materializes-consequence | admission-transaction | project-state |

These pairs are the actual declared pairs, never a Cartesian product of source and target sets. All 31 endpoint kind constructors and all three qualifier records are finite and closed.

## Qualifier and reference meanings

For `conforms-to`, `conformance_scope`, `exact_version_ref` and `conformance_evidence_refs` are nonempty strings. The plural reference field is one opaque token, not an array. The version token equals the target version. The evidence token resolves to an accepted conformance assessment whose subject, target and scope exactly match the assertion. A report concerns only that scope and those versions.

For `declares-effect-on`, `effect_kind` and `exact_target_version_ref` are nonempty strings, and the version equals the target version. Effect values remain opaque, distinct string values: the source does not supply an enum. Declaration executes no effect and does not translate one effect value into another.

For `materializes-consequence`, `application_receipt_ref`, `consequence_role` and `output_digest` are nonempty strings. The receipt resolves to an accepted application assessment bound to the exact transaction and output, role and digest. The output digest equals the target node's supplied content identity. A digest is an opaque string equality here; F0 proves neither cryptographic hashing nor real output creation. This represents a reported deterministic consequence of an already authorized transaction; it grants no additional authority or semantic correctness.

An assessment has a typed mode (conformance or application receipt), an opaque reference, exact subject and target references, scope, role, content token, and an accepted-result flag. `accepted = true` is supplied assessment data, never the result of the graph checker. Conformance assessment scope must be nonempty; receipt role and content token must be nonempty. All assessments resolve their exact endpoints, even when unused.

An independent admission root has a subject, decision reference and nonempty authority evidence token; the decision resolves to a decision node. Graph checking verifies its structure and bindings. It does not authenticate that authority evidence or execute admission. Conformance may coexist with such a root, and a graph with conformance but no roots is also valid. These two inhabited models refute an overstrong blanket prohibition on coexistence.

## Independent predicates and invariant

`NodeValid`: nonempty node identity, version and content identity. `EndpointValid`: two resolved exact node versions have a declared ordered kind pair. `QualifierValid`: matching closed qualifier constructor and required nonempty strings. `VersionScopeValid`: exact target version equality where declared and exact assessment bindings. `InstanceValid`: nonempty assertion identity and all three predicates.

`Inv(G)`: every node is valid; node keys are unique; every assessment is well formed and resolves; assessment tokens are unique; every admission root is well formed and resolves; every assertion is independently valid; assertion IDs are unique. These are propositions written without any reference to checker success. Decidability comes from finite-list membership and decidable string/constructor equality.

Addition appends one assertion and preserves all node, assessment and admission inventories. The checker rechecks the entire resulting graph. A valid new edge never compensates for an invalid pre-existing graph.

## Interpretation and trust

D01 records this static profile: reference resolution plus supplied scoped assessment bindings. A faithful adapter must interpret strings and source records exactly; external evidence authentication, assessment sufficiency, authorization and output creation require separate evidence. The theorem itself is unconditional over arbitrary typed finite inputs and proves this explicit input-relative invariant. It does not assume the checker conclusion, validity of every input edge or a base invariant.

D00 pins `leanprover/lean4:v4.33.1`, standard library only, with no custom axioms, `sorry`, native proof evaluation or opaque proof bypass. Allowlisted transitive standard axioms are `propext`, `Classical.choice` and `Quot.sound`; the actual closure is recorded per theorem. Kernel reduction witnesses use `decide`, not `native_decide`.

## Invalidation and ownership

Semantic source hashes are captured in context packs and the proof audit. Any source, contract, predicate, checker, theorem statement or toolchain change invalidates dependent evidence until replay and review. Codex owns implementation and the explicit self-review of F0. Independent organizational approval remains outside this candidate phase. No immutable registry, carrier, live runtime or authority state is changed.
