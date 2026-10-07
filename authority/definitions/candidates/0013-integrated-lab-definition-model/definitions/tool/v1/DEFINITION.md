<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Tool

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.tool`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:tool-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route. Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.

```text
Tool(x) => governed_identity_or_record(x) and bounded_scope(x); Tool(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Tool Definition. |

### Boundary conditions

- A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route.
- Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

### Testable conditions

- Every use of Tool resolves to this exact Definition version or an admitted successor.
- Every claimed instance or use stays within the applicability statement and exclusions.
- No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.

## Plain-language voice

A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route. Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Tool supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- tool:repository-patch accepts an exact patch and returns a receipt; the Agent’s Delegation separately determines whether it may be used.

## Applicability

A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route.

### Exclusions

- Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.
- The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.integrated-model-review@2026-10-05 | whole-file | `1c92c720e176027597db09579276f9ea6e1d13b3d52bda233f9b0c4543dcb5eb` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.tool@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Tool for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
