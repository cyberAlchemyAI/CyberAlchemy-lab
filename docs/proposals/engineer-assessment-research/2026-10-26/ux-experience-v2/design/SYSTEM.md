# Design system handoff — `UX-DS-01`

Status: candidate implementation contract. [Tokens](tokens.json) are the portable source; the [ten component records](index.json) specify reusable interaction patterns. The [twelve screen records](index.json) specify role-visible uses. The static [prototype](prototype.html) demonstrates visual direction but has no data path.

## Foundations

- **Layout:** single reading column up to 720 px for instructions, feedback and notices; wider 1120 px workspace for camera/case side by side or staff tables. Collapse to one column before content clips. At 200% zoom and mobile width, keep the primary action after its instructions in DOM order.
- **Typography:** system font for interface copy, 16 px body and 1.55 line-height; 14 px only for secondary labels that retain contrast; headings use a responsive scale and sentence case. Monospace is reserved for IDs and technical examples, not long prose.
- **Color:** semantic text/surface/action/status tokens. Candidate text pairs are checked to at least 4.5:1 by `validate_ux_records.py`; actual browser-rendered states, focus and icons still need checks. Never encode a criterion rating or score confidence solely with color.
- **Space and targets:** 4 px base spacing; primary controls have at least 44 px candidate height. Avoid placing destructive rights actions adjacent to “continue” without clear separation and confirmation of effect.
- **Motion:** transitions are optional and removed under reduced-motion preference. Recording state, clock and upload progress remain understandable without animation.
- **Content:** one primary action per step; put purpose, help allowance, time and consequences near the relevant choice. Use plain error codes translated into a next action. Preserve exact policy/notice version in any durable choice receipt.

## Component acceptance contract

| Component | Required visible state | Accessibility and failure behavior |
| --- | --- | --- |
| Action button | Verb, pending and disabled reason. | Native button, visible focus, disabled action never silently succeeds. |
| Adjacent detail | Collapsed/expanded purpose or rule detail beside choice. | `details/summary` or equivalent keyboard and expanded semantics; reopenable. |
| Status message | Pending, completed, blocked with next action. | Announce change without moving focus for ordinary updates; blocking error receives focus or explicit alert. |
| Timer | Server remaining time and end behavior. | Text clock and meaningful warnings; reconnect cannot reset authoritative time. Timing accessibility and alternative mode require owner review. |
| Recorder | Preview, blur on/off/unavailable, capture started/stopped. | Labels mirror actual capture state; denial routes to alternate path. Blur is visible to the participant and does not claim to remove recorded background. |
| Upload progress | Bytes received and verified media receipt. | Determinate progress when known; incomplete upload stays unresolved; retry is idempotent. |
| Reveal | Rule and revealed content state. | Keyboard and screen reader announcement; reveal timing pinned to policy and session event. |
| Evidence excerpt | Cited span, transcript version and uncertainty. | Text is selectable; source link and correction route; missing evidence is explicit. |
| Criterion rating | `0–4/NA/UNK` and exact anchor. | Reviewer can select by keyboard, cannot submit without evidence or reason. |
| Recovery notice | Cause, preserved state and retry/support route. | Focus on actionable resolution; never silently assigns a replacement case. |

Every component needs default, focus, unavailable, pending/success where applicable, error and reduced-motion states in a runnable fixture. The release implementation should use native elements where possible. The WAI-ARIA patterns guide custom behavior; ARIA attributes cannot repair missing keyboard interaction or unclear content.
