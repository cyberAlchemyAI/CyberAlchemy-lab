# Encrypted Durable Devnet Co-ownership context imported

Exact encrypted artifact and recipient envelope -> verified storage readiness -> finalized grant -> recipient retrieval/decryption -> policy-scoped key reissue.

The isolated bundle preserves 49 concepts, 54 relationships, 26 rules and 13 proof requirements. Every endpoint resolves locally. Definition bindings resolve to source concepts/rules, and three definition snapshots match their source registry hashes.

The source explicitly composes the base Solana and SQL three-layer recovery ontologies. Both references now bind to the exact previously imported context bundles. Their identities and source snapshots remain separate; no same-name node merger is implied.

[Context](context.json). [Ontology](ontology.json). [Bundle and composition bindings](bundle.json). Store: `.local/ontology-context-import-0041/`.

Lab Context and Ontology headers validate against migration-scoped contracts. The source has concept meanings and named relationships but no per-relationship meanings or generic role signatures. Import checks therefore establish structural closure, not full semantic equivalence or operational correctness.

[Verification](verification.json) covers replay, invalid endpoints/identities/relationship names, authority escalation, exact composed-context bindings, snapshot/pointer readback and preserved proof states. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0041-encrypted-devnet-context-import/verify.py` from the Lab root.

## Open questions and next unit

Source proof states remain not_evaluable. No cryptography, storage, transaction, decryption, recovery or deployment execution occurred.

Next: Hosted Devnet Knowledge Exchange context — relates the originator and recipient to the hosted coordinator, client-held cryptography, prepared/finalized access, SQL persistence and reissue. Its business/system branch distinctions need preserving.

Card implementation remains deferred.
