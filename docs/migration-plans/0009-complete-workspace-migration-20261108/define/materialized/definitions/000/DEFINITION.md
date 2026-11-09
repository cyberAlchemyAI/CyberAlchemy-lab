<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Lab Workspace

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.lab-workspace`
- Version: `2.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:lab-workspace-definition-proposal`
- Lifecycle posture reference: `proposal:lab-workspace:candidate-authored`

## Scientific/formal voice

A Lab Workspace is a durable, versioned operating scope bound to one explicitly selected primary subject of kind Product or Project. A Product workspace keeps its Product records, linked Project coordination and Work in one canonical home. A Project workspace binds one Project and may reference a Product or another declared purpose. It connects eight responsibility areas to an exact operating-model revision, accountable routes, source selections, configuration and lifecycle contracts. Workspace identity, subject identity, physical home, runtime instance and authority grants remain distinct. Shared operations and shared execution are the default; specialization does not require a runtime copy.

```text
W = (id, revision, primary_subject, purpose_refs, scope, owners, model_binding_ref, home_refs, selections, extensions, lifecycle, challenge_route). kind(primary_subject(W)) in {Product, Project}. identity(W) != identity(primary_subject(W)). location_change(W) does not imply identity_change(W). valid_profile(W) does not imply authorized(W).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| W | One proposed Lab Workspace record. |
| model_binding_ref | Exact parent/local Model Instance Binding, with separately scoped authority. |
| home_refs | Selected canonical-home manifests with their own lifecycle/recovery ownership. |

### Boundary conditions

- Exactly one primary subject kind is selected. A Product workspace may link zero or more Projects; a Project workspace binds its own Project and does not own other primary Projects.
- A Goal or Work record retains its existing Project ownership. Product-wide operations may omit a Project; Project-owned operations require a selected linked Project.
- A Project, Goal, Person, Team or model record does not automatically create another workspace.
- One Product has one canonical operating home. Co-located Project records do not provision extra homes or duplicate Product identity.
- Workspace kind and behavior specialization do not force dedicated execution, separate installation, copied runtime code or new authority.
- An unselected native subject identity remains explicitly unselected. A catalog key, folder or passing validation does not admit an identity or grant native permission.
- Lab Workspace names the durable scope; runtime instance names execution. Incompatible model/profile revisions require an explicit conversion.

### Testable conditions

- Both Product and Project profiles validate with exactly one matching primary subject kind.
- Linked Projects and Goal ownership are explicit and wrong-scope operations refuse.
- All eight responsibilities resolve to one canonical Product home.
- Multiple workspaces resolve to one shared execution target without code copies.
- Legacy Project profiles convert explicitly with unchanged subject and Goal membership.
- Native permission gates remain enforced by the existing host.

## Plain-language voice

A workspace is the durable working home of a Product or Project. Products keep their Projects and Work together; the Lab supplies shared operations. A workspace does not need its own runtime installation.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

This is a new scoped meaning proposal. Existing generic contracts remain applicable; no canonical Definition registry or running Craft configuration is changed.

### Examples

- Craft is a Product workspace containing its existing development Project and Goals.
- Ontology and its lifecycle Project share one Product home.
- A Project can have an operating workspace without creating a new Product.

## Applicability

Durable Product or Project operating scopes using one selected Lab model revision, including shared execution and embedded Project coordination.

### Exclusions

- Redefining Project, Product, Goal, Work, Bounded Context or Canonical Package Home.
- The existing owned-candidate-operation-workspace protocol.
- Creating owner assignments, global relations, admission, installation, deployment or runtime permissions.

## Boundaries

- Exactly one primary subject kind is selected. A Product workspace may link zero or more Projects; a Project workspace binds its own Project and does not own other primary Projects.
- A Goal or Work record retains its existing Project ownership. Product-wide operations may omit a Project; Project-owned operations require a selected linked Project.
- A Project, Goal, Person, Team or model record does not automatically create another workspace.
- One Product has one canonical operating home. Co-located Project records do not provision extra homes or duplicate Product identity.
- Workspace kind and behavior specialization do not force dedicated execution, separate installation, copied runtime code or new authority.
- An unselected native subject identity remains explicitly unselected. A catalog key, folder or passing validation does not admit an identity or grant native permission.
- Lab Workspace names the durable scope; runtime instance names execution. Incompatible model/profile revisions require an explicit conversion.

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

- lab-workspace-model/v2

## Lookup and drift

- Index: `ontology/lab-workspace/INDEX.json` / `cal.definition.lab-workspace@2.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `docs/proposals/0012-lab-workspace-model/RESIDUE.md`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- docs/migration-plans/0009-complete-workspace-migration-20261108/REPORT.md

## Residue

- Candidate semantic standing does not create native admission or authority grants.

## Claim ceiling

Scoped Definition candidate only. Its normative voice is proposed, not admitted authority; schema/projection checks do not create workspace adoption, owner permission or runtime effects.
