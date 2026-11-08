<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Context Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.context-profile`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:context-profile-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Context Profile is a reusable versioned policy contract that constrains how purpose-bound Contexts may be constructed and resolved through permitted anchor kinds, cardinalities, identity fields, source rules, freshness, exclusions, succession, and challenge handling. It is not a Context instance and carries no Product, Project, Goal, purpose-bound Context identity, resolved source selection, or consumer-specific view.

```text
ContextProfile(x) => governed(x) and bounded(x); ContextProfile(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Context Profile contract. |

### Boundary conditions

- Context supplies the purpose-specific relevance boundary; Context Profile supplies reusable construction and resolution policy.
- A Profile can govern many Contexts while retaining its own owner, version, lifecycle, and challenge route.
- Profile revisions do not silently reinterpret existing Context versions.

### Testable conditions

- Every Context Profile declares allowed anchor kinds, cardinalities, identity rules, source constraints, freshness, succession, owner, and challenge route.
- A Context claiming conformance names one exact Profile version.
- No Context identity or resolved source set is inferred from the Profile alone.

## Plain-language voice

A Context Profile is a reusable versioned policy contract that constrains how purpose-bound Contexts may be constructed and resolved through permitted anchor kinds, cardinalities, identity fields, source rules, freshness, exclusions, succession, and challenge handling. It is not a Context instance and carries no Product, Project, Goal, purpose-bound Context identity, resolved source selection, or consumer-specific view.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

Context Profile receives its own positive meaning so its carrier no longer borrows a broader Definition as its primary semantic identity.

### Examples

- profile:product-project-context/v1 permits exactly one Product anchor, an optional Project anchor, explicit source digests, a 24-hour freshness ceiling, and successor-only revision.

## Applicability

A Context Profile is a reusable versioned policy contract that constrains how purpose-bound Contexts may be constructed and resolved through permitted anchor kinds, cardinalities, identity fields, source rules, freshness, exclusions, succession, and challenge handling.

### Exclusions

- It is not a Context instance and carries no Product, Project, Goal, purpose-bound Context identity, resolved source selection, or consumer-specific view.
- Profile conformance does not create a Context or prove that resolution inputs are current.
- This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment.

## Boundaries

- Context supplies the purpose-specific relevance boundary; Context Profile supplies reusable construction and resolution policy.
- A Profile can govern many Contexts while retaining its own owner, version, lifecycle, and challenge route.
- Profile revisions do not silently reinterpret existing Context versions.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.step3.remaining | whole-file | `9e80895df1887113cfc407de6ed4d11f6cd37d4ac10857389ee060e1139c9f36` | `candidate-unadmitted` |

## Primary consumers

- CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014

## Lookup and drift

- Index: `authority/definitions/candidates/0014-definition-specialization-resolution/DEFINITIONS-INDEX.md` / `cal.definition.context-profile@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0014-definition-specialization-resolution/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- authority/artifact-types/candidates/0005-remaining-18-complete-model/model.json
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner admission remains required.
- Artifact Type rebinding and admission remain separate.

## Claim ceiling

This candidate defines Context Profile for Step 3 review only and has no admission or downstream activation effect.
