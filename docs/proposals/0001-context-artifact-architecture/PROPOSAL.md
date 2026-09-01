<!-- Generated from proposal.json. Do not edit this projection directly. -->

# Context and artifact architecture

- Proposal: `CAL-PROP-0001`
- Schema: `cyberalchemy-lab-architecture-proposal/v0`
- Status: `draft`
- Decision posture: `not-selected`
- Authority effect: `none`
- Artifact type: `candidate:architecture-proposal/v0` (`candidate-unadmitted`)

> This is a non-effectful architecture candidate. It does not authorize implementation, installation, migration, publication, release, or deployment.

## Evidence

- `domainspec-core:cyberAlchemy-v2/development/research/2026-08-31-cyberalchemy-lab-context-artifact-architecture/findings.md` (`sha256:192d26e32ff9bb846be0ba85f65027e620df2644e75671225fb8ec4f93cb3a1c`) — `research-input-only`
- `domainspec-core:cyberAlchemy-v2/development/research/2026-08-31-cyberalchemy-lab-context-artifact-architecture/validation/witness-mutant/RESULT.md` (`sha256:b4fbe8f02234bc854b3e02edd8ed036a3c133fcdbf6ee5287ad664256fd6b767`) — `synthetic-validation-input-only`
- `domainspec-core:cyberAlchemy-v2/development/research/2026-08-31-cyberalchemy-lab-context-artifact-architecture/validation/witness-mutant/receipts/run-001.json` (`sha256:7bcfc561a01d93f79d0c1b491337790226120684445bc2a37073ce07763d2e9a`) — `research-receipt-only`

## Decision Question

What repository structure can keep semantic ownership, authority, bounded contexts, recursive capability instances, and machine-canonical artifacts orthogonal without repeating the whole repository at every level?

## Recommendation

Use an owner-local logical artifact record inside an owner-local recursive capability-instance envelope. Share only a mechanics contract for source direction, schema identity, generator identity, deterministic projection, source-admission references, and typed relation envelopes.

## Architectural Units

- Product Capability: the stable product outcome and parent meaning.
- Capability instance: an owner-local realization envelope with explicit parent binding, construction binding, budget, stop, recomposition, and handoff.
- DDD Bounded Context: an explicit language, scope, exclusion, owner, and directional context-map boundary.
- CAV2 Context: a durable coordination/work-frame identity; it is not a DDD Bounded Context.
- Artifact type: an owner-local contract for permitted record shape, origin constraints, lifecycle vocabulary, and relations.
- Artifact instance: a typed record bound to one exact artifact type and its owning capability/context identities.
- Shared Artifact Mechanics Contract: mechanics only; never shared semantic meaning or authority.

## Four Facets

- Classification facet: every artifact declares its semantic kind, authority kind, artifact type, and lifecycle posture as separate fields.
- Schema facet: every artifact binds an exact schema identity and digest; schema validity proves shape only.
- Human-continuation facet: every artifact has a deterministic human projection generated from the canonical machine record.
- Machine-checkable facet: the machine record is canonical and validators compare regenerated projection bytes against the checked-in projection.
- Any missing facet is typed residue with an owner and consequence; it is never silently inferred.

## Orthogonality Rules

- Artifact type, semantic kind, authority kind, artifact instance, capability instance, CAV2 Context, DDD Bounded Context, Product, Governance, module, package, layer, and directory are independent axes.
- A filename or directory never establishes type, ownership, authority, source admission, bounded-context identity, or recursion.
- Definition, Axiom, Premise, Invariant, Constitution, Decision, and Schema remain distinct semantic kinds even when an authority model groups some of their carriers.
- Product and Governance are not automatically bounded contexts. Each needs an owner-selected context identity, ubiquitous language, scope, exclusions, and directional maps.
- Cross-context relations are typed, directional, and owned; identical labels do not imply identical meaning.

## Artifact Contract

```json
{"artifact_type_fields":["artifact_type_id","version","semantic_owner_ref","schema_ref","schema_digest","producer_constraints","origin_constraints","lifecycle_vocabulary_refs","allowed_relation_kinds","projection_contract_ref"],"artifact_instance_fields":["artifact_instance_id","artifact_type_ref","semantic_kind","authority_kind","semantic_owner_ref","capability_instance_ref","context_ref","bounded_context_refs","source_admission_ref","source_direction","schema_ref","generator_ref","evidence_refs","residue_refs","typed_relations"]}
```

## Shared Mechanics Responsibilities

- Declare source direction.
- Bind schema identity and digest.
- Bind generator identity, version, and digest.
- Regenerate deterministically and compare exact bytes.
- Carry a source-admission reference shape without making the decision.
- Carry typed relation envelopes without interpreting owner-local semantics.

## Shared Mechanics Forbidden Scope

- Semantic taxonomy or defaults.
- Lifecycle interpretation.
- Authority classification or admission decisions.
- Bounded-context classification.
- Promotion, conformance, release, or enforcement authority.

## Owner Role Registry

- `lab-architecture-owner`: Select immutable repository architecture candidates and their dependency model.
- `artifact-mechanics-owner`: Own source direction, schema and generator binding mechanics without owning artifact meaning.
- `artifact-type-owner`: Own each artifact type contract and its allowed lifecycle and relations.
- `source-admission-owner`: Decide whether exact external source bytes become admitted Lab inputs.
- `definition-owner`: Own canonical definition meaning and stable identity.
- `invariant-owner`: Own formation and preservation invariant meaning independently from definitions.
- `lineage-owner`: Own legacy-to-active identity mappings and tombstones.
- `formalization-owner`: Own FormalClaims and provider bindings without becoming definition authority.
- `platform-owner`: Own language, tool, runtime, profile, environment, and lock declarations.
- `migration-owner`: Own bounded migration manifests, phase write sets, and rollback boundaries.
- `evidence-conformance-owner`: Own independent checks and receipts without selecting semantic truth.
- `craft-product-owner`: Own Craft Product meaning and capability selection.
- `craft-project-owner`: Own Craft coordination state, goals, and execution authorization boundaries.

## Recursive Instance Contract

- Bind capability_instance_id, capability_ref, semantic_owner_ref, and one independent context_id.
- Reference zero or more evidenced bounded contexts; do not infer them from placement.
- Carry Project/Goal coordination refs and an owner-local business ontology.
- Carry complete recursive parent/instance and specification construction bindings.
- Declare directional context maps, residue, resource budget, recursion stop, recomposition route, and terminal handoff.
- A higher recursive altitude requires a fresh complete binding; copied folders do not count as recursion.

## Repository Tree

```text
CyberAlchemy-lab/
├── README.md
├── docs/
│   ├── decisions/
│   └── proposals/
├── contracts/
│   └── artifact-mechanics/
│       └── v1/
│           ├── contract.json
│           ├── CONTRACT.md
│           ├── schema.json
│           └── generator-binding.json
├── authority/
│   ├── artifact-types/
│   │   ├── artifact-type/v1/
│   │   ├── migration-proposal/v1/
│   │   ├── source-admission/v1/
│   │   ├── definition/v1/
│   │   ├── axiom/v1/
│   │   ├── premise/v1/
│   │   ├── invariant/v1/
│   │   ├── constitution/v1/
│   │   ├── decision/v1/
│   │   ├── schema/v1/
│   │   ├── lineage-map/v1/
│   │   ├── formal-claim/v1/
│   │   ├── native-source-bundle/v1/
│   │   ├── provider-binding/v1/
│   │   └── receipt/v1/
│   ├── definitions/
│   ├── axioms/
│   ├── premises/
│   ├── invariants/
│   ├── constitutions/
│   ├── decisions/
│   │   └── source-admission/
│   ├── lineage/
│   └── schemas/
├── product/
│   ├── products/
│   │   └── craft/v1/
│   ├── capabilities/
│   │   └── <capability-id>/
│   │       └── v1/
│   │           ├── capability.json
│   │           └── CAPABILITY.md
│   └── ontology/
├── coordination/
│   ├── projects/
│   │   └── craft/
│   └── goals/
├── contexts/
│   └── <bounded-context-id>/
│       ├── context.json
│       ├── CONTEXT.md
│       ├── language/
│       ├── maps/
│       └── instances/
│           └── <capability-instance-id>/
│               ├── envelope.json
│               ├── artifacts/
│               │   └── <artifact-instance-id>/
│               │       ├── artifact.json
│               │       ├── ARTIFACT.md
│               │       ├── evidence/
│               │       └── residue/
│               ├── specification/
│               │   ├── project.json
│               │   ├── authored/
│               │   └── generated/
│               ├── implementation/
│               │   ├── components/
│               │   └── bindings/
│               ├── construction/
│               └── handoff/
├── platform/
├── evidence/
│   ├── conformance/
│   ├── validation/
│   └── receipts/
├── tooling/
│   ├── schemas/
│   ├── validators/
│   └── generators/
└── tests/
    ├── fixtures/
    └── conformance/
```

## Layout Interpretation

- The root separates cross-cutting contracts, shared authority surfaces, product capability definitions, bounded-context packages, platform mechanics, evidence, tooling, and tests.
- Every bounded context uses the same minimal package form: context identity, generated view, language, directional maps, and capability instances.
- The recursive full form belongs to capability instances, not to arbitrary folders. This prevents repeating the entire repository and keeps recursion explicit.
- A capability definition lives under product; an owner-local capability instance lives under a bounded-context package and binds back to that definition.
- Compiled specification output remains capability-instance-local because it is a projection of that authored source, not a repository-wide generated directory.
- Product identity, Project coordination, Product Capability, CAV2 Context, and DDD Bounded Context remain separate carriers; the tree does not collapse them into one folder meaning.

## Enforcement Obligations

- Reject hand-edited human projections.
- Reject schema identity or digest drift.
- Reject missing or wrong artifact_type_ref.
- Reject missing or inferred semantic owners.
- Reject stale generator bindings.
- Reject label-only or directory-only cross-context dependencies.
- Reject recursion without a stop and recomposition route.
- Reject discovered or copied external material represented as admitted without an exact owner decision.
- Prove two-run byte identity for every generated human projection.

## Source Admission Policy

- CyberAlchemy-v2 remains an external source and evidence ledger.
- Every candidate import binds source repository, exact path or selector, content digest, original owner, boundary class, and candidate posture.
- Only an immutable owner decision may move a candidate to admitted; copying, placement, readability, or schema PASS cannot do so.

## Required Decisions

- Select or reject this architecture against one immutable proposal digest.
- Bind the candidate owner-role registry to accountable identities without collapsing its separate authorities.
- Select the first bounded contexts; do not assume Product or Governance.
- Select one initial artifact type and complete its schema, generator, validator, and negative-test contract.
- Select the first capability and capability-instance witness with complete recursion and construction boundaries.
- Select exact RN-2-aligned paths for Craft Product, Project coordination, active specification source, lineage, and source-admission records.

## Typed residue

### No admitted architecture-proposal artifact type or schema exists.

- Owner needed: CyberAlchemy Lab artifact-type owner
- Effect: This draft cannot be treated as an admitted governed artifact.

### The bootstrap projection renderer is not an admitted generator binding.

- Owner needed: CyberAlchemy Lab projection toolchain owner
- Effect: Projection generation here demonstrates direction only, not enforcement.

### Product and Governance bounded-context identities remain unselected; neither is inferred from the new Product or coordination carriers.

- Owner needed: Respective semantic owners
- Effect: No context directory or context map may be inferred for either.

## Claim ceiling

This draft records a planning candidate. It does not select or admit an architecture, constitute an owner, create an artifact type, admit source, satisfy recursive or CAV2-D65 construction invariants, authorize implementation, prove enforcement or conformance, publish, release, deploy, or establish v1.0.0.

