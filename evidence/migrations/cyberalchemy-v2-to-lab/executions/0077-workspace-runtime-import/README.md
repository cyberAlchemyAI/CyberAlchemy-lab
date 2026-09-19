# Workspace runtime import

Workspace model -> three exact external references -> complete runtime graph -> replay/export.

Imported twelve original Workspace nodes, fourteen relationships and 41 supporting documents through the existing tested v4 runtime. A separate reference package contains three explicit projections: Project (CAV2-D60), Product Capability (CAV2-D67), and the historical Essays explorer baseline. Together these form seventy semantic/governance event pairs. No runtime code changes were needed.

The reference nodes carry exact selected definition text or the original baseline record, source paths, fingerprints, and source owner routes. They are migration references, not newly owned definitions or accepted Essays implementation. The baseline's transitive evidence references remain inert historical data; this import does not validate all of that baseline's dependencies or acceptance claims.

Original `relations.json` remains unchanged. A separate adapter qualifies only its three external targets using the v4 cross-package alias mechanism. Reversing that declared mapping reproduces the original source relationships exactly. A Workspace context query includes the referenced nodes; a Workspace export retains its own package boundary.

The 0076 definitions successor remains selected, with all five section digests unchanged. Only Workspace's material fingerprint changes in the isolated legacy registry copy; every other registry entry is preserved. It matches the selected package material independently. This is candidate registration evidence for this snapshot, not activation or full validation of the legacy Python runtime.

Native validation passes. Twelve import checks and four rejection cases verify source selections, reversible relationship mapping, exact records/documents, external endpoint closure, restart equality, deterministic fresh stores, refusal to overwrite, corruption detection and missing-reference rejection. The same binary and its 23 passing tests from 0074 remain bound.

Store: `.local/workspace-runtime-0077/`. The full export and committed-store archive are retained here. The sibling Workspace dashboard and Essays source are unchanged; no server or enforcement hook is started.

Inspect:

```sh
.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime summary .local/workspace-runtime-0077
.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime export .local/workspace-runtime-0077
```

Reproduce from the Lab root: `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0077-workspace-runtime-import/verify.py`.

## Open Questions

- The generated Workspace system model and receipts are preserved documents; no system recompilation, dashboard functionality or conformance is claimed.
- Reference projections do not merge global identity or grant source authority to the Lab.
- Combined registration, currentness reporting and request/validator integration remain separate work.
- Next: Durable Storage registration — connect the already imported business model to the existing runtime and verify exact replay and evidence preservation.
