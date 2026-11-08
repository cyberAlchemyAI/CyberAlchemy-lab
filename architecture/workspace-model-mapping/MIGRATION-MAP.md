# Current-to-proposed ownership and migration map

This is a planning map, not a move list. Ownership anchors denote proposed responsibility, not selected physical nesting. The machine [region map](inventory/path-map.json) gives the complete set of path-region rules and explicit mixed/unresolved dispositions.

Current names are **Product Workspace** and **Project Workspace**. The [catalog](WORKSPACES.md) resolves proposed `workspaces/products/` and `workspaces/projects/` registrations; the `@owner` anchors below remain ownership shorthand rather than physical move commands. The [model revision](MODEL-REVISION.md) records the still-unimplemented change from the earlier Project-only profile.

The [7 November cleanup](CLEANUP-20261107.md) supersedes earlier candidate hosting recommendations for TROQAR, Engineer Assessment, Agentic Research Network, Definition NFT, Lab migration and Ontology. Those choices do not rewrite immutable source evidence.

## Disposition rules

- **Retain exact:** immutable admission bundles, reviewed targets, source snapshots, original history and frozen profiles retain their bytes and resolvable historical paths. A later authored home does not overwrite them.
- **Reconcile selection:** records sharing identity require selected revision, lineage and primary/projection handling before a new current home is used.
- **Classify selected contents:** mixed regions require a bounded manifest of current functional source, fixture input, current state, execution evidence and derived output. Filename extensions and parent folder names do not decide this.
- **Propose new current home:** apply a destination to selected current authored material, with consumer updates and verification. Original historical records can remain accessible under old paths.
- **Resolve owner:** do not manufacture a new Project/Product or transfer ownership merely to fit the layout.

## Mapping by region

| Current region | Proposed current home / owner | Disposition and dependencies |
| --- | --- | --- |
| `authority/definitions`, `artifact-types`, `relation-kinds`, `profiles` | `@lab/authority/` with selected distribution to adopters | Retain exact registries/contract bytes; distinguish meanings, carrier schemas and instance admission |
| `authority/admissions`, `foundation`, `owners`, `decisions`, `lineage`, `project-state-transitions` | Owning instance's authority/state references | Retain exact historical homes and frozen profile resolution; current lookup is not the whole Project State |
| Other authority candidate/model packs | Applicable `authority/`, `product/`, `ontology/` or `work/` | Classify selected contents; candidate status and owner route must survive |
| `coordination/projects/craft` | `@craft/project/` | Reconcile byte-identical Project record with `craft/project/project.json`; choose primary/projection/compatibility policy |
| `coordination/goals/craft-product-foundation` | `@craft/work/goals/`, referenced from `@craft/project/` | Preserve Goal identity and exactly-one-Project relation; placing it under Work does not make Goal equal Work |
| `coordination/projects/definition-formal-assurance` | Lab root project/definition-formal-assurance/ and work/ | Preserve the explicit Project identity inside the Lab Product home; no standalone workspace or transfer into Craft |
| `coordination/contexts`, `contexts/governance`, `contexts/ontology-lifecycle`, `contexts/maps` | Owning `ontology/contexts/` and context-map homes, provisionally | Distinguish Bounded/Coordination Context records from generated Agent Context Views; contract-specific placement remains open |
| `contexts/migrations`, `contexts/lineage` | Owning `work/plans/` or `authority/lineage/` plus retained originals | Split operational migration from semantic lineage; preserve source provenance |
| `product/lab/design`, Product acceptance/scope files | `@lab/product/` | Current journeys, capability meaning, scope and acceptance stay Product material |
| Executable source/packaging inside `product/lab/release-candidates` | `@lab/implementation/` | Select actual source/package manifests first; preserve exact frozen generations and active runtime selectors |
| Receipts, pilot executions and saved release results in that tree | Producing `work/outcomes/` references or retained evidence homes | Fixtures/templates stay with implementation; actual owner outcome and release permission retain separate status |
| `product/products/craft`, `product/prototypes/craft-first-capability` | `@craft/product/` and `@craft/implementation/` as applicable | Reconcile Product Identity/v1 vs v2 proposal for the same subject before selecting current representation |
| `product/products/ontology` | Product identity → `@ontology-product/product/`; executable/build/test/fixture source → `implementation/`; authored ontology → `ontology/`; contracts → applicable owner/home | Mixed Product/application subtree: host alongside the lifecycle Project/engine in one proposed Ontology workspace; preserve their identities and package boundaries; preserve candidates and saved results separately |
| `product/products/engineer-assessment` | External Engineer Assessment workspace; retained Lab Product snapshot | External editable source is established; retain Lab capture/admission dependencies and do not create a duplicate hosted workspace |
| `implementation/lab-*`, `implementation/bindings` | `@lab/implementation/` | Already reusable implementation; current source, frozen packages and saved results need distinct handling |
| `define/` plus `implementation/define-cli/` | `@define/{implementation,work,docs,authority}` or explicit Lab application ownership | Reconcile imported snapshot, launchers, connector and adapters; retain source import metadata and exact runtime manifests |
| `ontology-lifecycle/runtime`, runtime candidates and scripts | Ontology workspace implementation, with separate lifecycle package and selected shared consumers | Enumerate import paths, Cargo bindings, runtime/profile selectors and Body War consumers first |
| Its authored model/context/schema inputs | Relevant instance's `ontology/` or `authority/` | Resolve model vs application ownership and selected epoch; ontology output is not all root Lab ontology |
| Its activation, rehearsal, migration, benchmarks and conformance | Owning `authority/`, `work/`, implementation fixtures or preserved evidence, by record | Split approval/activation record, test input, execution report and prototype source |
| Craft's eight-area import | `@craft/` | Reference pattern; preserve explicit entrypoint and its selected shared dependencies |
| Craft legacy `impl`, `formalization`, root definitions/research | Selected `@craft/implementation`, `authority`, `work` or retained legacy home | Do not merge with new implementation or retire `RUNTIME.json` consumers without explicit source/consumer disposition |
| `docs/lab` | `@lab/docs/` | Keep reader material; captured records retain their dated source scope |
| `docs/decisions`, admission/definition/artifact/context/identity packs | Relevant `authority/` plus retained historical envelopes | Decision evidence, executable apply scripts, definitions and explanations require finer classification |
| `docs/plans`, `migration-plans`, construction chains, proposals, research | Owning `work/{plans,research,discovery,experiments}` and selected other areas | Large mixed region: separate actionable definitions/source from saved runs/snapshots; no bulk rename |
| `evidence/` | Retained evidence with explicit producing Work/subject references | Historical evidence remains accessible; only selected current evidence is included in a functional instance export |
| `tooling/`, `tests/` | `@lab/implementation/tooling` and owner-specific test homes, provisionally | Enumerate CLI/import references; test source, schemas and fixtures are functional inputs |
| `website/` | `@website/{product,implementation,work,docs}` or Lab delivery capability | Preserve canonical docs ownership, captured source pins, release/deployment selection and Body War promotion link |
| `.arcanum/inventory`, ontology-vault | Derived navigation vs authored synthesis, respectively | Refresh indexes after migration; an authored research note and a generated database have different roles |
| `.github`, Git metadata, `claude` pointers | Repository infrastructure and explicit context navigation | Preserve root requirements and automate no authority changes from a directory move |
| `output`, ignored `.local`, build/dependency/cache trees | Retained execution material or private/regenerable local state | No deletion or private-store inspection in this task; no bulk export into functional workspaces |
| Root `test.ts`, `test.spec.ts`, `{exit}` | Unresolved | Ownership/disposition deferred; no cleanup inferred |

## Actual collisions and consumers

The evidence capture checks that `craft/project/project.json` and `coordination/projects/craft/v1/project.json` are byte-identical. `craft/product/product.json` and `product/products/craft/v1/product.json` share `CA2-PRODUCT-CRAFT` but differ: schema v2 / `2.0.0-proposal.2` versus schema v1 / `1.0.0-candidate.1`. Neither newer location nor newer label selects adoption automatically.

All twelve inspected `/home/vlad_/projects/body-war/` links point into Lab: `implementation`, `product/lab`, `craft/formalization`, `craft/impl`, `ontology-lifecycle/runtime`, `ontology-lifecycle/runtime-candidates`, `ontology-lifecycle/execution-prototypes`, `docs/plans`, `docs/proposals`, `evidence/migrations`, `output`, `website/promotion`. The inventory records link metadata only; these shared targets must be treated as upstream references, with compatibility or explicit consumer rebinding before moves.

## Dependency order for future work

| Unit | Result | Depends on |
| --- | --- | --- |
| M00 | Select workspace boundaries, hosted/external locations and initial Project scopes | [Boundary proposal](WORKSPACE-BOUNDARIES.md); declared purposes/owners; Goal/entity versus capability distinction |
| M01 | Resolve scope ownership and primary representations for Craft, Define, People and Teams, Ontology and delivery | M00; exact local owners/identities |
| M02 | Specify the common eight-area adoption record and compatibility rules | M01; existing contract/profile/install mechanisms |
| M03 | Describe Lab capability slices and bind Lab's own Product/Project/Work to the model | M02; exact existing identities, no inferred new authority |
| M04 | Select a bounded current-functional manifest and consumer map for Craft | M01, M02; preserve legacy bindings, input fixtures and historical proofs |
| M05 | Demonstrate one real upgrade on an isolated Craft instance | M04; explicit before/after profiles, carrier/state migration, retained reader and evidence |
| M06 | Relocate selected current authored material by scope | M05; complete dispositions, compatibility routes, links/tests/source closure |
| M07 | Generalize creation/adoption to remaining instances and refresh navigation | M06; per-instance ownership and qualified transitions |

These are proposed dependencies, not registered Work, authorized source retirement or completed migration tasks. Exact implementation Work and completion criteria should be created when execution scope is selected.

Current hosting follows [one home per Product](PRODUCT-COLOCATION.md). Product-specific development Projects and Work remain inside that home. The theorem-checker plan maps to Lab Work rather than an invented independent Project workspace. Historical source regions and references remain exact.

## Physical migration applied: 7 November 2026

The physical homes in [FOLDER-STRUCTURE.md](FOLDER-STRUCTURE.md) are now applied. Earlier proposed-path descriptions above are retained design context. Current locations and source pins are in [WORKSPACES.md](WORKSPACES.md). Old locations are compatibility links. Shared Lab operations remain in root implementation/; shared runtimes were not copied. Imported snapshots, frozen Define Packs, native identities and admissions retain their existing standing. See the [migration report](../../docs/migration-plans/0008-product-workspaces-20261107/REPORT.md).
