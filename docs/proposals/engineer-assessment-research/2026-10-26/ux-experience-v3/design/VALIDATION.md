# Interface evidence contract

Mode: `spec` for the UX evidence validator. No runnable frontend or participant study has been validated. The [prototype](prototype.html) is a static review artifact and does not satisfy the release checks.

| Layer | Planned evidence | Example scenario |
| --- | --- | --- |
| L0 source | Record exact screen, component, policy, metric and source-card versions. | Invitation and purpose screen match the selected notice. |
| L1 structure | DOM, semantic labels, landmark, ARIA state and accessibility scan. | Purpose detail opens with keyboard and reports expanded state. |
| L2 behavior | Playwright user-facing interaction, clock/recovery fixture and API receipt assertions. | Upload interruption resumes the same attempt without resetting the clock. |
| L3 visual | Viewport screenshots at mobile, desktop, 200% zoom, forced colors and reduced motion. | Recording status and blur state remain visible. |
| L4 content | Copy/claim and forbidden-data checks. | Feedback says provisional and does not label a person “hireable”. |
| L5 human | Moderated task and comprehension study. | Participant explains research choice and missing-evidence feedback. |
| L6 decision | Owner review of failures, access gaps and research results before release. | A failed purpose or custody check blocks collection. |

Scenario schema: `scenario_id`, `role`, `screen_ref`, `viewport`, `input_mode`, `initial_state`, `action`, `expected_visible_state`, `expected_receipt`, `policy_ref`, `event_spec_ref`, `claim_class`, `source_cards`, `fixture_ref`. Fixtures need known-good, known-bad and false-positive examples for disclosures, timer, upload, feedback, rights, reviewer blinding and export gating. Browser evidence, when implemented, writes metadata, findings, console/network logs, ARIA/accessibility snapshots, screenshots, measurements, traces for interactive paths and a residue ledger under `output/playwright/ux-validator/<run-id>/`.

**Hard gates:** missing accessible name, inaccessible keyboard path, absent focus/status announcement, failed required receipt, event payload outside allowlist, feedback claim violation, purpose/export bypass. **Soft flags:** unusually long copy, crowded layout or repeated help requests. **Screenshot review:** visual hierarchy, clipping and status salience. **Human study:** comprehension, perceived burden/trust and real task success. **Not automatable:** whether the brand feels credible, whether feedback truly helps learning, and whether scores predict engineering performance.

An automated check may fail or flag a screen. It cannot mark the entire service accessible, user-friendly or scientifically valid without the corresponding evidence and owner decision.
