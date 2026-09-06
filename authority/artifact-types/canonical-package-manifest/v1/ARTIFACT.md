<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Canonical Package Manifest Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.canonical-package-manifest/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Canonical instance: `package.json`
- Human projection: `PACKAGE.md`

## Semantic bindings

- `cal.definition.artifact-type@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/artifact-type/v1/definition.json`
- `cal.definition.canonical-package-home@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0008-canonical-package-home/definitions/canonical-package-home/v1/definition.json`
- `cal.definition.canonical-package-manifest@1.0.0-candidate.1` — `candidate-unadmitted` — `authority/definitions/candidates/0009-artifact-surface-foundation/definitions/canonical-package-manifest/v1/definition.json`
- `cal.definition.artifact-surface-classification@1.0.0-candidate.1` — `candidate-unadmitted` — `authority/definitions/candidates/0009-artifact-surface-foundation/definitions/artifact-surface-classification/v1/definition.json`

## Distinct validation purpose

Proves one package home declares its aggregate, owner, unit of change, canonical carriers, supporting roles, transients, and independent nested packages without deriving semantics from paths.

## Orthogonality rules

- **ASF-CPM-01**: Package identity, aggregate identity, Artifact Type identity, context identity, and filesystem root remain distinct.
- **ASF-CPM-02**: Every canonical carrier has exactly one admitted type resolution and one package home.
- **ASF-CPM-03**: An independent nested lifecycle requires its own manifest and explicit parent relation.

## Four facets

- **Classification**: The package manifest is a distinct Artifact Type/v2 candidate.
- **Schema**: schema.json closes file roles, carrier resolution, nested packages, owner, and unit of change.
- **Human Continuation**: PACKAGE.md is generated from package.json.
- **Machine Checkable**: One-home resolution, declared roles, nested lifecycle boundaries, hostile role collapse, and projection parity are executable.

## Typed residue

- `ASF-CPM-R1` (role:definition-owner): The manifest and surface-classification Definitions remain candidate-unadmitted. Consequence: The type cannot be admitted.
- `ASF-CPM-R2` (role:artifact-mechanics-owner): Existing package homes have no manifests under this contract. Consequence: Current-tree audit findings remain diagnostic and migration is not authorized.

## Claim ceiling

Candidate package-declaration contract only. PASS does not select a package home, migrate files, or grant lifecycle authority.
