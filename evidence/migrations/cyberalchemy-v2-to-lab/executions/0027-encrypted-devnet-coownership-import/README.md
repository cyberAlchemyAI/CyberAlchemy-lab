# Encrypted Durable Devnet Co-ownership imported as a candidate

Verified encrypted material and recipient envelope -> authorized grant -> matching finalized activation -> recipient retrieval and decryption.

The candidate obligation registry contains all 26 exact source rules. Ten explicit semantic mappings bind the capability's missing realization, consumer, input/output and policy reference IDs to existing source concepts and rules. [Exact mappings](plan.json). [Result](result.json).

The rules preserve the original owner, require durable storage before submission, distinguish prepared material from active access, and require policy-authorized reissue without changing artifact identity or ownership. The mappings provide candidate semantic descriptions, not executable API schemas or runtime proof.

**36 imported / 5 blocked / 3 reference examples / 1 excluded.** [Inventory](inventory.json). Store: `.local/capability-inventory-import-0027/imports.json`.

[Verification](verification.json) covers source replay, missing/duplicate/empty rules, exact queue transition, preserved prior records and graph validity. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0027-encrypted-devnet-coownership-import/verify.py` from the Lab root.

No transaction, deployment, encryption, decryption or recovery action was executed. Runtime evidence remains source metadata, not newly verified evidence.

## Open questions

Next unreviewed capability: CA2-CAP-GRANT-ENCRYPTED-KNOWLEDGE-COOWNERSHIP. Its existing gap is an ambiguous Knowledge Originator reference. Definition NFT remains reviewed and blocked; the three AlchLang examples retain their corrected classification.
