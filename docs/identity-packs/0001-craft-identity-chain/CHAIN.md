<!-- GENERATED FILE: edit chain.json and run build.py. -->

# Craft Product Project Method and Goal Identity Chain

> Candidate construction chain; no admission or implementation authority.

## Sequence

### CML07-S0-ADMIT-SOURCES-AND-BIND-OWNERS

After this stage, we know whether every identity meaning and accountable owner can be named without importing authority from the legacy repository.

Outputs:

- `authority/decisions/source-admission/craft-identity-v1/v1/admissions.json`
- `authority/owners/foundation-01/v1/candidates/0004-craft-identity/owner-bindings.json`

Effect: Makes the semantic Definition stage evaluable only.

### CML07-S1-AUTHOR-CANONICAL-DEFINITIONS

After this stage, we know whether Product, Project, Method, Craft Method, Goal, and their non-collapse relations have sufficient canonical meaning for artifact contracts.

Outputs:

- `authority/definitions/candidates/0006-craft-identity/definitions/product/v1/definition.json`
- `authority/definitions/candidates/0006-craft-identity/definitions/method/v1/definition.json`
- `authority/definitions/candidates/0006-craft-identity/definitions/craft-method/v1/definition.json`
- `authority/definitions/candidates/0006-craft-identity/definitions/goal/v1/definition.json`
- `authority/definitions/candidates/0006-craft-identity/definitions/project/v1/definition.json`
- `authority/definitions/candidates/0006-craft-identity/definitions/identity-relation/v1/definition.json`

Effect: Makes identity Artifact Type authoring evaluable only.

### CML07-S2-AUTHOR-IDENTITY-ARTIFACT-TYPES

After this stage, we know whether each identity carrier can be independently validated without collapsing Product, Project, Method, Goal, or graph membership.

Outputs:

- `authority/artifact-types/product-identity/v1/`
- `authority/artifact-types/project-identity/v1/`
- `authority/artifact-types/method-binding/v1/`
- `authority/artifact-types/goal/v1/`
- `authority/artifact-types/identity-graph/v1/`
- `authority/artifact-types/identity-lineage/v1/`

Effect: Makes candidate identity instances evaluable only.

### CML07-S3-MATERIALIZE-CRAFT-IDENTITY-CARRIERS

After this stage, we know whether the selected Craft Product lineage can be represented through separate Product, Project, Method, Goal, lineage, and relation carriers.

Outputs:

- `product/products/craft/v1/product.json`
- `product/products/craft/v1/PRODUCT.md`
- `product/products/craft/v1/method-binding.json`
- `product/products/craft/v1/METHOD-BINDING.md`
- `coordination/projects/craft/v1/project.json`
- `coordination/projects/craft/v1/PROJECT.md`
- `coordination/goals/craft-product-foundation/v1/goal.json`
- `coordination/goals/craft-product-foundation/v1/GOAL.md`
- `authority/lineage/craft/v1/lineage.json`
- `authority/lineage/craft/v1/LINEAGE.md`
- `product/products/craft/v1/identity-graph.json`
- `product/products/craft/v1/IDENTITY-GRAPH.md`

Effect: Makes one exact CML-07 admission request set eligible for review only.

### CML07-S4-VALIDATE-AND-AUTHOR-ADMISSION-BUNDLE

After this stage, we know whether the complete Craft identity graph is dependency-closed, rollback-bound, and ready for one final owner decision.

Outputs:

- `tests/conformance/cml07-craft-identity/`
- `evidence/validation/cml07-craft-identity/receipts/`
- `docs/admission-bundles/0002-craft-identity-v1/manifest.json`
- `docs/admission-bundles/0002-craft-identity-v1/receipts/validation.json`

Effect: Presents one digest-bound Decision Request Set; performs no admission.

## Non-regression guarantees

- Machine records remain canonical and every human view is generated.
- Product, Project, Method, Goal, Product Capability, capability instance, Bounded Context, module, package, and directory remain separate identities.
- Craft remains the same Product lineage renamed from DomainSpec v2.
- Stable CAV2 and DS source IDs are preserved where an actual source Definition exists.
- Craft Product does not imply a Craft root Bounded Context.
- Source repositories remain read-only and no bulk copy or global replacement occurs.
- Each stage validates before its successor becomes evaluable; validation never auto-admits the successor.
- Human approval occurs once, at the final digest-bound CML-07 bundle boundary.

## Recommended next unit

`CML07-W0-SOURCE-OWNER-DEFINITIONS` — Author the exact source-admission candidate, owner-binding successor, and six-Definition candidate pack for stages S0 and S1.

## Claim ceiling

This candidate authors the dependency graph, paths, decision boundaries, and validation obligations for CML-07 only. It does not admit a source, owner, Definition, Artifact Type, Product, Project, Method, Goal, relation, lineage, context, implementation, publication, deployment, or stable release.
