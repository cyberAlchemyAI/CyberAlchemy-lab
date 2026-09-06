---
dispatch_id: 2026-07-17-domainspec-evolvable-validation-framework
artifact: findings
status: candidate
authority: non-authoritative research
phase: post-review
review_status: revised-after-tarski-popper-quine
---

# Evolvable DomainSpec Validation Framework

## Goal

Define a project-agnostic validation framework that can evolve beyond the current enumerated backend kinds while preserving the distinction between:

- authored source and generated representations;
- node-local structure and graph-level relationships;
- deterministic validators and formal/query complements;
- test derivation and test execution;
- evidence receipts and authoritative specifications.

The framework must identify where structural YAML/JSON/table-walk validation ends and where FOL, Cedar, Datalog, SMT, Alloy, TLA, Lean, or runtime evaluation becomes justified.

## TL;DR

Evidence anchor: [Church] structural-kernel findings (`impl/spec/minted-project/node.schema.json:4-36`, `impl/test-derivation-engine/src/ir/types.ts:5-100`); [Curry] formal boundary findings; [Popper] missing end-to-end evaluator/receipt gate.

A generic framework is viable, but only as a layered candidate substrate.

The current repository already has most of the structural kernel:

- generic node envelopes;
- registry/profile admission;
- formation contracts;
- typed relationship signatures;
- normalized graph and obligation IR;
- deterministic structural validators;
- generated test and residue surfaces;
- digest-bound build receipts.

The missing part is not another universal validator. The missing part is a governed adapter boundary that can route each obligation to the smallest adequate evaluator and return a typed, claim-limited receipt.

The candidate framework should therefore:

1. keep `NodeSource`, `EdgeSource`, and source authority distinct from normalized IR;
2. separate registry membership, profile admission, and formation validation;
3. represent constraints and obligations as typed references to governed predicate families, not as an undeclared DSL;
4. route node and edge shape to schema/table-walk validators;
5. route cross-rule and cross-graph relations to a bounded FOL/Cedar/Datalog complement;
6. route static graph counterexamples to bounded Alloy;
7. route temporal traces to TLA+/TLC;
8. preserve existing Lean ownership for already-owned satisfaction/decidability;
9. return typed receipts with explicit `receipt_family` and `claim_limit`;
10. treat Inventory as a read model, never as specification authority.

The framework is not yet implementation-ready. Popper’s objection remains material: there is no end-to-end `TestCase -> evaluator -> typed ReceiptEnvelope` path and no runnable cross-graph evaluator. The cycle example is hand-built and hand-run in research, not a shipped evaluator result. Alloy and TLA sketches remain unvalidated.

## Context and evidence posture

Evidence anchor: [Church] profile/compiler inventory; [Gödel] relationship authority and fixture run; [Curry] formal-method tower and Inventory entries.

This is a candidate research result, not a DomainSpec authority change.

The repository currently contains:

- a generic minted-node envelope whose `kind` is opaque at the envelope level;
- a release-deferred profile that admits only four formation kinds;
- a registry containing thirteen active backend members, with a deliberate gap at `DS-D1.10`;
- a relationship authority that currently reports thirty active signatures;
- a historical composability synthesis that reports twenty-nine, which must be treated as read-model drift;
- a deterministic test-derivation engine with generic graph and obligation IR;
- a structural content validator that performs table-walk checks;
- a formal-methods tower that positions Alloy for bounded static graph counterexamples and TLA for temporal traces;
- Inventory entries that describe formal/query complements but mark them intended-not-shipped.

Primary evidence appears in the explorer transcript and the cited local sources, especially:

- `projects/domainspec-v2/impl/spec/minted-project/node.schema.json`
- `projects/domainspec-v2/definitions/minted-project/supported-profiles.yml`
- `projects/domainspec-v2/definitions/meta-types/meta-types.yml`
- `projects/domainspec-v2/definitions/relationships/relationships.yml`
- `projects/domainspec-v2/impl/tools/minted-project/compiler.ts`
- `projects/domainspec-v2/impl/tools/validate-content.ts`
- `projects/domainspec-v2/impl/tools/validate-relationships.ts`
- `projects/domainspec-v2/impl/test-derivation-engine/src/ir/types.ts`
- `projects/domainspec-v2/impl/test-derivation-engine/src/rules/index.ts`
- `projects/domainspec-v2/impl/test-derivation-engine/src/emit/spec.ts`
- `projects/domainspec-v2/impl/test-derivation-engine/src/emit/tests.ts`
- `projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md`
- `projects/domainspec-v2/research/alloy-tla-modeling/TOWER.md`
- `projects/domainspec-v2/research/alloy-tla-modeling/BRIDGE-DECISIONS.md`
- `projects/domainspec-v2/research/alloy-tla-modeling/CLAIM-LEDGER.md`
- `projects/domainspec-v2/development/meta-type-formalization/research/2026-07-02-formalism-and-primitives/findings.md`
- `.arcanum/inventory/entries/deterministic-validation-for-all-cav2-synthesis.md`
- `.arcanum/inventory/entries/fol-constitution-validation-complement-synthesis.md`

## Strict authority and derivation matrix

Evidence anchor: [Church] reports the canonical/generated split and compiler hooks (`impl/spec/minted-project/node.schema.json:4-36`, `graph.schema.json:4-54`, `tools/minted-project/compiler.ts:461-635`); [Tarski] confirms the existing owners and classifications; [Quine] requires the non-collapse distinctions.

| Surface | Role | Authority | Derived? | Required claim limit | Primary anchor |
|---|---|---|---:|---|---|
| `KindDefinition` | Describes a backend kind and its admission/formation bindings | Meta-type registry plus selected profile | No, but binding is configuration | Must not imply that registry membership means profile support | `meta-types.yml:9-17,37-50`; `supported-profiles.yml:18-67` |
| `NodeSource` | Authored node document | Consumer project source | No | Canonical source only | `node.schema.json:4-36`; [Church] |
| `EdgeSource` | Authored outgoing relationship or edge record | Consumer source plus relationship registry | No | Generated inverse edges are not authored | `relationships.yml:17-273`; [Gödel] |
| `NormalizedGraph` | Canonicalized node/edge graph for deterministic processing | Compiler/test-engine projection | Yes | Read model; never source authority | `graph.schema.json:4-54`; [Quine] |
| `Constraint` | Typed validation requirement | Governed predicate family or evaluator contract | Usually | Must not become an undeclared general-purpose DSL | `validate-content.ts:3-10`; [Church] |
| `Obligation` | Content-addressed requirement emitted by derivation | Test-derivation IR and source declarations | Yes | An obligation is not evidence of satisfaction | `ir/types.ts:42-100`; [Church] |
| `TestCase` | Fixture plus evaluator/oracle request | Generated test plan or explicit fixture | Yes | Must identify polarity and expected evidence type | `emit/spec.ts:15-70`; `emit/tests.ts:71-120`; [Popper] |
| `ReceiptEnvelope` | Result and residue evidence | Evaluator output | Yes | Must carry `receipt_family`, evaluator identity, subject digest, and `claim_limit` | `build-receipt.schema.json:4-40`; `residue/receipt.ts:1-6`; [Quine] |
| Inventory entry | Searchable knowledge/read model | Inventory compiler and source references | Yes | Never specification authority | `.arcanum/inventory/schema.md:4-13,88-105`; [Quine] |
| Generated tests | Executable evidence projection | Test emitter | Yes | Cannot promote or rewrite source intent | `emit/tests.ts:1-21,71-120`; [Church] |
| Build/residue receipt | Verification/accounting evidence | Compiler or evaluator | Yes | Does not become a node, edge, or rule | `build-receipt.schema.json:4-40`; `residue/receipt.ts:30-50`; [Tarski] |

### Required `KindDefinition` separation

Evidence anchor: [Church] (`definitions/meta-types/meta-types.yml:9-17,37-50`, `definitions/minted-project/supported-profiles.yml:18-67`, `impl/tools/minted-project/compiler.ts:274-290`) and [Quine] review correction 1.

The candidate kind record must separate three references that are currently easy to conflate:

```json
{
  "kind_id": "Entity",
  "version": "1",
  "category": "structural",
  "status": "active",
  "registry_ref": "definitions/meta-types/meta-types.yml#DS-D1.1",
  "profile_admission_ref": "definitions/minted-project/supported-profiles.yml#feature-with-independent-node-files@1",
  "formation_ref": "impl/spec/meta-types/entity.schema.yml",
  "edge_participation": ["owns", "performs", "emits"],
  "owner": "domainspec"
}
```

`registry_ref` answers “does this kind exist in the vocabulary?”<br>
`profile_admission_ref` answers “is this profile allowed to consume it?”<br>
`formation_ref` answers “how is its source body structurally validated?”

A kind must not be considered supported merely because it appears in the registry.

## Candidate framework contract

Evidence anchor: [Church] candidate shapes and the existing neutral IR (`impl/test-derivation-engine/src/ir/types.ts:5-100`); [Gödel] edge/signature shape (`definitions/relationships/relationships.yml:17-273`, `impl/tools/lib/relationship-signatures.ts:85-143`). These are candidate contracts, not canonical schemas.

The following shapes are candidate contracts, not yet canonical schemas.

### `NodeSource`

Evidence anchor: [Church] (`impl/spec/minted-project/node.schema.json:4-36`, `tools/minted-project/compiler.ts:461-504`).

```json
{
  "schema_version": "minted-node/v1",
  "node_id": "feature.player",
  "feature_id": "feature",
  "kind": "Entity",
  "intent": "Represent a player",
  "body": {
    "fields": [
      {
        "name": "player_id",
        "type": "string",
        "identity": true
      }
    ]
  },
  "connections": [
    {
      "edge_id": "feature.player-performs-unlock",
      "type": "performs",
      "to": "feature.unlock-door"
    }
  ]
}
```

The source-owned `connections` remain canonical. The compiler may strip them when emitting a normalized graph; the generated graph is paired with a source manifest that retains per-node and per-edge source paths and digests (`tools/minted-project/compiler.ts:558-613`), while the graph carries the source-set digest.

### `EdgeSource`

Evidence anchor: [Gödel] (`definitions/relationships/relationships.yml:17-273`, `definitions/relationships/relationships.md:1-42,44-106`) and [Quine] review correction 2.

```json
{
  "edge_id": "feature.player-performs-unlock",
  "predicate": "performs",
  "from": {
    "node_id": "feature.player",
    "kind": "Entity",
    "feature_id": "feature"
  },
  "to": {
    "node_id": "feature.unlock-door",
    "kind": "Operation",
    "feature_id": "feature"
  },
  "scope": "same-feature",
  "multiplicity": "one_to_many",
  "source_anchor": "nodes/player.json#connections[0]",
  "status": "authored"
}
```

The relationship registry remains the authority for endpoint signatures, scope, multiplicity, status, validation obligations, and composition direction. A generated `owned-by` inverse is not an authored `EdgeSource`.

### `Constraint`

Evidence anchor: [Church] (`impl/tools/validate-content.ts:3-10,80-118`, `impl/spec/meta-types/**/*.schema.yml`) and [Curry] formal-boundary report.

```json
{
  "constraint_id": "entity.identity-field-required",
  "scope": "node",
  "owner_ref": "impl/spec/meta-types/entity.schema.yml",
  "predicate_ref": "table-has-column",
  "inputs": {
    "table": "body.fields",
    "column": "identity",
    "expected": true
  },
  "severity": "error"
}
```

`predicate_ref` must point to a governed finite family such as:

- `at-least-one`;
- `all-nonempty`;
- `none`;
- `table-has-column`;
- `attribute-equals`;
- `attribute-present`;
- `attribute-one-of`;
- `section-contains`;
- JSON Schema;
- attribute-map;
- relationship-signature lookup.

A new evaluator may be introduced through an explicit governed `evaluator_ref`. The framework must not silently grow a private expression language.

### `Obligation`

Evidence anchor: [Church] (`impl/test-derivation-engine/src/ir/types.ts:42-100`, `src/rules/index.ts:1-39,78-119`).

```json
{
  "obligation_key": "sha256:...",
  "constraint_id": "edge.endpoint-signature",
  "scope": "edge",
  "class": "formation",
  "source_anchor": "SPEC.md#edges[2]",
  "canonical_params": {
    "predicate": "enforces",
    "source_kind": "Rule",
    "target_kind": "Operation"
  },
  "expected_polarity": "positive",
  "description": "An enforces edge must match an active relationship signature"
}
```

The existing test-derivation engine already has a content-addressed `Obligation` substrate and tiering for `derivable-pure`, `derivable-needs-harness`, and `needs-formal`. The candidate framework should extend that IR rather than introduce an unrelated test model.

### `TestCase`

Evidence anchor: [Church] (`impl/test-derivation-engine/src/emit/spec.ts:15-70`, `src/emit/tests.ts:1-21,71-120`) and [Popper] non-vacuity correction: no end-to-end path is currently witnessed.

```json
{
  "case_id": "edge-cycle-typed-negative",
  "obligation_id": "sha256:...",
  "polarity": "typed-negative",
  "fixture_ref": "fixtures/cycle.json",
  "oracle": {
    "kind": "datalog",
    "evaluator_ref": "candidate.cross-graph.v1"
  },
  "expected": {
    "result": "counterexample",
    "claim_limit": "bounded-relation-check"
  },
  "source_anchor": "research/cycle-witness.md"
}
```

Supported polarity should remain explicit:

- `positive`;
- `typed-negative`;
- `counterexample`;
- `trace`.

Generated tests must preserve source and obligation pointers and report unresolved cases as coverage gaps rather than fabricated assertions.

### `ReceiptEnvelope`

Evidence anchor: [Church] (`impl/spec/minted-project/build-receipt.schema.json:4-40`, `impl/test-derivation-engine/src/residue/receipt.ts:1-6,30-50`) and [Quine] review correction 4.

```json
{
  "schema_version": "validation-receipt/v1",
  "receipt_family": "structural|graph|formal-static|temporal|runtime|freshness",
  "subject_digest": "sha256:...",
  "profile_digest": "sha256:...",
  "registry_digests": [
    "sha256:..."
  ],
  "evaluator_id": "relationship-table-walk",
  "evaluator_version": "1",
  "status": "pass|fail|counterexample|coverage_gap|stale",
  "claim_limit": "shape-only|bounded-relation-check|bounded-static-model|finite-trace-result|runtime-observation|freshness-only",
  "results": [
    {
      "obligation_id": "sha256:...",
      "verdict": "pass|fail|counterexample|unresolved",
      "witness_or_violations": [],
      "source_refs": []
    }
  ],
  "residue": []
}
```

The existing build receipt and residue receipt provide precedent for digest binding and structural accounting. A general receipt must not claim semantic proof unless the evaluator and evidence actually support that claim.

## Canonical versus generated boundary

Evidence anchor: [Church] (`impl/spec/minted-project/node.schema.json:36`, `graph.schema.json:4-54`, `tools/minted-project/compiler.ts:558-635`); [Tarski] owner review; [Quine] ontology/non-collapse correction 6.

| Artifact | Canonical status | Allowed use | Prohibited interpretation |
|---|---|---|---|
| Consumer node file | Canonical | Source intent and formation validation | Must not be regenerated from graph output |
| Authored edge/connection | Canonical | Relationship validation and provenance | Must not be inferred from generated inverse edges |
| Registry/profile | Canonical configuration | Admission and signature lookup | Registry membership is not profile support |
| Normalized graph | Generated | Deterministic graph queries and derivation | Not an alternate source of intent |
| Generated SPEC | Generated | Human-readable projection | Not authority for omitted source facts |
| Generated test plan/code | Generated | Executable evidence | Not an implementation oracle |
| Build receipt | Generated evidence | Digest and artifact accounting | Not a specification |
| Formal/query result | Generated evidence | Bounded counterexample or relation result | Not universal proof |
| Inventory | Generated/read model | Discovery and reuse | Not authority or promotion gate |

This boundary is already reflected in the compiler and test engine. The framework should make it explicit in all receipts and adapters.

## Obligation-routing matrix

Evidence anchor: [Curry] formal boundary and class table (`.arcanum/inventory/entries/fol-constitution-validation-complement-synthesis.md`, `projects/domainspec-v2/development/meta-type-formalization/research/2026-07-02-formalism-and-primitives/findings.md`); [Gödel] structural/graph routing (`impl/tools/validate-relationships.ts:1-80`, `impl/governance/tags/tools/check-code-tag-composability.ts:22-117,431-474`).

| Obligation class | Default evaluator | Evidence output | Claim limit |
|---|---|---|---|
| Node identity, required fields, typedness, formation shape | JSON Schema, `.schema.yml`, attribute-map, deterministic table walk | Pass/fail plus field diagnostics | Shape only |
| Edge predicate, endpoint signature, multiplicity, scope, status | Relationship registry plus structural graph validator | Edge-local diagnostics | Shape/signature only |
| Source path safety, ID uniqueness, profile/registry/source digests | Compiler manifest and deterministic checks | Manifest/build receipt | Deterministic accounting |
| Generated projection parity | Compiler provenance and digest checks | Source-to-generated parity evidence | Projection consistency only |
| Rule-cell return sort | Declarative return-type check or tiny internal parser | Return-sort verdict | No satisfiability or meaning claim |
| Per-rule satisfaction already owned by Lean | Existing Lean kernel/decider | Relabeled owned result | Do not rebuild as generic FOL |
| Cross-rule common state, contradiction, reachability, cycles, closure | Cedar/Datalog/FOL complement | Query result, witness, counterexample, or unsat core | Bounded/decidable relation claim; no Row-3 meaning |
| Stable finite encodings where an SMT adapter is already governed | Private SMT candidate adapter | `sat`, `unsat`, model, or counter-witness | Not public default; encoding-dependent |
| Static graph completeness and structural counterexamples | Alloy bounded model | Satisfying instance or counterexample with scope | Bounded evidence, not proof |
| Temporal ordering, retries, compensation, cancellation, freshness behavior | TLA+/PlusCal with TLC | Invariant violation trace or finite-state result | Finite model result, not unbounded proof |
| Runtime operation/event behavior | Runtime or integration harness | Runtime observation and test output | Implementation-observation claim |
| Semantic satisfiability, purity, non-thinness, implementation meaning | Private engine, Lean/categorical residue, or human review | Proof artifact, residue, or review decision | Not a public structural-validator claim |
| Fact freshness and acceptance | DCB/hash/rerun wrapper | Current/stale/accepted receipt | Freshness only, never behavior proof |

The formalization finding establishes the structural floor: no per-instance FOL, SMT, or Lean validator; schema/table-walk remains the default. `O_spec` remains independent from public structural validation, with its solver boundary in the private engine.

SMT is therefore not the universal route. Alloy and TLA are not interchangeable with structural validation, and neither should be described as an unbounded proof system.

## Real structural witnesses

### Minted-project compiler witness

The existing `key-and-door` positive fixture provides a real source-to-graph witness:

- four nodes;
- three edges;
- seven provenance records;
- source-owned `Player` entity;
- typed `performs` relationship to `UnlockDoor`;
- byte-identical repeated compiler output;
- provenance back to source paths and digests.

Relevant evidence:

- `projects/domainspec-v2/impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/`
- `projects/domainspec-v2/impl/tools/tests/minted-project-compiler.test.ts`
- `projects/domainspec-v2/impl/spec/minted-project/node.schema.json`
- `projects/domainspec-v2/impl/spec/minted-project/graph.schema.json`

This proves the current structural compiler path, not the full evolvable framework.

### Relationship validator witness

The valid relationship fixture was run with:

```bash
cd projects/domainspec-v2/impl
npx tsx tools/validate-relationships.ts \
  --features-root spec/__fixtures__/relationships/valid \
  --schema-dir spec/meta-types \
  --relationships ../definitions/relationships/relationships.yml
```

Observed result:

```text
validate-relationships: PASS (1 specs checked, edgesChecked=6, canonicalSignatures=30)
```

This is a real deterministic node/edge table-walk witness. It does not demonstrate graph closure, temporal behavior, or cross-rule evaluation.

## Typed negative witnesses

Evidence anchor: [Church] compiler mutation tests (`impl/tools/tests/minted-project-compiler.test.ts:106-187`); [Gödel] relationship negatives (`impl/spec/__fixtures__/relationships/bad-*/SPEC.md`, `impl/tools/validate-relationships.ts:1-80`); [Popper] confirms these are real structural negatives, not evidence for a cross-graph engine.

Existing negative fixtures and compiler tests demonstrate that the structural lane can reject malformed or authority-collapsing inputs:

- missing canonical `intent` -> `NODE_SCHEMA_INVALID`;
- generated `authority` field on a canonical node -> `NODE_SCHEMA_INVALID`;
- unsupported profile or digest mismatch -> `PROFILE_UNSUPPORTED`;
- `Value Object` under the current four-kind profile -> `KIND_UNSUPPORTED`;
- invalid operation formation -> `FORMATION_INVALID`;
- duplicate node or edge IDs -> duplicate diagnostics;
- unknown, generated, deprecated, or deferred authored relationship labels -> corresponding edge-type diagnostics;
- dangling endpoint -> `EDGE_ENDPOINT_MISSING`;
- endpoint-kind mismatch -> `EDGE_ENDPOINT_KIND_MISMATCH`;
- cross-feature edge where unsupported -> `CROSS_FEATURE_UNSUPPORTED`;
- `Operation --enforces--> Value Object` -> invalid signature;
- reversed `enforces` endpoints -> invalid signature;
- `Operation --emits--> Event` -> invalid event causality;
- `Calculation --queries--> Policy` -> invalid target kind;
- authored `owned-by` inverse -> generated-authority rejection;
- `Saga --orchestrates--> Operation` -> current Workflow-only signature residue, not silently normalized;
- deprecated `enforces-cross` -> rejection.

These are structural negatives. They do not establish that a cross-graph evaluator exists.

## Candidate cross-graph witness and its limit

Evidence anchor: [Curry] hand-built cycle witness and candidate receipt from `.arcanum/inventory/entries/fol-constitution-validation-complement-synthesis.md`; [Popper] explicitly classifies it as not a shipped evaluator result.

A hand-built research witness demonstrates why table-walk alone is insufficient:

```text
nodes: C2, C13, C4
edges:
  governs(C2,C13)
  governs(C13,C4)
  governs(C4,C2)

local_result: all unary per-rule lints pass
query: reach(X,X) / governs_acyclicity
result: counterexample
cycle: [C2,C13,C4,C2]
```

Candidate receipt shape:

```json
{
  "query_id": "governs-acyclicity",
  "scope": "typed-corpus",
  "engine": "Cedar|Datalog candidate",
  "result": "counterexample",
  "witness": {
    "cycle": ["C2", "C13", "C4", "C2"]
  },
  "claim": "bounded/relation-check",
  "status": "candidate-non-authoritative",
  "source_refs": [
    "fol-constitution-validation-complement-synthesis.md"
  ]
}
```

This witness is useful as a design target and typed-negative architecture example. It is not a shipped evaluator result. The repository currently has no end-to-end cross-graph path from `TestCase` through an evaluator to a typed `ReceiptEnvelope`.

## Alloy and TLA evidence limits

Evidence anchor: [Curry] (`projects/domainspec-v2/research/alloy-tla-modeling/TOWER.md:7-21,38-65,85-92`, `BRIDGE-DECISIONS.md:7-15`, `CLAIM-LEDGER.md:31-38`) and [Gödel] fixture boundary (`fixtures/formal-saga-fixture.schema.json:145-223`).

The formal saga fixture supplies reusable nodes, edges, facts, traces, and model expectations. The research tower assigns:

- Alloy: bounded static graph structure and counterexamples;
- TLA+/TLC: temporal traces, safety, retries, compensation, and freshness behavior;
- TypeScript: first extraction and bounded witness preparation.

However:

- Alloy syntax/checking is not currently validated;
- TLA syntax/checking is not currently validated;
- the extractor-to-model contract is absent;
- fixture expectations are declarations, not solver receipts;
- bounded no-counterexample results must not be described as universal proofs.

The `orchestrates` Saga-versus-Workflow mismatch remains open and must not be widened by a formal fixture.

## Evolution path beyond the current four-of-thirteen profile

Evidence anchor: [Church] compiler/profile evolution path (`definitions/minted-project/supported-profiles.yml:18-67`, `impl/tools/minted-project/compiler.ts:274-290`); [Tarski] correction that the current schema still has four hard-coded formation branches; [Popper] required end-to-end witness gate.

1. Freeze the authority boundary and the three-way kind separation: `registry_ref`, `profile_admission_ref`, and `formation_ref`.
2. Make profile admission data-driven for additional backend kinds. Adding a kind should normally require a registry/profile binding, formation adapter, positive fixture, and typed-negative fixture—not a compiler-core union branch.
3. Reuse one generic node, edge, constraint, obligation, test, and receipt substrate.
4. Derive structural obligations first. Preserve explicit source rows and refuse invented semantics.
5. Implement a minimal runnable cross-graph evaluator with a stable query identifier, typed input records, positive and typed-negative fixtures, a `TestCase`, evaluator output, a typed `ReceiptEnvelope`, and explicit bounded claim limits.
6. Add Cedar/Datalog/FOL only for cross-rule and cross-graph obligations where local table-walk cannot express the property.
7. Add Alloy and TLA adapters only after syntax/model validation and an extractor contract exist.
8. Preserve existing Lean ownership and relabel owned results rather than rebuilding them in a new generic solver.
9. Bind receipts to profile, registry, source, and evaluator digests.
10. Publish only read-model projections to Inventory; do not promote the candidate framework into DomainSpec authority without a separate decision.

## Verdict matrix

Evidence anchor: [Tarski] precedent matrix; [Popper] non-vacuity matrix; [Quine] definitional-soundness matrix; local owners are cited in each relevant row's source list above. Structural witness commands are recorded in `Real structural witnesses`.

| Surface or claim | Owner | Witnessed | Soundness posture | Verdict | Evidence anchor |
|---|---|---:|---|---|---|
| Generic minted-node envelope | Node schema and compiler | Yes | Structural shape only | ACCEPT; already deployed | `node.schema.json:4-36`; [Church] |
| Registry/profile/formation separation | Registry, profile, formation schemas | Partial | Existing pieces are real but not unified in one generic contract | ACCEPT WITH CORRECTION | `meta-types.yml:9-17`; `supported-profiles.yml:18-67`; [Tarski] |
| Four-kind profile admission | Supported profile | Yes | Correct for current profile only | ACCEPT; not thirteen-kind completion | `supported-profiles.yml:18-49`; [Church] |
| All thirteen active backend kinds admitted | No single owner | No | Unsupported claim | REVISE; future evolution work | [Popper] non-vacuity review; 4-of-13 evidence |
| Generic graph/node/edge/obligation IR | Test-derivation engine | Yes | Deterministic structural substrate | ACCEPT AS FOUNDATION | `ir/types.ts:5-100`; [Church] |
| Canonical source versus normalized/generated artifacts | Compiler, graph schema, receipts | Yes | Authority boundary is evidenced | ACCEPT | `graph.schema.json:4-54`; `compiler.ts:558-635`; [Quine] |
| Structural node/edge validators | Schema/table-walk tools | Yes | Positive and typed-negative fixtures exist | ACCEPT | `validate-relationships.ts:1-80`; [Gödel]/[Popper] |
| Cross-rule FOL/Cedar/Datalog evaluator | None wired | No | Hand-built research witness only | REVISE; implementation blocker | [Curry] cycle witness; [Popper] no engine |
| End-to-end `TestCase -> evaluator -> ReceiptEnvelope` | None wired | No | Missing executable path | REVISE; implementation blocker | [Popper] non-vacuity review |
| SMT adapter | Inventory candidate architecture | No | Intended-not-shipped and encoding-dependent | CANDIDATE ONLY | `.arcanum/inventory/entries/deterministic-validation-for-all-cav2-synthesis.md`; [Curry] |
| Alloy static model | Research tower | No | Sketch/fixture unvalidated; bounded only | CANDIDATE; no proof claim | `TOWER.md:7-21,38-65`; [Curry]/[Gödel] |
| TLA temporal model | Research tower | No | Sketch/fixture unvalidated; bounded only | CANDIDATE; no proof claim | `TOWER.md:54-65`; `CLAIM-LEDGER.md:31-38`; [Curry] |
| Existing Lean satisfaction boundary | Existing formal owner | Partial | Preserve and relabel; not revalidated here | ACCEPT AS OWNER; no rebuild | formalization findings; [Curry] |
| Current relationship count | Root relationship authority | Yes for 30 | Historical 29 is drift | ACCEPT 30 as current authority; reconcile read models | `relationships.yml:17-18`; [Gödel]/[Tarski] |
| Saga/Workflow `orchestrates` mismatch | Relationship authority and formal fixture | Yes as residue | Must remain explicit | OPEN; do not normalize | bad fixture + `formal-fixture.json:268-271`; [Gödel] |
| Code-level composability coverage | Composability checker | Partial | Several predicates have call semantics; many are coverage gaps | PARTIAL; no universal realization claim | `impl/governance/tags/tools/check-code-tag-composability.ts:22-117,431-474`; [Gödel] |
| Inventory formal/query entries | Inventory | Yes as candidate research | Read model only | ACCEPT AS READ MODEL | `.arcanum/inventory/schema.md:4-13,88-105`; [Quine] |
| Universal solver or single formalism | None | No | Contradicted by routing evidence | REJECT | formalization findings; [Curry] |

## Pairwise evidence sentences

Evidence anchor: the six sentences below are the frozen pairwise tensions required by the dispatch sheet; source-side support is preserved in [Church], [Curry], [Gödel], [Tarski], [Popper], and [Quine] returns in `research.md`.

- **Church/Curry — structural-kernel vs formal-query on methodology:** Current node and edge obligations are finite parsed records with existing table-walk precedents, while formal queries add value only for cross-rule and cross-graph properties; using a solver for per-node formation would be a structural-table-walk re-skin.
- **Church/Gödel — node/constraint vs edge/graph on source-corpus:** Node and constraint records preserve source-owned formation evidence, while edge and graph records supply endpoint signatures, reachability, cycles, and composition relations that cannot be recovered from node-local fields alone.
- **Curry/Gödel — logic-fragment vs bounded graph counterexample on methodology:** A Cedar/Datalog/FOL fragment should answer a typed relation query over a stable graph corpus, whereas Alloy should be reserved for bounded static counterexamples when the graph law is not adequately represented by a finite table lookup.
- **Tarski/Popper — precedent vs runnable witness on attack-vector:** Existing schemas, compiler hooks, relationship validators, and obligation IR establish precedent for the structural kernel, but precedent does not satisfy the framework claim until a minimal end-to-end runnable witness produces a typed receipt.
- **Tarski/Quine — precedent vs definitional-collapse on attack-vector:** The proposal may reuse existing owners and artifacts, but it must not collapse registry membership, profile admission, formation validation, normalized nodes, obligations, tests, receipts, and Inventory into one overloaded definition.
- **Popper/Quine — non-vacuity vs definitional-collapse on attack-vector:** A positive and typed-negative fixture must exercise distinct evaluators and produce claim-limited evidence; otherwise a re-labeled structural pass can appear to validate a cross-graph or semantic obligation without actually doing so.

## Non-goals

Evidence anchor: [Curry] no-universal-solver boundary; [Quine] authority/non-collapse review; [Popper] non-vacuity review; local mutation boundary from the dispatch constitution.

This candidate does not:

- create a universal solver;
- route every obligation through FOL, SMT, Lean, Alloy, or TLA;
- introduce an undeclared DomainSpec validation DSL;
- claim per-instance semantic satisfiability or non-thinness;
- claim that all thirteen backend kinds are currently admitted;
- promote generated graphs, tests, receipts, or Inventory entries to source authority;
- repair the Saga/Workflow relationship mismatch;
- reconcile the historical twenty-nine signature count by mutating authority;
- claim that Alloy or TLA sketches are model-checked;
- claim that bounded results are unbounded proofs;
- assert complete code-level composability for all active relationships;
- mutate DomainSpec schemas, profiles, relationship definitions, or engine code.

## Residue and next gates

Evidence anchor: [Curry] formal residue (`.arcanum/inventory/entries/fol-constitution-validation-complement-synthesis.md`); [Gödel] relationship/composability residue (`definitions/relationships/relationships.yml:494-537`, `impl/governance/tags/tools/check-code-tag-composability.ts:431-474`); [Popper] missing TestCase/Receipt and cross-graph gates; [Quine] authority/non-collapse gates.

The framework remains candidate until the following are resolved:

1. Define and validate the minimal `TestCase -> evaluator -> ReceiptEnvelope` path.
2. Implement one runnable cross-graph evaluator, preferably for a bounded cycle/reachability property.
3. Add positive, typed-negative, and counterexample fixtures for that evaluator.
4. Decide the owner and lifecycle for evaluator/query definitions.
5. Verify receipt-family and claim-limit semantics against actual evaluator outputs.
6. Reconcile the current thirty-signature authority with historical twenty-nine-signature read models.
7. Keep the Saga/Workflow mismatch explicit until a separate owner decision.
8. Re-measure composability coverage from current source rather than relying on historical nine-of-twenty-nine figures.
9. Validate Alloy and TLA syntax and establish the extractor-to-model contract.
10. Determine whether any SMT adapter is needed after structural and graph-query lanes are proven.
11. Add or update Inventory entries only as candidate read-model projections.
12. Revisit the private `O_spec`/semantic boundary before any claim about non-vacuity or meaning.

**Current decision:** proceed with the layered abstraction as a research and implementation candidate, but do not treat the validation framework as complete until the runnable cross-graph evaluator and typed receipt path exist.
