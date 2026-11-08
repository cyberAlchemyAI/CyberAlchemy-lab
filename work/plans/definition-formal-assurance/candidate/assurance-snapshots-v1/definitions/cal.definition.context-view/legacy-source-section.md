## CAV2-D66: Context

Status: active
Term: context
Aliases: governed context, work context, product-work context
Promoted: 2026-08-30 by explicit owner direction to make Context a first-class CyberAlchemy v2 concept before Registry Context migration and implementation; definition authority only

### Normative Definition

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

### Formal Interpretation

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

### Schema

Schema handle: `CAV2-D66-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The first closed machine-checkable candidate contract is owned by
[../../context/schemas/context.schema.json](../../context/schemas/context.schema.json).
The Context package, its example instances, and its validation receipts remain
separate from canonical definition authority.

### Operational Interpretation

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

### Plain-Language Intuition

Context is the named frame that says what this work is about, why information
is needed, and what belongs in the conversation.

### Domain-Context Voice

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

### Boundary

A Context is not a Product, Product Thesis, Project (`CAV2-D60`), Goal
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

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../context/README.md](../../context/README.md)
- [../../ontology/product/README.md](../../ontology/product/README.md)
- [../../goals/README.md](../../goals/README.md)
- [../../language/README.md](../../language/README.md)
