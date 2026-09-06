---
node_type: subagents-research
is_session: false
---

## Agent 1 - executable graph compatibility

## Executable-graph verdict

The proposed YAML is a good ontology source shape, but it is not a valid `minted-node/v1` source. The mechanically coherent route is:

1. Keep one DomainSpec graph engine.
2. Add a development ontology profile.
3. Normalize the authority-envelope fields into the node’s typed `body`.
4. Represent traversable semantic links as ordinary source-owned `connections`.
5. Compile them into the existing `minted-graph/v1` read model.
6. Keep evidence paths and unresolved governance pressure as provenance/residue, not counterfeit graph edges.

A new profile is sufficient only if the rich fields live under `body`. Preserving the exact proposed top-level shape would require a new node schema and compiler changes, because the current compiler both rejects and discards unknown top-level fields.

### Direct mechanical probe

I ran the proposed shape through `projects/domainspec-v2/impl/tools/minted-project/schema-validator.ts` against `projects/domainspec-v2/impl/spec/minted-project/node.schema.json`.

It failed with:

- six missing required fields: `schema_version`, `feature_id`, `kind`, `intent`, `body`, `connections`;
- an invalid `node_id`;
- ten unexpected top-level properties.

I then placed the complete envelope under `body.authority_envelope` in an otherwise valid admitted `Mapping` node. The base node schema returned no violations. This proves metadata carriage, not semantic correctness: coercing Validation Governance into `Mapping` would be false classification.

The two live UI engine suites also pass: 12/12 tests in:

- `projects/domainspec-v2/impl/tools/tests/ui-profile-engine.test.ts`
- `projects/domainspec-v2/impl/tools/tests/ui-profile-graph-source.test.ts`

### Field-by-field compatibility

| Proposed field | Current compatibility | Required normalization or change |
|---|---|---|
| `node_id` | Field exists, value fails | `dsv2.ontology.validation-governance` violates the one-dot, Pascal-style terminal pattern. A valid example is `ontology.ValidationGovernance`. |
| `instantiates` | No top-level field; no admitted relationship | Encode as a `connections[]` edge only after `instantiates` receives a relationship signature and profile admission. Otherwise keep it as non-traversable body metadata. |
| `label` | No top-level field | Put in the formation body. `intent` remains the required executable node explanation. |
| `local_authority_kind` | No engine field | Formation-body attribute; compiler preserves it but currently assigns it no behavior. |
| `candidate_status` | No engine field | Formation-body attribute or profile-owned status. It must not imply admission. |
| `owner_route` | No engine field | Formation-body/provenance attribute. A file or section route is not a graph endpoint. |
| `source_refs` | Can be stored in `body`, but are not compiler provenance | Current resolver hashes only project, feature, and node files. Referenced authority files and fragment anchors are not included in the source-set digest. |
| `confidence` | Can be stored, not evaluated | Formation schema can type the two confidence dimensions. Current engine will preserve but not transition them. |
| `challenge_contract` | Can be stored, not executed | Needs a profile formation schema. Its nested “edge” arrays are not graph edges and are invisible to graph traversal. |
| `contradiction_edges` | Not graph edges as written | Promote only graph-worthy relations into `connections[]`; target IDs must be valid nodes in the same feature under the current compiler. |
| `validation_edges` | File paths cannot be graph endpoints | Rename to validation references unless validators become first-class nodes with an admitted relationship. |
| `residue` | Body storage works; UI precedent uses a sidecar | Prefer typed residue when the item is unresolved and must not enter the graph. Core compiler does not currently ingest residue sidecars. |
| `forbidden_collapse` | Body storage works | A formation validator can require nonempty statements, but enforcement by an implementer requires an explicit consumer contract. |

The source contract is closed by `additionalProperties: false` in `projects/domainspec-v2/impl/spec/minted-project/node.schema.json`. The generated contract is equally closed in `projects/domainspec-v2/impl/spec/minted-project/graph.schema.json`.

More importantly, `projects/domainspec-v2/impl/tools/minted-project/compiler.ts` constructs generated nodes using only:

- `node_id`
- `feature_id`
- `kind`
- `intent`
- `body`

Therefore adding top-level fields only to the source schema would still lose them during compilation.

## The three implementation choices

### 1. Rich metadata inside `body`

Mechanically viable now for an already admitted kind whose formation allows the fields. The compiler preserves the complete body in `graph.json`.

This is the smallest engine change, but it is sound only with a proper `Authority Envelope` formation. Reusing an unrelated kind merely because its body validator is permissive would be node coercion.

### 2. Linked sidecar

The UI package demonstrates sidecars:

- `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/traceability.json`
- `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/residue.json`
- `projects/domainspec-v2/impl/spec/features/ui-profile-create-player/representations/`

This is coherent for a profile-specific projection, but not yet for authoritative implementer traversal. None of those paths appears in the generated core source manifest. The resolver at `projects/domainspec-v2/impl/tools/minted-project/resolver.ts` follows only `project.features`, `feature.node_sources`, and their node files.

Making sidecars trustworthy inputs would require:

- manifest fields that enumerate them;
- schemas for each sidecar role;
- resolver/source-digest inclusion;
- graph or projection compilation;
- build-receipt verification.

Without that, the implementer has one digested graph plus a second undigested information surface.

### 3. New ontology development profile

This is the strongest route. The explicit-profile mechanism already exists and fails closed:

- canonical profile registry: `projects/domainspec-v2/definitions/minted-project/supported-profiles.yml`
- UI development precedent: `projects/domainspec-v2/impl/spec/ui-profile/minted-project-profile.json`
- selection and handle checks: `projects/domainspec-v2/impl/tools/minted-project/compiler.ts`

A profile can admit:

- new node kinds;
- their body formation contracts;
- allowed relationship signatures and endpoint pairs.

A profile cannot redefine the top-level node envelope. Therefore the proposed record must still be normalized into `minted-node/v1`, or DomainSpec must deliberately evolve to `minted-node/v2`.

## Implementer traversal consequences

The core compiler emits a normalized graph but no generic traversal artifact. The current traversal implementation is UI-specific in `projects/domainspec-v2/impl/tools/build-ui-profile-feature.ts`. It:

- selects Page, Operation, Query, and Interface roots;
- follows directed edges for executable reachability;
- follows edges in either direction for learning-map connectivity;
- joins profile traceability and representation handles afterward.

An `Authority Envelope` would not become a current traversal root automatically.

There is also a larger initial gap: `compiler.ts` rejects every cross-feature edge with `CROSS_FEATURE_UNSUPPORTED`. A repository-wide ontology cannot yet connect concepts distributed across features using the current executable edge model. That requires either project-wide edge admission or a compiled overlay. It should not become an independent second truth graph.

## Smallest concrete witness

The smallest existing witness is:

`projects/domainspec-v2/impl/spec/features/ui-profile-create-player/nodes/create-player-adapter.json`

It proves that:

- an existing graph kind can carry profile-specific metadata in `body.profile_metadata`;
- the metadata survives into generated `graph.json`;
- the node participates in an admitted `maps` edge;
- a sidecar can declare that the graph node represents an alias;
- the learning traversal can report that representation without creating a second compiler.

It does not prove an Authority Envelope formation.

The smallest new witness should be two same-feature nodes and one edge:

```json
{
  "schema_version": "minted-node/v1",
  "node_id": "ontology.ValidationGovernance",
  "feature_id": "ontology",
  "kind": "Authority Envelope",
  "intent": "Route challenges to validation-governance without granting release authority.",
  "body": {
    "label": "Validation Governance",
    "local_authority_kind": "validation-governance",
    "candidate_status": "candidate",
    "owner_route": "projects/domainspec-v2/authority/AUTHORITY-MODEL.md#authority-kinds",
    "source_refs": [
      "projects/domainspec-v2/authority/AUTHORITY-MODEL.md#authority-kinds"
    ],
    "confidence": {
      "evidence_confidence": "medium",
      "commitment_confidence": "medium"
    },
    "challenge_contract": {
      "challenge_response": "owner_review",
      "valid_challenge_modes": ["evidence", "contradiction", "owner_review", "validation"]
    },
    "residue": ["L2 attestation seal pending"],
    "forbidden_collapse": ["Not runtime correctness or implementation conformance."]
  },
  "connections": [
    {
      "edge_id": "ontology.edge.validation-governance-instantiates-authority-envelope",
      "type": "instantiates",
      "to": "ontology.AuthorityEnvelope"
    }
  ]
}
```

This witness requires:

- an explicit development profile;
- `Authority Envelope` and `Concept` formation contracts;
- an admitted `Authority Envelope --instantiates--> Concept` signature;
- a second node named `ontology.AuthorityEnvelope`.

Only after those changes does `instantiates` become implementer-traversable. File-backed validation and contradiction references should remain typed references until DomainSpec deliberately models their targets as nodes.

The architectural conclusion is one executable graph contract with profile-governed node formations and optional compiled projections—not two unrelated graph engines, and not one universal node shape overloaded with every governance concern.

## Agent 2 - authority-envelope semantics

## Verdict

The proposed record is semantically useful, but it is not a DS-D1 feature node and it is not the authority kind itself.

It is best classified as:

```text
candidate local ontology workflow envelope
  about → DomainSpec v2's ratified Validation governance kind
  owned by → validation-governance / DomainSpec v2 owner
  authority effect → none until a local owner decision
```

`concept.authority_envelope` is a candidate CyberAlchemy workflow concept, used only as modeling precedent. The subject it describes—DomainSpec v2 **Validation governance**—is already ratified local authority in `projects/domainspec-v2/authority/AUTHORITY-MODEL.md` and `projects/domainspec-v2/authority/decisions/2026-06-29-ratify-governance-kinds.md`.

These statuses do not conflict:

- ontology envelope: `candidate`
- represented authority kind: `ratified`
- L1 integrity evidence: `pass-l1-integrity`
- L2 external actor attestation: pending

### Role classification

| Dimension | Correct classification | Existing owner/evidence |
|---|---|---|
| DS-D1 kind | **None.** Validation Governance is not Entity, Rule, Operation, or another feature-domain meta-type. | DS-D1 is the aspect-file node alphabet owned by `projects/domainspec-v2/definitions/meta-types/meta-types.yml`. |
| Ontology concept role | `workflow object`, via candidate `concept.authority_envelope`. | Supporting precedent only: `cyberAlchemy-v2/ontology/NODE-MODEL.md`. |
| Local authority kind | **Validation governance**, already ratified. | `projects/domainspec-v2/authority/AUTHORITY-MODEL.md#authority-kinds`; ratification in `projects/domainspec-v2/authority/decisions/2026-06-29-ratify-governance-kinds.md`. |
| Owner route | `validation-governance`. | Exact local route in `projects/domainspec-v2/authority/AUTHORITY-MODEL.md#authority-kinds`. |
| Ontology workflow status | `candidate`. | Candidate local surface in `projects/domainspec-v2/ontology/README.md`. |
| Subject authority status | `ratified`; L1 integrity witnessed; L2 actor signature pending. | `projects/domainspec-v2/authority/attestations/2026-07-12-governance-kinds-l1/RESULT.md`. |
| Confidence | Confidence in the **ontology entry**, not confidence in or status of the authority kind. | The two-axis shape comes from `cyberAlchemy-v2/authority/definitions/DEFINITIONS.md#cav2-d23-authority-lifecycle-axis`, supporting precedent only. |
| Challenge contract | Candidate review protocol for the entry; not verdict, proof, confidence, or promotion. | Shape from `cyberAlchemy-v2/authority/definitions/DEFINITIONS.md#cav2-d40-challenge-contract`, supporting precedent only. |
| Residue | Must distinguish envelope residue from subject-authority residue. | Typed distinction required by `cyberAlchemy-v2/ontology/NODE-MODEL.md`; local owner decides its adoption. |

## Field-level findings

- `node_id`: valid as a local ontology identifier, but not a current `minted-node/v1` identifier or DS-D1 node identity.
- `instantiates: concept.authority_envelope`: correct as candidate package classification. It must not be interpreted as executable DS-D1 typing.
- `local_authority_kind: validation-governance`: ambiguous because `validation-governance` is also the owner-route token. The represented kind should be explicitly identified as DomainSpec v2 **Validation governance**, separately from `owner_route: validation-governance`.
- `candidate_status: candidate`: correct for the ontology envelope. It does not demote the represented ratified kind.
- top-level `owner_route`: currently a Markdown anchor. That is an owner reference, not a route. Semantically it should be:
  ```yaml
  owner_route: validation-governance
  owner_ref: projects/domainspec-v2/authority/AUTHORITY-MODEL.md#authority-kinds
  ```
  Adding `owner_ref` would itself require a local schema/profile decision.
- `source_refs`: admissible provenance. Add the exact ratification decision and L1 result if the entry claims `ratified`, `L1`, or `L2 pending`.
- `evidence_confidence: medium` and `commitment_confidence: medium`: presently unsupported local judgments. DomainSpec has not localized a machine vocabulary or rationale contract for these values. They must remain candidate/local inference.
- `contradiction_edges`: the named target appears only as a string in `projects/domainspec-v2/ontology/README.md`; no materialized target node exists. It is therefore a dangling candidate link, not an admissible executable edge.
- `validation_edges`: the two values are file paths, not graph endpoints. Moreover:
  - `projects/domainspec-v2/impl/tools/validate-doc-links.ts` checks link integrity;
  - `projects/domainspec-v2/impl/tools/validate-relationships.ts` checks DomainSpec relationship signatures.

  Neither validates the truth or authority of this ontology envelope. They should be `validation_refs` or evidence nodes, not represented as proof-bearing validation edges.
- `resolution_gate: projects/domainspec-v2/authority/decisions/`: names a decision location, not a specific gate verdict. It is acceptable as a candidate route pointer; promotion needs an exact local owner decision.
- `residue: L2 attestation...`: this is residue of the represented authority kind’s attestation state, not necessarily residue of the ontology record. Prefer an explicit `subject_residue` relation or materialized residue node. The envelope’s own residue includes absent local schema/profile validation and dangling challenge endpoints.
- `forbidden_collapse`: the listed boundaries are sound and align with `projects/domainspec-v2/authority/AUTHORITY-MODEL.md`. Add:
  - not a DS-D1 feature-domain meta-type;
  - not a `minted-node/v1` source record;
  - not an executable DS-D8 relationship endpoint.

## Semantically admissible relation set

As candidate ontology/projection semantics, the strongest relations are:

- authority envelope → authority kind: `classifies_authority_kind`
- authority envelope → local owner route: `uses_owner_profile`
- evidence artifact → ontology envelope: `supports_candidate`
- source artifact → source posture: `declares_source_posture`
- ontology envelope → owner route: `requests_promotion_gate`
- envelope or represented kind → residue: `records_residue`
- owner decision → promotion record: `decides_transition`
- approved promotion record → projection: `emits_projection_when_allowed`

These predicates come from `cyberAlchemy-v2/ontology/RELATION-MODEL.md` and remain supporting candidate semantics until DomainSpec v2 localizes and admits them.

Not presently admissible as live DomainSpec graph edges:

- `instantiates`
- `contradicts`
- `validates`
- file-path-valued `validation_edges`
- any relation that writes authority or promotion status

They are absent from the 30 active DomainSpec relationship signatures in `projects/domainspec-v2/definitions/relationships/relationships.yml`, and the current experimental minted profile admits only `enforces`, `performs`, and `produces` between Entity, Event, Operation, and Rule nodes in `projects/domainspec-v2/definitions/minted-project/supported-profiles.yml`.

## Candidate boundary

The following must remain candidate:

- the ontology envelope record and its encoding;
- its `instantiates` classification;
- confidence values and their value vocabulary;
- challenge modes and challenge-link encoding;
- ontology-specific relations;
- any graph profile that admits governance/ontology nodes;
- any projection of this record into the executable minted graph.

The following are already locally owned facts, not candidates:

- Validation governance is a DomainSpec v2 authority kind;
- its owner route is `validation-governance`;
- it is owner-ratified;
- L1 integrity passes;
- external L2 actor authentication remains pending;
- it cannot declare runtime correctness or implementation conformance.

The central non-collapse rule is therefore:

```text
candidate encoding of a ratified thing
≠
candidate authority kind
```

DomainSpec v2 may model the already-ratified kind through a candidate ontology envelope without reopening or weakening the kind’s ratification.

## Agent 3 - implementer and learning-map boundary

## Systems-boundary verdict

The strongest architecture is:

> **One typed DomainSpec semantic graph, compiled under one explicit composite profile, plus generated learner/navigation overlays keyed by the same stable IDs.**

That is one semantic truth and multiple views—not two authoritative graphs.

The user’s authority-envelope record is a good candidate **node body**, but it is not currently a valid executable DomainSpec node. It needs a DomainSpec ontology-learning profile and several engine gaps closed before an implementer agent can safely traverse it.

### Architecture comparison

| Candidate | Traversal | Bounded context | Provenance / authority | Determinism | Two-truth risk | Verdict |
|---|---|---|---|---|---|---|
| Flat universal graph | Easy, but all edges appear equivalent | Weak; agents cannot distinguish implementation, authority, challenge, and learner relations | Authority axes collapse into labels | Easy mechanically | Medium: one file, ambiguous meaning | Reject |
| Enriched existing node bodies | Existing compiler carries `body` into `graph.json` | Good only if body fields have a typed formation contract | Source-node authority is preserved | Strong with present compiler | Medium: hidden pseudo-edges inside body can disagree with real connections | Useful migration tactic, insufficient alone |
| Separate ontology graph | Each graph is internally traversable | Requires joins and identity mapping | Clean ownership separation initially | Two deterministic builds possible | **Highest**: mappings, endpoints, status, and edges can drift | Reject as the implementation substrate |
| Typed multi-profile graph | Semantically strongest in principle | Strong: query by kind, relation, hop, profile | Profile admits kinds and relation signatures | Present compiler already binds profile and registry digests | Low if one compiled result | Current engine does **not** support several profiles in one graph; use one composite profile |
| Projection overlay | Excellent for learner journeys and alternative views | Learner context can be purpose-specific | Safe if generated one-way from semantic IDs | Strong if overlay digests bind semantic hash | Low when removal cannot change semantic bytes | Adopt over the typed semantic graph |

The current project manifest selects exactly one profile and binds its digest (`projects/domainspec-v2/impl/spec/minted-project/project.schema.json:12-35`). The compiler then admits node kinds and edge signatures only from that selected profile (`projects/domainspec-v2/impl/tools/minted-project/compiler.ts:404-458,480-548`). Therefore “multi-profile graph” should presently mean **one common graph contract with a purpose-built composite profile**, not several independently authoritative profiles inside one output.

The UI work proves this extension route mechanically: `ui-development@0.1` adds kinds, formation contracts, and relation signatures while remaining explicitly `development-only` and `release_admission: not-granted` (`projects/domainspec-v2/impl/spec/ui-profile/minted-project-profile.json:1-89`).

## Why the proposed YAML does not compile today

`minted-node/v1` requires:

- `schema_version`
- `node_id`
- `feature_id`
- `kind`
- `intent`
- `body`
- `connections`

It also forbids extra top-level properties (`projects/domainspec-v2/impl/spec/minted-project/node.schema.json:7-16`). The example instead has ontology-package fields at top level, and `dsv2.ontology.validation-governance` does not match the current one-dot minted node-ID grammar.

A mechanically coherent adaptation would be:

```json
{
  "schema_version": "minted-node/v1",
  "node_id": "dsv2-ontology.ValidationGovernance",
  "feature_id": "dsv2-ontology",
  "kind": "Authority Envelope",
  "intent": "Model the local lifecycle and challenge boundary of validation governance.",
  "body": {
    "instantiates": "concept.authority_envelope",
    "label": "Validation Governance",
    "local_authority_kind": "validation-governance",
    "candidate_status": "candidate",
    "owner_route": "validation-governance",
    "source_refs": [],
    "confidence": {},
    "challenge_contract": {},
    "residue": [],
    "forbidden_collapse": []
  },
  "connections": []
}
```

That still requires a profile which admits `Authority Envelope`, validates its body formation, and admits its relationships. It is an architectural witness, not a currently valid release node.

Fields that imply traversal should not remain hidden arrays:

- `contradiction_edges` should become typed graph connections to contradiction nodes.
- `validation_edges` currently mixes file paths with edge semantics; file paths belong in provenance/source references, while traversable validators should be nodes with typed connections.
- `instantiates` should become a typed edge if an agent must traverse to the concept definition.
- The top-level owner path and the challenge contract’s short owner name risk becoming conflicting owner truths. Prefer one stable owner ID plus a separate source anchor.

CyberAlchemy’s node and relation models explicitly remain candidate package predicates, not executable edge families or schema amendments (`cyberAlchemy-v2/ontology/NODE-MODEL.md:6-10`; `cyberAlchemy-v2/ontology/RELATION-MODEL.md:6-11`). DomainSpec’s local ontology README likewise says these entries have no authority effect and may only project after local owner review (`projects/domainspec-v2/ontology/README.md:1-15,105-116`).

## Initial engine gaps exposed

1. **No ontology-learning profile.** Current admitted experimental profile contains only `Entity`, `Event`, `Operation`, and `Rule`; the UI extension is development-only (`projects/domainspec-v2/definitions/minted-project/supported-profiles.yml:18-68`).

2. **Cross-feature edges are forbidden.** The compiler raises `CROSS_FEATURE_UNSUPPORTED` when endpoints belong to different features (`projects/domainspec-v2/impl/tools/minted-project/compiler.ts:523-533`). Separate `craft` and `cyberalchemy-method` features therefore cannot yet form the connected map proposed by the learning package.

3. **Independent connection files are unsupported.** The current feature contract is specifically `per-node-connections`; outgoing edges live inside their source node (`projects/domainspec-v2/impl/spec/minted-project/feature.schema.json:5-17`). The learning-map refresh proposes `connections/<connection-id>.json`, which is presently plan/runtime drift (`cyberAlchemy-v2/development/interactive-ontology-learning-map/refreshes/2026-07-15-minted-runtime-route/REFRESH-PATCH-PROPOSAL.md:102-130`).

4. **External source provenance is not yet bound by the minted source manifest.** It maps graph records to contained project-local JSON source files (`projects/domainspec-v2/impl/spec/minted-project/source-manifest.schema.json:5-40`), while the learning map requires revision-pinned anchors into broader source material.

5. **Implementer mapping is absent.** The compiler validates nodes and edges, but it does not yet emit the node→code-pattern and edge→composition contract. That remains the unexecuted spec–ontology hypothesis measured by M1–M4 (`projects/domainspec-v2/research/spec-ontology-unification/SEED.md:14-30`; `DESIGN.md:57-77`). Rich governance metadata alone does not tell an agent what code to write.

6. **Semantic, learner, and navigation views are not yet a minted-project contract family.** The learning spec requires them to be independently serialized and proves learner removal cannot change semantic bytes (`cyberAlchemy-v2/development/interactive-ontology-learning-map/SPEC.md:23-33,86-103,157-169`).

## Minimal graph witness

Semantic source graph:

```text
ValidationGovernance [Authority Envelope]
  ├─ requires-check ──> ValidateRelationships [Operation]
  └─ bounded-by ──────> PassingDerivedTestIsNotRuntimeCorrectness [Rule]
```

Typed implementation interpretation:

```text
Authority Envelope -> context only; emits no code
Operation          -> validator/use-case pattern
Rule               -> pure predicate/non-collapse guard
```

Implementer traversal:

1. Root at `ValidateRelationships`.
2. Request one-hop connected semantic neighborhood.
3. Read the `Operation` implementation pattern.
4. Import `ValidationGovernance` as authority context.
5. Import the boundary `Rule` as an obligation.
6. Ignore learner/navigation edges entirely.

Learner traversal:

1. Root at `ValidationGovernance`.
2. Read the same two semantic edges.
3. Add a generated learner journey such as:

```text
ValidationGovernance -> boundary rule -> validation operation
```

That journey order is stored only in `learnerView`/`navigationView`; it never becomes a semantic relation. This matches the learning spec’s six-plane model and its rule that learner edges are not semantic edges (`cyberAlchemy-v2/development/interactive-ontology-learning-map/SPEC.md:73-117`).

## Recommended evolution order

1. Create a **development-only composite ontology-learning profile** with explicit authority/concept/evidence/operation/rule kinds and typed relations.
2. Keep one node per source file and current source-owned connections for the first witness.
3. Add cross-feature-edge support with explicit profile admission and endpoint ownership; do not work around it by pretending Craft and CyberAlchemy are one feature.
4. Add typed formation schemas for authority-envelope bodies and move traversable references into connections.
5. Add deterministic semantic/learner/navigation projections whose hashes prove overlays cannot mutate semantic bytes.
6. Only then add node→pattern and edge→composition bindings for implementer traversal.

The refresh’s “one graph contract and one projection pipeline” direction is sound (`cyberAlchemy-v2/development/interactive-ontology-learning-map/refreshes/2026-07-15-minted-runtime-route/REFRESH-REPORT.md:21-29`). The correction is that the current engine cannot yet realize its two-feature, independent-connection-file layout.

## Connections

- derives -> ./findings.md
