<!-- GENERATED FILE: edit chain.json and run build.py. -->

# Craft Identity Chain with Semantic and Conformance Closure

> Candidate successor chain; no admission or implementation authority.

- Chain: `CAL-CML07-CRAFT-IDENTITY-CHAIN-0002`
- Predecessor: `CAL-CML07-CRAFT-IDENTITY-CHAIN-0001`

## Conformance vocabulary

- **Evaluation** — `cal.definition.evaluation@1.0.0-candidate.1`; Apply one exact profile to one exact subject and collect every declared outcome.
- **Validation** — `cal.definition.validation@1.0.0-candidate.1`; Evaluate declared validation criteria and emit a Validation Receipt.
- **Schema Conformance** — `cal.definition.conformance@1.0.0-candidate.1`; Assert only that an exact machine artifact satisfies an exact closed schema under a complete applicable profile.
- **Identity Contract Conformance** — `cal.definition.conformance@1.0.0-candidate.1`; Assert only that exact CML-07 carriers and relations satisfy their admitted identity and non-collapse obligations.
- **Implementation Conformance** — `cal.definition.conformance@1.0.0-candidate.1`; deferred-beyond-cml07
- **Runtime Conformance** — `cal.definition.conformance@1.0.0-candidate.1`; deferred-beyond-cml07

Validation PASS does not imply conformance; schema or identity-contract conformance does not imply implementation or runtime conformance; no conformance scope implies admission.

## Sequence

### CML07-S0-ADMIT-SOURCES-AND-BIND-OWNERS

After this stage, we know whether every selected meaning and accountable owner is exact without importing authority by proximity.

Outputs:

- `authority/decisions/source-admission/craft-identity-v1/v1/admissions.json`
- `authority/owners/foundation-01/v1/candidates/0004-craft-identity/owner-bindings.json`

Effect: Makes the two-part semantic candidate stage evaluable only.

### CML07-S1A-AUTHOR-IDENTITY-DEFINITIONS

After this stage, Product, Project, Method, Craft Method, Goal, and Identity Relation have independent candidate meanings without identity collapse.

Outputs:

- `authority/definitions/candidates/0006-craft-identity/`

Effect: Makes semantic-closure candidate authoring evaluable only.

### CML07-S1B-AUTHOR-SEMANTIC-CLOSURE

After this stage, Artifact Type construction and schema or identity-contract conformance use explicit meanings without implying runtime conformance or authority.

Outputs:

- `authority/definitions/candidates/0007-cml07-semantic-closure/`
- `authority/artifact-types/artifact-type/v2/`

Effect: Makes S2 reviewable only after exact semantic and Artifact Type predecessors are admitted at the final configured boundary.

### CML07-S2-AUTHOR-IDENTITY-ARTIFACT-TYPES

After this stage, each identity artifact kind has a closed schema and explicit semantic Definition bindings under Artifact Type/v2.

Outputs:

- `authority/artifact-types/product-identity/v1/`
- `authority/artifact-types/project-identity/v1/`
- `authority/artifact-types/method-binding/v1/`
- `authority/artifact-types/goal/v1/`
- `authority/artifact-types/identity-graph/v1/`
- `authority/artifact-types/identity-lineage/v1/`

Effect: Makes candidate identity instances evaluable only.

### CML07-S3-MATERIALIZE-CRAFT-IDENTITY-CARRIERS

After this stage, the selected Craft Product lineage is represented through separate Product, Project, Method, Goal, lineage, and relation carriers.

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

Effect: Makes schema-and-identity-contract conformance assessment and one exact admission request set eligible for review only.

### CML07-S4-VALIDATE-ASSESS-CONFORMANCE-AND-AUTHOR-ADMISSION-BUNDLE

After this stage, we know whether the exact Craft identity artifact set passes its validation profiles and separately conforms to its schema and identity contracts, without any implementation or runtime claim.

Outputs:

- `tests/conformance/cml07-craft-identity/schema-and-identity-contract/`
- `evidence/validation/cml07-craft-identity/receipts/`
- `evidence/conformance/cml07-craft-identity/schema-and-identity-contract/`
- `docs/admission-bundles/0002-craft-identity-v1/manifest.json`
- `docs/admission-bundles/0002-craft-identity-v1/receipts/validation.json`

Effect: Presents one digest-bound Decision Request Set; performs no admission.

## Non-regression guarantees

- Machine records remain canonical and every human view is generated.
- Candidate 0006 and chain 0001 remain byte-preserved predecessors.
- Product, Project, Method, Goal, Product Capability, capability instance, Bounded Context, module, package, and directory remain separate identities.
- Craft remains the same Product lineage renamed from DomainSpec v2.
- Every Artifact Type registration authored under v2 carries explicit semantic Definition references.
- Validation PASS never implies conformance or admission.
- Schema and identity-contract conformance never imply implementation or runtime conformance.
- Human approval occurs once, at the final digest-bound CML-07 bundle boundary configured by the active workflow decision profile.

## Recommended next unit

`CML07-W0B-SEMANTIC-CLOSURE-REVIEW` — Review candidate 0006, semantic-closure candidate 0007, Artifact Type/v2, source admissions, owner bindings, and this successor chain as one dependency-closed pre-S2 cohort.

## Deferred

- Product Capability selection and capability instance construction (CML-08)
- capability-local business ontology (CML-09)
- Craft authored specification and compiled graph
- implementation binding
- implementation conformance
- runtime conformance
- publication
- stable release

## Claim ceiling

This successor candidate authors the revised CML-07 dependency graph, semantic bindings, terminology, and validation obligations only. It preserves predecessor bytes and does not admit a source, owner, Definition, Artifact Type, identity carrier, relation, lineage, context, conformance claim, implementation, publication, deployment, or stable release.
