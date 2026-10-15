[Documentation home](../../README.md)

# Context Request

<a id="def-cal-definition-context-request"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Context Request

# Context Request

States what an identified task or consumer needs from a context, including selection and freshness conditions, without changing that context’s identity.

**When it applies**

Create a Context before assembling a reusable context view for a Product, Project, or Goal. Keep the Context identity and purpose stable, then let a resolver create immutable Views bound to exact requests and source epochs. Consumers may reuse the Context identity across CLI, chat, and session continuations, but they must not silently reuse a stale View.

**Record formats**

[Context request · v1](type-cal-artifact-type-context-request-v1.md#type-cal-artifact-type-context-request-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-context-request-section-2"></a>

## Source explanatory wording

It asks for a particular usable slice of a context without changing the context itself.

<a id="def-cal-definition-context-request-section-3"></a>

## Exact governing statement

Context Request is the normalized definition identified by semantic.context-request, owned within scope.context-resolution, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D66 without silently merging it with another target.

Target-specific normative meaning:

A Context Request is a bounded, attributable request to resolve a declared Context for named consumers and intended uses under exact selectors, freshness requirements, exclusions, and output constraints; it neither mutates the Context nor grants authority over selected sources.

Bound source-semantic basis:

A Context is a durable, identity-bearing, owner-qualified boundary of relevance and interpretation for one declared purpose. It names the Product, optional Project, optional Goal, intended consumers and uses, subject scope, and source policies that frame what information and meaning may be assembled for the work.

Every CyberAlchemy Context belongs to exactly one Product. A project Context belongs to exactly one Project. A goal Context belongs to exactly one Project and focuses on exactly one Goal that already belongs to that Project. The first contract intentionally allows only one primary Goal per Context; cross-goal work requires separate Contexts or a later explicitly defined composite model.

A Context identity remains stable across new source epochs, resolution requests, immutable views, interface presentations, session pauses, and refreshes that preserve its Product, Project, Goal, and purpose. A material change to any of those anchors creates a successor Context and supersedes the earlier one instead of silently changing what the earlier identity meant.

````
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
````

- A Context is not a Product, Product Thesis, Project (`CAV2-D60`), Goal (`CAV2-D59`), Project Space (`CAV2-D15`), DDD Bounded Context, Language, Registry, source selection, request, immutable View, Snapshot, Context Pack, Session, prompt, event ledger, authority envelope, owner decision, or execution permission. Declaring a source relevant does not make it true, current, authoritative, accepted, or executable. Activating a Context does not activate its Project or Goal. A passing Context validator does not prove that a consumer understood or used the Context correctly. Canonical admission of this definition does not admit a Context instance, accept a resolver contract, or authorize runtime, publication, release, deployment, or external effects.
- This target remains distinct from the sibling targets semantic.context, semantic.context-view reconstructed from CAV2-D66; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/context-request/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.context-request@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9e0364f581e5a5323bc2f6c12306386b3bd0936527192b575f4629e81fb4a0b4

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Create a Context before assembling a reusable context view for a Product,\nProject, or Goal. Keep the Context identity and purpose stable, then let a\nresolver create immutable Views bound to exact requests and source epochs.\nConsumers may reuse the Context identity across CLI, chat, and session\ncontinuations, but they must not silently reuse a stale View.\n\nUse a Context to answer: which Product frames this work, which Project and Goal\napply, why context is needed, who will use it, which subjects are in scope, and\nwhich DDD Bounded Context meanings must remain intact, and which source policies\ngovern resolution. Put selected records, digests,\nbindings, and residue in a Context View or Snapshot, not in the Context\nidentity itself.",
  "authority_scope_ref": "scope.context-resolution",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
