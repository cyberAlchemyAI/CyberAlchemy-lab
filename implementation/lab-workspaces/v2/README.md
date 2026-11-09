# Shared workspace runtime model v2

The current Lab runtime selects this contract through ../CURRENT.json. The Lab root and six Product homes use the same eight responsibilities: product, project, work, authority, ontology, architecture, implementation and docs. Product-owned source stays in its Product home; shared operations stay in the Lab.

A Product profile selects one Product scope and zero or more linked Projects. A Project profile selects one Project and may refer to a Product or another purpose. A Goal or Work item retains its existing Project membership. Product-wide operations need no fabricated Project. No standalone Project workspace is currently provisioned.

Profiles and their authority/workspace-model-binding.json selections use model version lab-workspace-model/v2. Unknown revisions refuse; migrate_v1 performs an explicit Project-only conversion while preserving identity and Goal membership. The current Craft Product profile retains its earlier workspace reference and embeds the existing Craft Project.

From the Lab root:

    python3 implementation/lab-runtime/lab.py workspace verify
    python3 implementation/lab-runtime/lab.py workspace list
    python3 implementation/lab-runtime/lab.py workspace resolve product/craft
    python3 implementation/lab-runtime/lab.py workspace dispatch product/craft --operation verify

All seven local profiles reference the same existing native v2 host. Resolve performs no installation. Specialization is bounded configuration and can use that same host. An explicitly selected dedicated target is optional; this migration creates none.

Dispatch executes the existing native host, rather than reimplementing its authority checks. Source-only reads use an ephemeral uninitialized store selection so they cannot accidentally read the operator's default private store. Project-owned commands require a selected Project, an explicit store and an exact native_store_bindings catalog selection. A binding names workspace_ref, project_ref, store_path and native_scope_ref. Native sealed-store replay must independently confirm the scope, Project and current source cut before existing review/authorize/apply gates run. There are no newly granted permissions or automatically provisioned stores.

The semantic successor was captured, prepared, inspected, materialized and reconstructed by the actual Define CLI. Native semantic admission remains distinct from selecting this executable configuration contract.

The current entrypoint requires an explicit workspace context for its operations. Low-level native Project-protocol compatibility is available through --native-project-protocol or the versioned native v2 entrypoint; it is not an implicit workspace conversion. Parent model, profile schema, Definition and local profile bindings are checked by exact SHA-256. Changing a selected profile requires an updated exact binding and an explicit successor revision.
