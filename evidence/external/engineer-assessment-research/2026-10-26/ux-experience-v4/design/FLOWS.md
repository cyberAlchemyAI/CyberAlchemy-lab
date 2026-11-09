# Role journeys and state transitions

The four [Experience Flow records](index.json) identify role, task, steps, exceptions, policy and metrics. These transitions add the handoff logic that screens and backend receipts must implement. They remain candidate designs until permissioned use.

## Participant — `UX-FL-01`

| Transition | Visible condition and action | Required receipt or exception |
| --- | --- | --- |
| Invite → purpose | The participant sees time, modes, assistance, provisional feedback and support before proceeding. | Redeemed invitation and exact notice version. Invalid/expired invite gives support route. |
| Purpose → access | Required processing and optional research/contact are distinct choices with adjacent details. | Purpose-specific choice receipt; optional refusal still follows the approved challenge path. |
| Access → practice | Device checks and response-mode selection precede unscored practice. | Practice receipt. Denied device or access barrier routes to an offered alternative or staff; no score penalty. |
| Ready → recording | Exact case/rules and server time are visible before explicit start. | Pinned case, policy and start receipt; maximum 10 recorded minutes per session. |
| Recording → upload | Stop action or time cap ends capture; upload shows local and server progress. | Only verified committed media advances. Reconnect resumes transfer without clock reset; an unresolved upload stays visible. |
| Upload → transcript | ASR processing status is shown; correction creates a new version. | Original retained, diff and final approved version; failure routes to human transcription/UNK. |
| Transcript → feedback | Human review and evidence availability govern publication. | Report version and delivery receipt; qualitative default, no percentile or hiring verdict. |
| Feedback → rights | Purposes, retention state, withdrawal and rights routes stay reachable. | Request and resolution receipts; withdrawal changes future research eligibility and export access. |

A failed case keeps its original assignment and exposure. A replacement is linked to the same scored slot under the [recovery protocol](../software/RECOVERY-PROTOCOL.md); the participant sees why and whether the old answer is retained. Do not ask for a new case simply because a connection dropped.

## Reviewer — `UX-FL-02`

Queue → pinned case/rubric → source evidence → independent `0–4/NA/UNK` submission → discrepancy queue → adjudication. Hide identity and other ratings before independent submission. If media or transcript is unusable, mark `UNK` and escalate; do not infer missing reasoning. Record conflict-of-interest and access decisions. An adjudicator sees both original ratings and records the resolution reason without rewriting them.

## Researcher — `UX-FL-03`

Protocol/role access → allocation and denominator view → missingness and quality review → purpose-filtered export request → manifest review → export receipt. Every export rechecks withdrawal and current purpose at execution. A small cell, invalid protocol, case exposure or custody incident blocks or narrows the export and leaves an audit receipt. A dashboard estimate carries its population, window and uncertainty.

## Support — `UX-FL-04`

Request → identity/scope verification → accessible or recovery route → resolution → participant receipt. Support cannot silently change a score, policy or research choice. Failed verification, deletion propagation and unavailable mode are escalated with a visible pending state and an owner route.
