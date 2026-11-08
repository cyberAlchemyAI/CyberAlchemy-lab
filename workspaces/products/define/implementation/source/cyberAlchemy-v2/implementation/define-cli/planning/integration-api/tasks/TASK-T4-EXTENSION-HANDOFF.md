# TASK T4 — Extension And Plan Handoff Proof

Layer: L4. Status: testable candidate complete. Authority effect: none.

## Objective

Add a third ontology through configuration and adapter files only, expose more
than one valid entry point, and prove one Plan consumer can read the handoff
without treating it as approval or implementation authority.

## Inputs And Outputs

Inputs are L3 protocols, one selected third ontology, and one selected Plan
consumer schema. Outputs are the adapter/configuration delta, entry-point
fixtures, a no-Define-core-edit witness, and Plan consumer contract evidence.

## Smallest Working Units

1. `SWU-T4-01`: register and exercise the third adapter without core edits.
2. `SWU-T4-02`: validate one exact exported receipt at the Plan boundary.

## Ordered Rules

Add ontology-owned Alch and adapter bytes; add one exact registry record; select
an entry point explicitly; compute only its dependency closure; export through
the Client API; let Plan validate protocol and digests while preserving
candidate state.

## Edge Cases And Failure Modes

Unknown entry point, two valid entry points, unrelated branch unavailable,
consumer schema mismatch, stale receipt, admission/effect fields introduced by
the consumer, and accidental edits to Define core.

## Verification And Completion

A path/diff allowlist proves no Define-core source changed; both entry points
are deterministic; Plan accepts valid candidate evidence and rejects drift or
authority escalation; the complete L0–L4 suite passes.

## Selected Identities

- Third ontology: `define/system-ontology`, bound through exact byte digests for
  `PROFILE.json`, `NODES.json`, and `RELATIONS.json`.
- Plan consumer schema: `cav2.plan-ontology-handoff-input/v1` from
  `schemas/integration/plan-ontology-handoff.schema.json`.
- System stage: `define-system-ontology`, requiring the exact
  `alch-business-ontology` handoff.
- System Alch entry points: `SystemOntologyQuestion` and
  `SystemOntologyReadiness`.

## Implementation Evidence

- The System adapter was added through `configuration/ontology-authoring.mjs`;
  no existing file under `src/`, `packages/client-api/`, or
  `packages/ontology-stage-port/` changed in L4.
- Definition Pack, Product, Business, and System are explicit selectable stages;
  omitting System makes only that stage unavailable and leaves Product candidate
  bytes unchanged.
- The exact Definition → Product → Business → System chain exports
  deterministic candidate bytes and handoff receipts.
- Plan accepts the confirmed System export only as `candidate-evidence-only`,
  with `planning_effect: none` and `implementation_authority: not-granted`.
- Plan rejects incompatible schemas, stale graph bindings, non-canonical or
  changed candidate bytes, broken receipt integrity, and authority escalation.
- Focused L4 tests passed twice at 3/3; the complete Define surface passed
  69/69; the 61-file System Alch bundle rebuilt byte-identically.
- The selected System source validator reported 55 PASS checks and one
  `NOT_EVALUABLE` DomainSpec compiler-conformance check, so its preserved source
  posture is `FLAG`, not PASS.

This is local product-construction evidence. It does not implement or admit the
source System Ontology, register a canonical Plan schema, or grant authority.

Open questions and blockers are owned by [the work pack](../WORK-PACK.md#blockers).
