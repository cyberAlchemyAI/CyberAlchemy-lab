# Three-Layer Protection and Recovery context imported

Operational database + recovery journal + independent immutable archive -> restore candidate -> destination retrieval -> verified restoration.

The isolated context contains 25 source concepts, 21 relationships, 12 rules and nine proof requirements. All endpoints resolve internally. Twelve definition bindings resolve to graph concepts, and the preserved definition file matches its source registry digest. Twelve source files are preserved byte-for-byte.

[Context](context.json). [Ontology](ontology.json). [Bundle](bundle.json). Store: `.local/ontology-context-import-0039/`.

The source graph contains labels and named relationships, including PostgreSQL adapter and Docker environment labels. These remain source records, not active provider selections. Unlike the earlier contexts, this graph has no per-record meaning sentences; the normative definitions remain a separately pinned snapshot. No relation-role signature validation or full semantic normalization is claimed.

[Verification](verification.json) checks deterministic import, endpoint closure, unique concepts, required relationship names, authority boundary, stored snapshot readback, source proof states and unchanged capability storage. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0039-three-layer-recovery-context-import/verify.py` from the Lab root.

## Open questions and next unit

All nine source proof requirements retain their not_evaluable posture. No backup, database, container, archive or restoration action was executed. Independent failure domains and successful recovery are not established by graph checks.

Next: the base No-Price Solana Co-ownership context — signing-key bindings, program state, owner memberships, encrypted-envelope commitments, atomic grants and replay prevention. It supplies the underlying relationships used by the imported Solana sharing capability.

Collectible-card implementation remains deferred.
