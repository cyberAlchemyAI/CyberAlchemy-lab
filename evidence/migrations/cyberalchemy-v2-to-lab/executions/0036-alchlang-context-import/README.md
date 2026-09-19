# Migration resumed: first capability-linked context bundle

Imported AlchLang capability -> 20 source concepts -> 16 typed relationships -> isolated context and ontology candidates.

The capability-description queue is complete. This starts the next bounded migration stage: preserving source business graphs as recoverable, capability-linked context bundles. It does not claim completion of context evolution or runtime recovery.

[Context](context.json). [Ontology](ontology.json). [Complete bundle](bundle.json). Eight source JSON files are preserved byte-for-byte in `source/`. Their exact origin hashes, source relation signatures, concept owners and existing candidate/blocked postures are retained. All 16 relationship endpoints and their eight source type signatures validate.

The Context and Ontology headers validate against the migration-scoped Lab artifact contracts. Their concepts remain source-shaped; no automatic merging or global semantic admission occurs. The profile reference points to the preserved source profile. References from that profile to validators and external evidence remain source metadata rather than a claim that the snapshot is a standalone executable package.

Store: `.local/ontology-context-import-0036/bundle.json`, with companion source snapshots. [Verification](verification.json) covers replay, invalid endpoints/types/authority, schema validity and stored-byte readback. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0036-alchlang-context-import/verify.py` from the Lab root.

## Remaining boundaries

Both the construction handoff output and DomainSpec handoff boundary remain blocked as declared in the source. This import grants no compiler execution or handoff authority. Source runtime tests were not rerun.

The earlier source-runtime corpus import is a separate historical/raw import. This execution adds an explicit capability-linked, source-qualified business context; it does not repeat or replace that corpus.

Collectible-card implementation is deferred at the user's request. Its imported candidate description remains in the capability inventory.

## Next migration unit

The core KEP business context: artifact versions, participant identities, sharing permissions, recipient envelopes and acknowledgements. It supplies the relationships behind the already imported encrypted co-ownership capability. Cross-context semantic normalization and runtime migration remain later stages.
