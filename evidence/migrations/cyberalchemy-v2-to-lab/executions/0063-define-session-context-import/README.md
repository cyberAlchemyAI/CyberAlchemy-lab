# Define session system model

Session -> preserve questions, answers and evidence -> track revisions -> export a Definition Pack.

Imported a candidate session model with 65 concepts, 131 source-owned relationships, six navigation views and five residue items. The source DomainSpec nodes remain authoritative for this local model; NODES.json and RELATIONS.json are exact checked indexes, not an independently authored graph. The existing capability and owner remain unchanged.

All 23 evidence versions were recovered exactly. Three missing files came from historical Git blobs: the semantic-evaluator README, meta-type implementation baseline and supported profile registry. The ontology type catalog came from its local mirror. One older Definition Pack document came from the sibling orchestrator. Recovery paths and original hashes are recorded in source-recovery.json. No source models, bindings or receipts were edited.

The unchanged source validator reports 55 PASS, zero BLOCK and one NOT_EVALUABLE check, producing overall FLAG and exit code 2. Its remaining limit is complete-backend-criteria@2 compiler conformance; the runtime remains explicitly not implemented. The source's deterministic Design subpackage checks pass. This import does not compile or execute a session runtime. Thirteen import checks verify identities, typed relation vocabulary, source index equivalence, exact inputs, receipt output and candidate limits. The original receipt remains current against the restored snapshot.

Because 131 relationships exceed the admitted ontology header's 100-item limit, this context uses the exact larger **unadmitted candidate schema from execution 0048**. The admitted schema and registry are unchanged; schema admission remains outstanding. Context headers use the existing admitted context contract.

Store: `.local/ontology-context-import-0063/`. Verify with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0063-define-session-context-import/verify.py`. The snapshot contains a plain `.git` marker solely for the validator's root discovery; it is not a Git repository and no Git operation is invoked against it. `recover.py` and `prepare.py` record preparation; normal import restores the frozen archive.

## Open questions

Compiler conformance, implementation, measured behavior, operational activation and the five source residue items remain unresolved. Historical evidence is pinned without claiming it represents current global authority. Ontology-schema admission and prior D65 full-conformance work remain separate.

Next: Define business/system bridge — check how the business promises map to session operations and what evidence is still missing between them.
