# Current workspace runtime model

Use [the current shared runtime model](../../implementation/lab-workspaces/v2/README.md), [the current meaning and operating model](../../ontology/lab-workspace/v2/operating-model.json), and [the implementation/verification report](../../docs/migration-plans/0009-complete-workspace-migration-20261108/REPORT.md).

All six local Product homes share the eight-area layout. The Lab root is the seventh local workspace profile. Product records, Project coordination and Work stay in one Product home. Root implementation contains shared operations and compatibility references; product-owned code has one physical owner.

The selected schema is lab-workspace/v2, with Product and Project kinds. Both profiles use one shared target by default. Workspace, subject, physical home and execution identities remain distinct. Goal/Work ownership, current revision, exact parent/local bindings and native permissions are checked. Older Project-only contracts and frozen Packs remain exact predecessors.

The current entrypoint requires a workspace context. Explicit low-level native Project-protocol compatibility does not imply a workspace conversion. No workspace runtime installation, semantic admission or authority grant is created by this migration.
