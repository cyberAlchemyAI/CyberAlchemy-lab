<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Model Instance Binding

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.model-instance-binding`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:model-instance-binding-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling. It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.

```text
ModelInstanceBinding(x) => governed(x) and bounded(x); ModelInstanceBinding(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Model Instance Binding contract. |

### Boundary conditions

- The parent owns its contract; the instance owner controls only the declared extension scope.
- Inherited clauses retain parent provenance and cannot be silently weakened locally.
- A generic relation projection is read-only when the specialized Binding is canonical.

### Testable conditions

- Every Binding resolves exact parent and instance identities and versions.
- Inherited, extended, overridden, prohibited, and unresolved clauses are explicit.
- Every override is inside declared extension scope and cites authority and evidence.
- Changing parent, instance, or authority scope creates a successor Binding.

## Plain-language voice

A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling. It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

Model Instance Binding receives its own positive meaning so its carrier no longer borrows a broader Definition as its primary semantic identity.

### Examples

- binding:agent-profile-instance-22 binds profile:definition-curator@v3 to a local instance, inherits stop and evidence rules, permits only budget overrides, and leaves admission authority prohibited.

## Applicability

A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling.

### Exclusions

- It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.
- Conformance, inheritance, adoption, realization, and identity remain separate claims.
- This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment.

## Boundaries

- The parent owns its contract; the instance owner controls only the declared extension scope.
- Inherited clauses retain parent provenance and cannot be silently weakened locally.
- A generic relation projection is read-only when the specialized Binding is canonical.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.step3.remaining | whole-file | `9e80895df1887113cfc407de6ed4d11f6cd37d4ac10857389ee060e1139c9f36` | `candidate-unadmitted` |

## Primary consumers

- CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014

## Lookup and drift

- Index: `authority/definitions/candidates/0014-definition-specialization-resolution/DEFINITIONS-INDEX.md` / `cal.definition.model-instance-binding@1.0.0-candidate.1`
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

This candidate defines Model Instance Binding for Step 3 review only and has no admission or downstream activation effect.
