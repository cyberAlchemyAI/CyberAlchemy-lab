# Decision 0073 candidate review

Review these records in order:

1. `instances/artifacts/project-state.json` and the two Project histories.
2. `instances/artifacts/context-request.json` and `context-view.json`.
3. `classification-scheme.json`, `classification-value.json`, and `classification-assignment.json`.
4. `principal.json`, `agent-profile.json`, `agent-capability.json`, and `implementation.json`.
5. `work.json`, `agent-assignment.json`, `agent-instance.json`, and `agent-session.json`.
6. `ontology.json`, `ontology-cut.json`, and `ontology-view.json`.
7. The Typed Relations and validation receipt.

The ontology projection is intentionally minimal: it contains only the exact Decision 0072 Project State, its Project, and the candidate global `member-of` relation. It introduces no local interpretation and binds every projected subject and edge by digest.
