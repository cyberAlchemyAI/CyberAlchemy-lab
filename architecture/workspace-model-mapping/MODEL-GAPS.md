# Definitions and artifact prerequisites

Status: semantic/contract audit plus proposed remediation, 5 November 2026. Authority effect: none. No canonical Definition, Artifact Type, registry, relation or runtime selection is changed here.

## Conclusion

The foundation is substantially present. Most remaining work is a Lab-specific composition/profile and concrete model, workspace, binding, distribution-selection and transition records. One candidate semantic gap remains: a precise scoped meaning of **Lab Workspace**, distinguishing an operating home from Project identity, Canonical Package Home, Bounded Context, Capability Instance, repository and operation-staging workspace.

Do not turn every proposed record name into a new canonical Definition. Existing Model Instance Binding already covers much of what earlier discussion called a missing adoption binding. The unestablished piece is the concrete eight-area Lab composition and its actual per-instance adoption and upgrade records.

G01 also needs an explicit terminology decision for "Lab instance": is that an alias for the modeled workspace, or a running installation serving it? A workspace's durable identity, a model-instance binding and a runtime installation must remain distinguishable; one ambiguous term must not silently merge them.

## Existing foundations

The [Definition registry](../../authority/definitions/registry.json) resolves admitted meanings. The selected [Artifact Type registry](../../authority/admissions/project-state-bootstrap/v1/registries/artifact-type-registry.json) resolves carrier contracts and historical/resolved alternatives. Descriptor and schema hashes for six relevant current contracts matched their registry selections during this audit. This verifies selected contract source, not runtime execution or instance admission.

| Existing meaning/contract | What it supplies | Application here |
| --- | --- | --- |
| Project, Goal and Work | Durable coordination identity, Project-owned outcomes and bounded efforts | Reuse meanings and select/create real records; folders do not replace identities. |
| [Canonical Package Home](../../authority/definitions/candidates/0008-canonical-package-home/definitions/canonical-package-home/v1/definition.json) | Owner-local aggregate, lifecycle owner, unit of change and canonical home; separate homes for independent lifecycle/recovery boundaries | Strong existing foundation for physical boundaries. A workspace can reference several independently owned homes. |
| [Canonical Package Manifest](../../authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/canonical-package-manifest/v1/definition.json), [selected schema](../../authority/artifact-types/canonical-package-manifest/v1/candidates/0002-executable-surface/schema.json) | Exact root, aggregate, owner, unit of change, member surface roles, canonical carriers and independent nested packages | Create actual manifests; a folder catalog is not a substitute. The older root schema is not assumed to be the current selected contract. |
| [Governed Model](../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/governed-model/v1/definition.json), [carrier](../../authority/artifact-types/governed-model/v1/schema.json) | Versioned representation with scope, owner, sources, assumptions, validation and lifecycle | Represent the reusable Lab operating model as a concrete model artifact. |
| [Model Instance Binding](../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/model-instance-binding/v1/definition.json), [carrier](../../authority/artifact-types/model-instance-binding/v1/schema.json) | Exact parent/local revision, separate authority, inheritance, extensions, overrides, conformance, adoption, succession and challenge | Reuse for whole-model instance adoption; specify Lab-specific references/profile constraints. |
| [Capability Instance](../../authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/capability-instance/v1/definition.json), [current v2 carrier](../../authority/artifact-types/capability-instance/v2/schema.json) | Exact parent capability, local realization/specialization, separate authority, adoption, construction, evidence and bounded recursion | Apply to selected capability instances; v1 is admitted-historical, not the current carrier. |
| [Capability Realization Binding](../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/capability-realization-binding/v1/definition.json) | Exact capability-to-Implementation association, compatibility and realization posture | Keep implementation selection distinct from whole-workspace model adoption. |
| [Repository Migration Manifest](../../authority/definitions/candidates/0011-repository-migration-manifest/definitions/repository-migration-manifest/v1/definition.json), [current carrier](../../authority/artifact-types/repository-migration-manifest/v1/candidates/0001/schema.json) | Complete source accounting, exact mappings, target baseline/postimage, validation and additive rollback boundary | Use for selected repository relocation. It excludes overwrite, deletion and context-local semantic succession; it is not a universal in-place state-upgrade contract. |
| [Bounded Context](../../authority/definitions/candidates/0002-ctx06-context-map-reference-normalization/definitions/bounded-context/v2/definition.json), Context Map and Authority Boundary | Semantic boundaries, directional context contracts and scoped effect authority | Reference where applicable; a workspace need not equal one Bounded Context or one authority owner. |
| [Parent/instance separation](../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/parent-instance-authority-separation-invariant/v1/definition.json), [bounded self-application](../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/bounded-self-application-invariant/v1/definition.json) | Independent parent/local authority; declared recursive scope, owner, state, recomposition and stop | The Lab can apply its model to its own development without unlimited recursion or inherited permission. |

The six checked current carrier selections were Canonical Package Manifest/v1 (executable-surface candidate 0002), Governed Model/v1, Model Instance Binding/v1, Capability Instance/v2, Project Identity/v1 and Repository Migration Manifest/v1. Source-directory candidate labels do not override admitted-current registry standing. Generic Project/v1 is a resolved duplicate pointing to Project Identity/v1; do not instantiate the duplicate merely because its schema exists.

## Remaining prerequisites

| ID | Needed item | Gap category | Recommended construction |
| --- | --- | --- | --- |
| G01 | Precise Lab Workspace meaning and relationships | Candidate scoped semantic addition / specialization decision | First test whether an explicit profile of existing meanings suffices. If distinct reusable meaning is needed, prepare one scoped Definition with owner, lifecycle and exclusions. |
| G02 | Reusable eight-area Lab operating model | Missing concrete governed-model artifact | Declare responsibilities, required/optional references, allowed extensions and self-application boundaries. Current Markdown is an explanatory proposal, not this admitted model instance. |
| G03 | Boundary/identity records for selected workspaces | Missing selections and instances | Bind purpose, Project, Product-or-other-purpose, owners, exclusions, Goals, location and primary state ownership for Lab, Craft, Define and People and Teams. Reconcile established identities. |
| G04 | Canonical home manifests and selected functional contents | Missing selected instances | Use the current manifest contract, with independent nested homes and member roles; resolve Craft representation conflicts. |
| G05 | Exact Lab distribution and per-workspace selection profile | Missing Lab-specific composition contract and instances | Reference exact models, contracts, components, environment requirements and source profiles; compose existing package/install manifests. |
| G06 | Parent/local and per-capability bindings | Missing concrete bindings/profile constraints | Apply Model Instance Binding and applicable Capability Instance/Realization Binding contracts with exact revisions, extension limits and owner routes. A new generic adoption Definition is not yet justified. |
| G07 | Integrated compatibility, upgrade and recovery protocol | Existing mechanisms need composition | Specify before/after selections, compatibility checks, data/profile transitions, uncertain-effect reconciliation and retained-reader recovery. Respect existing installer/replay scope. |
| G08 | Exact relocation envelope | Missing selected migration instance | Use Repository Migration Manifest after boundaries and source selection. Region coverage is not its per-file allowlist or rollback set; in-place state changes require an appropriate separate contract. |
| G09 | Cross-workspace connection signatures/projections | Endpoint/signature audit pending | Prefer canonical binding artifacts and permitted read-only relation projections. Extend Relation Kinds only if current endpoint pairs/qualifiers cannot express a required connection. |
| G10 | Executable validation and pilot outcomes | Missing integrated checks/evidence | Validate references, owners, selections, overrides, transitions and one real isolated adoption/upgrade. Existing component results do not qualify this new composition. |

The existing [operation workspace schema](../../product/lab/release-candidates/v1/interface/api-integration-v17/workspace.schema.json) is a bounded candidate-staging contract. It does not define the proposed Lab operating workspace and must not be silently broadened or renamed.

Workspace catalogs and reverse indexes can be derived from selected manifests/bindings. Listing locations does not require independent identity/admission authority.

## Smallest coherent next package

1. Resolve G01 with a scoped meaning/profile proposal, preserving Project, Work and Goal semantics.
2. Author one Lab operating-model instance and its specialization/profile constraints (G02/G05).
3. Complete Craft's boundary, selected canonical manifests and actual parent/local bindings first (G03/G04/G06). Keep other candidates visible without inventing their records.
4. Specify the compatible transition/recovery contract, exact relocation envelope where needed, and endpoint audit (G07–G09).
5. Validate creation and one isolated upgrade, including refusal of incompatible, stale and ambiguous inputs (G10).

This audit inspected the live Definition registry, selected Artifact Type registry, relevant exact schemas/definitions, current map and bounded runtime/profile/install sources. Missing means not established for this whole-Lab composition, not proof that similarly named code is absent everywhere. Definitions and indexes were inspected; none were updated or synchronized. No new runtime conformance test was run.
