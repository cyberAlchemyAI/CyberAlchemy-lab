# Recent Context candidate import

Recent committed changes -> bounded metadata -> freshness check -> context for the task.

Six concepts and six definitions cover commits, changed files, project scope, recent views, freshness and explicit cache refresh. Five source relationships connect them. The source scaffold has no relation IDs or endpoint-kind signatures; the normalized header uses exact positional source references, without inventing semantic identity or signatures.

This import restores the pinned repaired package from 0051 and reuses its unchanged build evidence and 22 Git fixture tests. The source model validator passes against that repaired compiler snapshot. Context and Ontology headers use the existing admitted migration-scoped contracts; the records remain candidate-unadmitted.

The query remains read-only. Cache refresh requires an explicit request. Hooks remain uninstalled, and durable task-state recovery remains a future capability: recent change metadata does not recover goals, decisions or unfinished work. No query, refresh or hook operation is executed by this import.

The store is `.local/ontology-context-import-0052/`. Its package is restored from 0051's archive, which remains pinned in the bundle. `verify.py` checks malformed concepts, definitions and relationships; registration and query-boundary violations; restored pointers; and unchanged capability storage. The source's task-state ownership question remains explicit.
