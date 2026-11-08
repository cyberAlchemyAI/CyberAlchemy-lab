# Whole-Lab workspace model mapping

Status: current candidate workspace catalog plus retained earlier architecture/path evidence. Authority effect: none.

Use **Product Workspaces** under workspaces/products/ and **Project Workspaces** under workspaces/projects/. The Lab Product remains at repository root. Shared operations serve both kinds by default; specialization does not require a dedicated runtime.

The 7 November active map contains **8 Product scope entries and no separately selected Project Workspace**. TROQAR, Engineer Assessment and Agentic Research Network are external workspaces. Definition NFT and Lab migration are removed from the active plan. Ontology Product and Ontology Lifecycle share one proposed Product workspace, with distinct Product/Project/component identities.

Each Product keeps its development Project coordination and Work in one home. Craft coordination stays in Craft; Ontology Lifecycle stays in Ontology. The Lab root contains its Formal Assurance Project and related theorem-checker Work. See [the one Product home rule](PRODUCT-COLOCATION.md) and [the complete folder structure](FOLDER-STRUCTURE.md).

## Read selectively

| Need | Record |
| --- | --- |
| Current active map, external references and retired entries | [Workspace catalog](WORKSPACES.md), [machine source](inventory/workspace-catalog.json) |
| Cleanup and content migration findings | [Cleanup result](CLEANUP-20261107.md), [file comparison](inventory/external-comparison-20261107.json) |
| Ontology Product versus lifecycle and one shared development home | [Ontology workspace](ONTOLOGY-WORKSPACE.md) |
| Naming, boundary and Goal/entity rules | [Workspace boundaries](WORKSPACE-BOUNDARIES.md) |
| Earlier Project-only model compatibility gap | [Model revision](MODEL-REVISION.md) |
| Cross-area responsibilities and current source | [Architecture](ARCHITECTURE.md), [capability map](CAPABILITY-MAP.md) |
| Future source/consumer transitions and evolution | [Migration map](MIGRATION-MAP.md), [evolution](EVOLUTION.md) |
| Earlier reusable architecture patterns | [Pattern library](ARCHITECTURE-PATTERN-LIBRARY.md) |
| Source-bound catalog checks and dated whole-path evidence | [Inventory](inventory/README.md) |

## Current evidence

The content audit compared 5,139 selected ARN/Engineer Assessment Lab files with explicit current external paths. No missing current source requiring migration was identified. External source was not overwritten; older proposal/capture cuts remain historical evidence.

The catalog checker verifies source hashes, subject identities, exact D71 overlay standing, external registrations, removed and embedded scopes, coverage and Markdown parity. It does not establish native adoption, runtime qualification or lifecycle completion.

The earlier whole-path inventory and pattern package retain their dated evidence. Their observations are not silently refreshed. The old concrete workspace profile still requires one primary Project; Product/Project typing needs the successor specified in MODEL-REVISION.md.

No physical workspace containers or source moves were created by this catalog work.

## Physical migration applied: 7 November 2026

The physical homes in [FOLDER-STRUCTURE.md](FOLDER-STRUCTURE.md) are now applied. Earlier proposed-path descriptions above are retained design context. Current locations and source pins are in [WORKSPACES.md](WORKSPACES.md). Old locations are compatibility links. Shared Lab operations remain in root implementation/; shared runtimes were not copied. Imported snapshots, frozen Define Packs, native identities and admissions retain their existing standing. See the [migration report](../../docs/migration-plans/0008-product-workspaces-20261107/REPORT.md).
