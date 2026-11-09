# Definition map

The exact candidate statements and exclusions are in [definitions.json](definitions.json). Define v2 packages them for the named consumer and intended use. The following map explains the distinction between reused Lab meanings and assessment-specific proposals.

## Reuse from the current Lab registry

| Concept | Lab definition | Local use |
| --- | --- | --- |
| Product | `cal.definition.product` | Durable value identity, separate from research project and implementation. |
| Product Thesis | `cal.definition.product-thesis` | Owner-held value and evidence proposition. |
| Product Capability | `cal.definition.product-capability` | Product outcome, separate from feature and realization. |
| Project | `CAV2-D60` | Bounded coordination effort, separate from the durable Product. |
| Goal | `CAV2-D59` | Desired result and success condition, separate from an achieved result. |
| Research Inquiry | `cal.definition.research-inquiry` | Question, source policy, method and stopping condition before investigation. |
| Experiment Design | `cal.definition.experiment-design` | Prospective comparison and falsifier, separate from run. |
| Measurement Method | `cal.definition.measurement-method` | Bounded scoring procedure and interpretation, not the score itself. |
| Evidence | `cal.definition.evidence` | Source-bound observation supporting or contradicting a claim. |
| Authority | `cal.definition.authority` | Exact decision permission, separate from a receipt or recommendation. |

Exact version, source path, original-file digest and selected-content digest are recorded across `define-v2/request.json` and `define-v2/project-goal-request.json` and captured in their respective packages. The Lab registry decides current standing; this document does not.

## Assessment-specific meanings

The 16 terms are: Engineering Role Profile, Target Outcome, Assessment Construct, Case Family, Case Version, Assessment Session, Candidate Response, Transcript, Rubric, Scoring Run, Score Report, Validation Study, Claim Tier, Consent Record, Cohort, and Decision Policy. Each is task-local and proposed. Particular candidate and participant identities are separate private records, not ontology definitions.

The most important non-collapse relations are:

1. `Case Version != Response != Transcript != Scoring Run != Score Report`.
2. `Construct != Rubric != Model`; a score estimates a construct under a declared method and population.
3. `Research Inquiry != Experiment Design != Experiment Run != Evidence != Finding != Owner Decision`.
4. `Product != Project != Goal != Product Capability != Implementation`.
5. `Challenge feedback != employment decision`; the same recording cannot change purpose silently.
6. `Candidate ranking != observed future performance`; selection quality requires independent later outcome evidence.

## Open definition decisions

- "Best engineer" needs a selected role, level, candidate pool, performance criterion, time horizon, and capacity. The proposed Target Outcome definition forces those parameters.
- "Creativity," "analysis," and "ingenuity" have operational anchors in session 1, but construct validity and their relation to future work remain research questions.
- "Cooperation" inferred from a recorded scenario may differ from observed team behavior; the two are separately measured in validation.
- The named accountable human principal for each role and the exact retention schedule remain open.
