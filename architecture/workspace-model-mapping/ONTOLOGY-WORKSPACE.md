# One Ontology Product Workspace

Status: source-backed workspace organization proposal, 7 November 2026. Authority effect: none.

## Different responsibilities inside one scope

| Existing asset | Responsibility |
| --- | --- |
| [Ontology Product](../../product/products/ontology/v1/product.json) | Product value and output boundary: source-bound, typed ontology packages that can be inspected, retrieved and evolved. Product identity is CA2-PRODUCT-ONTOLOGY. |
| [Ontology Product package implementation](../../product/products/ontology/v1/runtime/src/lib.rs) | Constructs and validates the package interface: source references, typed nodes/relations, retrieval and residue. Rust package is cal-ontology-product. |
| [Ontology Lifecycle engine](../../ontology-lifecycle/runtime/src/lib.rs) | Stores semantic/governance changes and rebuilds state at a selected history cut. Rust package is cal-ontology-lifecycle. |
| [Lifecycle integration Project selection](../../docs/plans/0003-d65-native-ontology-integration/d65-plan.json) | Coordinates the existing CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE Project, with its own Goals and construction history. |

The Product describes the usable output and value boundary. Lifecycle supplies change/history behavior. These different responsibilities do not require different workspaces.

There is already a [Product event-runtime realization candidate](../../product/products/ontology/v1/candidates/0006-event-runtime-realization/README.md) that converts selected ontology records into canonical event histories and uses the Rust lifecycle engine to derive current views. The earlier [cohesive system candidate](../../product/products/ontology/v1/candidates/0005-cohesive-lab-system/README.md) also composes Product and lifecycle/context material while retaining each source's standing.

## Proposed workspace home

Use workspaces/products/ontology/ as one development home. Its eight areas can select:

| Area | Selected content / responsibility |
| --- | --- |
| product | Ontology Product identity, thesis, package output and capabilities |
| project | Existing lifecycle/integration Project identity reference and future independently identified Projects |
| work | Ontology development, integration Goals, plans, tasks, blockers and current assessments |
| authority | Applicable source-owned meanings/contracts and exact Product/Project decisions |
| ontology | Business/system models, bridge declarations and selected source bindings |
| architecture | Package/interface versus event-engine boundaries and dependency rules |
| implementation | Separate ontology-package and ontology-lifecycle packages plus explicitly selected adapters/readers |
| docs | Usage, package interface, lifecycle behavior and recovery explanations |

A Product workspace can contain several Projects without turning each capability, runtime or namespace into another workspace. The lifecycle Project remains a Project with its original identity. The workspace does not transfer semantic ownership or create a new combined native identity.

## Preserve implementation and history boundaries

Keep both Cargo packages and their public interfaces. Consolidating workspace organization does not mean flattening two Rust libraries into one crate. Current source remains at product/products/ontology/v1/ and ontology-lifecycle/ until a bounded functional-source/consumer transition is selected.

Frozen Product candidates, D65 activation/adoption evidence, semantic/governance histories and source snapshots remain exact. Selected current authored material can later receive new homes, with explicit imports and compatibility updates. Shared consumers such as Craft's ontology reader and Body War's runtime links must continue to resolve.

The [current catalog](WORKSPACES.md) now has one active Ontology Product Workspace and records the lifecycle Project as embedded. Physical migration, a successor operating-model binding, Product acceptance and runtime adoption remain separate work.

## Physical migration applied: 7 November 2026

The physical homes in [FOLDER-STRUCTURE.md](FOLDER-STRUCTURE.md) are now applied. Earlier proposed-path descriptions above are retained design context. Current locations and source pins are in [WORKSPACES.md](WORKSPACES.md). Old locations are compatibility links. Shared Lab operations remain in root implementation/; shared runtimes were not copied. Imported snapshots, frozen Define Packs, native identities and admissions retain their existing standing. See the [migration report](../../docs/migration-plans/0008-product-workspaces-20261107/REPORT.md).
