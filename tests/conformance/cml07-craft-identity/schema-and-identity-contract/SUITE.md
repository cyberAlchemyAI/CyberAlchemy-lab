<!-- GENERATED FILE: canonical source is suite.json. -->

# CML-07 Craft Identity Schema and Contract Suite

- Suite: `CAL-CML07-S3-S4-CRAFT-IDENTITY-SUITE-0001`
- Status: `candidate-evidence`
- Carrier subjects: `6`
- Hostile cases: `10`
- Approval checkpoints before final bundle: `0`
- Final approval checkpoints: `1`

## Carrier subjects

- `cal.artifact-type.product-identity/v1` → `product/products/craft/v1/product.json` (identity field `product_id`)
- `cal.artifact-type.project-identity/v1` → `coordination/projects/craft/v1/project.json` (identity field `project_id`)
- `cal.artifact-type.method-binding/v1` → `product/products/craft/v1/method-binding.json` (identity field `binding_id`)
- `cal.artifact-type.goal/v1` → `coordination/goals/craft-product-foundation/v1/goal.json` (identity field `goal_id`)
- `cal.artifact-type.identity-lineage/v1` → `authority/lineage/craft/v1/lineage.json` (identity field `lineage_id`)
- `cal.artifact-type.identity-graph/v1` → `product/products/craft/v1/identity-graph.json` (identity field `graph_id`)

## Hostile cases

- `CML07-H01-PRODUCT-PROJECT-FIELD-COLLAPSE` must reject `closed-product-schema`
- `CML07-H02-INFERRED-CRAFT-CONTEXT` must reject `no-context-inference`
- `CML07-H03-PROJECT-ID-COLLAPSES-INTO-PRODUCT` must reject `cross-carrier-identity-distinctness`
- `CML07-H04-METHOD-SUBJECT-COLLAPSE` must reject `method-and-subject-distinctness`
- `CML07-H05-GOAL-ACHIEVEMENT-INFERENCE` must reject `closed-goal-schema`
- `CML07-H06-LINEAGE-CONTEXT-SUBSTITUTION` must reject `product-lineage-only`
- `CML07-H07-LINEAGE-ENDPOINT-COLLAPSE` must reject `explicit-lineage-endpoints`
- `CML07-H08-UNRESOLVED-GRAPH-ENDPOINT` must reject `endpoint-resolution`
- `CML07-H09-INVALID-RELATION-SIGNATURE` must reject `directional-relation-signature`
- `CML07-H10-DUPLICATE-GRAPH-NODE` must reject `unique-node-identity`

## Single approval boundary

All S3 carrier construction and S4 evidence collection complete before one immutable digest-bound owner decision is requested.

## Claim ceiling

PASS establishes only validation plus schema and identity-contract conformance for the exact candidate CML-07 carrier set. It does not admit a carrier, achieve the Goal, establish implementation or runtime conformance, complete migration, publish, deploy, or establish a stable release.
