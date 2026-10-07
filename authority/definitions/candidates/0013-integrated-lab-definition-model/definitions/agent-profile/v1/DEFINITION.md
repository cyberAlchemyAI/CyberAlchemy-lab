<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Agent Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.agent-profile`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:agent-profile-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions. A Profile is neither an active Agent Instance, Session, capability grant, Implementation, model, nor authority grant.

```text
AgentProfile(x) => governed_identity_or_record(x) and bounded_scope(x); AgentProfile(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Agent Profile Definition. |

### Boundary conditions

- An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.
- A Profile constrains behavior but grants no Assignment, authority, tool access, or successful performance.
- A Profile change creates a versioned successor under owner review; an active Machine Agent cannot silently rewrite or activate its own Profile.
- Profile memory or retained lessons must be explicit governed references; hidden cross-session memory is forbidden.

### Testable conditions

- Every Agent Instance binds one exact Profile version.
- Every Profile declares input, output, Policy, Context, tool, evidence, escalation, failure, and stop contracts.
- No Profile field grants authority without a separately valid Delegation or Authority Claim.
- Every activated Profile revision has an attributable owner Decision and preserved predecessor.

## Plain-language voice

An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions. An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Agent Profile supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- profile:definition-curator requires source-bound Definitions, deterministic projections, hostile fixtures, and owner review before admission.

## Applicability

An Agent Profile is a reusable versioned contract for allowed inputs, outputs, behavior, Policies, Context, tool classes, evidence, escalation, and stop conditions.

### Exclusions

- An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.
- A Profile constrains behavior but grants no Assignment, authority, tool access, or successful performance.
- A Profile change creates a versioned successor under owner review; an active Machine Agent cannot silently rewrite or activate its own Profile.
- Profile memory or retained lessons must be explicit governed references; hidden cross-session memory is forbidden.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- An Agent Profile is durable reusable Project State and is never the active Agent, Instance, Session, model, or Implementation.
- A Profile constrains behavior but grants no Assignment, authority, tool access, or successful performance.
- A Profile change creates a versioned successor under owner review; an active Machine Agent cannot silently rewrite or activate its own Profile.
- Profile memory or retained lessons must be explicit governed references; hidden cross-session memory is forbidden.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.agent-profile@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-actor-agent-model-review.md
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Agent Profile for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
