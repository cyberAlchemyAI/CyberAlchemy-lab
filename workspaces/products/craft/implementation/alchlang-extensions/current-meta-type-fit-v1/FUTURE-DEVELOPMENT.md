# Deferred: missing-meaning Meta-Type Factory

Recorded 2026-09-05 at the user's request. Status: future development, not part of the current pricing implementation.

When an authored concept cannot resolve to an existing suitable meta-type, investigate in this order:

1. Reuse an existing meaning and profile where they fit.
2. If the meaning fits but execution is missing, extend its typed contract, Alch lowering or target generator. Do not create a synonymous meta-type to bypass a realization gap.
3. Only for a demonstrated semantic gap, construct a new meta-type candidate through the factory.

The proposed factory output must include selected meaning and distinguishing criteria; profile; node and relation definitions with direction and cardinality; constraints and positive/negative examples; language AST and resolution/type rules; typed lowering; generators; and conformance tests. Record source provenance and explicit dependencies. Ambiguous meaning remains unresolved rather than silently selected.

Follow the construction sequence: prototype definitions, agent-facing ontology scaffolds, product/business/DomainSpec/compiled-system/implementation prototypes, one exact testable candidate, current tests, then product approval. Registration, admission, activation, release and deployment remain separate owner decisions. A normal compilation must never silently create or admit registry entries.

The previously inspected `projects/domainspec-v2/development/meta-type-factory-reproducibility/PROTOTYPE-VALIDATION-REPORT.md` concerns reproducibility for existing mapped types. It is not evidence that this proposed missing-meaning construction flow already exists.

Reopen only after the existing-type pricing prototype identifies a concrete requirement that cannot faithfully use an existing meaning. No such gap was established in this assessment. The unresolved term “TAP” is not treated as a registered type or protocol.
