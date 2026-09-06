---
node_type: subagents-findings
is_session: false
dispatch_id: 2026-07-17-spec-ontology-node-layering
status: candidate
---

# DomainSpec ontology node layering findings

## Goal

Determine whether the proposed Validation Governance authority-envelope YAML should be a DomainSpec graph node, and identify the smallest sound route from that record to one graph that both an implementer agent and an interactive learning application can traverse.

## TL;DR

Yes, the proposed record is useful as a **candidate ontology node source**, but it is not a current `minted-node/v1` record, not presently a DS-D1 feature node, and not an admitted `Authority Envelope` kind. `Authority Envelope`, `Concept`, and `instantiates` are provisional labels from supporting precedent, not settled DomainSpec types or relations. The exact top-level YAML fails the current closed node schema. Its fields can be preserved now under `body`, but that proves only metadata carriage—not semantic typing, traversal, authority, or implementation meaning. [Agent 1](./research.md#agent-1---executable-graph-compatibility)

The settled architectural boundary is **one typed DomainSpec semantic graph with learner and navigation overlays generated from that graph's stable IDs**. The engine currently selects one admitted profile for one source set. A future composite ontology-learning profile is only one candidate and requires an owner decision after comparison with a narrower existing-profile/role solution. The first kind test must ask whether the existing DS-D1 `Workflow` formation can express the envelope without collapsing its independent status and ownership axes; a new local kind is considered only if that test fails. A separately authored ontology graph would create competing identity, status, edge, and provenance truths. [Agent 3](./research.md#agent-3---implementer-and-learning-map-boundary)

The modeled object and the thing it describes have independent status. The ontology envelope remains candidate; the represented DomainSpec v2 Validation governance kind remains ratified, with its own attestation state. Modeling a ratified subject through a candidate envelope neither promotes the envelope nor demotes the subject. [Agent 2](./research.md#agent-2---authority-envelope-semantics)

## Context

The example combines four concerns that the engine must not collapse:

1. a graph-node source envelope;
2. ontology classification and semantic relations;
3. local authority, ownership, challenge, and residue metadata;
4. implementer and learner traversal behavior.

Current `minted-node/v1` has a closed top-level contract: `schema_version`, `node_id`, `feature_id`, `kind`, `intent`, `body`, and `connections`. The compiler emits only the normalized identity, kind, intent, body, and compiled connections. Unknown top-level fields are therefore both schema-invalid and, without compiler changes, non-preserving. The direct probe recorded six missing required fields, an invalid node ID, and ten unexpected properties for the proposed shape. [Agent 1](./research.md#agent-1---executable-graph-compatibility)

DomainSpec has a relevant extension seam: the engine selects one explicit admitted profile for one source set, and that profile may admit kinds, body formations, relationship signatures, and endpoint pairs. The UI development profile proves the seam and its fail-closed selection behavior, but does not establish an ontology kind, a composite-profile requirement, or release admission. A narrower `Workflow` role/formation solution must be tested before a new local kind or broader composite ontology-learning profile is proposed. [Agent 1](./research.md#agent-1---executable-graph-compatibility) [Agent 3](./research.md#agent-3---implementer-and-learning-map-boundary)

Canonical operational meaning must remain in consumer-owned node sources together with admitted kind, formation, relationship, and profile authorities. Subject-authority Markdown documents remain owner-governed references; the present minted source manifest does not compile or digest those external authority documents. Consequently, a source reference can establish traceability for review, but must not be described as compiler-enforced authority or digest-bound proof. [Agent 1](./research.md#agent-1---executable-graph-compatibility)

## What the proposed record is

The record is best classified as a:

```text
candidate local ontology workflow envelope
  about -> DomainSpec v2 Validation governance
  owned by -> validation-governance for subject claims
  authority effect -> none until an appropriate local owner decision
```

`concept.authority_envelope` is CyberAlchemy modeling precedent, not a DomainSpec-admitted kind or relationship. `Authority Envelope`, `Concept`, and `instantiates` remain provisional vocabulary. DomainSpec must first test the existing DS-D1 `Workflow` formation and must localize any new node kind, formation, relation, and promotion behavior through its own owners. [Agent 2](./research.md#agent-2---authority-envelope-semantics)

The non-collapse rule is:

```text
candidate encoding of a ratified subject
!= candidate authority kind
!= executable implementation instruction
```

## Separate status axes

| Axis | Current state | Meaning | Must not imply |
|---|---|---|---|
| Ontology envelope lifecycle | candidate | The proposed encoding and ontology classification are under evaluation. | That `Authority Envelope` is admitted by DomainSpec. |
| Represented authority kind | ratified | Validation governance is an already ratified DomainSpec v2 authority kind. | That the ontology envelope is ratified. |
| Subject attestation | L1 integrity witnessed; external L2 actor attestation pending | This is evidence state about the represented authority kind. | Runtime correctness, implementation conformance, or ontology admission. |
| Evidence confidence | candidate local judgment | Confidence in evidence supporting the ontology entry. | Commitment, authority, or lifecycle transition. |
| Commitment confidence | candidate local judgment | Confidence that an owner will retain or promote the entry. | Evidence quality or present admission. |
| Implementability | unproven | No node-to-pattern and edge-to-composition contract has yet been witnessed for this ontology node. | That rich governance metadata tells an agent what code to write. |

## Separate ownership axes

| Owned concern | Owner route | Boundary |
|---|---|---|
| Truth and lifecycle of the represented Validation governance kind | `validation-governance` | May decide subject-authority claims and attestation interpretation; does not silently admit a graph kind. |
| Ontology entry content and candidate classification | `projects/domainspec-v2/ontology/` owner | May curate the candidate record and its provenance; has no authority effect by itself. |
| Minted node/profile/relationship formation | `projects/domainspec-v2/definitions/minted-project/` owner | Must admit any new kind, body formation, edge signature, and endpoint pair. |
| Compiler, resolver, source manifest, and cross-feature behavior | `projects/domainspec-v2/impl/tools/minted-project/` owner | Must witness deterministic preservation and traversal; cannot infer authority from Markdown references. |
| Learner and navigation projections | `interactive-ontology-learning-map` consumer owner | May generate purpose-specific order and presentation from stable semantic IDs; must not alter semantic graph bytes. |
| Promotion or release admission | DomainSpec v2 local decision owner | Must be explicit and local; CyberAlchemy precedent cannot promote a DomainSpec artifact. |

## Field disposition

| Field | Disposition | Why | Owner route |
|---|---|---|---|
| `node_id` | Normalize to the current one-dot minted ID grammar for any executable witness. | `dsv2.ontology.validation-governance` is not a valid current minted ID. | `projects/domainspec-v2/impl/spec/minted-project/node.schema.json` owner |
| `instantiates` | Treat the name and semantics as provisional body metadata until a relationship owner selects and separately admits a local relation; only then emit it as a source-owned connection. | Hidden pseudo-edges are not traversable and can diverge from real connections. | `projects/domainspec-v2/definitions/minted-project/` owner |
| `label` | Store in the selected role/kind's typed body; retain `intent` as the executable explanation. | It is not a current top-level engine field. | Role/kind formation owner |
| `local_authority_kind` | Split represented kind identity from owner-route identity. | `validation-governance` currently ambiguously names both. | `validation-governance` |
| `candidate_status` | Rename or type as envelope lifecycle status under whichever `Workflow` role or new local kind wins the fork. | It must not imply that the represented ratified kind is candidate. | Role/kind formation owner |
| `owner_route` | Use the stable owner token; add a separate owner/source reference if admitted. | A Markdown anchor is a reference, not the owner-route token. | `validation-governance` plus selected role/kind formation owner |
| `source_refs` | Preserve as typed provenance references. | External referenced files are not presently included in the minted source digest. | Minted source-manifest owner |
| `confidence` | Preserve as candidate two-axis metadata only after local value/rationale formation is defined. | Current engine stores but does not interpret or transition it. | Role/kind formation owner |
| `challenge_contract` | Type as body metadata first under the selected role/kind; promote only separately admitted graph-worthy links to connections. | Current compiler does not execute challenge semantics. | Role/kind formation owner plus `validation-governance` |
| `contradiction_edges` | Materialize target nodes and admit a typed relationship before traversal. | The example target is not a materialized current node. | Relationship/profile owner |
| `validation_edges` | Rename file values to `validation_refs`; model a validator as a node only when a typed endpoint exists. | File paths are not graph endpoints and cited validators do not prove the envelope's truth. | Validation-governance plus relationship/profile owner |
| `resolution_gate` | Use a specific decision/gate record when claiming a transition. | A decisions directory is a route pointer, not a verdict. | DomainSpec v2 local decision owner |
| `residue` | Separate envelope residue from represented-subject attestation residue under the selected role/kind. | Conflation would transfer status across axes. | Role/kind formation owner plus `validation-governance` |
| `forbidden_collapse` | Require as typed, nonempty body statements for whichever candidate role/kind is tested. | Storage alone does not make an implementer enforce the boundary. | Role/kind formation owner; implementer-contract owner for execution |

## Architecture decision

Adopt only the graph/view invariant as the target:

```text
consumer-owned node files
  -> one engine-selected admitted profile for one source set
  -> one compiled semantic graph
  -> generated semantic / learner / navigation views keyed by stable IDs
```

The graph contains only admitted semantic connections. Learner order, presentation, and navigation are generated overlays, never semantic edges. An implementer selects executable roots and imports bounded context; a learner may start from the same stable semantic IDs. `Authority Envelope`, `Concept`, and `instantiates` remain provisional examples and are not prerequisites of this invariant. [Agent 3](./research.md#agent-3---implementer-and-learning-map-boundary)

No composite ontology-learning profile is adopted here. The engine currently selects one admitted profile for one source set. The next owner decision must compare these candidates in order:

1. **Narrow existing-role candidate:** test whether the existing DS-D1 `Workflow` formation, with the smallest profile/role adaptation, expresses the record's independent status, owner, challenge, confidence, and residue axes without permissive-body evasion or semantic collapse.
2. **New local-kind candidate:** only if the `Workflow` gate fails, define and test a new locally named kind with a closed formation. `Authority Envelope` is a provisional working label, not the automatic name.
3. **Composite ontology-learning profile candidate:** consider only if the winning role/kind and minimum relation set cannot be expressed through a narrower single-profile solution without changing unrelated type semantics.

Decision criterion: choose the narrowest candidate that passes the closed-formation, non-collapse, bounded-traversal, and deterministic-compilation gates. Decision owner route: `projects/domainspec-v2/definitions/minted-project/` owner, with DomainSpec v2 local decision owner for admission and `projects/domainspec-v2/impl/tools/minted-project/` owner for compiler feasibility.

Reject as authority-bearing substrates:

- a flat universal graph, because edge families become semantically indistinguishable;
- an independently authored ontology graph, because identity, status, relations, and provenance can drift;
- pseudo-edges hidden only in `body`, because implementers cannot traverse them;
- undigested sidecars treated as authoritative inputs, because current resolution and source-manifest behavior does not bind them.

This is one semantic graph with multiple views, not two graphs with separate truth.

## Verdict matrix

| candidate | owner | witnessed | sound | verdict |
|---|---|---|---|---|
| Original top-level YAML compilation as `minted-node/v1` | Minted node schema/compiler owner | Yes: direct rejection | No | Preserve as the Phase 0 negative fixture |
| Normalized edgeless node using the existing DS-D1 `Workflow` formation/role | Workflow formation and selected-profile owner | No | Conditional on closed formation and non-collapse | Test first in Phase 1A |
| Normalized edgeless node using a new local kind | Local kind/formation owner | No | Conditional, only if `Workflow` fails | Gate behind Phase 1A; do not assume the provisional `Authority Envelope` name |
| Composite ontology-learning profile | Minted profile owner and local decision owner | No | Unresolved | Compare only after narrower role/profile candidates |
| Provisional classification edge such as `instantiates` | Relationship/profile owner | No | Unresolved | Name, admit, compile, and traverse separately in Phase 2 |
| File paths represented as graph edges | Validation-governance and relationship owner | Yes: paths exist, endpoints do not | No | Keep as references |
| Independently authored ontology graph beside the minted graph | DomainSpec v2 architecture owner | Not required | No: duplicate truth | Reject |
| Bounded traversal over one separately admitted semantic edge | Traversal and relationship owners | No | Conditional | Phase 2 verdict; compilation alone cannot pass it |
| Active node/edge binding drives implementation output | Implementer-contract owner | No | Conditional | Phase 3 verdict; traversal alone cannot pass it |
| One semantic graph plus generated learner/navigation overlays | Profile, compiler, and consumer-view owners | Partly: extension and traversal precedents exist | Conditional on projection integrity | Phase 4 verdict |

## What works now

1. **Body carriage.** A valid admitted node can carry additional profile metadata inside `body`, and the compiler preserves the body in `graph.json`. Owner route: minted node/compiler owner.
2. **Single-profile extension seam.** The engine can select one explicit profile for one source set; that profile can add kinds, formations, and relationship signatures while remaining development-only and fail-closed. This does not decide between an existing `Workflow` role, a new local kind, or a broader composite profile. Owner route: `projects/domainspec-v2/definitions/minted-project/` owner.
3. **Source-owned same-feature connections.** Current nodes can emit admitted connections to nodes in the same feature. Owner route: minted compiler owner.
4. **Purpose-specific traversal precedent.** The UI builder demonstrates root selection, directed executable reachability, undirected learning connectivity, and joining representation metadata. Owner route: UI profile implementation owner.

These witnesses establish mechanism, not admission of `Authority Envelope`, `Concept`, `instantiates`, ontology semantics, trusted `source_refs`, or implementation conformance. [Agent 1](./research.md#agent-1---executable-graph-compatibility)

## Owner-routed profile, role, kind, and relation decisions

Recommendation 1 — Owner route: DS-D1 `Workflow` formation owner plus `projects/domainspec-v2/definitions/minted-project/` owner. Test the normalized, edgeless record as a narrowly role-qualified `Workflow` first. Passing requires a closed formation that preserves separate envelope/subject status and owner axes; merely accepting an arbitrary body is not a semantic pass.

Recommendation 2 — Owner route: DomainSpec v2 local kind/formation owner. If and only if Recommendation 1 fails its stated criteria, propose a new local kind and closed formation. Treat `Authority Envelope` only as an input name candidate, not an admitted or preselected kind.

Recommendation 3 — Owner route: `projects/domainspec-v2/definitions/minted-project/` owner plus DomainSpec v2 local decision owner. Compare the winning narrow role/kind solution against a composite ontology-learning profile. Select a composite only if the narrower solution cannot admit the minimum formations and relation without changing unrelated semantics; either development candidate must declare no release admission.

Recommendation 4 — Owner route: selected role/kind formation owner plus `validation-governance`. Type the body so that represented authority identity, owner route, source references, envelope status, subject status, confidence, challenge contract, envelope residue, subject residue, and forbidden-collapse statements cannot be conflated.

Recommendation 5 — Owner route: relationship/profile owner. After an edgeless node compiles soundly, separately name and admit only the one relation required by the bounded traversal witness. `instantiates`, its endpoint role/kind, and `Concept` are all provisional. Do not admit path-valued `validates` or dangling `contradicts` relations.

Recommendation 6 — Owner route: minted compiler owner. Keep current source-owned `connections` through the same-feature witnesses. Do not introduce independent connection files until the resolver, source digest, schemas, and build receipt bind them.

Recommendation 7 — Owner route: implementer-contract owner. Require an explicit active node binding and active edge-composition binding before saying the graph drives implementation. Compilation and traversal are insufficient evidence.

Recommendation 8 — Owner route: projection compiler owner plus interactive-ontology-learning-map consumer owner. Generate learner/navigation overlays only after canonical semantic bytes and hash behavior are specified; reject stale, unknown-ID, or semantic-mutating overlays.

## Required and optional gaps

| Gap | Required for | Classification | Owner route | Acceptance condition |
|---|---|---|---|---|
| `Workflow`-versus-new-local-kind fork | Any semantically sound envelope node | Required now | Workflow and local kind/formation owners | `Workflow` is tested first against closed-formation and non-collapse criteria; a new kind is considered only on recorded failure. |
| Narrow profile/role versus composite-profile decision | Selecting one profile for one source set | Required after kind fork | Minted profile owner plus local decision owner | The narrow solution is preferred unless it cannot admit the winning kind/role and minimum relation without unrelated semantic change. |
| Edgeless same-feature compile | Formation proof independent of relations | Required now | Selected role/kind formation and fixture owners | Normalized node validates and compiles deterministically with `connections: []`. |
| Separately named and admitted one-edge contract | Traversable classification | Required after edgeless compile | Relationship/profile owner | A locally selected relation and endpoint role/kind compile without relying on provisional `instantiates` or `Concept`. |
| Explicit bounded traversal contract | Traversal proof independent of compilation | Required before graph-walk claims | Traversal owner | Root, allowlists, direction, hop bound, node bound, deterministic ordering, and negative fixtures all pass. |
| External source-reference digest binding | Claims that authority refs are build-bound | Required before such claims | Resolver/source-manifest owner | Authority refs and revisions appear in a verified source manifest or equivalent receipt. |
| Active node-to-pattern and edge-to-composition contracts | Claim that the graph drives implementation | Required before implementation claim | Implementer-contract owner | Deterministic output and node/edge removal tests prove causal implementation effect. |
| Semantic/learner/navigation projection contracts | Interactive learning product | Required before product reliance | Projection compiler plus consumer owner | Canonical semantic bytes/hash, overlay binding, invariance/change, stale, unknown-ID, and mutation rejection tests pass. |
| Cross-feature edges | Connected multi-feature map | Required last | Minted compiler/profile owner | All same-feature gates pass first; then one authorized cross-feature edge compiles and traverses with endpoint ownership and digest coverage. |
| Independent connection files | Alternative authoring ergonomics | Optional | Feature schema/resolver owner | Only adopt if fully schema-bound, digested, and compiled; otherwise retain source-owned connections. |
| New top-level node envelope (`minted-node/v2`) | Preserving the exact YAML shape | Optional and not recommended initially | Minted schema/compiler owner | Versioned migration proves need that typed `body` cannot meet. |
| First-class validator/evidence nodes | Traversing validation provenance | Optional after minimal witness | Ontology and relationship owners | Endpoints have admitted kinds and relations without implying truth from link existence. |

## Falsifiable phased witness

Each phase has its own verdict. A later pass cannot retroactively turn an earlier compile into traversal evidence or a traversal into implementation evidence. `source_refs` remain untrusted external references throughout these phases until the resolver/source-manifest owner supplies a separate digest-binding witness.

### Phase 0 — Original-shape negative fixture

Owner route: minted node schema/compiler test owner.

Run the original top-level YAML unchanged against `minted-node/v1`. Expected result: rejection for the missing required envelope fields, invalid node ID, and unexpected top-level properties already observed by Agent 1. The gate fails if the fixture is accepted without an explicit schema-version change, or if the test does not assert the rejection categories. Passing proves only that the original YAML is not a current node source.

### Phase 1 — Kind fork and edgeless same-feature compile

Owner route: DS-D1 `Workflow` formation owner, selected-profile owner, and local kind/formation owner if the fallback is reached.

Phase 1A normalizes the record into `minted-node/v1`, uses `connections: []`, and tests the existing DS-D1 `Workflow` formation through the narrowest eligible profile/role route. It passes only if a closed formation validates all required fields, keeps envelope and subject statuses separate, keeps subject owner and encoding owner separate, and does not obtain acceptance from an unrelated permissive body.

If Phase 1A fails, record the exact formation mismatch. Phase 1B may then propose a newly named local kind—without assuming `Authority Envelope`—and compile the same edgeless node under a closed development formation. The compile must be reproducible from a clean checkout with identical normalized bytes/hash. A Phase 1 pass proves formation and compilation only; it does not prove any relation, traversal, authority effect, or implementation behavior.

### Phase 2 — Separately admitted one-edge bounded traversal

Owner route: relationship/profile owner plus traversal owner.

Only after Phase 1, materialize a second same-feature endpoint using a locally selected admitted role/kind. Separately select and admit one local relation; `instantiates` and a `Concept` endpoint remain provisional candidates, not assumptions. Compile exactly one source-owned edge, then traverse with an explicit contract:

- root: the Phase 1 node's stable ID;
- node-role/kind allowlist: exactly the two locally admitted endpoint roles/kinds;
- relation allowlist: exactly the one locally admitted relation;
- direction: outgoing;
- maximum hops: 1;
- maximum returned nodes: 2;
- ordering: deterministic by the selected stable ordering rule.

The positive fixture must return the same ordered IDs and traversal digest across repeated clean runs. Negative fixtures must reject an unknown root, dangling target, unallowlisted relation, wrong direction, disallowed endpoint role/kind, hop overflow, node-bound overflow, and nondeterministic ordering. Passing proves bounded traversal only, not implementation effect.

### Phase 3 — Active implementation binding

Owner route: implementer-contract owner.

Add an explicit active node-to-pattern binding and active edge-to-composition binding to the Phase 2 fixture. The implementer must emit a deterministic implementation-obligation output that identifies the active node, active edge, selected pattern, composition rule, source semantic digest, and executable validation command/result contract.

Run causal removal tests: removing the active edge binding must remove the composed obligation; removing the active node binding must remove its implementation output; changing context-only envelope metadata must not independently emit code. The gate fails if output survives removal, if metadata without an active binding emits implementation, or if repeated clean runs differ. Only this phase can pass the claim that the graph drives implementation.

### Phase 4 — Projection integrity

Owner route: projection compiler owner plus interactive-ontology-learning-map consumer owner.

Define canonical semantic serialization bytes and their hash before generating overlays. Every learner/navigation overlay must bind that exact semantic hash and reference only stable semantic IDs. Required tests are:

- **invariance:** learner-only content changes leave canonical semantic bytes and hash unchanged;
- **semantic change:** changing a semantic node or edge changes the canonical semantic hash;
- **stale rejection:** an overlay bound to the pre-change hash is rejected after semantic change;
- **unknown-ID rejection:** an overlay that references an absent semantic ID is rejected;
- **mutation rejection:** an overlay that attempts to add, delete, or rewrite semantic nodes, fields, or edges is rejected.

Passing proves projection integrity only. It does not establish cross-feature behavior or implementation effect beyond Phase 3's separate result.

### Phase 5 — Cross-feature edge last

Owner route: minted compiler/profile owner plus both endpoint feature owners.

Only after Phases 0–4 pass, move the two already witnessed endpoints into separately owned features and admit exactly one cross-feature edge with explicit endpoint ownership, conflict rules, source-manifest coverage, and digest coverage. Re-run the Phase 2 bounded traversal and the Phase 3 binding-removal tests. Reject an unauthorized endpoint owner, unbound source, stale digest, or cross-feature edge not explicitly admitted by the selected profile. Passing proves only the witnessed cross-feature case; it does not generalize to arbitrary repository-wide joins.

## Reviewer convergence

The independent reviewer round converged on the boundary and architecture findings after applying these non-collapse corrections:

- `Authority Envelope` is only a provisional kind label, not an admitted or selected DomainSpec kind;
- subject-authority documents are owner-governed references, not presently compiled or digest-bound inputs;
- canonical operational meaning remains with consumer-owned node sources and admitted type, relationship, formation, and profile authorities.

Convergence does **not** settle the local profile, role/kind, endpoint, or relation choices. Whether `Workflow` suffices, whether a new local kind is required, whether a composite profile is justified, and what relation replaces or localizes provisional `instantiates` all remain unresolved and owner-routed through the phased gates above.

## Dispatch closeout

Verified parent completion state:

- audit verdict: `APPROVE` after one bounded writer repair
- exit reason: `resolved`
- agents spawned: 11 total — 3 explorers, 1 synthesizer, 3 skeptics, 1 writer, 1 auditor, and 2 check-tension helpers
- reviewer loops used: 2
- dispatch ledger close row: appended exactly once for `2026-07-17-spec-ontology-node-layering`
- inventory backfill: `.arcanum/inventory/entries/domainspec-v2-spec-ontology-node-layering-dispatch-closeout-synthesis.md`

This slot records dispatch execution only; it must not alter the research verdict or promote the candidate architecture.

## Connections

- derives-from -> ./research.md

## Open Questions

1. **Can the existing DS-D1 `Workflow` formation express this record with closed validation and without collapsing envelope status, subject status, owner identity, challenge, confidence, or residue?** Owner route: DS-D1 `Workflow` formation owner plus selected-profile owner.
2. **If `Workflow` fails the Phase 1A criteria, what local name and closed formation should the fallback kind use?** Owner route: DomainSpec v2 local kind/formation owner; `Authority Envelope` remains only one provisional input label.
3. **Can the winning role/kind and minimum relation fit a narrower single-profile solution, or is a composite ontology-learning profile justified by a recorded formation/signature mismatch?** Owner route: `projects/domainspec-v2/definitions/minted-project/` owner plus DomainSpec v2 local decision owner.
4. **What locally admitted relation and endpoint role/kind should replace or localize provisional `instantiates` and `Concept`?** Owner route: DomainSpec v2 relationship/profile owner.
5. **What stable identifier names Validation governance independently from the `validation-governance` owner-route token?** Owner route: `validation-governance` plus DomainSpec v2 ontology owner.
6. **Which revision-pinning and digest mechanism will make `source_refs` trusted inputs without compiling Markdown prose as graph semantics?** Owner route: minted resolver/source-manifest owner.
7. **Which stable ordering and digest rule defines deterministic bounded traversal?** Owner route: DomainSpec v2 traversal owner.
8. **What endpoint-ownership and conflict rules admit the final cross-feature witness?** Owner route: minted compiler/profile owner with both endpoint feature owners participating.
9. **What is the minimal active node-to-pattern and edge-to-composition vocabulary whose removal changes implementation output?** Owner route: DomainSpec v2 implementer-contract owner.
10. **Which fields belong in canonical semantic bytes versus generated learner/navigation projections?** Owner route: selected role/kind formation owner for semantics; interactive-ontology-learning-map consumer owner for projections.
