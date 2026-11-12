# Canonical definitions

Use current.json to resolve the live admitted registry and signed canonical location map. DEFINITIONS-INDEX.md and V2-CATALOG.json are human and machine views of that selection.

Current bodies live in each owning Lab Workspace:

    authority/definitions/<readable-name>/<version>/definition.json
    authority/definitions/<readable-name>/<version>/DEFINITION.md
    authority/definitions/<readable-name>/<version>/field-lineage.json
    authority/definitions/<readable-name>/<version>/evidence.json

The shared Lab workspace uses this root directory. Product-owned definitions use the same tree inside their own workspace.

registry.json and older candidate/admission paths remain immutable historical source dependencies. Their old current_lookup values describe their original frozen source epoch; they are not the active catalog selector. Do not edit or regenerate them to simulate migration.

Definition/v2 identifies the full record carrier and required structure. Existing record version strings, including candidate suffixes, are preserved byte-exactly when accepted. Admission and current standing are recorded separately by the verified shared Lab workflow.

Semantic ownership remains in the definition and its bound owner disposition. The maintenance-home map assigns technical custody only.
