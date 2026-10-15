# Event-Sourced Ontology Lifecycle Witness

Status: **candidate implementation; automated verification passes; human verification pending**

This package is the first Lab-native witness for reconstructing an ontology from
canonical semantic events. Events calculate state. Generated graphs, snapshots,
indexes, JSON views, and Markdown views remain discardable projections.

## Runtime model

1. Each ontology node or relation is an `OntologySubject`.
2. Its canonical stream identity is derived as `node:<subject-id>` or
   `relation:<subject-id>`.
3. Each `SemanticEvent` carries the subject's complete resulting state.
4. The first single-writer witness allocates contiguous graph cursors beginning
   at 1 and maintains an exact digest chain per subject.
5. `ontology_at(cursor)` selects the latest event for every subject through that
   cursor and validates all active relation endpoints in the same cut.
6. Governance events remain in a separate stream and join semantic events only
   by exact event ID, raw canonical-file digest, and cursor.
7. Snapshots and machine/human views are calculated outputs and never canonical
   replay inputs.

The candidate lifecycle vocabulary is `active | retired`. Retired subjects keep
their identity and event history; they cannot satisfy an active relation
endpoint. Both this choice and contiguous cursor allocation remain pending the
final human verification in `candidate-selections.json`.

## DomainSpec event-sourcing contract

`domainspec/event-sourcing/source.json` now expresses the selected runtime
mechanics through the reusable DomainSpec event-sourcing compiler rather than
through names alone. The compiled contract fixes:

- one semantic stream per node or relation subject identity;
- a separate governance process stream for challenge-contract state;
- complete-resulting-state events bound to closed payload schemas;
- one graph-wide commit-position cut for projections;
- an exact identity, digest, and commit-position join from challenge governance
  to semantic node or relation state;
- rebuildable ontology, governed-node, and latest-snapshot projections.

`domainspec/event-sourcing/generated/contract.json` is the canonical compiled
projection. `compile-receipt.json` binds its exact source, payload schemas,
compiler sources, selected event-topology decision, business ontology, and the
unselected governed-node successor proposal. The verifier compiles and checks
the projection twice and rejects source, schema, compiler, or output drift.

The thin node and relation schemas match the current Rust witness. The
challenge-contract schema is a candidate input from unselected `CAL-PROP-0004`
and is not yet implemented by the Rust reducer. Compiler PASS therefore proves
the candidate contract is deterministic and topologically closed; it does not
prove challenge runtime conformance or select that successor architecture.

## Governed ontology node architecture

The thin `Node` and `Relation` payloads in this witness prove event mechanics;
they are not the stable cross-ontology record model. The successor architecture
candidate is
[`CAL-PROP-0004`](../docs/proposals/0004-governed-ontology-node-architecture/proposal.json).
It proposes a calculated `GovernedOntologyNodeView` composed from:

- stable node identity and a typed semantic state;
- ontology-profile-specific semantic fields;
- exact provenance and owner routing;
- separate evidence and commitment confidence axes;
- the complete challenge contract for a load-bearing candidate;
- lifecycle, authority posture, residue, conflicts, drift, and invalidation;
- exact semantic and governance event references used to calculate the view.

Semantic node and relation histories remain canonical in their subject streams.
Governance facets remain canonical in separate governance streams and bind exact
semantic event identity, digest, and cursor. A challenge cannot edit semantic
history: an owner-approved meaning change appends a new semantic event, while
the challenge and decision remain governance events. `contradicts` and
`validates` remain first-class relation subjects; a challenge contract only
references their identities or selectors.

The proposed facet-rich schema, DomainSpec model, generated system ontology,
Rust payloads, migration mappings, and conformance tests are successor work.
The current automated PASS therefore remains limited to the thin witness and
does not establish conformance to `CAL-PROP-0004`.

## Context-artifact interaction

Contexts do not own alternate ontology truth. A context selects an exact
semantic event cut and produces a bounded projection for its consumer. Context
meaning, governance authority, and semantic event state remain separate:

```text
canonical semantic events ──ontology_at(cursor)──> consistent ontology cut
                                                        │
                                  exact context selector │
                                                        ▼
                                              context projection

separate governance events ──exact ID + digest + cursor──┘
```

This permits different contexts to calculate different bounded views without
forking the canonical event history or promoting a view into authority.

## D65 chain

| Stage | Candidate artifact |
| --- | --- |
| Definitions | `../docs/definition-packs/0001-ontology-lifecycle-semantic-predecessors/` |
| Product Capability | `product-capability.json` |
| Business ontology | `business-ontology.json` |
| DomainSpec source | `domainspec/project.json` and its 15 node files |
| Compiled graph | `domainspec/.domainspec/generated/graph.json` |
| Event-sourcing contract source | `domainspec/event-sourcing/source.json` and its payload schemas |
| Compiled event-sourcing contract | `domainspec/event-sourcing/generated/contract.json` |
| System ontology | `system-ontology/` |
| Implementation binding | `conformance/construction-binding.json` |
| Conformance evidence | `conformance/verification.json` and 12 Rust tests |

`conformance/d65-status.json` is the current non-authoritative stage projection;
the earlier planning readiness file remains preserved as historical planning
evidence rather than being rewritten after execution.

The DomainSpec profile and its 16 reducer relationships are Lab-owned
development candidates. They intentionally do not modify or claim admission of
the concurrently edited canonical DomainSpec relationship registry.

## Final verification

From this directory, run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify.py --node /tmp/cal-node-v26.8.1/bin/node
```

The verifier performs two byte-current DomainSpec graph checks, validates the
exact construction-binding digests and node-to-symbol coverage, and runs all
Rust tests with the locked dependency set. Run
`scripts/compile-event-sourcing-contract.ts --check` twice from the DomainSpec
runtime workspace for the separate event-sourcing compiler receipt; keeping
that check separate preserves the existing construction-binding evidence epoch.

To inspect the calculated witness state directly:

```bash
cargo run --manifest-path runtime/Cargo.toml --quiet --bin ontology-at-cursor -- \
  runtime/fixtures/semantic-events runtime/fixtures/governance-events 4
```

## Claim ceiling

The current evidence proves a focused candidate witness is deterministic and
fail-closed for the exercised obligations. It does not admit the candidate
definitions, Product Capability, business ontology, DomainSpec profile, or
system ontology. It does not prove production durability, concurrency,
compaction, legacy migration, publication, release, or deployment.
