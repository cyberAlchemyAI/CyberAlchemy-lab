# Hosted Devnet Knowledge Exchange bridge imported

Participant intent -> hosted coordination -> client-held cryptography and finalized access -> recipient retrieval and reissue.

The isolated bundle preserves six business nodes, six system nodes, 14 relationships and ten rules. Eight relationships cross business/system branches. Endpoint and branch checks ensure those distinctions survive import. Five implementation files cited by the source relationships are preserved as exact snapshots; their presence is not runtime conformance evidence.

[Context](context.json). [Ontology](ontology.json). [Bundle](bundle.json). Store: `.local/ontology-context-import-0042/`.

Three definition files match their source-registry digests. The profile declares no separate proof-requirement registry. Relationship evidence references and node definition references remain source metadata; no generic role-signature vocabulary, definition adoption or operational validation is inferred.

Lab Context and Ontology headers validate against migration-scoped contracts. [Verification](verification.json) checks replay, endpoints, duplicate identities, branch separation, evidence presence, authority limits and stored-byte readback. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0042-hosted-exchange-context-import/verify.py` from the Lab root.

## Open questions and next unit

The source deployment posture remains not_authorized. No hosted service, wallet, encryption, transaction, database or deployment action was executed. Profile references to other validators or historical receipts are not a claim that the snapshot is a standalone executable package.

Next: Trusted Dataset Materialization's context — source windows, transformed datasets, validation/quarantine, accepted history, publication checkpoints and recovery. Its standalone Product assignment is already recorded in the imported capability.

Collectible-card implementation remains deferred.
