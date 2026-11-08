# Dependency and ownership rules

Status: observed constraints plus recommendations for a future migration.

| Boundary | Observed mechanism | Mapping requirement |
| --- | --- | --- |
| Local instance → shared capability | [Craft component bindings](../../../craft/implementation/bindings.json) select local source and external runtimes | Preserve exact selections and read-only shared installations; no uncontrolled mutable dependency adoption |
| Project → Product / Work / Goal | [Project](../../../authority/definitions/candidates/0006-craft-identity/definitions/project/v1/definition.json), [Goal](../../../authority/definitions/candidates/0006-craft-identity/definitions/goal/v1/definition.json) and [Work](../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/work/v1/definition.json) preserve separate identities | Folder containment cannot synthesize membership, change identity or grant authority |
| Candidate → effective authority | [Existing admissions](../../../authority/admissions/) and [registry](../../../authority/definitions/registry.json) supply exact overlays | Keep source posture, registry standing, local owner outcome and runtime activation separate |
| Runtime → source profile | [v2 profile](../../../implementation/lab-runtime/v2/profile.json) and [source adapter](../../../implementation/lab-runtime/v2/lab_runtime/sources.py) pin selected sources | Relocation changes require explicit successor bindings; do not refresh historical pins silently |
| Candidate families → repository roots | [Work episode](../../../implementation/lab-work/candidates/v1/episode.py), [context source](../../../implementation/lab-context/candidates/v1/context.py) and [provisioning source](../../../implementation/lab-provisioning/candidates/v1/provision.py) import sibling/runtime source | Enumerate imports, diagnostic fixtures and path resolution before moving a family |
| Package/install → active generation | [Installation source](../../../product/lab/release-candidates/v1/interface/api-installation-release-v4/installation_release.py) binds preimages and retained generations | Existing install/rollback is reused; semantic/carrier migrations and whole-instance adoption still need composition |
| State → context/ontology views | [Session source](../../../implementation/lab-runtime/v2/lab_runtime/session.py) verifies freshness and expiry | Do not migrate ephemeral memory as durable state or equate Project/ontology cursors |
| Lab → external consumers | Twelve Body War symlinks in the source baseline | Retain compatible paths or explicitly rebind and qualify consumers before relocation |

Historical snapshots and admission bundles remain exact even when a successor current home is introduced. Test source and required fixtures move with their owning implementation selection; saved execution reports retain their own evidence provenance.
