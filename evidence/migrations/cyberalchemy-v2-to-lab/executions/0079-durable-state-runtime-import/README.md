# Durable Capability State — obsolete dependency removed

Reworked Define -> remove old Invoke Define requirement -> validate twelve Product Capability requirements -> import through the existing Lab runtime.

The user clarified: “we dont need this, define is already reworked without it”. This execution applies that scope decision to a separate successor of 0078. It removes DS-REQ-EXTERNAL-INVOKE-DEFINE, updates the coverage schema and validator, and replaces its old assignment test with a test rejecting reintroduction. Define Shared Meaning keeps its own storage requirement. No private Define CLI substitution is made.

The business model remains 25 nodes, 22 relationships, seven storage classes and twelve Product Capability requirements. The four explicit source fingerprint successors from 0078 remain. Original source files and prior executions are preserved. Two old receipts retain their exact bytes in `historical/durable-storage-receipts`, outside the candidate's active receipt directory, because their original counts do not describe this successor. Source evidence can still mention historical external capabilities; it is not an active requirement.

The revised native validator passes; all twelve source tests pass (one baseline and eleven rejection cases). `verify.py` checks source/archive integrity, exact scope removal, unchanged graph, the tested 0074 runtime binary, exact exports, deterministic fresh import, and rejection of overwrite, unknown package and transaction corruption.

The runtime store is `.local/durable-state-runtime-0079`. Its manifest is local to this execution. This imports the storage requirements model, not a storage provider or proof that capability data survives crashes. Implementation binding, system ontology, compiled graph and conformance remain not evaluable. The shared runtime's combined manifest and validator integration remain next work.

Reproduce validation/import verification from the repository root with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0079-durable-state-runtime-import/verify.py`. `prepare.py` stages the successor from the preserved 0078 snapshot; existing committed evidence should be verified rather than regenerated.
