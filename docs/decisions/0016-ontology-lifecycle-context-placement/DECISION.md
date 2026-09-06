<!-- GENERATED FILE: edit decision.json and run render.py. -->

# Select Ontology Lifecycle as a separate bounded-context candidate

> Human projection generated from `decision.json`; it is not canonical.

- Decision: `CAL-DECISION-0016-ONTOLOGY-LIFECYCLE-CONTEXT-PLACEMENT`
- Status: `owner-selected-planning-candidate`
- Selected option: `OLC-2-SEPARATE-BOUNDED-CONTEXT`
- Principal: `person:<vrondelli>`
- Role posture: `candidate:lab-architecture-owner` (`unbound-candidate-role`)
- Authority effect: `context-placement-planning-selection-only`

## Selected model

Ontology Lifecycle is selected as the separate bounded-context candidate `CAL-BC-ONTOLOGY-LIFECYCLE`.

- Candidate path: `contexts/ontology-lifecycle`
- Current package: `ontology-lifecycle`
- Current disposition: `retain-in-place-until-context-admission-and-migration-authorization`
- Dependency direction: `Ontology Lifecycle -> Governance`
- Upstream: `Governance`
- Downstream: `Ontology Lifecycle`
- Context-map pattern: `unresolved`

Ontology Lifecycle consumes Governance-owned authority, decision, admission, challenge, and invalidation meanings without acquiring their ownership.

## Semantic scope

- Semantic event histories for ontology nodes and relations.
- Temporal ontology cuts and deterministic replay.
- Calculated projections and snapshots derived from canonical histories.
- Lifecycle transitions, retirement behavior, and historical identity preservation.
- Exact joins from governance events to semantic-event identity, digest, and cursor.

## Semantic exclusions

- Canonical definition meaning and promotion.
- Governance authority, decision rights, Constitution adoption, and admission policy.
- Product capability adoption and product outcome ownership.
- Storage-provider selection, deployment, publication, and external effects.

## Non-collapse rules

- Ontology Lifecycle bounded context is not the existing ontology-lifecycle directory.
- Ontology Lifecycle bounded context is not its Project, Goal, Product Capability, runtime, DomainSpec source, system ontology, or implementation binding.
- Governance context is not the Governance module, Governance Product, canonical authority store, or enforcement runtime.
- A directional dependency does not transfer semantic ownership or authority.

## Decision Gate

- Result: `PASS`
- Route: `gate`
- Request digest: `a6a1f623277aa78eddbfcdcf26596f139b9be30b2e0e9decb5a772f344c542db`
- Limitation: The owner selected option 2 in conversation before the durable option IDs and prefilter receipt were materialized. The durable record maps that unambiguous selection to OLC-2-SEPARATE-BOUNDED-CONTEXT without broadening its scope.

## Residue transition

### Resolved

- `CAL-CTX-R1-ONTOLOGY-LIFECYCLE-PLACEMENT` — Select a separate Ontology Lifecycle bounded-context candidate rather than classifying the current vertical as a Governance capability instance or leaving placement indefinitely unclassified.

### Remaining

- `CAL-CTX-R2-ACCOUNTABLE-ROLES` — lab-architecture-owner, migration-owner, Governance context owner, and Ontology Lifecycle context owner are not yet bound in the admitted owner registry.
- `CAL-CTX-R3-CONTEXT-METAMODEL` — Bounded Context, CAV2 Context, Ubiquitous Language, Context Map, Capability Instance, Context Migration Manifest, and Context Lineage Record terms and artifact types are not admitted.
- `CAL-CTX-R4-GOVERNANCE-CONTEXT` — Governance has external candidate evidence but no Lab-owned admitted bounded-context artifact.
- `CAL-CTX-R5-ONTOLOGY-LIFECYCLE-CONTEXT` — No Lab-owned Ontology Lifecycle context.json, language, contracts, context maps, or admission decision exists.
- `CAL-CTX-R6-CONTEXT-MAP-PATTERN` — The exact DDD context-map integration pattern and owner contract between Ontology Lifecycle and Governance remain unselected.
- `CAL-CTX-R7-MIGRATION` — No source-admission manifest, migration manifest, lineage postimage, relocation plan, or migration authorization exists.

## Explicit exclusions

- This decision does not admit either Ontology Lifecycle or Governance as a bounded context.
- This decision does not create the contexts/ directory or move, rename, copy, delete, or rewrite ontology-lifecycle/.
- This decision does not select the exact context-map relationship pattern or publish a cross-context contract.
- This decision does not admit external CyberAlchemy-v2 source material or make source evidence Lab authority.
- This decision does not admit definitions, artifact types, language, capability instances, DomainSpec sources, ontologies, runtimes, implementation bindings, or conformance.
- This decision does not authorize Git commit, push, publication, release, deployment, external effect, or a stable-version claim.

## Successor obligations

- Bind accountable architecture, migration, Governance-context, and Ontology-Lifecycle-context owner identities without collapsing their scopes.
- Complete CTX-00 by authoring and admitting the context migration terms and artifact-type contracts.
- Author the Lab-owned Governance bounded-context candidate from exact admitted source selectors.
- Author the Lab-owned Ontology Lifecycle bounded-context candidate with its own ubiquitous language, scope, exclusions, and capability-instance boundaries.
- Select the exact directional context-map relationship pattern and contract between the two context candidates.
- Prepare source-admission, lineage, migration, validation, and rollback artifacts before any physical relocation.

## Claim ceiling

This decision resolves only the planning placement of Ontology Lifecycle as a separate bounded-context candidate downstream of Governance meaning. It does not bind the currently unregistered architecture-owner role, admit either context, select the exact context-map pattern, migrate bytes, authorize implementation, publish, deploy, or establish the first stable version.
