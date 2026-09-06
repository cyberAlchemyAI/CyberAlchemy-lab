# Event-sourced ontology first vertical

Status: `decision-gate-complete`  
Gate result: `PASS`  
Authority effect: `none`  
Route: `CA2-ROUTE-GOVERNANCE`  
Date opened: `2026-09-01`  
Date closed: `2026-09-01`

## Target

Resolve the design decisions required to create the first event-sourced ontology vertical in CyberAlchemy Lab without inferring a Product or Governance bounded context, changing canonical ontology bytes, or granting implementation, admission, acceptance, publication, release, or deployment authority.

## Bound evidence

- Architecture proposal: `docs/proposals/0001-context-artifact-architecture/proposal.json`
- Proposal SHA-256: `7ee7288a8e376c2634230be0e123fdb65c858369495a7f21283c77f7124e31b2`
- Repository placement: CyberAlchemy Lab is the active Craft target; DomainSpec-core remains external legacy evidence under Decision 0002.

## Resolved premise

`RESOLVED-CANONICALITY`: the append-only ontology events are canonical. Current ontology state, machine artifacts, human views, indexes, and validation summaries are deterministic projections calculated from those events. This premise does not select event vocabulary, stream boundaries, storage, runtime, governance topology, or migration policy.

## Recorded selections

- `CAL-ESOV-D01-FIRST-BOUNDED-CONTEXT` → `CTX-1`: the first vertical belongs to the `Ontology Lifecycle` bounded context. This selects context ownership only. Its ubiquitous language, scope, exclusions, context maps, event vocabulary, implementation, admission, and enforcement remain unresolved or separately governed.
- `CAL-ESOV-D02-FIRST-ONTOLOGY-WITNESS` → `WIT-1`: prove the vertical with one small Lab-native ontology witness. This selects the witness strategy only; it does not create, define, admit, or accept an ontology artifact.
- `CAL-ESOV-D03-STREAM-GRANULARITY` → `STR-2`: each ontology node and relation has its own canonical event stream. Each subject's latest state is a calculated, disposable projection; the ontology is calculated by joining subject projections at a separately selected consistent cut.
- `CAL-ESOV-D03A-GRAPH-ASSEMBLY-CONSISTENCY` → `ASM-1`: every completed append receives a graph-wide monotonic commit cursor. `ontology_at(cursor)` calculates each subject through that cursor and then joins the subject projections. The cursor is ordering metadata, not a global semantic stream.
- `CAL-ESOV-D04-EVENT-PAYLOAD-MODEL` → `PAY-1`: use typed semantic events carrying the complete resulting state of the affected node or relation. Each event also carries stable subject identity, event type, schema version, subject-stream revision, and graph commit cursor. External evidence can remain an exact immutable digest reference.
- `CAL-ESOV-D05-RUNTIME-STORAGE` → `RUN-1`: use a Rust reducer over canonical JSON event files. This selects the runtime language and storage form, not the file layout, append-lock protocol, implementation, conformance, admission, or enforcement status.
- `CAL-ESOV-D06-CALCULATED-PROJECTION-POLICY` → `PRJ-1`: check in deterministic machine and human projections. Every projection must declare its graph commit cursor and canonical event-set digest and remain visibly calculated, disposable, and non-authoritative.
- `CAL-ESOV-D07-GOVERNANCE-EVENT-TOPOLOGY` → `GOV-2`: semantic node/relation streams and governance streams remain separate. Governance events bind exact semantic event identities, digests, and cursors; accepted state is a deterministic join and never a mutation of semantic history.
- `CAL-ESOV-D08-MIGRATION-CUTOVER` → `MIG-1`: prove the small Lab-native witness before any legacy ontology migration. Existing ontologies remain external evidence until separately selected, exactly bound, owner-reviewed, and admitted.

## Decision register

| Order | Decision ID | Admissible choices | State |
|---:|---|---|---|
| 1 | `CAL-ESOV-D01-FIRST-BOUNDED-CONTEXT` | `CTX-1`, `CTX-D`, `CTX-S` | selected: `CTX-1` |
| 2 | `CAL-ESOV-D02-FIRST-ONTOLOGY-WITNESS` | `WIT-1`, `WIT-2`, `WIT-D`, `WIT-S` | selected: `WIT-1` |
| 3 | `CAL-ESOV-D03-STREAM-GRANULARITY` | `STR-1`, `STR-2`, `STR-D`, `STR-S` | selected: `STR-2` |
| 3a | `CAL-ESOV-D03A-GRAPH-ASSEMBLY-CONSISTENCY` | `ASM-1`, `ASM-2`, `ASM-D`, `ASM-S` | selected: `ASM-1` |
| 4 | `CAL-ESOV-D04-EVENT-PAYLOAD-MODEL` | `PAY-1`, `PAY-2`, `PAY-D`, `PAY-S` | selected: `PAY-1` |
| 5 | `CAL-ESOV-D05-RUNTIME-STORAGE` | `RUN-1`, `RUN-2`, `RUN-3`, `RUN-D`, `RUN-S` | selected: `RUN-1` |
| 6 | `CAL-ESOV-D06-CALCULATED-PROJECTION-POLICY` | `PRJ-1`, `PRJ-2`, `PRJ-D`, `PRJ-S` | selected: `PRJ-1` |
| 7 | `CAL-ESOV-D07-GOVERNANCE-EVENT-TOPOLOGY` | `GOV-1`, `GOV-2`, `GOV-D`, `GOV-S` | selected: `GOV-2` |
| 8 | `CAL-ESOV-D08-MIGRATION-CUTOVER` | `MIG-1`, `MIG-D`, `MIG-S` | selected: `MIG-1` |

## Structurally rejected choices

- `CTX-2` and `CTX-3`: Product and Governance bounded-context identities remain owner-unselected.
- `WIT-3`: the architecture proposal is not an ontology witness.
- `STR-3`: one repository-global stream collapses semantic and authority boundaries.
- `ASM-3`: independently joining whichever subject snapshots are currently latest is timing-dependent and can create a fractured ontology.
- `PAY-3`: generic JSON Patch records document edits rather than closed semantic intent.
- `RUN-4`: the suspended Python ontology runtime cannot become the authoritative kernel.
- `PRJ-3`: on-demand-only projection removes the required checked-in human continuation surface.
- `GOV-3`: mutating historical events destroys canonical history and can manufacture lifecycle state.
- `MIG-2`: a legacy-first witness conflicts with the selected Lab-native witness and would reopen Decision D02.
- `MIG-3`: bulk migration lacks source admission, dependency closure, owner gates, and a proven first vertical.

## Receipts

Each blocker has a schema-validated request and prefilter receipt under `admissibility/`. Every receipt routes to `gate`; no option was selected directly by the prefilter. Human selections are recorded separately under `selections/`. The complete machine decision is `decision.json`, and its digest-bound closure evidence is `decision-gate.receipt.json`.

## Outcome and claim ceiling

All decision-gate blockers are resolved without defer or stop. `PASS` means the design-selection set is coherent and complete for this gate.

It does not create the witness, change the architecture proposal, admit an ontology, implement the Rust reducer, activate governance, import legacy sources, publish artifacts, or authorize deployment. Construction must still cross the D65 chain from canonical definitions through Product Capability, capability-local business ontology, DomainSpec v2 source, compiled graph, implementation binding, and conformance evidence.
