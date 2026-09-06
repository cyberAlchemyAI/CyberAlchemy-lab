---
dispatch_id: 2026-07-17-domainspec-evolvable-validation-framework
artifact: explorer-transcript
status: candidate
authority: non-authoritative research transcript
---

# Explorer transcript

The following returns are preserved verbatim from the three independent explorer lanes. The parent has not normalized or merged their claims.

## Agent 1 — Church, Alonzo

## Findings
1. Current source node contract is already generic at the envelope: `minted-node/v1` requires `node_id`, `feature_id`, opaque nonempty string `kind`, `intent`, nonempty `body`, and source-owned `connections`; node schema marks this as consumer-owned canonical source (`impl/spec/minted-project/node.schema.json:4-16,18-36`). The closed behavior is profile admission, not envelope shape.
2. The current profile is the bottleneck: `feature-with-independent-node-files@1` admits only `[Entity, Event, Operation, Rule]`, and only four formation schemas; `relationships` admits exactly enforces/performs/produces. It is experimental/release-deferred and non-goals include cross-feature completeness and independent edge lifecycle (`definitions/minted-project/supported-profiles.yml:18-67`). The registry separately says 13 active backend members, IDs DS-D1.1..9, DS-D1.11..14; DS-D1.10 Saga is deliberately superseded/gapped (`definitions/meta-types/meta-types.yml:9-17,37-43`). Thus `kind` can be generic, but admission is currently 4-of-13, not a 13-kind generic engine.
3. Canonical-vs-generated boundary is explicit: source node has authority `consumer-project-source`; normalized graph is generated semantic read model (`impl/spec/minted-project/node.schema.json:36`, `graph.schema.json:4-5,54`); build receipt is generated verification evidence with profile/registry/source/artifact digests (`build-receipt.schema.json:4-5,7-40`). Compiler emits graph nodes stripped of `connections` and records each node/edge back to source path+digest (`tools/minted-project/compiler.ts:558-613`). Never promote graph, generated tests, or receipt to authored node authority.
4. Compiler already supplies generic admission hooks: profile `kinds`, `formation_schemas` OR `formation_contracts` (JSON Schema or attribute-map), then `validateFormation` (`compiler.ts:274-290`); profile/registry digest checks (`compiler.ts:384-440`); node envelope/formation check, kind admission, node feature/ID uniqueness (`compiler.ts:461-504`); edge label classification (unknown/generated/deprecated/deferred/unsupported), endpoint existence, same-feature boundary, endpoint-kind signature (`compiler.ts:507-555`). Extending to new kinds should add registry/profile entries + formation contract adapters, not a new union branch in compiler core.
5. Existing `.schema.yml` backend criteria are structural and heterogeneous but composable: Entity = fields table with >=1 identity + all typed; Value Object = no identity + typed + Equality prose marker; Enum = Value table; Operation/Query/Calculation/Rule/Policy/Event/Interface/Mapping/Workflow/State Machine use attribute predicates (`impl/spec/meta-types/{structural,behavioral,connective,lifecycle}/*.schema.yml`, e.g. entity.schema.yml lines 7-24; operation/query/rule/policy/event/interface/mapping/workflow/state-machine schemas). Current content validator explicitly says criterion is decidable table-walk, shape-only, no δ import/satisfiability (`impl/tools/validate-content.ts:3-10`).
6. The deterministic test engine already has the neutral internal substrate: `ConceptGraph` = sorted `Node[]` + `Edge[]`; node has `type`, `source_anchor`, fields, optional `needs_formal`; `Obligation` has content-addressed `obligation_key`, `rule_type`, source anchor, canonical params, description (`impl/test-derivation-engine/src/ir/types.ts:5-31,42-66,68-100`). Normalized SPEC adapter preserves only explicit concepts/relationships/fields/attributes/omitted rows and refuses invented behavior (`src/grammar/index.ts:912-1011`; residue receipt says structural accounting, not satisfiability/generation at `src/residue/receipt.ts:1-6`).
7. Generated tests are evidence projections, not source: `emitSpec` sorts by obligation key; tier split is `derivable-pure`, `derivable-needs-harness`, `needs-formal` (`src/emit/spec.ts:15-70`). Hybrid emitter derives expected values from Formal AST, never implementation; unresolved/human-oracle classes become counted `it.skip` coverage gaps, never faked (`src/emit/tests.ts:1-21,30-53,71-120`). Rule derivation is pure/total/deterministic and surfaces unclassified prose as `needs_formal`, not guessed (`src/rules/index.ts:1-39,78-103`).

## Candidate generic framework (non-authoritative shape)
- `KindDefinition`: `{kind_id, version, category, status, source_contract:{format,path}, criterion_refs[], edge_participation, owner}`. Registry/profile supplies this; core treats `kind_id` as opaque. A new backend kind is a data/profile addition when it has a formation contract + positive/typed-negative fixtures; no compiler union edit.
- `NodeSource`: `{schema_version, node_id, feature_id, kind, intent, body, connections[]}` (current envelope). `kind` remains a registry key; body is validated through the selected contract.
- `EdgeSource`: `{edge_id,type,from,to,feature_scope,source_anchor}`; authored outgoing connection remains source-owned; relationship registry supplies typed endpoint/multiplicity/status. Generated graph edge is a projection.
- `Constraint`: `{constraint_id, scope:'node'|'edge'|'graph'|'source-set', owner_ref, predicate_ref, inputs, severity}`. Predicate references current finite families (`at-least-one`, `all-nonempty`, `none`, `table-has-column`, `attribute-equals`, `attribute-present`, `attribute-one-of`, `section-contains`, JSON Schema/attribute-map) instead of inventing a full DSL. Add explicit `evaluator_ref` only for a new governed evaluator.
- `Obligation`: extend existing IR with `constraint_id`, `scope`, `class`, `source_anchor`, canonical params, expected polarity. Structural obligations are produced from source declarations; graph/formal obligations are separate derivations.
- `TestCase`: `{case_id, obligation_id, polarity:'positive'|'typed-negative'|'counterexample'|'trace', fixture_ref, oracle:{kind:'schema'|'table-walk'|'graph'|'datalog'|'cedar'|'alloy'|'tla'|'runtime'}, expected, source_anchor}`. Generated test code must carry obligation/source pointers and explicit coverage-gap status.
- `Receipt`: `{schema_version, subject_digest, profile_digest, registry_digests, evaluator_id/version, status, results:[{obligation_id, verdict, witness_or_violations, source_refs}], residue:[...]}`. This generalizes current build receipt + residue receipt; it is evidence, never authority.
- Evolution path: (a) make profile admission data-driven for all 13 active backend kinds by binding each kind to a formation adapter; (b) use one generic node/edge/constraint IR; (c) add new kinds as registry/profile+fixtures; (d) derive structural obligations first; (e) add graph/cross-rule evaluator only where node-local predicate is inexpressive; (f) add runtime/formal adapters without changing source node contract; (g) receipt binds exact profile/registry/source/evaluator digests.

## Source_refs (path + anchors)
- `projects/domainspec-v2/definitions/meta-types/meta-types.yml:9-17,37-50` — 13 active backend registry; superseded ID gap.
- `projects/domainspec-v2/definitions/minted-project/supported-profiles.yml:18-67` — profile admits 4 kinds; formation schemas; edge slice; release/non-goals.
- `projects/domainspec-v2/impl/spec/minted-project/node.schema.json:4-16,18-36` — canonical generic source envelope + four conditional formations.
- `projects/domainspec-v2/impl/spec/minted-project/graph.schema.json:4-5,7-12,24-54` — generated graph contract.
- `projects/domainspec-v2/impl/spec/minted-project/build-receipt.schema.json:4-5,7-40` — generated evidence receipt and digest bindings.
- `projects/domainspec-v2/impl/tools/minted-project/compiler.ts:274-290,347-369,384-440,461-555,558-635` — formation adapters, relationship classification, profile/registry admission, typed graph emission and source manifest.
- `projects/domainspec-v2/impl/tools/validate-content.ts:3-10,80-118` — shape-only table walk, no δ/satisfiability.
- `projects/domainspec-v2/impl/tools/lib/relationship-signatures.ts:85-143,248-297,402-470` — finite relationship authority; schema participation; triple endpoint checks and generated-view rejection.
- `projects/domainspec-v2/impl/test-derivation-engine/src/ir/types.ts:5-31,42-100` — generic graph/node/edge/obligation IR.
- `projects/domainspec-v2/impl/test-derivation-engine/src/grammar/index.ts:912-1011,1127-1148` — normalized source adapter preserves explicit rows only; no invented semantics.
- `projects/domainspec-v2/impl/test-derivation-engine/src/rules/index.ts:1-39,78-119` — pure total derivation; unclassified -> needs_formal.
- `projects/domainspec-v2/impl/test-derivation-engine/src/emit/spec.ts:15-70,81-176` — deterministic ordering + obligation tiers/gap ledger.
- `projects/domainspec-v2/impl/test-derivation-engine/src/emit/tests.ts:1-21,71-120,129-140` — generated assertions from formal source only; honest skips.
- `projects/domainspec-v2/impl/test-derivation-engine/src/residue/receipt.ts:1-6,30-50,68-133` — structural residue accounting and binding commitments.
- `.arcanum/inventory/entries/deterministic-validation-for-all-cav2-synthesis.md` — candidate typed-record/query architecture; intended-not-shipped.
- `.arcanum/inventory/entries/fol-constitution-validation-complement-synthesis.md` — three fibres; Row-2 cross-rule FOL/Cedar/Datalog complement; Row-1 relabel; Row-3 categorical/Lean boundary.
- `projects/domainspec-v2/development/meta-type-formalization/research/2026-07-02-formalism-and-primitives/findings.md` — frozen no-DSL/no-SMT-per-instance; structural table walk; one cross-graph solver; semantic meaning/purity boundary.

## Runnable positive node witness
Existing `key-and-door` fixture (source files under `impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/specs/key-and-door/nodes/`) compiles with the command already sent. The positive `Player` node is canonical Entity with `body.fields=[{name:'player_id',type:'string',identity:true}]`, source-owned `performs` edge to `UnlockDoor`; compiler emits corresponding graph node/edge and source digests. Full fixture result: 4 nodes + 3 edges + 7 provenance records; repeated compiler call is byte-identical (covered by `impl/tools/tests/minted-project-compiler.test.ts` first test).

## Typed negative witnesses
- `impl/test-derivation-engine/__fixtures__/minted-project/contract/negative/missing-machine-field/case.json` — missing `intent` in canonical node; node schema required field -> `NODE_SCHEMA_INVALID`.
- `.../generated-authority-field/case.json` — canonical node carries `authority: generated-semantic-read-model`; `additionalProperties:false` -> `NODE_SCHEMA_INVALID`; tests authority non-collapse.
- `.../profile-language-mismatch/case.json` — unsupported profile/digests -> `PROFILE_UNSUPPORTED`/digest mismatch.
- `.../source-path-escape/case.json` — project-relative path escape -> resolver/schema rejection.
- Compiler mutations in `impl/tools/tests/minted-project-compiler.test.ts`: unsupported `Value Object` under current 4-kind profile -> `KIND_UNSUPPORTED`; `Operation.state_change=no` -> `FORMATION_INVALID`; duplicate node/edge IDs -> `NODE_ID_DUPLICATE`/`EDGE_ID_DUPLICATE`; unknown/generated/deprecated/deferred/unsupported relationship labels -> corresponding `EDGE_TYPE_*`; dangling endpoint -> `EDGE_ENDPOINT_MISSING`; wrong endpoint kind -> `EDGE_ENDPOINT_KIND_MISMATCH`; cross-feature target -> `CROSS_FEATURE_UNSUPPORTED`.
- Registry evidence: `definitions/relationships/relationships.yml:17-18,500-531` has 30 active signatures, generated `owned-by`, deferred `depends-on`/etc, deprecated `enforces-cross`; compiler must reject generated/deferred/deprecated authored labels.

## Obligation classification (structural-kernel lane)
| Scope | Obligation class | Current evidence | Evaluator boundary |
|---|---|---|---|
| node | formation/criterion (identity, typedness, attribute discriminator, shape) | `.schema.yml` + `validate-content.ts`; minted four JSON formation schemas | bounded table walk / JSON Schema / attribute-map; no solver |
| edge | canonical label + endpoint signature + multiplicity/scope | relationship registry + compiler + relationship validator | finite lookup/table walk; typed negative fixture |
| source-set | profile/kinds/relationship digests, source path and ID uniqueness | compiler + build receipt/source manifest | deterministic digest/manifest check |
| graph | reachability, cycle, cross-rule closure, composability | not currently enforced in minted compiler; registry semantics/`relationships.yml` | separate finite graph evaluator (Datalog/Cedar); bounded Alloy for counterexamples where static graph laws are not table-local |
| behavior | transitions, query/operation runtime, event consumer behavior, workflow ordering | test-derivation engine rule classes + bindings | runtime harness/integration; generated tests may be real or honest `coverage_gap` |
| formula | closed arithmetic/range/count-cap | formal AST + exact rational evaluator | pure deterministic test from authored formula; expected never from impl |
| temporal | traces, retries, cancellation, saga/workflow lifecycle | Alloy/TLA research tower (candidate) | bounded Alloy static counterexample / TLA temporal model; no proof claim |
| meaning | satisfiability, semantic purity, non-vacuity/implementation semantics | explicit moat boundary; no public validator | residue/DEFINE-falsified/private engine, not generic structural checker |

## Pair evidence
- Church (structural methodology) vs Curry (formal-query): structural kernel wins at node/edge formation because all current criteria are finite parsed records and already have table-walk precedents; formal query is a *complement* for cross-rule/global properties, not a replacement. A solver on per-node formation would add weight and drift toward private δ semantics.
- Church vs Gödel (graph source-corpus): source corpus supplies endpoint signatures, profile admission, source anchors, and digest bindings; graph-only checks cannot recover omitted authority. Per-edge signature is finite lookup; graph-level cycles/reachability need relation-aware evaluator. Keep authored node/edge source separate from generated graph/receipt.
- Pairwise evidence sentence required by sheet: `structural-kernel vs formal-query on methodology` and `node/constraint vs edge/graph on source-corpus` (my lane contributes the structural/source side; Curry/Gödel must supply formal/graph counter-evidence).

## Agent 2 — Curry, Haskell

## findings
The formal-query layer should consume typed structural records, not replace them. The formal boundary is layered: (1) per-concept/per-edge shape remains `.schema.yml` + deterministic table walk; (2) per-rule boolean return shape is a schema/return-sort check; (3) cross-rule/cross-graph properties (reachability, cycles, common-state consistency) are the genuine Row-2 residue for FOL/Cedar/Datalog; (4) static bounded graph counterexamples belong to Alloy; (5) temporal traces/safety/failure/compensation/retry/freshness behavior belong to TLA+/TLC; (6) Lean remains the owned Row-1 satisfaction/decidability and Row-3 residue/gluing boundary. Do not collapse these into one universal solver or call bounded checks proofs.

Pair evidence (formal-query methodology vs Church structural kernel + Goedel graph source-corpus): formal queries should take Church-like typed structural records as their input kernel, while Goedel-like graph-level source-corpus relations (edges/reachability/cycles) are where queries add information beyond node-local structure. A query that only rechecks node fields is a structural-table-walk re-skin; a graph query must expose an edge witness/counterexample.

## source_refs
- `.arcanum/inventory/entries/deterministic-validation-for-all-cav2-synthesis.md`: candidate shared SMT adapter over typed records; 3 sibling query families (non-collapse, closure, build-from-owned); schema typing is precondition; SMT cannot choose axes or prove absolute non-thinness; intended/not shipped.
- `.arcanum/inventory/entries/fol-constitution-validation-complement-synthesis.md`: 3 fibres: Row 1 per-rule satisfaction already Lean-owned/relabel; Row 2 cross-rule consistency/open residue (common state, cycles) where FOL/Cedar/Datalog complement applies; Row 3 residue/behavior gluing where FOL is blind; Cedar/Datalog preferred; Alloy first counterexamples.
- `projects/domainspec-v2/development/meta-type-formalization/research/2026-07-02-formalism-and-primitives/findings.md`: no DSL; no FOL/SMT/Lean for per-instance validation; schema/table-walk floor; FOL/Cedar/Datalog only cross-graph/cross-rule; SMT no for per-instance/meaning; Lean not per-instance; public shape vs private engine meaning boundary; no cross-graph engine wired; Alloy/TLA/Lean residues.
- `projects/domainspec-v2/research/alloy-tla-modeling/TOWER.md`: TypeScript first extraction/bounded witness; Alloy structural graph; TLA temporal behavior; no proof claim.
- `.../BRIDGE-DECISIONS.md`: TypeScript borrow-carefully; Alloy promotion-candidate for graph completeness; TLA promotion-candidate for saga execution; DCB freshness only; universal Alloy/TLA use blocked.
- `.../CLAIM-LEDGER.md`: Alloy/TLA claims bounded; `orchestrates` Saga-vs-Workflow mismatch open; sketches and extractor contract unvalidated.
- `.../fixtures/formal-saga-fixture.schema.json` + `order-fulfillment.formal-fixture.json`: reusable node/operation/edge/trace/fact/expectation/residue shape; expected Alloy/TLA outputs are declared, not proof of actual runs.

## one runnable witness
**Cross-rule cycle witness (hand-built + hand-run in the FOL synthesis; candidate adapter only, not shipped):**
```
nodes: C2, C13, C4 (each individually closure/kind/location clean)
edges: governs(C2,C13), governs(C13,C4), governs(C4,C2)
local_result: all unary per-rule lints pass
query: reach(X,X) / governs_acyclicity
result: counterexample; cycle = [C2,C13,C4,C2]
```
A minimal portable receipt shape is:
```
{ query_id: "governs-acyclicity", scope: "typed-corpus", engine: "Cedar|Datalog candidate", result: "counterexample", witness: {cycle:["C2","C13","C4","C2"]}, claim: "bounded/relation-check", status: "candidate-non-authoritative", source_refs:["fol-constitution-validation-complement-synthesis.md"] }
```
This is exactly a property unary table-walk cannot state. For a concrete richer fixture, `order-fulfillment.formal-fixture.json` is the runnable TypeScript-first input with operations, typed edges, facts, trace, and declared Alloy/TLA expectations; its Alloy/TLA sketches remain unvalidated.

## typed negatives
1. **Cross-edge cycle disguised as local validity:** the C2→C13→C4→C2 graph passes all unary kind/location checks but must fail `governs` acyclicity with the cycle witness above.
2. **Endpoint-signature mismatch:** `orchestrates` currently owns `Workflow -> Operation[]`; a `Saga -> Operation` edge in the fixture is a known residue and must be rejected or explicitly marked as a typed exception, not silently normalized. (Do not mutate relationship authority.)
3. **Solver overreach:** routing identity/field-existence/edge-signature to FOL/SMT/Lean is a typed-negative architecture test; table-walk dominates and solver use is a collapse/reclassification error.
4. **Temporal/static confusion:** asking Alloy static graph check to prove retries/liveness or asking TLA to fill missing static edge signatures is wrong-formalism negative.
5. **Proof overclaim:** treating a TLC finite result or Alloy bounded no-counterexample as unbounded proof is invalid; receipt must say bounded and include scope/state-space.
6. **Freshness/behavior confusion:** DCB/hash/rerun receipts establish freshness/acceptance of a fact, not behavioral proof; stale waiver in fixture is an explicit negative for `FreshnessSafety` until semantic repair.

## obligation classification
| Obligation class | Preferred layer/formalism | Output | Claim limit |
|---|---|---|---|
| Node identity, required fields, typedness | `.schema.yml` + table walk | deterministic pass/fail + field diagnostics | shape only |
| Edge endpoint signature/cardinality | schema/table walk (`validate-relationships.ts` owned) | edge-local diagnostics | shape only |
| Rule cell returns Boolean (P5) | declarative `formal_return_type: boolean`; tiny internal parser only if needed | return-sort verdict | no satisfiability/meaning |
| Per-rule `r ⊨ rule` | existing Lean `AgentPermissionKernel`/decider | trusted satisfaction result | relabel owned; do not rebuild as FOL |
| Cross-rule common state, contradiction, reachability/cycles | Cedar/Datalog/FOL Row-2 complement (Cedar preferred; Datalog blueprint) | query result + witness/unsat core/cycle | bounded/decidable relation claim; no Row-3 meaning |
| Finite typed-record constraints where encoding stable | SMT candidate/private adapter only | sat/unsat + model/counter-witness | not public default; encoding chooses axes; no absolute non-thinness |
| Static graph completeness/counterexamples | Alloy bounded model | satisfying instance or counterexample; scope | bounded evidence, not proof |
| Temporal safety/failure/compensation/retry/freshness | TLA+/PlusCal + TLC | invariant violation trace or finite pass with state-space | finite model result; not unbounded proof |
| Semantic satisfiability/purity/non-thinness | private engine/Lean categorical residue; not public table walk | engine/proof artifact or human review | FOL blind for Row 3; absolute non-thinness remains review frontier |
| Fact freshness/acceptance | DCB/hash/rerun | accepted/rejected stale/current receipt | not behavior proof |

## boundary matrix
- Public/canonical contract: typed YAML/schema records, table-walk validators, explicit relation signatures; generated tests/receipts are derived and non-authoritative.
- Cross-graph private complement: Cedar/Datalog/FOL relation queries for Row 2; must expose query, scope, witness/counterexample, and freshness markers. No engine is wired today.
- SMT: do not make it the universal path; only a candidate adapter over stable finite encodings/private engine. It cannot pick semantic axes or establish absolute non-thinness.
- Alloy: promotion-candidate static graph lane, scoped; current syntax/check unvalidated.
- TLA/TLC: promotion-candidate temporal lane, scoped; current syntax/check unvalidated.
- Lean: already-owned Row-1 satisfaction/decidability and Row-3 boundary proofs; no per-instance validator. Cited Lean assets are not `lake build`-verified in the finding.
- DCB: freshness/acceptance wrapper only; preserve stale/current markers and never treat as behavioral proof.

## residue
1. No FOL/Cedar/Datalog cross-graph engine is wired into domainspec-v2; adapter and receipt contract remain net-new work.
2. Alloy and TLA examples/fixtures have declared expectations but are not syntax/model-checked; TypeScript extractor-to-model contract is absent.
3. `orchestrates` Saga-vs-Workflow signature mismatch remains open; do not silently repair.
4. A1–A6 axiom encoding and non-vacuous derivation/collapse test are unbuilt; absolute non-thinness stays Row-3/Lean/review.
5. SMT adapter/query families are intended candidate only; schema field stability and query ownership must precede implementation.
6. Keep `Inventory` as candidate read-model (not authority) and classify every receipt as bounded/proof/freshness evidence explicitly.
7. Future framework should route obligations by class, with typed negatives that prove wrong-formalism use is rejected rather than accepted.

## Agent 3 — Gödel, Kurt

## findings
1. The graph has a stable three-level decomposition: node alphabet (each concept owns one kind), typed edge-law (allowed endpoint pairs), and composability realization (code/reference behavior). `2026-07-01-composability-edges-taxonomy-synthesis.md:31-34,78-96,98-115` states this explicitly. Root `definitions/relationships/relationships.yml` is machine authority; loader accepts JSON-compatible YAML, filters deprecated/deferred, and enforces `signature_count` (`impl/tools/lib/relationship-signatures.ts:85-143`). Root currently reports 30 active signatures (`relationships.yml:17-18`; `relationships.md:17-27`), while the older synthesis says 29; treat 29 as historical/read-model drift.
2. Candidate generic edge record should preserve source-vs-generated boundaries:
```json
{
  "edge_id":"feature.edge.rule-enforces-operation",
  "predicate":"enforces",
  "from":{"node_id":"feature.Rule","kind":"Rule","feature_id":"feature"},
  "to":{"node_id":"feature.Operation","kind":"Operation","feature_id":"feature"},
  "scope":"same-feature",
  "evidence":{"source_ref":"SPEC.md#Feature Concept Graph","composition":"operation_checks_rule_before_mutation"},
  "status":"authored"
}
```
Use `signature` as `{predicate, source_types|source_type, target_types|target_type, multiplicity, feature_scope, validation_obligations, composition, status}`. This mirrors root signatures (`relationships.yml:20-33,84-97,148-161,212-225`) and fixture edge shape (`formal-saga-fixture.schema.json:145-156`), while generated node sources currently use `{edge_id,type,to}` (`impl/spec/features/ui-profile-create-player/nodes/*.json`) and generated SPEC uses `{Edge,From,Type,To}` (`generated/SPEC.md:28-53`).
3. Endpoint signature families: backend `Entity->Operation` performs; `Operation->Event` produces; `Operation->Entity` produces-for (cross-feature); `Event->Operation` triggers-cross; `Rule->Operation` enforces; `Calculation->Operation` calculates; `Event->State Machine` transitions; `Interface->{Operation,Query}` exposes; `Workflow->Operation[]` ordered orchestrates; `Policy->{Operation,Calculation}` applies; `Mapping->{Entity,Interface}` maps; `Entity->Value Object` contains; `{Query,Calculation,Operation}->Entity` queries; `Entity->Event` emits; `Entity->Entity` owns or belongs-to. Root lines: `relationships.yml:20-273`; UI/cross-layer signatures are at `relationships.md:65-87`.
4. Graph invariants to validate before solver escalation:
   - every node ID is unique and has exactly one declared kind (taxonomy single-owner invariant; synthesis `:36-49`);
   - every authored edge ID is unique, endpoints exist, endpoint kinds match exactly one active signature, and source/target feature scope obeys `same-feature|cross-feature|ui|ui-backend`;
   - edge multiplicity (`one_to_many`, `many_to_one`, `many_to_many`, ordered) is represented and checked, not inferred from prose;
   - generated inverse `owned-by` is not authored; `owns` and `belongs-to` are semantically distinct (root `relationships.md:89-98`, yml `:244-273`);
   - event causality is typed: Operation produces Event, Entity emits Event; Operation emits is invalid (`relationships.md:100-106`);
   - composition is a separate realization obligation: target-calls-source for enforces/calculates/applies, source-calls-target for exposes/mutates/fetches/orchestrates (`check-code-tag-composability.ts:45-117`), with unsupported active predicates reported as coverage gaps, not silently considered proven;
   - graph-level derived checks should detect dangling endpoints, duplicate edges, forbidden reverse/cross labels, orphan workflow operations, and (where declared) ordered workflow paths/acyclicity.
5. Causal composition/removal: removal is material only when it changes one of D18/D20-D25 tracked properties (reject/allow, derivation, projection, composition path, owner route, generated artifact), as `relationships.md:9-12,29-42` requires. Examples: remove `enforces` => operation call path/invalid-input rejection changes; remove `produces` => event publication/derivation changes; remove `triggers-cross` => downstream activation path disappears; remove `transitions` => event no longer advances lifecycle; remove `owns` => lifecycle/custody owner route changes. Removing only generated `owned-by` changes reverse navigation, so it remains generated. A generic engine should expose a removal probe `{graph_without_edge, changed_properties[]}` and reject an edge promotion when `changed_properties=[]`.
6. Current runnable witness: `impl/spec/__fixtures__/relationships/valid/SPEC.md:3-26` has 10 typed concepts and 6 valid edges (enforces, produces, emits, orchestrates, owns, belongs-to). I ran `(cd projects/domainspec-v2/impl && npx tsx tools/validate-relationships.ts --features-root spec/__fixtures__/relationships/valid --schema-dir spec/meta-types --relationships ../definitions/relationships/relationships.yml)`; result `validate-relationships: PASS (1 specs checked, edgesChecked=6, canonicalSignatures=30)`. A second generated witness is `impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/expected/SPEC.md:5-22` with Rule->Operation, Entity->Operation, Operation->Event.
7. Formal promotion boundary: the Alloy/TLA fixture has a typed `edges` array (`formal-saga-fixture.schema.json:70-72,145-156`), participant/operation/policy/state-machine nodes, trace, facts, and model expectations. Existing Alloy sketch is static bounded graph checking for missing compensation / typed graph counterexamples (`alloy-tla-modeling/TOWER.md:17-21,42-52`; `examples/OrderFulfillmentSaga.alloy`); existing TLA sketch is state/trace behavior, safety, compensation, and freshness (`TOWER.md:54-65`; `examples/OrderFulfillmentSaga.tla`). Fixture expectations explicitly separate Alloy sat/unsat/no-counterexample and TLA invariants plus freshness residue (`order-fulfillment.formal-fixture.json:251-271`). Neither sketch is proof: tower says Alloy/TLA and TypeScript are bounded/evidence surfaces, not complete proof (`TOWER.md:7-21,85-92`; `BRIDGE-DECISIONS.md:7-15`).
8. Current checker is not full graph/composability coverage. Source has call semantics only for `enforces`, `calculates`, `applies`, `exposes`, `mutates`, `fetches`, `orchestrates` (`check-code-tag-composability.ts:45-117`); dynamic rule construction marks active signatures without semantics as unsupported (`:431-474`). Historical synthesis reports 9/29 tool-enforced and 4 “not yet” (`2026-07-01...:89-96`), but this is stale relative to current source and includes deprecated `enforces-cross`; do not claim all edges have code-level realization.

## source_refs
- `projects/domainspec-v2/definitions/relationships/relationships.yml:17-18,20-273,494-537` (machine relationship authority, endpoint/multiplicity/scope/validation/composition, generated/deferred/deprecated status).
- `projects/domainspec-v2/definitions/relationships/relationships.md:1-42,44-106` (authority boundary, non-collapse/removal test, signatures, owns-vs-belongs-to, event endpoint policy).
- `projects/domainspec-v2/impl/tools/lib/relationship-signatures.ts:4-15,85-143` (signature/loader schema and active/deprecated filtering).
- `projects/domainspec-v2/impl/tools/validate-relationships.ts:1-80` (table-walk validator and PASS/violation contract).
- `projects/domainspec-v2/impl/governance/tags/tools/check-code-tag-composability.ts:22-117,431-474` (call directions/codes and unsupported-active coverage behavior).
- `projects/domainspec-v2/research/2026-07-01-composability-edges-taxonomy-synthesis.md:31-34,55-76,78-126,137-150` (node/edge/realization decomposition, historical coverage gaps and residue).
- `projects/domainspec-v2/impl/spec/__fixtures__/relationships/valid/SPEC.md:3-26` (valid six-edge graph witness); bad fixtures `bad-operation-enforces-value-object/SPEC.md:3-14`, `bad-reversed-enforces/SPEC.md:3-14`, `bad-operation-emits-event/SPEC.md:3-14`, `bad-queries-target/SPEC.md:3-14`, `bad-saga-orchestrates-operation/SPEC.md:3-14`, `bad-generated-owned-by/SPEC.md:3-14` (typed negatives).
- `projects/domainspec-v2/research/alloy-tla-modeling/fixtures/formal-saga-fixture.schema.json:7-20,54-94,145-223` and `fixtures/order-fulfillment.formal-fixture.json:251-271` (nodes/edges/facts/trace/formal expectation and residue shape).
- `projects/domainspec-v2/research/alloy-tla-modeling/TOWER.md:7-21,38-65,85-92`, `BRIDGE-DECISIONS.md:7-15,17-34`, `CLAIM-LEDGER.md:15-20,31-38` (Alloy static vs TLA temporal boundary, no-proof posture, open residue).

## one runnable node+edge witness
```text
# Existing valid fixture, read-only command:
cd projects/domainspec-v2/impl
npx tsx tools/validate-relationships.ts \
  --features-root spec/__fixtures__/relationships/valid \
  --schema-dir spec/meta-types \
  --relationships ../definitions/relationships/relationships.yml
# PASS: 1 specs checked, edgesChecked=6, canonicalSignatures=30
```
Minimal edge triple in that witness: `MaxAmountRule (Rule) --[enforces]--> ProcessPayment (Operation)`. For a generated machine-source witness use `impl/spec/features/ui-profile-create-player/nodes/create-player-operation.json` + `can-create-player.json`: authored `enforces`/`produces`/`produces-for` connections with typed node records.

## typed negative graph witnesses
- `ProcessPayment(Operation) --[enforces]--> Money(Value Object)` => reject `unconstructible-edge` (bad-operation-enforces-value-object).
- `ProcessPayment(Operation) --[enforces]--> MaxAmountRule(Rule)` => reject reversed endpoint signature (bad-reversed-enforces).
- `ProcessPayment(Operation) --[emits]--> PaymentCompleted(Event)` => reject; only Entity emits Event, Operation produces Event (bad-operation-emits-event).
- `DealSplitCalculation(Calculation) --[queries]--> RetryPolicy(Policy)` => reject target must be Entity (bad-queries-target).
- `LegacyTransfer(Saga) --[orchestrates]--> ReserveFunds(Operation)` => reject current Workflow-only signature; preserve as explicit Saga/Workflow residue (bad-saga-orchestrates-operation; formal fixture residue).
- `Copy(Entity) --[owned-by]--> Library(Entity)` => reject noncanonical generated inverse (bad-generated-owned-by).
- `PaymentStatus(State Machine) --[enforces]--> ProcessPayment(Operation)` => reject wrong source kind (bad-state-machine-enforces-operation).
- `Rule --[enforces-cross]--> Operation` => reject deprecated verb; scope is metadata on `enforces` (composability test and yml deprecated list).
- Proposed generic negatives: dangling `to` ID; duplicate `edge_id`; cross-feature edge where signature only allows same-feature; two targets on `one_to_one`; edge removal with empty `changed_properties`; workflow ordered edge with missing position; authored edge whose target is only a generated view.

## obligation classification
| Obligation | Default lane | Evidence / escalation |
|---|---|---|
| Parse node/edge records, required fields, unique IDs, exactly-one node kind | structural YAML/JSON/schema + table walk | deterministic validator; no solver |
| Endpoint signature, active/deprecated/deferred/generated status, feature scope, multiplicity, concept existence | structural graph validator | deterministic reject/allow; root signatures are authority |
| Schema `source_of`/`target_of` participation and generated SPEC projection parity | structural validator + generated digest/receipt | deterministic; generated files are not authority |
| Code-call realization (`enforces`, `calculates`, `applies`, `exposes`, `mutates`, `fetches`, `orchestrates`) | code-tag composability checker | deterministic AST/tag evidence; currently partial coverage |
| Cross-feature/rule consistency, contradictory paths, ownership/event/trigger closure, graph acyclicity/counterexamples | FOL/Cedar/Datalog for finite relations; Alloy first for bounded static counterexample | solver receipt with model/scope; do not conflate with per-node schema checks |
| Temporal ordering, compensation, retries, state transitions, freshness acceptance | TLA+/PlusCal + TLC (bounded) | trace/state invariant receipt; no unbounded proof claim |
| Per-rule deterministic predicates | existing structural validator / owned checker; Lean only where already owned, not a new per-instance default | preserve owner; avoid solver escalation |
| Non-rerunnable waiver/provider facts and acceptance freshness | DCB/hash/rerun receipt | explicit read/current markers; DCB is wrapper, not behavior proof |

## residue
- Root machine authority says 30 active signatures; older composability synthesis says 29. Reconcile as read-model drift before any count-based claim.
- Root relationships intentionally only provide a typed graph fragment, not full category law; do not infer associativity/identity or universal path closure (`relationships.md:6-15`).
- `Saga -> Operation[]` remains an explicit open residue: current root says Workflow only; formal fixture records it at `order-fulfillment.formal-fixture.json:268-271`; do not widen until a separate owner decision.
- Most active edges have no code-call semantics in the current checker; coverage gaps are diagnostic, not proof of non-composability. Historical 9/29 and ~17 unpatterned numbers need remeasurement.
- Existing Alloy/TLA sketches are marked not run/validated; R1/R2/R4 in `CLAIM-LEDGER.md:31-38` remain open (syntax/tool run and extractor contract). No solver receipt should be claimed from sketches alone.
- Event payload/publisher composite and operation->Value Object remain deferred; `depends-on` remains deferred until a distinct removal/validation witness (`relationships.yml:513-524`).
- Pairwise evidence sentence (Church/Curry): graph/source-corpus findings must be compared against Church's node/constraint methodology and Curry's logic-fragment methodology; Church/Curry returns were not available in this lane, so this is a comparison requirement, not an asserted agreement.
