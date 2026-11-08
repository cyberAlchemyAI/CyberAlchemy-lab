<!-- GENERATED from frozen Define Pack revision 2 and exact captured source bytes. -->

# Define result: Lab workspace model

**Actual CLI result: prepared-with-gaps.** Revision 2 preserves revision 1 and the explicit user terminology answer.

The original proposal was authored directly before this Define pass. This run is corrective preparation, not retrospective proof that the original workflow occurred.

- Consumer: `lab-workspace-model-reviewer`
- Intended use: `prepare-owner-review`
- Goal: Prepare the semantic basis for the first Lab workspace operating model and concrete Craft candidate profile.
- Originating intent: Restructure the Lab around reusable capabilities and locally owned Project workspaces that can explicitly adopt future model evolution.

## Explicit answer

Use “Lab Workspace” for the durable scope and “runtime instance” for execution

This closes the terminology question for candidate authoring. It does not accept the entire Workspace meaning or establish native owner authority.

## Actual stages

| Stage | Observed result |
| --- | --- |
| Default Define/native-context integrity and read | Completed, no store/key setup |
| Define v3 Lab snapshot capture | Completed, exact registry/body snapshot matching |
| Prepare | Prepared with gaps |
| Inspect | Frozen package integrity verified |
| Materialize | Complete candidate Definition/v2 emitted with field lineage; owner outcome null |
| Reconstruct | Exact frozen members restored |
| Observe requested owner-review use | Blocked: local snapshot and current authority not established |

The materialization operation emitted candidate bytes. Frozen preparation readiness and actual materialization results are separate records; no Pack is rewritten to convert a blocked use into permission.

## Dispositions

| Concept | Disposition | Decision route |
| --- | --- | --- |
| project | reuse | `role:definition-owner` |
| goal | reuse | `role:definition-owner` |
| work | reuse | `role:definition-owner` |
| product | reuse | `role:definition-owner` |
| project-state | reuse | `role:definition-owner` |
| canonical-package-home | reuse | `role:definition-owner` |
| canonical-package-manifest | reuse | `role:definition-owner` |
| governed-model | reuse | `role:definition-owner` |
| model-instance-binding | reuse | `role:definition-owner` |
| capability-instance | reuse | `role:definition-owner` |
| capability-realization-binding | reuse | `role:definition-owner` |
| bounded-context | reuse | `role:definition-owner` |
| authority-boundary | reuse | `role:definition-owner` |
| parent-instance-separation | reuse | `role:definition-owner` |
| bounded-self-application | reuse | `role:definition-owner` |
| lab-workspace | propose | `role:definition-owner` |
| formal-symbol-fit | open | `role:definition-owner` |
| lab-instance-terminology | propose | `role:definition-owner` |
| semantic-owner-acceptance | open | `role:definition-owner` |

## New Workspace proposal

Candidate only, unchanged from the retained pre-Define draft. The CLI independently checked its carrier, symbol declarations and mechanical field attribution; semantic fidelity remains separately reviewable.

**Normative proposal**

A Lab Workspace is a durable, versioned operating scope for one explicitly identified primary Project, binding its locally owned records and referenced canonical package homes to an exact reusable Lab operating-model revision through a Model Instance Binding. It declares purpose, scope and exclusions, accountable routes, applicable contracts, local configuration and extension limits, source selections, lifecycle and challenge handling. Workspace identity remains separate from Project and Product identity, semantic context, canonical package home, repository location, runtime installation and authority grants. Location, hosting and model upgrades do not by themselves replace its identity or transfer ownership.

**Formal expression**

```text
W = (id, revision, primary_project_ref, purpose_refs, scope, owners, model_binding_ref, home_refs, selections, extensions, lifecycle, challenge_route). primaryProject(W) != identity(W). location_change(W) does not imply identity_change(W). valid_profile(W) does not imply adopted(W) or authorized(W).
```

**Notation**

- `W`: One proposed Lab Workspace record.
- `model_binding_ref`: Exact parent/local Model Instance Binding, with separately scoped authority.
- `home_refs`: Selected canonical-home manifests with their own lifecycle/recovery ownership.

**Plain-language interpretation**

A Lab Workspace is the durable working home of a Project using a selected version of the Lab model. It connects local records, owners and tools while preserving each record owner and keeping upgrades explicit.

**Domain interpretation**

This is a new scoped meaning proposal. Existing generic contracts remain applicable; no canonical Definition registry or running Craft configuration is changed.

- Craft has one proposed workspace profile referencing CA2-PROJECT-CRAFT and CA2-PRODUCT-CRAFT without copying those identities.
- A Goal of Craft stays a Goal record; it does not automatically provision another workspace.
- An installation may serve the workspace but is not the workspace identity.

**Applicability**

The proposed durable operating scope connecting one primary Project to selected Lab model capabilities, local records and referenced package homes.

**Boundaries**

- A workspace has one primary Project in this proposed profile; Product references are optional where the Project pursues another explicit purpose.
- A Project, Goal, Work item, Person or Team record does not automatically become another workspace.
- Distinct semantic owners and independently recoverable homes remain distinct even inside one workspace.
- The parent owns inherited contracts; local changes stay inside explicit extension scope.
- Unqualified Lab instance is not an alias here: use Lab Workspace for the durable modeled scope and runtime installation/instance for execution.
- A workspace can remain proposed with no installation or actual adoption outcome; preparation, schema validity and profile replay grant no authority.

## Local terminology convention

The explicit answer is recorded as a local Pack working meaning. It is not selected for another shared Definition:

For this model, Lab Workspace names the durable Project operating scope; runtime instance names execution. The two identities are kept separate.

Its scope is this candidate model. The source is the explicit user answer, not an inferred review decision.

## Open questions and stopping conditions

### formal-symbol-fit

Do the explicit candidate formal-symbol schemas faithfully represent the abstract Workspace definition and its concrete profile mapping?

- Reason: The draft had notation but no Define parameter declaration. This pass authors that declaration explicitly, without an application or assessment.
- Affected use: `governing-application`
- Owner route: `role:definition-owner`
- Next action: Definition owner reviews symbol schemas and concrete-profile correspondence; keep unaccepted mapping open.

### semantic-owner-acceptance

Who can accept the new Workspace meaning and the exact initial model adoption?

- Reason: Role labels and a conversation request to author the package are not independent semantic acceptance or native permission.
- Affected use: `governing-application`
- Owner route: `role:definition-owner`
- Next action: Obtain an exact appropriately scoped owner outcome through its own route after meaning review; no authorization or apply is executed here.

Owner-review use additionally remains blocked by `local-snapshot` and `current-authority`. No operator setup, signing, native review/apply or canonical registry admission was performed.

## Allowed use and claim ceiling

Inspect the prepared meaning and exact sources; challenge or revise candidate content; verify frozen bytes; materialize the explicitly selected candidate. Native review/adoption/publication follows its own qualified route.

Candidate preparation and exact binding checks only; no semantic acceptance, domain execution, permission or admission.

## Exact reused meanings

The Lab adapter records historical registry/body matches. Standalone Define keeps each meaning at local-reference standing; these snapshots are not authenticated current host permission. The excerpts below are complete selected normative statements, with original file and selected-entry hashes.

### Project

- Disposition: reuse
- Exact source: `CAV2-D60@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0006-craft-identity/definitions/project/v1/definition.json` / `""`
- Original-file SHA-256: `f342be625bee345590d9d1f4f20ff14f6005c8ec9ed9108f0cf70cd0ae05ca68`
- Selected-entry SHA-256: `1725fb43cac106bd2e95d46ef3f5c844a0702688222fd70366d28135c42abc45`
- Owner route: `role:definition-owner`

A Project is a durable coordination identity with purpose, scope, exclusions, owner routes, Goal references, evidence index, purpose or Product connections, lifecycle, and challenge route. Its identity survives changes to plans, tasks, folders, tools, and implementations.

**Boundary conditions**

- A proposed Project has at least one draft or active Goal.
- An active Project has at least one active Goal.
- Directory placement and membership do not create Project identity.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Goal

- Disposition: reuse
- Exact source: `CAV2-D59@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0006-craft-identity/definitions/goal/v1/definition.json` / `""`
- Original-file SHA-256: `f43a539e5f0f4db26dab0df0cb30c523868c6fef3dbb3d061614a4d288c5ae19`
- Selected-entry SHA-256: `5645c37d7cb176d383363cf276f2781dd16e8a6e984ac1ec6a1a916bde157b26`
- Owner route: `role:definition-owner`

A Goal states a desired future outcome for one Project and becomes achieved only when all required success conditions have adequate evidence and the Goal owner records the lifecycle transition. Progress or passing checks alone do not achieve it.

**Boundary conditions**

- A Goal belongs to exactly one Project in this contract.
- Evidence supports but does not perform the achievement decision.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Work

- Disposition: reuse
- Exact source: `cal.definition.work@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/work/v1/definition.json` / `""`
- Original-file SHA-256: `fcae28e30cb7aa64eca252b739ed4401709b7039770a6af52ac2b7a93bcad5b0`
- Selected-entry SHA-256: `99c34b529f852b9c072b74f9c006d93cd678938e964988274cdade6ff49fc639`
- Owner route: `role:definition-owner`

Work is a bounded unit of coordinated effort with a declared purpose, owner, participants, inputs, expected result, constraints, lifecycle, and outcome trace. Work is not necessarily a Project and does not imply authority, completion, successful outcome, or Product value.

**Boundary conditions**

- Work is a bounded unit of coordinated effort with a declared purpose, owner, participants, inputs, expected result, constraints, lifecycle, and outcome trace.
- Work is not necessarily a Project and does not imply authority, completion, successful outcome, or Product value.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Product

- Disposition: reuse
- Exact source: `cal.definition.product@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0006-craft-identity/definitions/product/v1/definition.json` / `""`
- Original-file SHA-256: `19c6b3bdb5e4c8515837d40c2b0a98b0fecb6edc3698aab359fa2a0d64d9a1cd`
- Selected-entry SHA-256: `0f911fc3a4916cbc1931cc0fe754fce8b824ecc7a0be6e24f96dffb8a17bd92b`
- Owner route: `role:definition-owner`

A Product is a durable identity-bearing boundary for a coherent purpose and promise of value. It may be coordinated by Projects, embody Methods, contain Product Features and Capabilities, and have many realizations, but none of those relations merges their identities or transfers their authority.

**Boundary conditions**

- A shared name, owner, path, or relation does not collapse Product with another identity.
- Product placement does not create a Bounded Context.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Project State

- Disposition: reuse
- Exact source: `cal.definition.project-state@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/project-state/v1/definition.json` / `""`
- Original-file SHA-256: `40e00c926c7ca2a9143c321e1681ebb7df480c71d4b8950e5524849758b4e784`
- Selected-entry SHA-256: `cf2e5c891872928931a8baed214f39c2734b62ed2edd637675c76f8fee454523`
- Owner route: `role:definition-owner`

Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records. Project State is not owned by an Agent and is not hidden cross-session Machine Agent memory.

**Boundary conditions**

- Project State belongs to the governed Project and its artifact owners, never to an Agent or model.
- Only explicit governed writes of artifacts, events, evidence, receipts, Decisions, and relations change Project State.
- Context Views and Ontology Views select Project State for a consumer; they do not create a competing canonical store.
- Hidden model state, caches, conversation recall, and expired Session Memory are excluded unless explicitly persisted through the governed Project path.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Canonical Package Home

- Disposition: reuse
- Exact source: `cal.definition.canonical-package-home@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0008-canonical-package-home/definitions/canonical-package-home/v1/definition.json` / `""`
- Original-file SHA-256: `c810597968723991449fe78458254679cc6dc87b2b81e54e16a9aa599c59f8ca`
- Selected-entry SHA-256: `44e7170133932b377af3ad7d3297513f2b274dba8d6ec631c0d8d3fd476a9bfa`
- Owner route: `role:definition-owner`

A Canonical Package Home is the unique governed artifact tree H selected for an owner-local aggregate A by an explicit lifecycle-owner binding and unit-of-change declaration. H carries A's canonical machine sources. Capability, bounded-context, product, DomainSpec, implementation, evidence, and projection facets may be colocated in H when they share A's lifecycle, but their identities and authorities remain distinct and are connected by explicit typed relations. Indexes and global views may reference or generate projections of H; they must not duplicate its canonical carriers.

**Boundary conditions**

- The lifecycle owner and unit of change select the home; the directory does not select the owner, identity, or context.
- Semantic orthogonality requires distinct identities and typed relations, not separate physical roots.
- A bounded context may be a facet of an aggregate without being the aggregate's directory or owning every colocated artifact.
- Artifacts with different lifecycle owners or independent recovery boundaries require separate canonical homes even when one global index presents them together.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Canonical Package Manifest

- Disposition: reuse
- Exact source: `cal.definition.canonical-package-manifest@1.0.0-candidate.2`
- Source path / selector: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/canonical-package-manifest/v1/definition.json` / `""`
- Original-file SHA-256: `2837753f9bbcf00e62edc7ebae07de9724e4eafbcd834d73ba2550ec5e2ba641`
- Selected-entry SHA-256: `40bc0a828084f243428c2811c0ddec7ccb83e01725a3ace820acf4ea033e3984`
- Owner route: `role:definition-owner`

A Canonical Package Manifest M declares one canonical package home, aggregate, lifecycle owner, unit of change, every governed member's unique surface role, and every independent nested package relation. M must classify its own package.json exactly once as a canonical instance of Canonical Package Manifest/v1. Membership and nesting are explicit data, not directory inference.

**Boundary conditions**

- Files with different lifecycle owners or recovery boundaries require separate package homes.
- A directory without its own manifest remains a facet of the nearest declared package.
- Manifest membership cannot change Artifact identity or type.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Governed Model

- Disposition: reuse
- Exact source: `cal.definition.governed-model@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/governed-model/v1/definition.json` / `""`
- Original-file SHA-256: `b53f09b48390daf9477c0d025e9c6f3b15798c82dba093033c03086cd4a4732f`
- Selected-entry SHA-256: `9dc3c1439ba772079326572cabd45876fd73c56c21eacce819dfa67d87e512d9`
- Owner route: `role:definition-owner`

A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route. It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.

**Boundary conditions**

- A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route.
- It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Model Instance Binding

- Disposition: reuse
- Exact source: `cal.definition.model-instance-binding@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0014-definition-specialization-resolution/definitions/model-instance-binding/v1/definition.json` / `""`
- Original-file SHA-256: `f5338122a26ebbf89d8e1f4b9255ba619d66b59b7542ce88edcd974687550ca3`
- Selected-entry SHA-256: `c593a4758e351f76f9b59a73f7d03a867cca4c777a984e8fe313574a19abb0f1`
- Owner route: `role:definition-owner`

A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling. It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.

**Boundary conditions**

- The parent owns its contract; the instance owner controls only the declared extension scope.
- Inherited clauses retain parent provenance and cannot be silently weakened locally.
- A generic relation projection is read-only when the specialized Binding is canonical.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Capability Instance

- Disposition: reuse
- Exact source: `cal.definition.capability-instance@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/capability-instance/v1/definition.json` / `""`
- Original-file SHA-256: `d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5`
- Selected-entry SHA-256: `6deb9f0f581f3ea1861779b12bdfc20731b0ac001aaf657bc85264011f8e0eb4`
- Owner route: `role:definition-owner`

A Capability Instance is an owner-local, version-exact realization or specialization of one Product Capability inside explicitly declared coordination and semantic contexts. It binds separate parent and instance authority lanes, inherited contract, extension scope, adoption decision, D65 construction stages, conformance evidence, lifecycle, drift and recomposition routes, recursion budget or stop, and terminal handoff.

**Boundary conditions**

- Exactly one parent capability version is explicit.
- Recursion includes a budget or stop and a recomposition route.
- Parent and instance authority claims remain separate.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Capability Realization Binding

- Disposition: reuse
- Exact source: `cal.definition.capability-realization-binding@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0014-definition-specialization-resolution/definitions/capability-realization-binding/v1/definition.json` / `""`
- Original-file SHA-256: `8a0f907bb854371b8946e071c9d01702de3f35799405cb8b0ee66e546990b1bd`
- Selected-entry SHA-256: `3fa46f2682943be2b0b273df49d1d5712255cfc1b5f19c0a580c997ba503ebdf`
- Owner route: `role:definition-owner`

A Capability Realization Binding is a lifecycle-bearing canonical association between one exact Product Capability revision and one or more exact Implementation revisions, with realization role, adoption posture, compatibility, conformance evidence, deployment applicability, owner, succession, and challenge handling. It is neither the Product Capability nor an Implementation and does not prove adoption, deployment, conformance, successful operation, or Product value.

**Boundary conditions**

- Product Capability states the durable outcome promised; Implementation supplies technical realization; the Binding owns their lifecycle-bearing association.
- The Binding is canonical for specialized realization state and may project one digest-bound Typed Relation.
- Changing either endpoint or adoption posture creates a successor Binding revision.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Bounded Context

- Disposition: reuse
- Exact source: `cal.definition.bounded-context@2.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0002-ctx06-context-map-reference-normalization/definitions/bounded-context/v2/definition.json` / `""`
- Original-file SHA-256: `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0`
- Selected-entry SHA-256: `715dbc59597c87d920cad8bc50753a3d1c0b0a96f2cd1cdce4de6d471bdb206f`
- Owner route: `role:definition-owner`

A Bounded Context is a versioned, owner-scoped semantic boundary inside which one declared domain model and one Ubiquitous Language are intended to remain internally consistent for an explicit scope and set of exclusions. It owns its identity, model, language, scope, contracts, semantic owner, lifecycle, evidence, and challenge route. A Bounded Context does not canonically own map membership or backreferences to Context Maps. Cross-context endpoint membership and directional relationships are owned only by separately governed Context Maps; reverse membership for a context is a generated projection derived from those maps.

**Boundary conditions**

- A folder name cannot establish context identity.
- Shared spelling across contexts does not imply shared meaning.
- A Bounded Context cannot carry a canonical Context Map backreference.
- Absence from a generated reverse-membership index does not amend any Context Map.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Authority Boundary

- Disposition: reuse
- Exact source: `cal.definition.authority-boundary@1.0.0-candidate.1`
- Source path / selector: `authority/definitions/candidates/0003-single-decision-checkpoint/definitions/authority-boundary/v1/definition.json` / `""`
- Original-file SHA-256: `e6928339ebf6cbd41966e268da7eeee32d395da382522da086f98c3e2737896c`
- Selected-entry SHA-256: `8803ce1e2777bfb499278acc9984d6888a48243700654a79e31d7ab82f29f57a`
- Owner route: `role:definition-owner`

An Authority Boundary is the explicit owner-scoped limit within which one role may make Governance Decisions about named meanings, targets, and effects. It binds an owner role, an accountable principal binding, an authority scope, allowed effects, excluded effects, and a challenge route. An Authority Boundary is independent of where a workflow requests a decision, and no workflow profile or user preference may create, move, merge, or widen it.

**Boundary conditions**

- One principal holding multiple roles does not merge their Authority Boundaries.
- A Decision Checkpoint does not grant authority.
- Validation evidence cannot substitute for an owner decision.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Parent-Instance Authority Separation Invariant

- Disposition: reuse
- Exact source: `cal.definition.parent-instance-authority-separation-invariant@1.0.0-candidate.1`
- Source path / selector: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/parent-instance-authority-separation-invariant/v1/definition.json` / `""`
- Original-file SHA-256: `abf1ae8f7112b09fd349848b44794b71b89aa77db07d54d3bae12b317832bfc4`
- Selected-entry SHA-256: `19afca83f9ad5a8d71e79389f601a62dc6ee1412e42be490f52e2d0db546f6af`
- Owner route: `role:definition-owner`

Parent-Instance Authority Separation Invariant is the normalized invariant identified by semantic.parent-instance-authority-separation-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D64 without silently merging it with another target.

Bound source-semantic basis:

The recursive instance ownership invariant is the must-hold CyberAlchemy v2
condition that a governed parent model and a locally owned instance remain
connected without collapsing their semantic authority, coordination boundary,
or lifecycle.

The parent-model owner holds scoped semantic authority for the shared contract
and the conditions under which it may be instantiated, specialized, or
composed. The named instance owner holds a separate scoped semantic authority
for the instance's local meaning, state, evidence, and lifecycle. Here,
`ownership` is shorthand for these explicit `CAV2-D34` authority claims; it is
not inferred from a folder, label, repository permission, or generic
responsibility. A Project carries the typed binding, goals, owners, evidence,
and challenge route that keep the instance connected to its purpose, but
Project membership or file placement does not itself create semantic,
adoption, or execution authority.

The parent and instance must be joined by an explicit `CAV2-D16` typed relation
bound to an exact parent version or state. The instance may narrow or realize
the parent contract only inside its declared specialization scope. It must not
silently redefine the parent. The parent must not absorb, overwrite, or treat
instance-local meaning as shared authority without the instance owner's route
and the applicable `CAV2-D48` promotion or adoption path.

**Boundary conditions**

- This invariant is not authority, ownership by file location, Project authority,
repository access, inheritance by naming, schema conformance, implementation
success, automatic adoption, or promotion. It does not require every artifact
to have a parent model, make every capability a Project, or make every instance
canonical. It governs only relationships where downstream work relies on a
parent model and an independently scoped owned instance remaining connected.

It is not a Discipline (`CAV2-D50`). A later Discipline may steward recurring
binding audits and hardening, and a Constitution may enforce selected bindings,
but neither is created or adopted by this definition.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.

### Bounded Self-Application Invariant

- Disposition: reuse
- Exact source: `cal.definition.bounded-self-application-invariant@1.0.0-candidate.1`
- Source path / selector: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/bounded-self-application-invariant/v1/definition.json` / `""`
- Original-file SHA-256: `43022dc89b33b3e88701ebe9225e7feaf806ef55565050bc84d82b36e0c7055f`
- Selected-entry SHA-256: `1fdb6ee013b75b9cd3c7af682c7505091a37e3b3994bce75afa26817eec05ad6`
- Owner route: `role:definition-owner`

Bounded Self-Application Invariant is the normalized invariant identified by semantic.bounded-self-application-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D30 without silently merging it with another target.

Bound source-semantic basis:

Bounded recursive self-application is the CyberAlchemy v2 invariant that a
governed process may be applied to artifacts produced by that same process only
when each recursive step declares its artifact, altitude or layer, scope, owner,
gate, carried state or residue, recomposition path, and stopping condition.

The recursive move must preserve authority boundaries: the process, the artifact
being processed, the owner route, and the resulting authority posture must remain
distinct unless an explicit promotion or coupling records otherwise.

**Boundary conditions**

- Bounded recursive self-application is not ordinary code recursion, not generic
self-hosting, not endless reflection, not child-folder nesting, not automatic
promotion, and not a license to run agents recursively without a budget. It does
not replace `CAV2-D17` reflection tower method or `CAV2-D20` Craft method; it
governs when process-on-own-artifact moves are admissible across those and
other methods.

**Applicability to this Pack:** Reuse this exact source meaning for candidate model examination. Recorded registry standing does not prove fit, current host permission or acceptance of the new workspace composition.
