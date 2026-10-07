<!-- GENERATED FILE: canonical data is artifact.json. -->

# Capability Realization Binding Artifact Type v2

- Type: `cal.artifact-type.capability-realization-binding/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Predecessor: `cal.artifact-type.capability-realization-binding/v1`

## Semantic identity

- `cal.definition.capability-realization-binding@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0014-definition-specialization-resolution/definitions/capability-realization-binding/v1/definition.json`

## Distinct validation purpose

Binds one exact Product Capability version to typed owner-qualified realizations while keeping adoption, conformance, observations, operation, and value as separate claims.

## Orthogonality rules

- **CRB2-BINDING-IDENTITY**: The binding, Product Capability, realization endpoint, Capability Instance, Implementation, owner, contract, evidence, and lifecycle state retain separate identities.
- **CRB2-ONE-CAPABILITY-VERSION**: Each binding names exactly one Product Capability version and one or more explicitly typed realization endpoints.
- **CRB2-CLAIM-SEPARATION**: Candidate, adopted, conformant, observed, operational, effective, and valuable remain independent claims with independent evidence and decisions.
- **CRB2-NO-IMPLICIT-REALIZATION**: Schema conformance or relation membership cannot imply that a realization exists, runs, conforms, succeeds, or produces Product value.

## Realistic example

One binding names `product-capability:governed-definition-admission@1` and an explicit `workflow:definition-admission:v1` realization. The binding records their governed connection; it does not become either endpoint or prove that the workflow runs successfully.

## Typed residue

- `CRB2-R1` (role:artifact-type-owner): Artifact Type owner admission for this exact v2 successor contract. Consequence: v2 remains candidate-only and v1 remains admitted-current.
- `CRB2-R2` (role:migration-consumer-owner): A separately admitted binding instance and consumer activation decision. Consequence: No implementation, workflow, service, or Agent capability is adopted or activated.

## Claim ceiling

This candidate is the immutable Capability Realization Binding/v2 successor with its own admitted positive Definition. PASS proves its exact schema, semantic binding, predecessor, fixtures, and non-collapse rules; it does not admit v2 or an instance, transition v1, adopt a realization, establish conformance, operation, effectiveness, or Product value, or activate a consumer.
