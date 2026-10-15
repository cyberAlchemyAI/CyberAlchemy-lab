# Define Runtime Architecture Candidate

## Outcome

The smallest coherent runtime unit is one versioned command applied to one
expected session revision. The command must pass exact authority and domain
rules, commit one confirmed snapshot and outcome atomically, and then be
resumable through either interface at the same revision and state digest.

This is a discovery architecture, not a governed Design bundle.

## View 1 — Context

```text
participant / owner
      |                         source and owner registries
 CLI adapter ----+                         |
                 +-- shared transport --> session application
 chat adapter ---+                         |
                                           +--> session domain
                                           +--> repository port --> backend TBD
                                           +--> Arcanum port (private adapter only)
                                           +--> semantic evaluator port
                                                (bounded private witness only)
                                           +--> DomainSpec conformance (not evaluable)
```

CLI and chat are projections over one session, not separate state owners.
Arcanum and DomainSpec remain dependencies with their own public/private and
admission boundaries.

## View 2 — High-level structure

| Part | Owns | Must not own |
| --- | --- | --- |
| CLI/chat adapters | interaction projection and contract translation | session meaning or independent state |
| Session application service | command sequencing, authority check, load/apply/commit coordination | product meaning or storage internals |
| Session domain | session, question, answer, pack, lifecycle, rule and policy invariants | transport, persistence, deployment |
| Context resolution service | source precedence, candidate provenance, frozen sufficiency requests, three-valued results, and additional-context routing | private-state inference, user intent, owner authority, or a general reasoning engine |
| Pack projector/validator | exact consumer projection and structural checks | content approval or authority grants |
| Persistence adapter | repository-port realization and atomic confirmed outcome | semantic migration or silent conflict resolution |
| Telemetry adapter | privacy-safe operational evidence | prompt, answer, source, or evidence content |

## View 3 — Low-level components and contracts

`SessionCommand` carries command identity, type, session identity, expected
revision, actor access context, payload schema version, and payload.

`SessionSnapshot` carries the complete resumable state: schema version,
revision, digest, goal, intent, context, current question, histories, sources,
evidence, dispositions, owners, gaps, checks, and authority envelope.

`SessionWriteResult` distinguishes confirmed, conflict, denied, invalid,
incompatible-schema, and storage-failure outcomes. An unconfirmed result may
never advance the visible revision.

`DefinitionPackExport` binds the pack to the exact session revision, consumer,
material digest, open gaps, validation result, and authority envelope.

`ContextCandidate` keeps explicit and inferred context separate through source
kind, source reference or session revision, content digest, derivation posture,
confidence, and user disposition. `ContextSufficiencyRequest` freezes the named
Define job requirements and candidate set. `ContextSufficiencyResult` returns
`sufficient`, `insufficient`, or `indeterminate` with derivation, residue, and a
non-authorizing evaluator receipt reference.

## View 4 — Workflow process

```text
receive/decode
  -> authenticate and evaluate exact authority
  -> load last confirmed revision
  -> resolve explicit user context and references
  -> if needed, derive current-window candidates
  -> if still needed, derive saved-session candidates
  -> evaluate frozen context sufficiency
  -> if insufficient or indeterminate, invite more context and preserve the gap
  -> compare expected revision
  -> if sufficient, apply domain rule or policy
  -> atomically commit snapshot + outcome event
  -> project session or pack
  -> return confirmed result or visible rejection
```

Failure precedence is authority/schema/revision/domain before effect, then
storage/durability at the commit boundary. A later successful cleanup cannot
turn an earlier failed commit into success.

## View 5 — Decision flow

| Decision | Inputs | Outcomes |
| --- | --- | --- |
| Authority | actor, matter, scope, requested effect, owner evidence | routine record; route; deny |
| Revision | expected and confirmed revisions | continue; conflict |
| Context sufficiency | named Define job requirements, ordered context candidates, provenance, conflicts | sufficient; insufficient; indeterminate |
| Domain validity | current state, command, exact rules/policies | state/event proposal; reject |
| Pack validation | exact snapshot and consumer contract | validated; all structural gaps |
| Export | validated revision and authority envelope | export; route; deny |

Retention values, identity providers, encryption, numeric SLOs, and
accessibility acceptance criteria remain owner decisions rather than hidden
defaults.

## View 6 — Dependency and interface

- `SessionTransportInterface` is versioned and shared by CLI/chat; protocol and
  process topology remain unselected.
- `SessionRepositoryInterface` supports load, compare-and-commit, and health;
  backend and durability implementation remain unselected.
- `SessionPersistenceMapping` must preserve semantic identity, evidence, gaps,
  owners, and authority limits across the repository boundary.
- `DefineRuntimeInterface` permits a private adapter to validation/handoff
  mechanics; it grants no external package migration.
- `SemanticEvaluatorInterface` is a private versioned port. The current Agent
  Reasoning Engine semantic-judgment evaluator is a bounded deterministic reuse
  candidate, not a Define adapter, general reasoning engine, or authority source.
- DomainSpec v2 constrains the semantic source but remains candidate and not
  compiler-conformant for this profile.

## Quality and operational boundaries

Security is least privilege plus exact matter/scope evaluation; the provider,
credential, encryption, and secret boundaries are open. Retention is explicit
and owner-approved; no duration or deletion authority is inferred. Telemetry is
content-minimizing. SLO categories are durability, availability, latency,
capacity, and recovery, but numeric targets are open. Accessibility requires
the current question, reason, state, owner route, and recovery actions to remain
perceivable and operable across both interfaces; exact acceptance criteria are
open.

## Plan boundary

The planned witnesses are contracts, not executed evidence. A later Plan may
materialize them only after canonical Design activation or an explicitly
accepted alternative lifecycle route. Nothing here authorizes implementation.
The sufficiency requirement catalog, current-window boundary, session retention
policy, evaluator adapter, and human-facing wording remain owner-routed gaps.
