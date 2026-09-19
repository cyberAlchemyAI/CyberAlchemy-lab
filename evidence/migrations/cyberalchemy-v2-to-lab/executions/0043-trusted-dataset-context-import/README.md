# Trusted Dataset Materialization context import

Source window -> transform -> validate -> publish or quarantine -> checkpoint.

This candidate preserves the standalone Trusted Dataset Materialization Product assignment from capability import 0035. Work orchestration remains a dependency.

Seven byte-exact source snapshots preserve the profile, capability, ontology, definitions, bindings, pipeline and system bindings. The ontology declares 34 named concepts (nine entities, 13 events and 12 operations) and five rules; the separate registry supplies eight definitions.

The source has no typed relationship registry. Empty normalized relationship IDs record this gap; no edges are inferred from names or rule prose. Definitions absent from the entity list remain separate. The normalized Context and Ontology headers validate against migration-scoped contracts, while source registries remain source-qualified candidates.

The isolated store is `.local/ontology-context-import-0043/`. It includes the bundle and its source snapshots. References to generated outputs and implementation code remain source metadata; this is not a standalone executable package. No pipeline, connector, publication, SQL or recovery behavior was executed, and no ontology admission is granted.

Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0043-trusted-dataset-context-import/verify.py` from the repository root. Verification covers deterministic replay, header schemas, invalid bindings/concepts/rules, standalone Product preservation, snapshot and pointer readback, source counts and unchanged capability storage.
