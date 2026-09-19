# Context Basis semantic decisions

Status: selected owner direction  
Decision Gate result: `PASS`  
Decision timestamp: `2026-09-01T05:09:02Z`  
Authority effect: none beyond binding these three development decisions  
Implementation effect: none  

## Decision source and exact binding

The user explicitly confirmed:

```text
001-A / 002-C / 003-C confirmed
```

UTF-8 SHA-256 of the exact confirmation text:
`c2a09785ca5cde8d48f044199865cba47c02ad387572313ad850fffb518568f8`.

This confirmation binds only the options presented by the following current
Decision Gate receipts:

| Decision | Receipt SHA-256 | Request digest | Selected option |
| --- | --- | --- | --- |
| `ARE-CONTEXT-OPEN-001` | `890cf1bc0ab6156f9e10dc079deff6beb979372835f4ad848b4a64f732fc4d17` | `5955adabc2bdbe421b33fd41bd1508203b8ed13f4e7bf54b0fe16013d4024f1d` | `OPEN-001-A-ROUTE-PROFILED-FIXED-POINT` |
| `ARE-CONTEXT-OPEN-002` | `0ec634d002e4b4dd21a1e08e3abdc04680c9ffda32fbcbfcd8cfae8bd6f4ceaf` | `95cc11372b7be8895df32a8493e1df5906a0acb336d0010f8ea033d40cf1e85c` | `OPEN-002-C-DECLARED-PLUS-AUDIT` |
| `ARE-CONTEXT-OPEN-003` | `f1d2b2cdacc2a80ad21f85112965c2887ea90b1b3df8f206a2bef5414e167027` | `080e6a9c7935b2653d02aa8461a4ff79b3c4988b6b56bc589a15b7c96db45f0c` | `OPEN-003-C-DUAL-LANE` |

The selected source package was current when the decision was bound:

- Context Basis Definition Pack SHA-256:
  `a3415a58ace35cb98d8774ed6d13c34317724407a31ace4f976c95ef570a590d`;
- bounded findings SHA-256:
  `6cf123a01a2416e6ee51518cc521e70c1250cd6c4df62f65639c7458fcb8b44b`;
- ARE business ontology SHA-256:
  `d0168c87a524b8732daf00a9a0e381859127f261d750a5cc601f971bba766714`;
- Codex Request Governance Definition Pack SHA-256:
  `90e33a6123f6af3a9b5406f7387537b326836e1be59db08718a3800d2eff4340`.

Changed decision-bound bytes require a new review and decision. Unrelated
ontology drift does not invalidate this decision.

## ARE-CONTEXT-OPEN-001 — route-profiled definition closure

### Question

Which typed relation kinds participate in request-relative definition closure,
and how does traversal terminate?

### Considered options

- `OPEN-001-A-ROUTE-PROFILED-FIXED-POINT` — selected;
- `OPEN-001-B-UNIFORM-FIXED-POINT` — not selected;
- `OPEN-001-C-DEFER` — not selected;
- `OPEN-001-D-STOP` — not selected.

### Selected rule

Definition closure is the least fixed point of a versioned base relation policy
plus additions declared by the selected route profile.

The seed contains the definition identities required to interpret:

1. the preserved request terms, targets, requested effects, constraints, and
   expected artifacts;
2. the selected route, its capability contract, and its declared first-read
   dependencies;
3. the selected ontology nodes and edge predicates;
4. the applicable authority, gate, provenance, and claim-proof posture.

The universal base relation classes are:

- canonical identity and alias normalization;
- specialization or inheritance from a selected term to its base meaning;
- normative requirement or semantic dependency;
- constraint, governance, scope, and owner-route dependency;
- conflict, exclusion, and distinguished-from boundary;
- version, replacement, and supersession/currentness dependency.

A route profile may add typed normative relation classes but cannot remove the
universal base classes. Provenance is always bound by exact selector and digest,
but provenance material is not recursively added as semantic context unless the
base policy or route profile declares its relation normative for the request.

Traversal uses the stable key `(definition_id, version_or_revision, digest,
authority_posture)`. Each key is evaluated once. Cycles are retained as finite
strongly connected dependencies and do not restart traversal. Closure terminates
when the work queue is empty and no unresolved required reference remains.

An unknown relation kind, missing target, ambiguous canonical identity,
conflicting current definition, or unresolved required reference produces a
typed semantic gap. The dependent Context Basis is `not_evaluable`; retrieval
success or semantic similarity cannot repair the gap.

### Rationale

This keeps a shared invariant across routes while allowing Research, Define,
Plan, Implement, and other owners to name genuinely route-specific semantic
dependencies. It avoids both repository-wide loading and a universal policy
that silently assumes every route uses meaning in the same way.

## ARE-CONTEXT-OPEN-002 — declared edge closure plus omission audit

### Question

What minimum dependency-closed ontology edge rule preserves selected-node
meaning without loading unrelated neighbors?

### Considered options

- `OPEN-002-A-MANIFEST-FIRST` — not selected;
- `OPEN-002-B-POLICY-DERIVED` — not selected;
- `OPEN-002-C-DECLARED-PLUS-AUDIT` — selected;
- `OPEN-002-D-DEFER` — not selected;
- `OPEN-002-E-STOP` — not selected.

### Selected rule

The binding selector lock is declaration-first. For every selected ontology it
records:

- ontology identity and source digest;
- selected node identities and selection reasons;
- exact required edge identities, types, directions, and endpoint identities;
- recursively required endpoint nodes and their required edges;
- excluded policy-relevant adjacent edges with typed reasons;
- conflicts, missing metadata, residue, and a deterministic lock digest.

Declared required edges are binding. Closure follows them recursively until no
new required endpoint or edge is introduced. A required edge whose source,
target, identity, type, direction, or source digest is missing or ambiguous
makes the dependent lock `not_evaluable`. A material unresolved conflict does
the same. Unrelated nodes and edges remain outside the lock, and their drift is
diagnostic only.

A separately versioned relation policy maps ontology identity, node kind,
relation kind, and direction to `required-candidate`, `optional`, or `ignore`.
It audits the declared closure for possible omissions. Audit output:

- cannot add an edge to the binding lock;
- cannot admit or reject ontology records;
- cannot select a route, authorize continuation, or grant an effect;
- produces an omission candidate that the ontology owner must resolve through
  an explicit required-edge declaration or typed exclusion.

Until the governed Rust ontology kernel is admitted, current Python
ontology-runtime output remains diagnostic and cannot enforce or block this
rule. The decision defines target semantics; it does not claim a conformant
runtime exists.

### Rationale

Owner declarations retain semantic authority, while a deterministic policy can
expose likely omissions without becoming a hidden ontology selector. This
preserves exact provenance and fail-closed gaps without allowing automation to
silently widen context.

## ARE-CONTEXT-OPEN-003 — dual-lane Context Window View identity

### Question

Does each Codex turn create a successor view, or may an unchanged view be
reused?

### Considered options

- `OPEN-003-A-RETAINED-IDENTITY` — not selected globally;
- `OPEN-003-B-PER-TURN-SUCCESSOR` — not selected globally;
- `OPEN-003-C-DUAL-LANE` — selected;
- `OPEN-003-D-DEFER` — not selected;
- `OPEN-003-E-STOP` — not selected.

### Selected rule

Every Context Window View declares exactly one lane:
`plan-bound` or `interaction-bound`. Lane selection is explicit and
digest-bound; ambiguity opens a gate and cannot default silently.

For a `plan-bound` view, identity is retained only when all of the following are
equal and current:

- request and plan binding;
- route decision and route profile;
- definition closure and ontology selector lock;
- selected dependency identities and digests;
- consumer, purpose, access scope, and transformation identity;
- protected fields, exclusions, conflicts, and residue;
- external freshness requirements;
- authority and effect posture.

Every retained use emits a per-turn reuse receipt containing the turn identity,
view identity, source epoch, reuse-predicate digest, equality result, and
authority effect `none`.

For an `interaction-bound` view, each human/chat interaction creates an
immutable successor view. The successor has a new view identity, predecessor
reference, interaction identity, and source epoch. It may retain the same basis
digest when semantic inputs are equal; digest equality does not collapse the
distinct interaction event or view identity.

In both lanes, changed selected dependencies, route, purpose, access,
transformation, conflict state, residue, or authority/effect posture require a
successor. Historical views are never rewritten.

### Rationale

Plan-bound work benefits from stable identity and cheap evidenced reuse. Human
interaction benefits from explicit causal history because clarifications,
choices, corrections, and scope changes are meaningful events even when much
of the semantic basis remains equal.

## Gate disposition

- Decisions resolved: 3.
- Blockers remaining within `ARE-CONTEXT-OPEN-001/002/003`: 0.
- Deferred decisions: none.
- Override: none requested or consumed.
- Admissible routing: gate, satisfied by the exact user confirmation above.
- Decision effect: the three selected semantics may be used as owner-directed
  inputs to revise the candidate Context Basis meaning and design its bounded
  experiment.

## Remaining boundaries and separate decisions

This decision does not:

- promote the candidate Context Basis definitions;
- admit or modify an ontology;
- adopt a Product Capability;
- select or authorize a runtime implementation;
- restore Python ontology-runtime enforcement;
- prove closure completeness, selector sufficiency, view correctness, latency,
  fidelity, isolation, or conformance;
- authorize publication, release, deployment, or another external effect.

Projection taxonomy, source lifecycle, route-specific projection policies,
authority/event vocabulary, experiment corpora, metrics, repetitions, and
thresholds remain separate owner decisions. The immediate permitted successor
is a candidate semantic-source revision or a bounded experiment design under a
newly selected route; neither successor is executed by this decision.
