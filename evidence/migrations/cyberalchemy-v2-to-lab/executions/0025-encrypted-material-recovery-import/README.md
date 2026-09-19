# Protect and Recover Encrypted Knowledge Material imported

Encrypted object -> operational SQL, recovery journal and independent archive -> destination retrieval -> exact verification.

The source already declares the obligation registry identity. Its 12 rules live in a separate ontology file. A local candidate registry now binds those exact statements without changing them. An explicit candidate consumer role fills the dangling encrypted-material consumer reference using the declared outcome and consuming-capability owner route. This role is not an implementation or a team.

The rules require independent failure domains, matching object identities, immutable journal/archive material, destination verification and bounded failure reporting. Product ownership and boundaries resolve from KEP ontology and its exact Product Thesis record.

[Result](result.json). [Obligation registry](obligation-registry.json). [Consumer projection](consumer.json). **34 imported / 7 blocked / 3 reference examples / 1 excluded.** [Inventory](inventory.json). Current store: `.local/capability-inventory-import-0025/imports.json`.

[Verification](verification.json) covers replay, invalid/missing rules, queue preservation and graph validity. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0025-encrypted-material-recovery-import/verify.py` from the Lab root.

This imports a capability description; it does not establish working backup or restoration. No database, Docker or recovery execution was performed.

## Open questions

Production topology and recovery time/data-loss objectives remain outside this candidate import. Next unreviewed capability: CA2-CAP-HOST-DEVNET-KNOWLEDGE-EXCHANGE.
