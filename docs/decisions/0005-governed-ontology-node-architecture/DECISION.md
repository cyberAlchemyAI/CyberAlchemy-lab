<!-- Human projection of decision.json. The canonical decision is decision.json. -->

# Governed ontology node architecture selection

- Decision: `CAL-GONA-0005`
- Status: `owner-selected`
- Decision posture: `selected`
- Selected option: `GONA-1`
- Selected at: `2026-09-01T14:36:41Z`
- Authority effect: `architecture-planning-selection-only`

## Decision

Select `CAL-PROP-0004`, “Governed event-sourced ontology node architecture,” at exact SHA-256 digest `a2257b185c1c4cbcbb92992e10fa202172e79c4603734edb24cff5bcc5d00b6c`.

The selected planning baseline is:

- a shared governed-node envelope;
- separately event-sourced semantic and governance facets;
- closed ontology-type-specific profiles;
- relations as first-class event-sourced subjects;
- per-subject latest state calculated from canonical events;
- exact semantic event ID, digest, and cursor joins for governance;
- context views calculated from one consistent semantic cut and its valid governance join; and
- snapshots, indexes, and projections excluded as replay sources.

## Rationale

This option preserves the already selected event topology while adding the stable node, relation, challenge-contract, evidence, authority, residue, and context-projection boundaries needed by the ontology model. It allows the next definition and schema stage to work against one immutable architecture digest instead of divergent informal node shapes.

## Decision Gate result

- Result: `PASS`
- Blocker decisions resolved: `1`
- Blocker decisions remaining: `0`
- Admissibility route: `gate`
- Admissibility request digest: `94661e5e5f3f180dcedfd43e69aff94d7a89ac1fc430a7740749a3cf61a2e08c`
- Admissibility request file SHA-256: `72457ba4b623f020e92b261bb7034429521e5fceb553b6324eb54ab44613f42b`
- Admissibility receipt file SHA-256: `0084ae25202d546fd4af4eeabcaf01e339551370134cc487537f80744840daef`

## W0 effect

`CAL-PLAN-0002/G-W0` is resolved for the exact selected proposal digest. The next bounded route is `CA2-ROUTE-DEFINE` for W1 candidate definitions and schema semantics.

## Remaining blockers

- The shared facet-rich node, relation, challenge-contract, and context-selector definitions and schemas are not authored or admitted.
- Invoke Plan v2 remains not evaluable until exact admitted Design source and admission receipts exist.
- The current DomainSpec development profile is not admitted.
- The Rust witness still proves only the thinner event-sourcing mechanics slice.
- Existing ontology packages have not been inventoried or migrated under this selected model.

## Non-effects

- The selected proposal bytes remain immutable and keep their pre-selection candidate posture as historical source evidence.
- This decision does not rewrite or supersede the selected `CAL-PROP-0001` context-artifact architecture baseline.
- This decision does not author or admit definitions, schemas, a Product Capability, a business ontology, DomainSpec source, a compiled graph, or a system ontology.
- This decision does not authorize W1 implementation, Task Session execution, ontology migration, publication, release, deployment, or external effects.
- This decision does not prove runtime conformance or complete the CyberAlchemy goal.

## Claim ceiling

Decision Gate PASS means only that one immutable governed-node architecture has been selected as the successor planning baseline. Every D65 successor remains independently owner-bound and evidence-gated.
