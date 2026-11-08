# FormalClaim Understanding Projection

Status: candidate contract and human view; not compiler-emitted

## Purpose

A FormalClaim is stored as exact formal source plus typed graph structure. That
shape is appropriate for identity, derivation, and machine inspection, but it
is not necessarily the order in which a person can understand the claim.

The `FormalClaimUnderstandingProjection/v1-candidate` contract preserves the
graph and adds two explicitly different views:

1. a provenance graph joining FormalClaim, clause, expression, predicate, and
   definition nodes; and
2. a guided serial presentation that orders those same nodes for human reading.

The projection explains exact source structure. It cannot amend the
FormalClaim, redefine a term, infer a missing definition edge, assert that a
reader understood the claim, or supply proof or runtime evidence.

## Source graph

The source graph uses stable nodes and typed edges:

```text
FormalClaim
  -> contains -> clause
  -> expression-root -> conjunction
  -> left-operand -> predicate
  -> right-operand -> predicate
  -> uses-definition -> definition identity
```

An understanding node attaches through `explains_node_id` to one exact node in
that graph. Its source selector names the FormalClaim, clause, expression path,
and source text. Its `definition_ids` must come from the exact
`definition_binding_ref`; name matching is forbidden.

Every understanding node records:

```text
Origin: structurally-derived or authored-explanation
Source: exact FormalClaim, clause, and expression selector
Definitions: zero or more exact bound definition identities
Authority: explanatory-only
```

## Serial presentation

Graph storage and human presentation are different concerns. The graph remains
the traceability structure. The default human view is a top-to-bottom reading
spine with provenance in a secondary rail:

```text
1. domain context
2. exact formal source
3. operator explanation
4. first operand explanation
5. first linked definition
6. second operand explanation
7. second linked definition
8. recomposed expression meaning
9. explanatory-authority boundary
```

The sequence is declared rather than inferred from screen position. A renderer
may use another accessible layout, but it must preserve the declared order,
source selectors, graph edges, and final recomposition step. Presentation never
changes semantics.

## Worked example

This example is illustrative and does not assert that an Order Submission
FormalClaim or its definitions are admitted repository artifacts.

```text
FormalClaim: FC-OrderSubmission-v1
Clause: 3
Expression: Eligible(o) and ValidTotal(o)

Step 1 - operator
  Explanation: both conditions must hold at the same time
  Origin: structurally-derived
  Source: clause 3, expression root
  Definitions: EligibleOrder@2, ValidTotal@1
  Authority: explanatory-only

Step 2 - left predicate
  Expression: Eligible(o)
  Explanation: the Order satisfies the governed eligibility conditions
  Origin: structurally-derived
  Source: clause 3, left operand
  Definition: EligibleOrder@2
  Authority: explanatory-only

Step 3 - linked definition
  Definition: EligibleOrder@2
  Voices: formal, plain-language, domain-context

Step 4 - right predicate
  Expression: ValidTotal(o)
  Explanation: the Order total satisfies the governed validity conditions
  Origin: structurally-derived
  Source: clause 3, right operand
  Definition: ValidTotal@1
  Authority: explanatory-only

Step 5 - linked definition
  Definition: ValidTotal@1
  Voices: formal, plain-language, domain-context

Step 6 - recomposition
  Explanation: the Order must be eligible and its total must be valid;
               neither condition is sufficient alone
  Authority: explanatory-only
```

## Contract boundary

- The FormalClaim remains the proposition authority.
- The definition authority remains the only owner of normative definition
  bodies; copied voices are consumer material only.
- Understanding nodes are derived or explicitly authored explanation objects,
  never new claim clauses.
- A missing clause, expression, or definition reference blocks the projection.
- A serial renderer is a view over the graph, not a replacement graph.
- No understanding projection establishes proof, implementation conformance,
  reader comprehension, business acceptance, or product approval.

## Open Questions

1. Should the first compiler implementation expose expression selectors as JSON
   Pointers, stable AST paths, or both?
2. Which operator explanations are safe to derive mechanically, and which need
   an authored explanation reviewed by the FormalClaim owner?
3. Should alternative accessible reading orders be separately content-identified
   or remain renderer-owned views over one declared sequence?
