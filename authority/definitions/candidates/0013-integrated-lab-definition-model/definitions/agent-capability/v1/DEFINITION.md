<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Agent Capability

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.agent-capability`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:agent-capability-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts. Agent Capability is distinct from Product Capability, Tool, Implementation, Role, authority, and successful performance.

```text
AgentCapability(x) => governed_identity_or_record(x) and bounded_scope(x); AgentCapability(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Agent Capability Definition. |

### Boundary conditions

- Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.
- Agent Capability is independent from Product Capability, Tool, model, Implementation, Role, Assignment, authority, and observed success.
- Possessing or advertising a Capability never authorizes its use in a particular Session or scope.
- Capability revision and activation require governed owner action; an Agent cannot self-upgrade by claiming a new Capability.

### Testable conditions

- Every claimed Agent Capability resolves to an exact versioned contract and supporting Implementation binding.
- Every use is separately allowed by Assignment, Policy, Context, and authority evidence.
- No Capability claim implies permission, successful performance, Product value, or external effect.
- Every failure mode and evidence obligation required by the Capability is available to the executing Session.

## Plain-language voice

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts. Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Agent Capability supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- capability:definition-pack-authoring can produce candidate JSON and projections but cannot admit them.

## Applicability

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts.

### Exclusions

- Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.
- Agent Capability is independent from Product Capability, Tool, model, Implementation, Role, Assignment, authority, and observed success.
- Possessing or advertising a Capability never authorizes its use in a particular Session or scope.
- Capability revision and activation require governed owner action; an Agent cannot self-upgrade by claiming a new Capability.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.
- Agent Capability is independent from Product Capability, Tool, model, Implementation, Role, Assignment, authority, and observed success.
- Possessing or advertising a Capability never authorizes its use in a particular Session or scope.
- Capability revision and activation require governed owner action; an Agent cannot self-upgrade by claiming a new Capability.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.agent-capability@1.0.0-candidate.1`
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

This candidate defines Agent Capability for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
