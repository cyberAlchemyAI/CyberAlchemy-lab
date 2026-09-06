# Governed Ontology Node Definition Selection

Decision: `CAL-GONDEF-0006`

Selected option: `GONDEF-1`

Status: `selected`

Decision source: explicit user selection

Decision time: `2026-09-01T15:48:42Z`

## Decision

Select `DEFINE-PACK-CAL-GOVERNED-ONTOLOGY-NODE-002` at SHA-256
`9128208f453869ccb96c381d09a8df0cdd3274a5c039751a9519ac0746af825d`
as the governed-node definition baseline for `CAL-PLAN-0002/W1`.

The selection covers the pack's 23 handled definitions, 25 typed
relationships, definition-level schema semantics, term normalizations,
negative-witness obligations, and retained open questions.

The selected pack remains unchanged. Its internal candidate posture records the
state of those exact bytes before this owner decision; this decision supplies
the external selection binding rather than rewriting the selected object.

## Why

The selected model provides one dependency-closed meaning baseline before
executable schema work. It preserves these invariants:

- canonical subject events calculate node and relation semantic state;
- governance events join only to an exact semantic event ID, digest, and cursor;
- semantic state and governance state remain separate;
- relations remain first-class subjects with endpoint integrity;
- evidence confidence, commitment confidence, and evidence strength remain
  distinct;
- typed residue and challenge contracts remain siblings rather than substitutes;
- contexts calculate bounded projections without owning alternate ontology
  truth.

## Exact bindings

| Artifact | SHA-256 |
| --- | --- |
| `definition-pack.json` | `9128208f453869ccb96c381d09a8df0cdd3274a5c039751a9519ac0746af825d` |
| `handled-definitions.json` | `c740dc445effa1188f29883abddfcd79a6087de98f60e086738279f243b614aa` |
| `schema-semantics.json` | `50dd47269e75c09f391272c368e3e2fceb7aa12a3aebf65b3106f3f5fea2d052` |
| `definition-drift-audit.json` | `30882f4006e049b8feae3eea757541d8486de410dd4eb48c04625a71562f2d91` |
| `receipts/validation.json` | `1e9697a94ff6ec8762aaf86c7f2812ac1d801112bb7b354c151cbbf9fa31b2fe` |

The Decision Gate request digest is
`3adfae079a83de68fc2ac6b63c0de58527f1323e5519748c68b21220889629f9`.
The canonical prefilter reproduced the stored admissibility receipt byte for
byte before this decision was recorded.

## Effect

Resolved:

- definition owner selection or admission absent.

Now eligible, under a separate authorization:

- use this exact pack epoch as the semantic input for executable schema work.

Still blocked:

- `GON-OQ-001`: select the closed `OntologyLifecycleState` vocabulary;
- author and validate executable schemas and the 12 required negative fixtures;
- pass `G-W1`.

Deferred without being erased:

- `GON-OQ-002`: evidence-profile-specific `EvidenceStrength` rubrics;
- `GON-OQ-003`: profile-local closed typed-property schemas.

## Authority ceiling

This decision selects only the exact local definition baseline. It does not
modify the selected pack, pass `G-W1`, authorize implementation, admit a
DomainSpec profile or compiled graph, prove conformance, or authorize
publication, release, deployment, migration, or external effects.
