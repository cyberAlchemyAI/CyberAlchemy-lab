# Question generation, tracking and evaluation

Status: candidate design for E02 and the first mixed-developer MVP. In this program a **question** becomes a scored item only as a released [Case Version](../model/definitions.json). The canonical meanings for every capitalized record are in [definitions.json](../model/definitions.json). This document defines proposed rules, use cases, operations and workflow; it does not authorize live collection or claim that any case is validated.

## What we generate

| Session | Generation target | Required variation and exclusion |
| --- | --- | --- |
| 1: creativity, analysis, ingenuity | Unusual problems with multiple defensible paths: assumption changes, causal explanations of an object/animal, constrained invention, linked-state puzzles or unfamiliar engineering analogies. | Vary the reasoning mechanism, not only nouns. Reject famous elephant/fridge/jungle answers and any form where recognition of a punchline dominates reasoning. Include a clue or changed constraint when the design tests revision. |
| 2: technical and product design | A bounded product need with users, operating constraints, tradeoffs and a later requirement change. | Vary architecture tradeoff and failure mode; avoid stack trivia and prompt ambiguity masquerading as difficulty. |
| 3: cooperation and communication | A work coordination dilemma with stakeholders, incentives, information limits, division of work/credit, an interaction turn and ethical constraints. | Vary strategic structure and counterparty response. Explain game rules in ordinary language; do not require Prisoner's Dilemma vocabulary. |

The first pilot can use one reviewed released form per session. It cannot estimate form equivalence or broad construct coverage from those three items. The research bank must grow across independent families and variants under the [full protocol](../research/full-protocol.md).

## Rules

| ID | Rule | Evidence or failure path |
| --- | --- | --- |
| Q-R01 source | Every draft has a Generation Brief, named human author or pinned Case Generator, Generation Run, prompt/configuration, source restrictions, and exact parent version. | Missing lineage blocks screening. |
| Q-R02 immutable drafts | Save every Case Candidate and rejection reason; revisions create successors. Never silently edit a shown or reviewed prompt. | Content hash and predecessor link. |
| Q-R03 mechanism | Record a Reasoning Mechanism Fingerprint and compare both wording and underlying solution mechanism across the bank and known public examples. | Similarity Assessment plus reviewer decision; a low automated score alone cannot clear the gate. |
| Q-R04 answerability | Independent reviewers verify all stated facts, solvability, multiple defensible answers, alternative answer paths, reveal logic and expected ten-minute response burden. | Case Review cites a Case Evaluation; ambiguity sends draft to revise/reject. |
| Q-R05 construct | Each intended scoring dimension must have observable answer evidence and plausible rival explanations such as prior exposure, game familiarity, fluent speech or stack expertise. | Unsupported dimension becomes `NA` or is removed before release. |
| Q-R06 access | Review language, culture, disability/access modes, device requirements and reference knowledge; run Case Trials where uncertainty remains. | Access issue blocks release until redesigned or a supported mode is available. |
| Q-R07 independent release | A person other than the generator records a Case Disposition. Release binds exact Case Version, compatible Rubric, Administration Policy, purpose, audience and exposure state. | No disposition or unresolved severe objection means no scored assignment. |
| Q-R08 controlled exposure | Public examples, practice items, Case Trials, scored administrations, leaks and reported familiarity update Case Exposure. Held-out mechanism families never enter generator context. | Quarantine affected forms and review assignments after a leak. |
| Q-R09 assignment | Only a released, purpose-compatible version enters an Assignment Manifest. Pin its hash before display. A case retired later remains attached to historical responses. | Assignment service rejects draft, held-out or retired versions. |
| Q-R10 monitoring | Post-session familiarity, alternative solutions, missing facts, time, mode, rater disagreement and item-level response patterns feed a new Case Evaluation. | Drift or exposure triggers hold/retire review, not silent rescoring. |
| Q-R11 research separation | Development, calibration and locked validation forms/participants are tagged before use. No tuning on holdouts. | Crossing the split invalidates that holdout for the affected claim. |
| Q-R12 traceable judgment | Automated screens create flags and measurements. Human reviewers resolve semantic ambiguity and release; research later estimates difficulty, reliability, fairness and transfer. | A passing screen is not a validity claim. |

## Use cases

| ID | Actor and purpose | Done when |
| --- | --- | --- |
| Q-U01 | Research designer creates a Generation Brief for one session and target audience. | Inputs, forbidden patterns and review criteria are frozen. |
| Q-U02 | Case author or generator proposes variants. | All candidates, parentage and rejected outputs are retained. |
| Q-U03 | Case analyst screens duplicates, leaks and repeated mechanisms. | Two-level similarity results and corpus version are recorded. |
| Q-U04 | Experts and volunteers test answerability, access and intended reasoning. | Independent Case Reviews and any Case Trials produce a versioned Case Evaluation. |
| Q-U05 | Case-bank owner releases, holds, revises or retires an exact version. | Case Disposition and compatible rubric/policy pins exist. |
| Q-U06 | Assignment service allocates only eligible cases. | Manifest records probability, strata, case hash and actual assignment. |
| Q-U07 | Researcher monitors live item health and exposure. | Deviations, drift and retirement decisions are reported without deleting old data. |
| Q-U08 | Reviewer audits a score or report months later. | Exact brief, candidate, release, assignment, response, transcript, rubric and scoring versions reconstruct the path. |

## Operations and records

| ID | Operation | Input → durable output | Refusal or retry condition |
| --- | --- | --- | --- |
| Q-O01 | Freeze brief | session blueprint + audience + exclusions → Generation Brief | Missing construct or review owner. |
| Q-O02 | Generate batch | brief + generator version/config/seed → Generation Run + all Case Candidates | Missing pinned input; job failure retained. |
| Q-O03 | Fingerprint and screen | candidate + bank/public corpus snapshot → Mechanism Fingerprint + Similarity Assessment | Corpus unavailable or severe duplicate flag. |
| Q-O04 | Evaluate draft | candidate + rubric blueprint + independent reviewers + optional trials → Case Evaluation + Case Reviews | Unresolved answerability, access or severe reviewer objection. |
| Q-O05 | Release or hold | evaluation + reviews + exposure + rubric/policy compatibility → Case Disposition + immutable Case Version if released | Generator self-approval, missing owner or incompatible rubric. |
| Q-O06 | Allocate | released versions + protocol + exclusions → Assignment Manifest + Session Assignment | Draft/retired/held-out version, or quota exhausted. |
| Q-O07 | Record exposure | public sighting, trial, administration or participant familiarity → Case Exposure update | Unknown source retained as uncertain, never discarded. |
| Q-O08 | Monitor/retire | post-use metrics + exposure evidence → new Case Evaluation and Case Disposition | Material leak quarantines new assignment pending review. |

The MVP case-bank service needs records for `generation_brief`, `generation_run`, `case_candidate`, `mechanism_fingerprint`, `similarity_assessment`, `case_review`, `case_trial`, `case_evaluation`, `case_disposition`, `case_exposure`, `case_family`, `case_version` and compatibility links to `rubric_version` and `administration_policy`. Each record has stable ID, version, actor, timestamps, source hash, purpose/audience and predecessor where relevant. Bank search and draft content are restricted; the participant API receives only its assigned visible slice.

## Workflow and evaluation

```text
Q-W01: brief frozen → candidates generated/retained → fingerprint and screen
     → expert review and optional non-scored trial → evaluation
     → reject | revise (new candidate) | hold | release (immutable case version)
     → assignment and exposure monitoring → hold/retire or controlled successor
```

Pre-release evidence has four layers. **Static checks** validate format, facts, source, leakage, duplicate wording and time budget. **Independent review** judges solution mechanism, alternative-valid answers, construct coverage, culture/access and rubric fit. **Case Trials** test comprehension, response paths and burden with consented volunteers; trials are development data, not scored pilot evidence. **Post-release analysis** measures familiarity, omission/ambiguity reports, timing, criterion missingness, rater agreement, mode differences, item difficulty/discrimination and drift by cohort. Any threshold, reviewer count, sample precision and retirement trigger must be selected in the versioned Study Protocol before data are analyzed. The first pilot can estimate descriptive item behavior; equivalent difficulty and predictive value require later designs.

E02 reports candidate acceptance/rejection by reason, surface and mechanism duplicate rates, reviewer disagreement, trial findings, exposure/retirement counts, and changes made before release. A released form remains versioned with its evidence packet. Negative results remain in the development ledger. The [session studies](../research/README.md) and [full protocol](../research/full-protocol.md) define later construct and transfer tests; those results must never be inferred from this lifecycle alone.

## Open decisions

- Select named case-bank owner, independent reviewers and conflict rule.
- Set languages, response modes, reference corpora, similarity methods and numerical escalation thresholds.
- Select trial sample, minimum precision, rubric anchors, accessibility acceptance and release count for the first three forms.
- Set exposure/quarantine/retirement triggers and whether any case family can be reused across cohorts.
- Register role-specific job-task linkage only for the later hiring-validation study.
