# Core KEP business context imported

Exact artifact version -> authorized sharing -> recipient envelope -> acknowledgement, with original ownership and immutable policy preserved.

The isolated bundle contains 29 source concepts, 17 relationships, 11 rules and six proof requirements. The one external endpoint, CyberAlchemy Product, resolves to an exact parent Product snapshot. Five source files are preserved byte-for-byte, including the digest-bound KEP definitions.

[Context](context.json). [Ontology](ontology.json). [Complete bundle](bundle.json). Store: `.local/ontology-context-import-0037/`.

The Lab context and ontology headers validate against the scoped migration contracts. Relationship checks cover unique identities, endpoint closure and explicit meanings. The source has no reusable relation-role signature vocabulary, so no signature validation is claimed. Source admission and construction states remain provenance, not Lab authority; the source's blocked/not-evaluable successor stages remain unchanged.

[Verification](verification.json) covers replay, endpoint/identity/meaning rejection, stored snapshots and pointer readback, preserved source proof state and unchanged capability storage. Run `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0037-kep-context-import/verify.py` from the Lab root.

## Open questions and next migration unit

Proof requirements are retained, not executed. Runtime, cross-context semantic normalization and operational authority remain separate.

Next: the generic Durable Storage business context — immutable encrypted objects, exact byte identities, storage bindings, verified retrieval and typed failures. This supplies the domain relationships behind Persist and Verify Encrypted Knowledge Material.

Collectible-card implementation remains deferred.
