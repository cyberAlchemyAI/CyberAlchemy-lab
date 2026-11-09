<!-- GENERATED from inventory/workspace-catalog.json by inventory/check_workspaces.py --render. -->

# Product Workspaces and Project Workspaces

Status: physical ownership migration and runtime model v2 implemented; native admission unchanged, 2026-11-07. Authority effect: none.

Product Workspaces use `workspaces/products/`; Project Workspaces use `workspaces/projects/`. Both use shared operations by default. Catalog registration does not provision a runtime or change native authority.

The active Lab map has **8 Product Workspace candidates and 0 Project Workspace candidates**. Three external workspaces are listed separately. Each Product keeps its Project coordination and Work in the same home. Craft, Ontology and the Lab have embedded Projects; the theorem checker is Lab Work. Definition NFT and Lab migration remain removed from the active plan.

## Active Product Workspaces

| Workspace | Existing source | Current physical material | Catalog location |
| --- | --- | --- | --- |
| **CyberAlchemy Lab** | `product:cyberalchemy-lab`<br>[Source](../../authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product.json) | `.` | `workspaces/products/cyberalchemy-lab`<br>physical home remains `.` |
| **Craft** | `CA2-PRODUCT-CRAFT`<br>[Source](../../workspaces/products/craft/product/product.json) | `workspaces/products/craft` | `workspaces/products/craft` |
| **Define** | product-document; native identity unselected<br>[Source](../../workspaces/products/define/README.md) | `workspaces/products/define` | `workspaces/products/define` |
| **Ontology** | `CA2-PRODUCT-ONTOLOGY`<br>[Source](../../workspaces/products/ontology/implementation/ontology-package/product.json) | `workspaces/products/ontology` | `workspaces/products/ontology` |
| **People and Teams** | boundary-proposal; native identity unselected<br>[Source](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0072-people-teams-context-import/README.md) | `workspaces/products/people-and-teams` | `workspaces/products/people-and-teams` |
| **CyberAlchemy Lab website** | product-document; native identity unselected<br>[Source](../../workspaces/products/lab-website/implementation/site/PRODUCT.md) | `workspaces/products/lab-website` | `workspaces/products/lab-website` |
| **Trusted Dataset Materialization** | `lab:trusted-dataset-materialization#CAL-PRODUCT-TRUSTED-DATASET-MATERIALIZATION`<br>[Source](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0032-trusted-dataset-product-import/result.json) | `workspaces/products/trusted-dataset-materialization` | `workspaces/products/trusted-dataset-materialization` |
| **Agent Reasoning Engine** | `CA2-PRODUCT-AGENT-REASONING-ENGINE`<br>[Source](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0045-agent-reasoning-context-preparation/source/product.json) | `evidence/migrations/cyberalchemy-v2-to-lab/executions/0045-agent-reasoning-context-preparation`<br>`evidence/migrations/cyberalchemy-v2-to-lab/executions/0048-agent-reasoning-context-import` | `workspaces/products/agent-reasoning-engine` |

## Project coordination and Work inside Products

No standalone Project workspace is selected. The projects container is reserved for a future independently justified operating scope. Product, Project and Work identities remain distinct records in one Product home.

| Existing subject | Product home | Record/Work home |
| --- | --- | --- |
| `CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE` | `product/ontology` | `workspaces/products/ontology/project` |
| `CA2-PROJECT-CRAFT` | `product/craft` | `workspaces/products/craft/project` |
| `cal.project.definition-formal-assurance` | `product/cyberalchemy-lab` | `project/definition-formal-assurance` |
| `work/relational-theorem-checker` | `product/cyberalchemy-lab` | `work/plans/relational-theorem-checker` |

Define, People and Teams, website and Trusted Dataset development also keep coordination and Work under their own Product home. Missing Project identities are left unselected rather than invented. The referenced ARE scope stays upstream. External Products keep their Project/Work in their existing external checkout.

- [Current folder structure](FOLDER-STRUCTURE.md)

## External workspaces

| Workspace | Existing checkout | Disposition |
| --- | --- | --- |
| **TROQAR / Body War** | `/home/vlad_/projects/body-war` | Editable source belongs externally. Lab cuts remain historical source/review evidence. |
| **Engineer Assessment** | `/home/vlad_/projects/engineer-assessment` | Editable source belongs externally. Lab cuts remain historical source/review evidence. |
| **Agentic Research Network** | `/home/vlad_/projects/agentic-research-network` | Editable source belongs externally. Lab cuts remain historical source/review evidence. |

These subjects have no proposed Lab-hosted Product or Project workspace. The [content comparison](inventory/external-comparison-20261107.json) checked 5,139 selected Lab files against explicit external source paths. No missing current source requiring migration was identified; no external file was overwritten.

ARN has all 156 counterparts, with 13 publication-specific adaptations. Engineer Assessment has 4,983 retained Lab files spanning exact current matches, earlier versions, frozen review material and Lab contracts. Its originating brief is present with only a repaired relative link. Body War owns its local app model/docs; Craft canary examples and shared dependencies remain referenced.

## One Ontology workspace

Use `workspaces/products/ontology/` for the Product interface, package implementation and embedded Ontology Lifecycle Project/engine. Keep Product identity `CA2-PRODUCT-ONTOLOGY` and Project identity `CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE` distinct.

The Product package turns source meaning into typed packages and retrieval interfaces. Lifecycle records changes and rebuilds state from event histories. Separate implementation packages can share one development workspace. An existing event-runtime Product candidate already composes them. See [the source-backed consolidation](ONTOLOGY-WORKSPACE.md).

## Removed active entries

| Entry | Disposition |
| --- | --- |
| `product/definition-nft` | User withdrew Definition NFT and removed it from the active workspace plan. Historical source/admission bytes remain retained. |
| `project/lab-migration` | User removed the migration Project from the active workspace plan as no longer needed there. Historical source/admission bytes remain retained. |

Removing Lab migration from active planning is not a new native completion Decision. Its D71 Project/state/history references remain exact. Definition NFT has no active workspace or pending workspace work in this map; its unaccepted historical proposal remains in the migration ledger.

## Remaining boundaries

| Active entry | Open items |
| --- | --- |
| `product/cyberalchemy-lab` | Root remains the Lab development workspace; catalog registration does not create a nested copy. |
| `product/craft` | Current runtime model v2 binds the Product workspace and preserves the embedded Craft Project and Goal ownership.<br>Older v1 and newer v2 Product candidates are retained; selection here does not admit or supersede them. |
| `product/define` | No Lab Product identity selected by this catalog.<br>Standalone and legacy CLI source belong to Define; Lab integration is a shared operation consumed by reference. |
| `product/ontology` | Both packages now share one Product home; Product/Project identities and historical contracts remain distinct. |
| `product/people-and-teams` | Workspace created with references to retained domain/model and runtime evidence; no independent native Product identity selected.<br>Person and Team remain domain entities. |
| `product/lab-website` | Confirm standalone Product boundary versus a delivery capability of Lab. Development coordination/Work shares the selected Product home.<br>Do not transfer canonical documentation meaning to the delivery application. |
| `product/trusted-dataset-materialization` | Workspace created with references to exact imported Product/context evidence; no snapshot unpacking or runtime installation. |
| `product/agent-reasoning-engine` | The selected identity is a retained source snapshot; later repaired package material has its own exact bindings.<br>Actual engine source/runtime lives upstream and remains referenced; do not copy it into Lab to satisfy this catalog. |

## Existing plans and proposals

Associations are navigation proposals. External scope labels direct future editing outside Lab. Retained Lab cuts remain addressable; a plan does not automatically create another Project.

| Existing scope | Navigation scope | Source |
| --- | --- | --- |
| `workspaces/products/ontology/work/plans/0001-event-sourced-ontology-first-vertical` | `product/ontology` | [Read](../../workspaces/products/ontology/work/plans/0001-event-sourced-ontology-first-vertical/PLAN.md) |
| `workspaces/products/ontology/work/plans/0002-governed-ontology-node-continuous-plan` | `product/ontology` | [Read](../../workspaces/products/ontology/work/plans/0002-governed-ontology-node-continuous-plan/PLAN.md) |
| `workspaces/products/ontology/work/plans/0003-d65-native-ontology-integration` | `product/ontology` | [Read](../../workspaces/products/ontology/work/plans/0003-d65-native-ontology-integration/PLAN.md) |
| `workspaces/products/ontology/work/plans/0004-d65-export-cutover-candidate` | `product/ontology` | [Read](../../workspaces/products/ontology/work/plans/0004-d65-export-cutover-candidate/README.md) |
| `workspaces/products/ontology/work/plans/0005-d65-post-approval-isolated-rehearsal` | `product/ontology` | [Read](../../workspaces/products/ontology/work/plans/0005-d65-post-approval-isolated-rehearsal/README.md) |
| `workspaces/products/ontology/work/plans/0006-d65-admitted-runtime-activation-cutover` | `product/ontology` | [Read](../../workspaces/products/ontology/work/plans/0006-d65-admitted-runtime-activation-cutover/README.md) |
| `docs/plans/0007-governance-architecture-ontology` | `product/cyberalchemy-lab` | [Read](../../docs/plans/0007-governance-architecture-ontology/PLAN.md) |
| `docs/plans/0008-lab-operational-runtime` | `product/cyberalchemy-lab` | [Read](../../docs/plans/0008-lab-operational-runtime/PLAN.md) |
| `docs/plans/0009-lab-integrated-roadmap` | `product/cyberalchemy-lab` | [Read](../../docs/plans/0009-lab-integrated-roadmap/PLAN.md) |
| `docs/plans/0010-lab-one-shot-execution` | `product/cyberalchemy-lab` | [Read](../../docs/plans/0010-lab-one-shot-execution/PLAN.md) |
| `docs/plans/0011-lab-runtime-completion` | `product/cyberalchemy-lab` | [Read](../../docs/plans/0011-lab-runtime-completion/PLAN.md) |
| `work/plans/definition-formal-assurance` | `product/cyberalchemy-lab` | [Read](../../work/plans/definition-formal-assurance/PROJECT.md) |
| `work/plans/relational-theorem-checker` | `product/cyberalchemy-lab` | [Read](../../work/plans/relational-theorem-checker/ANALYSIS.md) |
| `docs/proposals/0001-context-artifact-architecture` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0001-context-artifact-architecture/PROPOSAL.md) |
| `docs/proposals/0002-platform-environment-architecture` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0002-platform-environment-architecture/PROPOSAL.md) |
| `workspaces/products/craft/work/proposals/0003-craft-migration` | `product/craft` | [Read](../../workspaces/products/craft/work/proposals/0003-craft-migration/PROPOSAL.md) |
| `docs/proposals/0004-governed-ontology-node-architecture` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0004-governed-ontology-node-architecture/PROPOSAL.md) |
| `workspaces/products/craft/architecture/proposals/0005-craft-transplant` | `product/craft` | [Read](../../workspaces/products/craft/architecture/proposals/0005-craft-transplant/PROPOSAL.md) |
| `docs/proposals/0006-lab-artifact-storage` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0006-lab-artifact-storage/ARCHITECTURE.md) |
| `docs/proposals/0007-lab-integrated-schema-package` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0007-lab-integrated-schema-package/ARCHITECTURE.md) |
| `docs/proposals/0008-lab-api-contracts` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0008-lab-api-contracts/API-CONTRACTS.md) |
| `docs/proposals/0009-lab-runtime-documentation` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0009-lab-runtime-documentation/CONTENTS.md) |
| `workspaces/products/lab-website/work/proposals/0010-lab-craft-content` | `product/lab-website` | [Read](../../workspaces/products/lab-website/work/proposals/0010-lab-craft-content/README.md) |
| `workspaces/products/ontology/work/proposals/0011-open-ontologies-assurance-reuse` | `product/ontology` | [Read](../../workspaces/products/ontology/work/proposals/0011-open-ontologies-assurance-reuse/README.md) |
| `docs/proposals/0012-lab-workspace-model` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/0012-lab-workspace-model/README.md) |
| `evidence/external/agentic-research-network` | `external/agentic-research-network` | [Read](../../evidence/external/agentic-research-network/2026-10-29/model-v1/README.md) |
| `evidence/external/engineer-assessment-research` | `external/engineer-assessment` | [Read](../../evidence/external/engineer-assessment-research/2026-10-25/model-v1/README.md) |
| `docs/proposals/hammer-bias-strategies` | `product/cyberalchemy-lab` | [Read](../../docs/proposals/hammer-bias-strategies/ANALYSIS-LENSES.md) |

## Imported and historical contexts

These references are not additional active workspaces. Withdrawn proposals are historical only.

| Source scope | Subject | Association / disposition |
| --- | --- | --- |
| [0009-contextual-framings-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0009-contextual-framings-import/README.md) | Generate Contextual Framings imported | capability/context boundary unresolved; retain source identity |
| [0010-recent-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0010-recent-context-import/README.md) | Recover Recent Repository Context imported | capability/context boundary unresolved; retain source identity |
| [0032-trusted-dataset-product-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0032-trusted-dataset-product-import/README.md) | Trusted Dataset Materialization is a standalone Product | `product/trusted-dataset-materialization` |
| [0033-definition-nft-product-proposal](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0033-definition-nft-product-proposal/README.md) | Definition NFT — proposed Product rules | removed from active workspace plan by user |
| [0036-alchlang-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0036-alchlang-context-import/README.md) | Migration resumed: first capability-linked context bundle | `product/craft` |
| [0037-kep-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0037-kep-context-import/README.md) | Core KEP business context imported | capability/context boundary unresolved; retain source identity |
| [0038-durable-storage-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0038-durable-storage-context-import/README.md) | Durable Storage business context imported | capability/context boundary unresolved; retain source identity |
| [0039-three-layer-recovery-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0039-three-layer-recovery-context-import/README.md) | Three-Layer Protection and Recovery context imported | capability/context boundary unresolved; retain source identity |
| [0040-solana-coownership-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0040-solana-coownership-context-import/README.md) | No-Price Solana Co-ownership context imported | capability/context boundary unresolved; retain source identity |
| [0041-encrypted-devnet-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0041-encrypted-devnet-context-import/README.md) | Encrypted Durable Devnet Co-ownership context imported | capability/context boundary unresolved; retain source identity |
| [0042-hosted-exchange-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0042-hosted-exchange-context-import/README.md) | Hosted Devnet Knowledge Exchange bridge imported | capability/context boundary unresolved; retain source identity |
| [0043-trusted-dataset-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0043-trusted-dataset-context-import/README.md) | Trusted Dataset Materialization context import | `product/trusted-dataset-materialization` |
| [0044-work-orchestration-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0044-work-orchestration-context-import/README.md) | Work Orchestration context import | capability/context boundary unresolved; retain source identity |
| [0045-agent-reasoning-context-preparation](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0045-agent-reasoning-context-preparation/README.md) | Agent Reasoning Engine — checked, repairs prepared | `product/agent-reasoning-engine` |
| [0048-agent-reasoning-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0048-agent-reasoning-context-import/README.md) | Agent Reasoning Engine — repaired candidate context import | `product/agent-reasoning-engine` |
| [0049-contextual-framings-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0049-contextual-framings-context-import/README.md) | Contextual Framings context import | capability/context boundary unresolved; retain source identity |
| [0051-repository-routing-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0051-repository-routing-context-import/README.md) | Repository Work Routing — repaired candidate import | capability/context boundary unresolved; retain source identity |
| [0052-recent-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0052-recent-context-import/README.md) | Recent Context candidate import | capability/context boundary unresolved; retain source identity |
| [0053-governed-access-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0053-governed-access-context-import/README.md) | Governed System-Building Access candidate import | capability/context boundary unresolved; retain source identity |
| [0054-verified-patch-context-preparation](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0054-verified-patch-context-preparation/README.md) | Verified Patch Candidates — checked, successor required | `product/craft` |
| [0055-verified-patch-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0055-verified-patch-context-import/README.md) | Verified Patch Candidates — offline successor import | `product/craft` |
| [0056-continuous-task-loop-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0056-continuous-task-loop-context-import/README.md) | Continuous Construction Task Loop context import | capability/context boundary unresolved; retain source identity |
| [0057-continuous-construction-context-preparation](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0057-continuous-construction-context-preparation/README.md) | Continuous Construction Governance preparation | `product/craft` |
| [0058-continuous-construction-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0058-continuous-construction-context-import/README.md) | Continuous Construction Governance context import | `product/craft` |
| [0059-dependency-relevance-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0059-dependency-relevance-context-import/README.md) | Dependency Relevance context import | capability/context boundary unresolved; retain source identity |
| [0060-d65-construction-context-preparation](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0060-d65-construction-context-preparation/README.md) | D65 Construction Validation successor preparation | `product/craft` |
| [0061-d65-revision2-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0061-d65-revision2-context-import/README.md) | D65 revision-2 prototype context | `product/craft` |
| [0062-shared-meaning-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0062-shared-meaning-context-import/README.md) | Shared Meaning Definition business context | capability/context boundary unresolved; retain source identity |
| [0063-define-session-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0063-define-session-context-import/README.md) | Define session system model | `product/define` |
| [0064-define-bridge-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0064-define-bridge-context-import/README.md) | Define business/system bridge | `product/define` |
| [0065-essays-agent-business-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0065-essays-agent-business-context-import/README.md) | Essays Agent Runtime business context | capability/context boundary unresolved; retain source identity |
| [0066-essays-authority-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0066-essays-authority-context-import/README.md) | Essays authority model | capability/context boundary unresolved; retain source identity |
| [0067-essays-architecture-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0067-essays-architecture-context-import/README.md) | Essays architecture properties | capability/context boundary unresolved; retain source identity |
| [0068-essays-system-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0068-essays-system-context-import/README.md) | Essays Agent Runtime system model | capability/context boundary unresolved; retain source identity |
| [0071-essays-implementation-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0071-essays-implementation-context-import/README.md) | Essays exact implementation context | capability/context boundary unresolved; retain source identity |
| [0072-people-teams-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0072-people-teams-context-import/README.md) | People and Teams business context | `product/people-and-teams` |
| [0074-people-teams-runtime-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0074-people-teams-runtime-import/README.md) | People and Teams through the existing runtime | `product/people-and-teams` |
| [0076-workspace-context-preparation](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0076-workspace-context-preparation/README.md) | Workspace context preparation | capability/context boundary unresolved; retain source identity |
| [0080-define-package-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0080-define-package-import/README.md) | Define package source import | `product/define` |

## Evidence and compatibility

- [Machine catalog and source pins](inventory/workspace-catalog.json)
- [Cleanup and content-audit result](CLEANUP-20261107.md)
- [Ontology consolidation](ONTOLOGY-WORKSPACE.md)
- [Boundary rules](WORKSPACE-BOUNDARIES.md)
- [Required successor of the earlier Project-only model](MODEL-REVISION.md)

The earlier profile and frozen Define Packs remain exact predecessors. The current v2 runtime model implements Product/Project kinds and shared dispatch; physical ownership migration is applied with compatibility links. Native identity admission and runtime installation/deployment were not performed. The [previous catalog](inventory/workspace-catalog-20261106.snapshot.json) remains historical.

Check with `python3 architecture/workspace-model-mapping/inventory/check_workspaces.py`. Render with `--render`; write the local receipt with `--write-report`.
