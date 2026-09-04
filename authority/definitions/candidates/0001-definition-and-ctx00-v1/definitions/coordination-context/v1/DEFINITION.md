<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Coordination Context

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.coordination-context`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-coordination`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Coordination Context is a durable, identity-bearing, owner-qualified frame that binds exactly one Product, optional Project and Goal references, a stable purpose, intended consumers and uses, subject scope, source policies, and zero or more references to independently owned Bounded Contexts. A material change to Product, Project, Goal, or purpose requires a successor identity.

```text
CoordinationContext = (id, product_ref, project_ref?, goal_ref?, purpose, consumer_refs, intended_uses, subject_scope, source_policy_refs, bounded_context_refs, owner_ref, lifecycle, revision_history, challenge_route); |product_ref|=1; |project_ref|<=1; |goal_ref|<=1; MaterialAnchorChange => SuccessorRequired.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| bounded_context_refs | Explicit references to separately owned Bounded Context versions. |

### Boundary conditions

- It references Bounded Contexts but never becomes one by containment.
- Directory placement cannot supply identity or ownership.

### Testable conditions

- Product cardinality is exactly one.
- Project and Goal cardinalities are at most one.
- Every bounded context link is explicit.

## Plain-language voice

The durable frame saying what a piece of work is about, why information is needed, and who will use it.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Coordination Context candidates belong under coordination/contexts and may reference Governance or Ontology Lifecycle without becoming either bounded context.

### Examples

- A Craft project context can reference both Governance and Ontology Lifecycle meanings.

## Applicability

Durable product-work framing and references to independently owned semantic contexts.

### Exclusions

- DDD semantic boundary ownership.
- Execution authorization or transient chat/session state.

## Boundaries

- A Coordination Context is not a Bounded Context, Product, Project, Goal, prompt, source selection, decision, or execution permission.
- A source view changing does not mutate the durable coordination identity.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D66 | CAV2-D66 | `93ed5c852579f7e84af9c3163f737f4f37c822d1a49063a3fa8b5af1d2ae7769` | `admitted` |
| CAL-SOURCE-ADMISSION-CTX00-CONTEXT-PACKAGE | whole-file | `97550af74d600a415c562ffeca18e1515189d9437b90d0e650a769038909f041` | `admitted` |

## Primary consumers

- coordination/contexts
- contexts
- product/capabilities

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.coordination-context`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.coordination-context@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CAL-DECISION-0017-CTX00-SOURCE-ADMISSION
- DEFINE-PACK-CAL-CONTEXT-MIGRATION-METAMODEL-003

## Residue

- coordination-context-artifact-type-required
- coordination-context-owner-binding-required

## Claim ceiling

This candidate defines Coordination Context meaning only; it does not create a coordination context, bind its operational owner, or authorize execution.
