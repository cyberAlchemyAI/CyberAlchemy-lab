<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Context View

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.context-view`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.context-resolution`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Context View is the normalized definition identified by semantic.context-view, owned within scope.context-resolution, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D66 without silently merging it with another target.

Target-specific normative meaning:

A Context View is an immutable, digest-bound projection produced by resolving one Context Request against one exact Context identity and source epoch; it records included and excluded material, lineage, limitations, and expiry or refresh conditions without becoming the Context itself.

Bound source-semantic basis:

A Context is a durable, identity-bearing, owner-qualified boundary of relevance
and interpretation for one declared purpose. It names the Product, optional
Project, optional Goal, intended consumers and uses, subject scope, and source
policies that frame what information and meaning may be assembled for the work.

Every CyberAlchemy Context belongs to exactly one Product. A project Context
belongs to exactly one Project. A goal Context belongs to exactly one Project
and focuses on exactly one Goal that already belongs to that Project. The first
contract intentionally allows only one primary Goal per Context; cross-goal
work requires separate Contexts or a later explicitly defined composite model.

A Context identity remains stable across new source epochs, resolution
requests, immutable views, interface presentations, session pauses, and
refreshes that preserve its Product, Project, Goal, and purpose. A material
change to any of those anchors creates a successor Context and supersedes the
earlier one instead of silently changing what the earlier identity meant.

```text
```text
Context =
  (id, kind, product_ref, project_ref?, goal_ref?, purpose,
   bounded_context_refs, consumer_refs, intended_uses, subject_scope,
   source_policy_refs,
   owner_route, lifecycle_state, revision_history, challenge_route)

kind in { product, project, goal }
lifecycle_state in { draft, active, superseded, retired }
|product_ref| = 1
|project_ref| <= 1
|goal_ref| <= 1
|bounded_context_refs| >= 0
|consumer_refs| >= 1

kind = product => project_ref = null and goal_ref = null
kind = project => project_ref != null and goal_ref = null
kind = goal =>
  project_ref != null
  and goal_ref != null
  and belongs_to(goal_ref, project_ref)

material_change(product_ref, project_ref, goal_ref, purpose) =>
  successor_context_required

current(ContextView) =/=> current(Context)
active(Context) =/=> sources_true_or_authoritative
Context =/= BoundedContext
```
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.context-view | Stable normalized identity for Context View. |
| CAV2-D66 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A Context is not a Product, Product Thesis, Project (`CAV2-D60`), Goal
(`CAV2-D59`), Project Space (`CAV2-D15`), DDD Bounded Context, Language,
Registry, source selection, request, immutable View, Snapshot, Context Pack,
Session, prompt, event ledger, authority envelope, owner decision, or execution
permission.

Declaring a source relevant does not make it true, current, authoritative,
accepted, or executable. Activating a Context does not activate its Project or
Goal. A passing Context validator does not prove that a consumer understood or
used the Context correctly. Canonical admission of this definition does not
admit a Context instance, accept a resolver contract, or authorize runtime,
publication, release, deployment, or external effects.
- This target remains distinct from the sibling targets semantic.context, semantic.context-request reconstructed from CAV2-D66; shared source lineage does not merge their identities or validation purposes.

### Testable conditions

- The candidate identity remains cal.definition.context-view.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

It is a frozen answer to one context request at one point in the source history.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Context View is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

Inside CyberAlchemy v2, the first Context connects the CyberAlchemy Product,
the Define Project, the Define first-class ownership Goal, and the Define
shared-meaning consumer. Registry Context can resolve exact Product, Project,
Goal, Language, and Definition selections into one immutable View for that
Context without taking ownership of any source.

The Language package already uses a DDD-style Bounded Context to say where a
Language and model have consistent meaning. A Context may reference zero or
more of those Bounded Contexts. Such a reference preserves each domain model,
Language, conflict, and owner boundary; it does not merge them. A Bounded
Context is not an alias for this definition and is not promoted or redefined
by `CAV2-D66`.

### Examples

- Resolve semantic.context-view by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Context View.

## Applicability

Create a Context before assembling a reusable context view for a Product,
Project, or Goal. Keep the Context identity and purpose stable, then let a
resolver create immutable Views bound to exact requests and source epochs.
Consumers may reuse the Context identity across CLI, chat, and session
continuations, but they must not silently reuse a stale View.

Use a Context to answer: which Product frames this work, which Project and Goal
apply, why context is needed, who will use it, which subjects are in scope, and
which DDD Bounded Context meanings must remain intact, and which source policies
govern resolution. Put selected records, digests,
bindings, and residue in a Context View or Snapshot, not in the Context
identity itself.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A Context is not a Product, Product Thesis, Project (`CAV2-D60`), Goal
(`CAV2-D59`), Project Space (`CAV2-D15`), DDD Bounded Context, Language,
Registry, source selection, request, immutable View, Snapshot, Context Pack,
Session, prompt, event ledger, authority envelope, owner decision, or execution
permission.

Declaring a source relevant does not make it true, current, authoritative,
accepted, or executable. Activating a Context does not activate its Project or
Goal. A passing Context validator does not prove that a consumer understood or
used the Context correctly. Canonical admission of this definition does not
admit a Context instance, accept a resolver contract, or authorize runtime,
publication, release, deployment, or external effects.
- This target remains distinct from the sibling targets semantic.context, semantic.context-request reconstructed from CAV2-D66; shared source lineage does not merge their identities or validation purposes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D66 | ## CAV2-D66: Context | `cef43970ffab0e22afdb90fc5436cbe17da9d35cc570320285cdbb6dfd2ef06d` | `candidate-unadmitted` |

## Primary consumers

- semantic.product-capability

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.context-view@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.context-view | cyberalchemy-v2:CAV2-D66 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-context-view/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
