# Durable Storage business context imported

Encrypted object -> exact storage binding -> retrieval -> verified byte identity or typed failure.

The isolated context contains 25 concepts, 23 relationships, 13 rules and nine proof requirements. All relationship endpoints resolve locally. Definition-to-concept/rule references resolve, and the pinned definition source matches its source registry digest. Twelve source files are preserved byte-for-byte.

[Context](context.json). [Ontology](ontology.json). [Bundle](bundle.json). Store: `.local/ontology-context-import-0038/`.

Lab Context and Ontology headers validate against the scoped migration contracts. The original graph is assembled from separately preserved source registries. No generic relation-role signature vocabulary is declared by the source; checks cover identity, endpoints and explicit meanings rather than claiming signature validation.

[Verification](verification.json) covers replay, missing endpoints, duplicate concepts, missing meanings, authority escalation, stored snapshot readback and preserved proof states. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0038-durable-storage-context-import/verify.py` from the Lab root.

## Open questions and next unit

Source proof requirements remain not_evaluable. No storage adapter, write, retrieval, recovery or deployment was executed. Capability inventory is unchanged.

Next: Three-Layer Protection and Recovery's context — operational database, append-only recovery journal and independent immutable archive, followed by destination retrieval and restoration verification. This specializes generic storage into an explicit recovery model.

Card implementation remains deferred.
