<!-- GENERATED FILE: canonical suite is suite.json; result is receipts/validation.json. -->

# CML-07 S2 Identity Artifact Type Conformance

- Result: `PASS`
- Checks: `16/16`
- Subjects: `6`
- Hostile fixtures: `13`

## Subjects

- `cal.artifact-type.product-identity/v1` — identity field `product_id`
- `cal.artifact-type.project-identity/v1` — identity field `project_id`
- `cal.artifact-type.method-binding/v1` — identity field `binding_id`
- `cal.artifact-type.goal/v1` — identity field `goal_id`
- `cal.artifact-type.identity-graph/v1` — identity field `graph_id`
- `cal.artifact-type.identity-lineage/v1` — identity field `lineage_id`

## Cohort invariants

- **CML07-S2-I01**: Six Artifact Type identities, schemas, and instance identity fields are pairwise distinct.
- **CML07-S2-I02**: Every registration is classified under admitted Artifact Type/v2 and binds admitted semantic Definitions.
- **CML07-S2-I03**: Each closed schema owns one canonical machine filename and one generated human projection filename.
- **CML07-S2-I04**: Product, Project, Method Binding, Goal, Identity Graph, and Identity Lineage cannot substitute for one another through labels, directories, embedded endpoint definitions, or redundant canonical axes.
- **CML07-S2-I05**: All thirteen hostile collapse, inference, endpoint, and signature fixtures are rejected.
- **CML07-S2-I06**: Schema conformance is assessed separately from admission, identity-contract conformance, implementation conformance, and runtime conformance.

## Claim ceiling

A PASS suite proves only candidate schema-and-artifact-type-contract conformance for the six exact packages and their fixtures. It does not admit the types, execute S3, validate real Craft carriers, or establish identity-contract, implementation, or runtime conformance.
