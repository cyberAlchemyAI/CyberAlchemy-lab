<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Coordination Context Artifact Type v2

- Artifact Type: `cal.artifact-type.coordination-context/v2`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Distinct validation purpose

Proves one durable owner-qualified coordination frame with exactly one Product, independently optional Project and Goal anchors, stable purpose, explicit consumers, uses, subject scope, source policies, independently owned Bounded Context references, predecessor-directed lifecycle, non-collapse enforcement, and deterministic read-only relation projections.

## Orthogonality rules

- **CCV2-01-ENDPOINT-IDENTITY**: Coordination Context identity remains distinct from Product, Project, Goal, every referenced Bounded Context, and owner identity.
- **CCV2-02-OPTIONAL-AXES**: Product cardinality is exactly one while Project and Goal are independently zero-or-one and use explicit null for canonical absence.
- **CCV2-03-CARRIER-NON-COLLAPSE**: Coordination Context cannot become Product, Project, Goal, Context, Context Profile, Context View, Bounded Context, Agent Session, Work, source selection, decision, or execution authority by embedded fields or references.
- **CCV2-04-REFERENCE-NON-INFERENCE**: Framing references do not imply membership, ownership, authority, identity equivalence, adoption, execution, or target lifecycle state.
- **CCV2-05-SUCCESSION**: Changing Product, Project, Goal, or purpose requires a new Coordination Context identity that names its predecessor.
- **CCV2-06-RELATION-PROJECTION**: Canonical reference fields are the sole writable authority; Typed Relations are deterministic read-only projections admitted separately under the Typed Connection Extension Rule.

## Claim ceiling

This package is a Coordination Context/v2 Artifact Type successor candidate. PASS can prove only its exact schema, Definition and predecessor bindings, fixture behavior, expanded non-collapse and lifecycle checks, relation-extension residue, and deterministic projections. It does not admit or supersede an Artifact Type, migrate or create an instance, admit Relation endpoints, grant authority, activate work, or retain Agent Session memory.
