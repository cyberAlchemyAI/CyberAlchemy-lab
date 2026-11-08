<!-- GENERATED from inventory/workspace-catalog.json by inventory/check_workspaces.py --render. -->

# Product Workspaces and Project Workspaces

Status: candidate naming and source-backed scope catalog, 6 November 2026. Authority effect: none.

**Product Workspace** is the display label for a durable Product scope; **Project Workspace** is the label for a coordinated initiative. The catalog namespaces are `workspaces/products/` and `workspaces/projects/`. These are local planning labels, not newly admitted Definitions.

Both kinds use the eight responsibilities and shared operations. A Product can be advanced by several Projects. A Project references its Product or another declared purpose. A distinct catalog entry does not require a separate physical directory, database, runtime or copied business record.

This catalog has 12 Product-scope entries and 7 Project-scope entries. These are not 19 established operating workspaces: the list includes identities, documented Products, unaccepted proposals, one boundary proposal, a plan-only Project candidate and one external checkout. Only Craft has the previously authored candidate Lab Workspace profile in this selection.

## Product Workspaces

| Catalog name | Existing source / identity basis | Current material | Proposed location or registration |
| --- | --- | --- | --- |
| **CyberAlchemy Lab**<br>`product/cyberalchemy-lab` | `product:cyberalchemy-lab`<br>[Exact source](../../authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product.json) | `.`<br>`product/lab`<br>`implementation/lab-*`<br>`authority` | `workspaces/products/cyberalchemy-lab`<br>physical home remains `.` |
| **Craft**<br>`product/craft` | `CA2-PRODUCT-CRAFT`<br>[Exact source](../../craft/product/product.json) | `craft`<br>`product/products/craft/v1` | `workspaces/products/craft` |
| **Define**<br>`product/define` | product-document; native identity unselected<br>[Exact source](../../define/README.md) | `define`<br>`implementation/define-cli` | `workspaces/products/define` |
| **CyberAlchemy Ontology Product**<br>`product/ontology` | `CA2-PRODUCT-ONTOLOGY`<br>[Exact source](../../product/products/ontology/v1/product.json) | `product/products/ontology/v1` | `workspaces/products/ontology` |
| **People and Teams**<br>`product/people-and-teams` | boundary-proposal; native identity unselected<br>[Exact source](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0072-people-teams-context-import/README.md) | `evidence/migrations/cyberalchemy-v2-to-lab/executions/0072-people-teams-context-import`<br>`evidence/migrations/cyberalchemy-v2-to-lab/executions/0074-people-teams-runtime-import` | `workspaces/products/people-and-teams` |
| **Engineer Assessment**<br>`product/engineer-assessment` | `EA-PRODUCT-001`<br>[Exact source](../../product/products/engineer-assessment/v1/product.json) | `product/products/engineer-assessment/v1`<br>`docs/proposals/engineer-assessment-research` | `workspaces/products/engineer-assessment` |
| **Agentic Research Network**<br>`product/agentic-research-network` | `product:arn-network-001`<br>[Exact source](../../docs/proposals/agentic-research-network/2026-10-29/model-v1/records/product-identity.json) | `docs/proposals/agentic-research-network/2026-10-29/model-v1` | `workspaces/products/agentic-research-network` |
| **CyberAlchemy Lab website**<br>`product/lab-website` | product-document; native identity unselected<br>[Exact source](../../website/PRODUCT.md) | `website` | `workspaces/products/lab-website` |
| **Trusted Dataset Materialization**<br>`product/trusted-dataset-materialization` | `lab:trusted-dataset-materialization#CAL-PRODUCT-TRUSTED-DATASET-MATERIALIZATION`<br>[Exact source](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0032-trusted-dataset-product-import/result.json) | `evidence/migrations/cyberalchemy-v2-to-lab/executions/0032-trusted-dataset-product-import`<br>`evidence/migrations/cyberalchemy-v2-to-lab/executions/0043-trusted-dataset-context-import` | `workspaces/products/trusted-dataset-materialization` |
| **Definition NFT**<br>`product/definition-nft` | `lab:definition-nft#CA2-PRODUCT-DEFINITION-NFT`<br>[Exact source](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0033-definition-nft-product-proposal/proposal.json) | `evidence/migrations/cyberalchemy-v2-to-lab/executions/0033-definition-nft-product-proposal` | `workspaces/products/definition-nft` |
| **Agent Reasoning Engine**<br>`product/agent-reasoning-engine` | `CA2-PRODUCT-AGENT-REASONING-ENGINE`<br>[Exact source](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0045-agent-reasoning-context-preparation/source/product.json) | `evidence/migrations/cyberalchemy-v2-to-lab/executions/0045-agent-reasoning-context-preparation`<br>`evidence/migrations/cyberalchemy-v2-to-lab/executions/0048-agent-reasoning-context-import` | `workspaces/products/agent-reasoning-engine` |
| **TROQAR / Body War**<br>`product/troqar` | external-workspace; native identity unselected<br>`/home/vlad_/projects/body-war/integration/lab/source-manifest.json` | `/home/vlad_/projects/body-war` | `workspaces/products/troqar`<br>external home retained |

## Project Workspaces

| Catalog name | Existing source / identity basis | Product / related scope | Proposed location |
| --- | --- | --- | --- |
| **CyberAlchemy v2 to Lab migration**<br>`project/lab-migration` | `project:cyberalchemy-v2-to-lab-migration`<br>[Source / retained plan](../../authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/project.json) | `product/cyberalchemy-lab` | `workspaces/projects/lab-migration` |
| **Craft development and coordination**<br>`project/craft-development` | `CA2-PROJECT-CRAFT`<br>[Source / retained plan](../../craft/project/project.json) | `product/craft` | `workspaces/projects/craft-development` |
| **CyberAlchemy Lab Ontology Lifecycle**<br>`project/ontology-lifecycle` | `CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE`<br>[Source / retained plan](../../docs/plans/0003-d65-native-ontology-integration/PLAN.md) | `product/ontology`<br>`product/cyberalchemy-lab` | `workspaces/projects/ontology-lifecycle` |
| **Definition Formal Assurance**<br>`project/definition-formal-assurance` | `cal.project.definition-formal-assurance`<br>[Source / retained plan](../../coordination/projects/definition-formal-assurance/v1/project.json) | `product/cyberalchemy-lab` | `workspaces/projects/definition-formal-assurance` |
| **Engineer Assessment research program**<br>`project/engineer-assessment-research` | `project:ea-research-001`<br>[Source / retained plan](../../docs/proposals/engineer-assessment-research/2026-10-26/product-research-connection-v3/model/lab-records/project-identity.json) | `product/engineer-assessment` | `workspaces/projects/engineer-assessment-research` |
| **Agentic Research Network modelling**<br>`project/agentic-research-network-modeling` | `project:arn:research-network-001`<br>[Source / retained plan](../../docs/proposals/agentic-research-network/2026-10-29/model-v1/records/project-identity.json) | `product/agentic-research-network` | `workspaces/projects/agentic-research-network-modeling` |
| **Relational theorem checker**<br>`project/relational-theorem-checker` | Plan/work-pack only; native Project identity unselected<br>[Source / retained plan](../../docs/plans/relational-theorem-checker/ANALYSIS.md) | `project/definition-formal-assurance`<br>`product/cyberalchemy-lab` | `workspaces/projects/relational-theorem-checker` |

Craft development is currently co-located with the Craft Product. Its separate Project catalog entry exposes the existing coordination identity; `projects/craft-development/` is only a possible independent home, requiring a boundary and primary-source transition before use. TROQAR is likewise one external checkout with local Product/Project labels, not two copied workspaces.

Ontology Lifecycle maps to its existing Project ownership. The Ontology Product keeps its own Product identity. Their application/library/Product dependency boundary is unresolved; this catalog does not invent a separate Ontology Lifecycle Product or merge the existing subjects.

## Subject standing and open boundaries

| Catalog key | What exists / standing | Remaining work |
| --- | --- | --- |
| `product/cyberalchemy-lab` | D71 exact-instance overlay admitted-current; embedded candidate provenance retained | Root remains the Lab development workspace; catalog registration does not create a nested copy. |
| `product/craft` | candidate-or-source-only | Existing eight-area source and a candidate workspace profile; product/project typing is not yet implemented by that profile.<br>Older v1 and newer v2 Product candidates are retained; selection here does not admit or supersede them. |
| `product/define` | candidate-or-source-only | No Lab Product identity selected by this catalog.<br>Preserve imported source owner versus Lab-owned connector/adapters; some sources have different ownership. |
| `product/ontology` | test-candidate | Relationship with Ontology Lifecycle application/Project remains unresolved; do not merge subject identities. |
| `product/people-and-teams` | candidate-or-source-only | Existing shared domain/model scope, not a selected standalone Product identity or operating workspace.<br>Keep Person, Team, membership, Role and assignment identities separate; do not create workspaces for each entity. |
| `product/engineer-assessment` | candidate-or-source-only | v1 and v2 proposals share an identity; current representation selection remains explicit, not newest-file-wins.<br>Declared Product owner remains unassigned. |
| `product/agentic-research-network` | candidate-or-source-only | Candidate Product only; owner unassigned, no running network or economic authorization.<br>Engineer Assessment is a referenced Product, not owned by this network. |
| `product/lab-website` | candidate-or-source-only | Confirm separate Product/Project/release boundary versus a delivery capability of the Lab.<br>Do not transfer canonical documentation meaning to the delivery application. |
| `product/trusted-dataset-materialization` | local standalone Product candidate, not operational | Source explicitly selected its own Product; do not confuse it with Craft Test Derivation Engine (TDE).<br>Current source resides in import material; selecting functional homes and workspace binding remains pending. |
| `product/definition-nft` | unaccepted proposal; import and Product rules unresolved | A proposed Product identity exists; proposal is not accepted or imported as an operating Product.<br>Keep KEP rights/ownership and NFT representation separate. |
| `product/agent-reasoning-engine` | source Product snapshot and repaired candidate context; no Lab workspace adoption | The selected identity is a retained source snapshot; later repaired package material has its own exact bindings.<br>Actual engine source/runtime lives upstream and remains referenced; do not copy it into Lab to satisfy this catalog. |
| `product/troqar` | existing standalone checkout; no new Product/Project identity inferred | Manifest names TROQAR and local project_id body-war; inherited Lab records do not become its identities.<br>Keep existing shared links and external location. |
| `project/lab-migration` | D71 exact-instance overlay admitted-current; migration completion not implied | The migration Project is not a generic identity for every future Lab development effort. |
| `project/craft-development` | candidate-or-source-only | Current Product and Project records share the Craft home. A distinct catalog entry does not require another physical workspace or copied records.<br>A separate projects/craft-development home needs an explicit boundary and primary-source transition. |
| `project/ontology-lifecycle` | source Project proposed; Lab plan records registered-candidate owner selection | Project carrier is upstream and referenced by the Lab integration plan; it was not silently imported.<br>Separate the reusable runtime implementation from Project Work; do not invent a second Product solely from the ontology-lifecycle directory.<br>Ontology Product/application ownership relation remains a pending boundary decision. |
| `project/definition-formal-assurance` | candidate-or-source-only | Assurance coordinates evidence; semantic definition owners retain meaning/admission authority. |
| `project/engineer-assessment-research` | candidate-or-source-only | Source revisions/copies represent one Project, not several workspaces.<br>Research lead remains unassigned; no participant-data or hiring authority inferred. |
| `project/agentic-research-network-modeling` | candidate-or-source-only | Candidate Project and unassigned owner; synthetic pilot and subprograms are not separately provisioned workspaces. |
| `project/relational-theorem-checker` | candidate-or-source-only | Substantial independent plan/work-pack exists; no canonical Project identity selected by this catalog.<br>Decide independent Project boundary versus Work within formal assurance; keep as visible candidate meanwhile. |

## Proposed physical convention

```text
CyberAlchemy-lab/                  # Lab Product workspace stays at repository root
  product/ project/ work/ authority/ ontology/ architecture/ implementation/ docs/
  workspaces/
    products/
      craft/ define/ ontology/ people-and-teams/
      engineer-assessment/ agentic-research-network/ lab-website/
      trusted-dataset-materialization/ definition-nft/
      # agent-reasoning-engine: upstream reference until explicitly imported
      # cyberalchemy-lab: root registration; troqar: external registration
    projects/
      lab-migration/ ontology-lifecycle/ definition-formal-assurance/
      engineer-assessment-research/ agentic-research-network-modeling/
      # craft-development: currently co-located; independent home optional
      # relational-theorem-checker: identity / boundary still pending
```

The tree is a candidate destination convention. No container, folder move, native workspace identity or runtime installation is created by this catalog. Exact frozen admission and import material stays retained; only selected authored records could later receive new current homes.

## Existing plans and proposals

Every first-level `docs/plans/` and `docs/proposals/` scope is listed. Associations below are navigation proposals, not newly asserted Project ownership, Goal membership or Typed Relations. A plan, design, migration phase or research package does not automatically become another Project Workspace.

| Existing scope | Proposed navigation scope | Source |
| --- | --- | --- |
| `docs/plans/0001-event-sourced-ontology-first-vertical` | `project/ontology-lifecycle` | [Read scope](../../docs/plans/0001-event-sourced-ontology-first-vertical/PLAN.md) |
| `docs/plans/0002-governed-ontology-node-continuous-plan` | `project/ontology-lifecycle` | [Read scope](../../docs/plans/0002-governed-ontology-node-continuous-plan/PLAN.md) |
| `docs/plans/0003-d65-native-ontology-integration` | `project/ontology-lifecycle` | [Read scope](../../docs/plans/0003-d65-native-ontology-integration/PLAN.md) |
| `docs/plans/0004-d65-export-cutover-candidate` | `project/ontology-lifecycle` | [Read scope](../../docs/plans/0004-d65-export-cutover-candidate/README.md) |
| `docs/plans/0005-d65-post-approval-isolated-rehearsal` | `project/ontology-lifecycle` | [Read scope](../../docs/plans/0005-d65-post-approval-isolated-rehearsal/README.md) |
| `docs/plans/0006-d65-admitted-runtime-activation-cutover` | `project/ontology-lifecycle` | [Read scope](../../docs/plans/0006-d65-admitted-runtime-activation-cutover/README.md) |
| `docs/plans/0007-governance-architecture-ontology` | `product/cyberalchemy-lab` | [Read scope](../../docs/plans/0007-governance-architecture-ontology/PLAN.md) |
| `docs/plans/0008-lab-operational-runtime` | `product/cyberalchemy-lab` | [Read scope](../../docs/plans/0008-lab-operational-runtime/PLAN.md) |
| `docs/plans/0009-lab-integrated-roadmap` | `product/cyberalchemy-lab` | [Read scope](../../docs/plans/0009-lab-integrated-roadmap/PLAN.md) |
| `docs/plans/0010-lab-one-shot-execution` | `product/cyberalchemy-lab` | [Read scope](../../docs/plans/0010-lab-one-shot-execution/PLAN.md) |
| `docs/plans/0011-lab-runtime-completion` | `product/cyberalchemy-lab` | [Read scope](../../docs/plans/0011-lab-runtime-completion/PLAN.md) |
| `docs/plans/definition-formal-assurance` | `project/definition-formal-assurance` | [Read scope](../../docs/plans/definition-formal-assurance/PROJECT.md) |
| `docs/plans/relational-theorem-checker` | `project/relational-theorem-checker` | [Read scope](../../docs/plans/relational-theorem-checker/ANALYSIS.md) |
| `docs/proposals/0001-context-artifact-architecture` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0001-context-artifact-architecture/PROPOSAL.md) |
| `docs/proposals/0002-platform-environment-architecture` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0002-platform-environment-architecture/PROPOSAL.md) |
| `docs/proposals/0003-craft-migration` | `product/craft` | [Read scope](../../docs/proposals/0003-craft-migration/PROPOSAL.md) |
| `docs/proposals/0004-governed-ontology-node-architecture` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0004-governed-ontology-node-architecture/PROPOSAL.md) |
| `docs/proposals/0005-craft-transplant-architecture` | `product/craft` | [Read scope](../../docs/proposals/0005-craft-transplant-architecture/PROPOSAL.md) |
| `docs/proposals/0006-lab-artifact-storage` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0006-lab-artifact-storage/ARCHITECTURE.md) |
| `docs/proposals/0007-lab-integrated-schema-package` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0007-lab-integrated-schema-package/ARCHITECTURE.md) |
| `docs/proposals/0008-lab-api-contracts` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0008-lab-api-contracts/API-CONTRACTS.md) |
| `docs/proposals/0009-lab-runtime-documentation` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0009-lab-runtime-documentation/CONTENTS.md) |
| `docs/proposals/0010-lab-craft-content` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0010-lab-craft-content/README.md) |
| `docs/proposals/0011-open-ontologies-assurance-reuse` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0011-open-ontologies-assurance-reuse/README.md) |
| `docs/proposals/0012-lab-workspace-model` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/0012-lab-workspace-model/README.md) |
| `docs/proposals/agentic-research-network` | `project/agentic-research-network-modeling` | [Read scope](../../docs/proposals/agentic-research-network/2026-10-29/model-v1/README.md) |
| `docs/proposals/engineer-assessment-research` | `project/engineer-assessment-research` | [Read scope](../../docs/proposals/engineer-assessment-research/2026-10-25/model-v1/README.md) |
| `docs/proposals/hammer-bias-strategies` | `product/cyberalchemy-lab` | [Read scope](../../docs/proposals/hammer-bias-strategies/ANALYSIS-LENSES.md) |

## Imported and referenced contexts

The following source packages remain visible. Imported meaning, capability registration and a prepared context do not establish a new Product/Project workspace. Unlinked contexts retain an unresolved boundary; they are not silently assigned to a Product.

| Source scope | Existing subject | Catalog association / disposition |
| --- | --- | --- |
| [0009-contextual-framings-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0009-contextual-framings-import/README.md) | Generate Contextual Framings imported | capability/context boundary unresolved; retain source identity |
| [0010-recent-context-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0010-recent-context-import/README.md) | Recover Recent Repository Context imported | capability/context boundary unresolved; retain source identity |
| [0032-trusted-dataset-product-import](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0032-trusted-dataset-product-import/README.md) | Trusted Dataset Materialization is a standalone Product | `product/trusted-dataset-materialization` |
| [0033-definition-nft-product-proposal](../../evidence/migrations/cyberalchemy-v2-to-lab/executions/0033-definition-nft-product-proposal/README.md) | Definition NFT — proposed Product rules | `product/definition-nft` |
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

## Coverage, authority and model compatibility

The machine catalog also records every current root entry except `.git`, without reading private stores or ignored runtime content. Shared capability code, context packages, fixtures, generated compiler projects, replay stores, frozen snapshots, Goals and individual Person/Team records are not additional workspaces merely because they have directories or IDs.

The Lab Product and migration Project use the exact D71 instance-admission overlay; immutable embedded candidate labels remain provenance. Other candidates keep their source standing. Product Identity/v2 being an admitted carrier does not admit every Product instance.

This catalog does not convert the earlier Project-only Workspace Definition/profile. That earlier candidate and its three frozen Define Packs remain exact. The [required model revision](MODEL-REVISION.md) names the concrete discriminator, cardinality, binding and fixture changes needed before either kind can be represented operationally.

- [Machine catalog, all source hashes and root dispositions](inventory/workspace-catalog.json)
- [Boundary rules](WORKSPACE-BOUNDARIES.md)
- [Model revision and drift obligations](MODEL-REVISION.md)
- [Earlier candidate model](../../docs/proposals/0012-lab-workspace-model/README.md)

Validation: `python3 architecture/workspace-model-mapping/inventory/check_workspaces.py`. Render after an intentional catalog edit with `--render`; write only this catalog check receipt with `--write-report`. The older path/source inventory remains its dated snapshot and is not silently refreshed.
