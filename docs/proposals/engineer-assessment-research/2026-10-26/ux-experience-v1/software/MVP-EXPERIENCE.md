# Three-session developer challenge: MVP experience

Status: design. First pilot audience: invited adult **mixed software developers** and a small research/reviewer team. The experience is a **challenge with provisional feedback**. Employer screening, universal ranking, personality claims and automated rejection are outside this release. Report completion and scoring diagnostics by declared experience/role/stack strata where sample precision permits; do not compare people across those strata as if the score were equated.

## Participant promise and boundaries

The developer can complete up to three separate cases, each with at most ten minutes of recorded answer: (1) unfamiliar creative/analytical problem, (2) technical/product design, (3) cooperation and communication. The challenge shows a provisional criterion-level profile with answer evidence and suggestions for reflection under the [participant metric specification](PARTICIPANT-METRICS.md). It says how the profile was generated, where evidence is missing, and that the result is not a validated hiring decision. The developer can inspect/correct a transcript, request an accessible response path, and exercise the applicable data controls.

The first pilot uses reviewed, frozen cases. The generator may propose future candidates for the bank but cannot publish an unreviewed question. A common practice item tests microphone/camera and timing without scoring. Multiple defensible answers remain possible in each session. No face, emotion, eye-contact, accent, speaking-speed or personality inference enters scoring.

## Screen and state journey

| Step | Participant action and visible result | Required system record |
| --- | --- | --- |
| 1. Invitation | Open a private invite; see challenge purpose, estimated time, three topics, permitted help, recording rules and provisional feedback limit. | Invitation/cohort source and notice version; no media yet. |
| 2. Purpose choices | Accept necessary challenge processing; choose separately whether answer/score may enter research, whether follow-up contact is allowed, and whether optional subgroup information may be provided. A purpose detail panel sits beside the relevant choice and can be reopened. | Timestamped purpose-specific choices and notice hashes; no bundled research opt-in. |
| 3. Access check | Choose offered response mode, request accommodation/contact, test device, and complete an unscored practice item. | Mode, device readiness, issue/retry events; no inference from accessibility choice. |
| 4. Each case | See one assigned case version, its rules and a server-synchronized clock. Record an answer; any reveal appears at a pinned point. Pause/retry follows the published policy. Candidate sees upload confirmation before advancing. | Assignment, case/version, start/reveal/stop/receipt times, mode, attempt state, media digest, technical failures. |
| 5. Transcript review | See time-aligned ASR text after processing, play source if retained, correct mistakes without changing the original, and flag missing evidence. | Raw transcript version, correction diff, final candidate-approved version, ASR/model pin. |
| 6. Feedback | See six dimensions per session where fairly elicited, cited excerpts, assessment coverage and review status, plus a short improvement exercise. Numeric `0–4` anchors require the metric display gate. No percentile in this pilot. | Scoring run, evidence spans, human review/adjudication, pinned feedback metric version, score report version and delivery receipt. |
| 7. Data controls | View purposes and retention, withdraw optional research use, request export/correction/deletion, and contact the project. | Rights request, propagation state, response receipt and any exception decision. |

**Feedback before full calibration:** publish qualitative, human-reviewed observations such as “you identified the changed constraint” and “this tradeoff was not discussed.” A numeric `0–4` dimension anchor may appear only after the [metric display gate](PARTICIPANT-METRICS.md) passes for the exact case/rubric/mode; the default pilot display is qualitative. Session totals and peer comparisons remain hidden. The application must never describe a candidate as “hireable,” “top engineer,” honest, cooperative as a trait, or a percent match to jobs on this evidence.

## Reviewer and researcher experience

Reviewers receive pseudonymous, mode-normalized answers and exact rubric/case version. They independently mark evidence spans and `0–4/NA/UNK` criterion ratings; they do not see another rater's score or candidate identity before submitting. A discrepancy queue preserves raw ratings and adjudication. Research staff can inspect allocation balance, session completion, ASR correction rate, case exposure, scoring disagreements and missingness by approved cohort slices. They can export only a purpose-filtered dataset with a manifest and no raw media by default. Separate access is needed for source audio/video, contact data and subgroup data.

## Important failure paths

- **Camera/microphone denied, low bandwidth, or speech difficulty:** offer a documented accessible mode or staff route; do not record a zero. Mode equivalence is an experiment, not an assumption.
- **Upload interruption:** resumable upload with server receipt; incomplete media cannot advance silently. Retry creates a distinct attempt and reason.
- **ASR failure:** show `UNK` or human transcription route; do not score missing words as absent reasoning.
- **Withdrawal after scoring:** stop future optional research processing, update eligibility of derived extracts and record the applicable deletion/retention decision.
- **Case leak or ambiguous prompt:** retire the exact version, stop new assignment, mark affected sessions for research review and preserve existing evidence without silently changing their score version.
- **AI or rater disagreement:** send to human review; do not force a result merely to meet a feedback deadline.

## Pilot acceptance evidence

With synthetic fixtures first and permissioned developers later, demonstrate: three complete case journeys under the recorded-time caps; participant comprehension of purpose and provisional feedback; accessible completion or documented alternative; exact replay of a score from pinned inputs; transcript correction without overwriting the source; independent double rating; research opt-out honored in exports; deletion/correction lineage; and a readable failure report. Record completion, burden and feedback usefulness without equating satisfaction with predictive validity.
