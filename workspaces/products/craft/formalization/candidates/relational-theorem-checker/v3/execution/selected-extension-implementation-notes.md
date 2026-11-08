# Selected extensions: implementation and review notes

All seven extensions are selected. These are proposed implementation choices, not implemented or accepted capabilities. Each requires P11's actual assessment of the concrete core packet. Formal definitions and independently stated theorem targets come before runtime code. Each extension gets its own versioned profile; the current recursive entry point must continue refusing meanings it does not implement.

## E00: bounded condition expressions

Define a small expression tree with evidence-backed atomic conditions, conjunction, disjunction and negation. An atomic condition returns yes, no or unknown at its exact evaluation key. Fix every operator's truth table independently of the evaluator. Unknown input is not silently converted to false; unsupported operators are explicit refusals. Contradictory supplied evaluations remain a separate invalid-input condition rather than a way to derive arbitrary truth.

Implement closed expression/evaluation schemas with depth, node and work ceilings. Compile a concrete expression witness and the independently specified interpretation into Lean before permitting norm activation. The activation theorem must connect the exact expression, context, subject, target, scope and epoch to an active norm. A Python evaluator agreeing with itself is insufficient.

Review every truth-table row, nested unknown cases, conflicting evaluations, stale context, unsupported operators and cutoff behavior. External atomic evaluation truth stays a named assumption. No arbitrary executable condition string is introduced.

## E01: multiple conformance evidence references

Propose an explicit candidate policy: any current accepted matching assessment can establish the scoped conformance observation; retain every valid matching support in its explanation. Multiple pieces of ordinary evidence do not become an independent protected root. Record this policy before implementing the new input form and review it against the existing single-token meaning.

Define versioned evidence-reference collections, assessment identity and support selection. Prove that a produced conformance fact has an exact accepted source/assessment witness and that selected valid supports are retained. Keep legacy single-token requests mapped to their existing meaning without reinterpreting an old string as a collection.

Review empty and duplicate collections, mixed valid/stale evidence, different contract targets/scopes, conflicting assessments, and rule-derived or caller-supplied attempts to manufacture conformance. A count of evidence files is not an authority threshold.

## E02: finite redelegation chains

Define the chain judgment before choosing a traversal algorithm. Each hop must use an exact delegation revision, permit redelegation where required, cover the requested action/scope and remain effective at the named snapshot. The composed permission must satisfy every hop's restrictions; adding a hop cannot increase permission. Fix revocation and interval endpoint behavior explicitly.

State and prove restriction/non-amplification independently of runtime enumeration. Implement a finite declared graph with bounded traversal, explicit cycle handling and retained per-hop origins. A found path is a witness for that exact query. A negative answer requires completed exploration of the declared finite profile; a cutoff returns unknown. Do not infer graph completeness from an arbitrary depth limit.

Review expired/revoked middle hops, forbidden redelegation, narrowing scopes, different actions, version substitution, cycles, competing paths and resource cutoffs. Compare all direct-profile cases with the accepted direct checker. No unbounded or cross-context chain claim is added to the existing profile.

## E03: linkage and verified fulfillment

Resolve the source-name ambiguity with versioned meanings. Preserve the current legacy relation as a requested or asserted linkage where its evidence cannot establish criterion satisfaction. Introduce verified fulfillment only through an explicit criterion set and separately evaluated criterion evidence. A relation name alone cannot activate that stronger predicate.

Define linkage, criterion satisfaction, criterion-set completeness and verified fulfillment as distinct judgments. Prove the exact implication from complete accepted criterion evidence to fulfillment under the declared assessment assumptions. Preserve which criteria and assessments support the result; an omitted required criterion cannot be treated as passed.

Review partial criteria, failed/unknown evaluations, stale revisions, unrelated evidence and empty criteria. Examples must show a valid linkage without verified fulfillment. Independent criterion evaluation is evidenced separately from checking the relation's structure. The candidate does not certify real-world delivery merely because a kernel checks supplied assessments.

## E04: lifecycle succession

Define a separate lifecycle transition over immutable revisions and an explicit active selection. Fix what succession changes, which references remain meaningful, which obligations must be re-established and how conflicting proposals are resolved. Rule-only append theorems retain their original scope; they do not prove safety of removal or replacement.

State the transition invariant before mutation code: the new active state corresponds to one valid reviewed successor, retained history remains identifiable, and conflicting or potentially committed state requires reconciliation. Use a separately owned candidate transition store and adapt the proven publication discipline without claiming a filesystem theorem.

Review competing successors, stale parent revisions, changes to protected observations, references to historical revisions, interrupted transitions and recovery. Rollback must not silently erase a potentially committed lifecycle successor. No canonical project lifecycle is changed by these fixtures.

## E05: checked intermediate representation

Define typed references, predicate signatures, scoped assertions, assessments and interpretation records in an independently specified IR. Use one explicit snapshot identity rather than requiring callers to reconstruct context, inference and typed-query epochs independently. The P08 delegation fixture demonstrated why those repeated representations need a checked correspondence.

First prove universal properties over the formal IR: well-typed observations and rules preserve the declared interpretation, and the independently defined normalization/evaluation judgments agree under their exact finite-profile hypotheses. Then connect actual bounded source requests to concrete checked IR witnesses and retain the existing exact-input theorem checks. A universal theorem about formal IR values is not a theorem about every JSON decoder input.

Review numeric representations, field reordering, escaped strings, malformed references, duplicate identities, different target/scope values, source-evidence substitutions and round trips. Differential tests are finite evidence. The parser, host hashing, external assessment truth and compiler kernel remain explicit trust assumptions unless a separate theorem removes one of them.

## E06: independent-checker feasibility

Identify a small logic fragment and a certificate format whose propositions and inference rules can be translated without quietly changing their meaning. Evaluate a genuinely separate checker implementation/kernel, the translation trust boundary, unsupported Lean features, dependency cost and operational cost using primary documentation. An empty-environment replay through the same Lean binary is not independent.

The deliverable is a feasibility assessment with an optional accurately labeled sample. If a sample is built, fix the target statement independently, retain the exact translation/certificate/checker versions and report its actual checked scope. Do not extrapolate a sample to the full relational catalog or call a Python reference evaluator an independent checker of Lean proofs.

Review foundational assumptions, proposition identity, proof translation, unsupported features and failure behavior. Core delivery remains usable without an unproved second-checker path. The assessment must state exactly which parts remain trusted even if the sample checker succeeds.
