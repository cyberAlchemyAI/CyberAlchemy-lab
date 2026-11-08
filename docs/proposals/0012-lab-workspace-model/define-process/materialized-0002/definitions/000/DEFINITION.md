<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Lab Workspace

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.lab-workspace`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:lab-workspace-definition-proposal`
- Lifecycle posture reference: `proposal:lab-workspace:candidate-authored`

## Scientific/formal voice

A Lab Workspace is a durable, versioned operating scope for one explicitly identified primary Project, binding its locally owned records and referenced canonical package homes to an exact reusable Lab operating-model revision through a Model Instance Binding. It declares purpose, scope and exclusions, accountable routes, applicable contracts, local configuration and extension limits, source selections, lifecycle and challenge handling. Workspace identity remains separate from Project and Product identity, semantic context, canonical package home, repository location, runtime installation and authority grants. Location, hosting and model upgrades do not by themselves replace its identity or transfer ownership.

```text
W = (id, revision, primary_project_ref, purpose_refs, scope, owners, model_binding_ref, home_refs, selections, extensions, lifecycle, challenge_route). primaryProject(W) != identity(W). location_change(W) does not imply identity_change(W). valid_profile(W) does not imply adopted(W) or authorized(W).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| W | One proposed Lab Workspace record. |
| model_binding_ref | Exact parent/local Model Instance Binding, with separately scoped authority. |
| home_refs | Selected canonical-home manifests with their own lifecycle/recovery ownership. |

### Boundary conditions

- A workspace has one primary Project in this proposed profile; Product references are optional where the Project pursues another explicit purpose.
- A Project, Goal, Work item, Person or Team record does not automatically become another workspace.
- Distinct semantic owners and independently recoverable homes remain distinct even inside one workspace.
- The parent owns inherited contracts; local changes stay inside explicit extension scope.
- Unqualified Lab instance is not an alias here: use Lab Workspace for the durable modeled scope and runtime installation/instance for execution.
- A workspace can remain proposed with no installation or actual adoption outcome; preparation, schema validity and profile replay grant no authority.

### Testable conditions

- Primary Project and workspace identities remain distinct and explicit.
- All eight responsibilities resolve to selected homes and preserved source records.
- Parent/local model revisions, owners, authority scopes and extension limits resolve without collapse.
- A changed parent or local revision produces a successor binding; historical records remain exact.
- No Goal membership, adoption outcome or runtime activation is inferred from a folder or passing check.

## Plain-language voice

A Lab Workspace is the durable working home of a Project using a selected version of the Lab model. It connects local records, owners and tools while preserving each record owner and keeping upgrades explicit.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

This is a new scoped meaning proposal. Existing generic contracts remain applicable; no canonical Definition registry or running Craft configuration is changed.

### Examples

- Craft has one proposed workspace profile referencing CA2-PROJECT-CRAFT and CA2-PRODUCT-CRAFT without copying those identities.
- A Goal of Craft stays a Goal record; it does not automatically provision another workspace.
- An installation may serve the workspace but is not the workspace identity.

## Applicability

The proposed durable operating scope connecting one primary Project to selected Lab model capabilities, local records and referenced package homes.

### Exclusions

- Redefining Project, Product, Goal, Work, Bounded Context or Canonical Package Home.
- The existing owned-candidate-operation-workspace protocol.
- Creating owner assignments, global relations, admission, installation, deployment or runtime permissions.

## Boundaries

- A workspace has one primary Project in this proposed profile; Product references are optional where the Project pursues another explicit purpose.
- A Project, Goal, Work item, Person or Team record does not automatically become another workspace.
- Distinct semantic owners and independently recoverable homes remain distinct even inside one workspace.
- The parent owns inherited contracts; local changes stay inside explicit extension scope.
- Unqualified Lab instance is not an alias here: use Lab Workspace for the durable modeled scope and runtime installation/instance for execution.
- A workspace can remain proposed with no installation or actual adoption outcome; preparation, schema validity and profile replay grant no authority.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| authority/definitions/candidates/0006-craft-identity/definitions/project/v1/definition.json | whole-file | `f342be625bee345590d9d1f4f20ff14f6005c8ec9ed9108f0cf70cd0ae05ca68` | `admitted` |
| authority/definitions/candidates/0006-craft-identity/definitions/goal/v1/definition.json | whole-file | `f43a539e5f0f4db26dab0df0cb30c523868c6fef3dbb3d061614a4d288c5ae19` | `admitted` |
| authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/work/v1/definition.json | whole-file | `fcae28e30cb7aa64eca252b739ed4401709b7039770a6af52ac2b7a93bcad5b0` | `admitted` |
| authority/definitions/candidates/0008-canonical-package-home/definitions/canonical-package-home/v1/definition.json | whole-file | `c810597968723991449fe78458254679cc6dc87b2b81e54e16a9aa599c59f8ca` | `admitted` |
| authority/definitions/candidates/0014-definition-specialization-resolution/definitions/model-instance-binding/v1/definition.json | whole-file | `f5338122a26ebbf89d8e1f4b9255ba619d66b59b7542ce88edcd974687550ca3` | `admitted` |
| evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/parent-instance-authority-separation-invariant/v1/definition.json | whole-file | `abf1ae8f7112b09fd349848b44794b71b89aa77db07d54d3bae12b317832bfc4` | `admitted` |
| evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/bounded-self-application-invariant/v1/definition.json | whole-file | `43022dc89b33b3e88701ebe9225e7feaf806ef55565050bc84d82b36e0c7055f` | `admitted` |

## Primary consumers

- model:lab-workspace:operating-model@1.0.0-candidate.1
- workspace:craft:lab@1.0.0-candidate.1

## Lookup and drift

- Index: `docs/proposals/0012-lab-workspace-model/definition/INDEX.json` / `cal.definition.lab-workspace@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `docs/proposals/0012-lab-workspace-model/RESIDUE.md`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- docs/proposals/0012-lab-workspace-model/README.md

## Residue

- Definition-owner review and exact admission remain separate.
- Local workspace profile schema is an implementation/proposal contract, not an admitted Artifact Type.
- One native Craft upgrade remains unexecuted.

## Claim ceiling

Scoped Definition candidate only. Its normative voice is proposed, not admitted authority; schema/projection checks do not create workspace adoption, owner permission or runtime effects.
