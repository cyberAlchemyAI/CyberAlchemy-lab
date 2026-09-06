<!-- GENERATED FILE: canonical data is audit.json. -->

# Selected current-tree Artifact Surface audit

- Result: `complete-with-visible-residue`
- Authority effect: `none`

## Findings

### ASF-AUDIT-001 — resolved-by-admitted-type

The 17 principal Context carriers inspected have explicit admitted Artifact Type references.

- Path: `contexts/`
- Treatment: Preserve; package-home manifests remain later work.

### ASF-AUDIT-002 — resolvable-by-registry-discriminator

Goal resolves through schema_version to admitted Goal/v1 without directory inference.

- Path: `coordination/goals/craft-product-foundation/v1/goal.json`
- Treatment: Preserve; later declare its package home.

### ASF-AUDIT-003 — resolvable-by-registry-discriminator

Project resolves through schema_version to admitted Project Identity/v1.

- Path: `coordination/projects/craft/v1/project.json`
- Treatment: Preserve; later declare its package home.

### ASF-AUDIT-004 — resolvable-by-registry-discriminator

Ontology Product resolves through schema_version to admitted Product Identity/v1.

- Path: `product/products/ontology/v1/product.json`
- Treatment: Preserve; do not infer Product ownership for sibling files.

### ASF-AUDIT-005 — unresolved-first-class-candidate

Source Closure has no admitted Artifact Type mapping.

- Path: `product/products/ontology/v1/source-closure.json`
- Treatment: Owner must choose declared component or Artifact Type Request; no automatic type creation.

### ASF-AUDIT-006 — unresolved-first-class-candidate

Product Ontology has no admitted Artifact Type mapping.

- Path: `product/products/ontology/v1/product-ontology/ontology.json`
- Treatment: Route through exact semantic/type analysis before canonical use.

### ASF-AUDIT-007 — unresolved-first-class-candidate

Runtime Binding has no admitted Artifact Type mapping.

- Path: `implementation/bindings/ontology-product-lifecycle/v1/binding.json`
- Treatment: Likely Artifact Type Request; owner must confirm distinct validation purpose.

### ASF-AUDIT-008 — candidate-type-not-admitted

Ontology Package/v1 exists physically but is absent from the admitted registry postimage.

- Path: `authority/artifact-types/ontology-package/v1/artifact.json`
- Treatment: Keep candidate-only; do not consume as an admitted type.

### ASF-AUDIT-009 — nested-package-decision-open

The nested source package has migration, generator, validator, imported sources, and evidence but no explicit lifecycle-owner/unit-of-change declaration.

- Path: `product/products/ontology/v1/product-ontology/source-package/`
- Treatment: Do not infer independence; decide during package-manifest authoring.

## Claim ceiling

Selected-surface diagnostic only. It does not establish repository-wide conformance, decide whether unresolved files are components or Artifact instances, or authorize migration.
