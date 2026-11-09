# User analytics and measurement plan

Status: candidate event contract. [The 27 event specifications](index.json) expand the taxonomy already named in [experiment operations](../software/EXPERIMENT-OPERATIONS.md). They are **allowlists for future events**, not captured user behavior.

## Event boundary

Each permitted occurrence has a unique event and causal operation ID, server time, pseudonymous subject/attempt, actor, purpose and protocol version. Case/session/mode/reason fields are present only where required for the metric. Durable outcomes (`media_committed`, `report_published`, `rights_resolved`, `export_created`) come from a server receipt; a browser click is an intent, not completion. Retries and duplicate delivery retain one logical operation. Client clocks may aid UX diagnosis but cannot set the assessment timer or receipt time.

The allowlist excludes answer text, transcript, media, face features, contact, IP and arbitrary error text. Use enumerated failure codes. Research queries join event IDs to a separately governed purpose/withdrawal state at access time. The event ledger's service-operation purpose does not silently grant research reuse. Retention follows the approved data-class schedule; the draft schedule has open durations. No third-party analytics script, cookies or cross-site tracking are selected here.

## Metric crosswalk

| Question | Event family | Required companion data or test | Interpretation limit |
| --- | --- | --- | --- |
| `PS-01` start conversion | `invited`, `invite_redeemed`, `recording_started` | Eligible invitation denominator, delivery and refusal state. | Recruitment friction only. |
| `PS-02/03` completion and burden | assignment, case, recording, failure, retry, committed media | Server receipts, wall-clock boundaries, unfinished/censored attempts, survey burden. | A completed answer is not a valid score. |
| `PS-04/05` understood/actionable feedback | report published/viewed | Fixed comprehension and actionability tasks with nonresponse accounting. | A view event is not understanding. |
| `PS-06` access gap | journey events by approved mode | Separately permitted audit data, cell counts and intervals. | Do not infer ability or cause from an access mode. |
| `PS-07` ASR evidence loss | ASR and correction events | Human-verified source subset and paired pinned scoring. | Correction frequency is not criterion error. |
| `PS-08` case health | `case_retired`, exposure/failure events | Item bank and case evaluation. | Low retirement is not validity. |
| `PS-16` rights/trust | rights, withdrawal, export and incident receipts | Due dates, propagation proof, access audit. | A requested or resolved event alone is not deletion proof. |

`PS-09`–`PS-15` and `PS-17` require later research/outcome/finance sources; do not synthesize them from interaction telemetry. Participant `FM` values come from pinned scoring and review, never page analytics.

## Dashboard and quality checks

Display numerator, denominator, time window, exclusions, unknown/withdrawn counts, response mode, protocol version and interval beside every rate. Separate “not started”, “collecting”, “estimated with limitations”, “decision-ready” and “contradicted”. Show event ingestion lag, duplicate rate, missing required fields and receipt-to-event reconciliation. A metric is unavailable when its denominator or purpose eligibility is unresolved.

Before collection, an owner must sign off on the event field inventory, purpose/legal basis, retention, analytics processor/region, access role and incident route. Test synthetic duplicate, late, out-of-order, withdrawal, missing-case and rejected forbidden-field fixtures. For UX research, pair funnel counts with observed tasks and interviews; pre-register any comparison of copy or screens under E08.
