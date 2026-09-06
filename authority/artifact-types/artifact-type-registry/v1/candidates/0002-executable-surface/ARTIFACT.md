<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Artifact Type Registry Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.artifact-type-registry/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Canonical instance: `registry.json`
- Human projection: `REGISTRY.md`

## Semantic bindings

- `cal.definition.artifact-type@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/artifact-type/v1/definition.json`
- `cal.definition.artifact-type-registry@1.0.0-candidate.1` — `candidate-unadmitted` — `authority/definitions/candidates/0009-artifact-surface-foundation/definitions/artifact-type-registry/v1/definition.json`
- `cal.definition.artifact-type-resolution@1.0.0-candidate.2` — `candidate-unadmitted` — `authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/artifact-type-resolution/v1/definition.json`

## Distinct validation purpose

Proves one registry maps exact Artifact Type versions, discriminators, contracts, schemas, definitions, lifecycle overlays, and decisions without duplicating carriers or manufacturing admission.

## Orthogonality rules

- **ASF-ATR-01**: Registry entry, Artifact Type contract, schema, Definition, and admission decision retain separate identities.
- **ASF-ATR-02**: Current and historical state comes only from exact decision overlays, never embedded candidate status.
- **ASF-ATR-03**: A discriminator maps to at most one admitted current type.

## Four facets

- **Classification**: The registry is an Artifact Type/v2 candidate with no authority effect.
- **Human Continuation**: REGISTRY.md is generated from canonical registry bytes.
- **Machine Checkable**: Exact digests, unique identities and discriminators, lifecycle overlays, hostile candidates, and projection parity are executable.
- **Schema**: schema.json is a closed contract for registry.json.

## Typed residue

- `ASF-ATR-R1` (role:definition-owner): The semantic Definition candidates are not admitted. Consequence: The Artifact Type cannot be admitted.
- `ASF-ATR-R2` (role:artifact-type-owner): No owner decision admits this Artifact Type or initial registry postimage. Consequence: The live repository still has no current Artifact Type registry.

## Claim ceiling

Candidate Artifact Type contract only. PASS does not admit the type, create a live registry, or alter any recorded lifecycle state.
