<!-- GENERATED FILE: canonical data is audit.json. -->

# Computed selected-tree Artifact Surface audit

- Result: `PASS`
- Authority effect: `none`

## Findings

### ASF-AUDIT-002-001 — resolved

Governance Context v1 must resolve from explicit machine evidence.

- Path: `contexts/governance/v1/context.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-002 — resolved

Governance Language v1 must resolve from explicit machine evidence.

- Path: `contexts/governance/v1/language.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-003 — resolved

Governance Context v2 carrier must resolve from explicit machine evidence.

- Path: `contexts/governance/v2/context.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-004 — resolved

Governance Language v2 carrier must resolve from explicit machine evidence.

- Path: `contexts/governance/v2/language.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-005 — resolved

Governance successor Context must resolve from explicit machine evidence.

- Path: `contexts/governance/v3/context.json`
- Treatment: Preserve; candidate lifecycle remains separate.

### ASF-AUDIT-002-006 — resolved

Ontology Lifecycle Context v1 must resolve from explicit machine evidence.

- Path: `contexts/ontology-lifecycle/v1/context.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-007 — resolved

Ontology Lifecycle Language v1 must resolve from explicit machine evidence.

- Path: `contexts/ontology-lifecycle/v1/language.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-008 — resolved

Ontology Lifecycle Context v2 carrier must resolve from explicit machine evidence.

- Path: `contexts/ontology-lifecycle/v2/context.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-009 — resolved

Ontology Lifecycle Language v2 carrier must resolve from explicit machine evidence.

- Path: `contexts/ontology-lifecycle/v2/language.json`
- Treatment: Preserve; no path inference.

### ASF-AUDIT-002-010 — resolved

Ontology Lifecycle successor Context must resolve from explicit machine evidence.

- Path: `contexts/ontology-lifecycle/v3/context.json`
- Treatment: Preserve; candidate lifecycle remains separate.

### ASF-AUDIT-002-011 — resolved

Governance lineage v1 must resolve from explicit machine evidence.

- Path: `contexts/lineage/governance/v1/lineage.json`
- Treatment: Preserve.

### ASF-AUDIT-002-012 — resolved

Governance lineage v2 must resolve from explicit machine evidence.

- Path: `contexts/lineage/governance/v2/lineage.json`
- Treatment: Preserve.

### ASF-AUDIT-002-013 — resolved

Ontology Lifecycle lineage v1 must resolve from explicit machine evidence.

- Path: `contexts/lineage/ontology-lifecycle/v1/lineage.json`
- Treatment: Preserve.

### ASF-AUDIT-002-014 — resolved

Ontology Lifecycle lineage v2 must resolve from explicit machine evidence.

- Path: `contexts/lineage/ontology-lifecycle/v2/lineage.json`
- Treatment: Preserve.

### ASF-AUDIT-002-015 — resolved

Context Map v1 must resolve from explicit machine evidence.

- Path: `contexts/maps/governance-ontology-lifecycle/v1/map.json`
- Treatment: Preserve as historical carrier.

### ASF-AUDIT-002-016 — resolved

Context Map v2 must resolve from explicit machine evidence.

- Path: `contexts/maps/governance-ontology-lifecycle/v2/map.json`
- Treatment: Preserve as current admitted contract carrier.

### ASF-AUDIT-002-017 — resolved

Context migration manifest must resolve from explicit machine evidence.

- Path: `contexts/migrations/governance-ontology-lifecycle-v1-to-v2/v1/migration.json`
- Treatment: Preserve.

### ASF-AUDIT-002-018 — resolved

Goal must resolve by registered discriminator.

- Path: `coordination/goals/craft-product-foundation/v1/goal.json`
- Treatment: Preserve; later declare package membership.

### ASF-AUDIT-002-019 — resolved

Project must resolve by registered discriminator.

- Path: `coordination/projects/craft/v1/project.json`
- Treatment: Preserve; later declare package membership.

### ASF-AUDIT-002-020 — resolved

Ontology Product identity must resolve by registered discriminator.

- Path: `product/products/ontology/v1/product.json`
- Treatment: Preserve; sibling ownership is not inferred.

### ASF-AUDIT-002-021 — unresolved

Source Closure has no admitted-current Artifact Type mapping.

- Path: `product/products/ontology/v1/source-closure.json`
- Treatment: Owner must choose component treatment or an Artifact Type Request.

### ASF-AUDIT-002-022 — unresolved

Product Ontology has no admitted-current Artifact Type mapping.

- Path: `product/products/ontology/v1/product-ontology/ontology.json`
- Treatment: Route through semantic and type analysis before canonical consumption.

### ASF-AUDIT-002-023 — unresolved

Runtime Binding has no admitted-current Artifact Type mapping.

- Path: `implementation/bindings/ontology-product-lifecycle/v1/binding.json`
- Treatment: Likely Artifact Type Request; owner must confirm distinct validation purpose.

### ASF-AUDIT-002-024 — candidate-type-not-admitted

Ontology Package/v1 exists as a represented candidate type but is absent from the admitted registry.

- Path: `authority/artifact-types/ontology-package/v1/artifact.json`
- Treatment: Keep candidate-only; do not consume as admitted.

### ASF-AUDIT-002-025 — package-boundary-open

The source-package directory contains a lifecycle-shaped surface but has no selected package boundary.

- Path: `product/products/ontology/v1/product-ontology/source-package`
- Treatment: Do not infer independence; decide during package-manifest authoring.

## Claim ceiling

Computed selected-surface diagnostic only. It does not establish repository-wide conformance, choose package boundaries, admit types, or authorize migration.
