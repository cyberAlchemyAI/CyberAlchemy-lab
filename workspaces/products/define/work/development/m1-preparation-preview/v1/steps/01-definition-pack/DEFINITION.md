<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Pack

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-pack`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1:definition-pack:author-review`

## Scientific/formal voice

A Definition Pack is an identifiable, version-exact semantic bundle for one bounded goal, originating intent, declared context, named consumer and intended use. It records the required concept set and exactly one current handling disposition for each concept: reuse, specialize, propose or open. Each disposition has its matching payload. The Pack freezes selected sources and evidence with their standing at capture, owner routes or explicit ownership gaps, scoped relationship records, unresolved obligations, validation scope and the limits of its claim. Reused meanings retain their exact authority. A specialization explicitly distinguishes an application within an existing meaning from a proposed new or revised normative meaning. Pack existence, well-formedness and readiness for a named use do not themselves admit a Definition or permit execution.

```text
P=(id,revision,g,i,k,u,C,delta,H,E,O,R,Q,V,A); D={reuse,specialize,propose,open}; WellFormed(P) iff ExactIdentity(id,revision) and BoundedGoalContextUse(g,k,u) and TraceableIntent(g,i) and FiniteNonempty(C) and (delta in Functions(C,D)) and (dom(H)=C) and (forall c in C: PayloadMatches(H(c),delta(c))) and (forall r in References(P): (ResolvedWithStandingAtCapture(r) or DeclaredGap(r,Q))) and ValidationScopeDeclared(V) and NoNewAuthorityFromPack(A). WellFormed(P) does not entail ReadyFor(P,u,current_inputs), Admitted(Candidates(P)), or MayExecute(u).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P | The frozen bundle; id/revision identify its exact selected material and declared lineage. |
| g,i,k,u | Bounded goal, attributable intent, explicit context, named consumer with one declared intended use. |
| C | Finite nonempty set of distinct required concept identities. Duplicate rows must be rejected before constructing it. |
| D | Exactly reuse, specialize, propose and open. |
| delta in Functions(C,D) | One total single-valued current handling choice for every required concept. |
| H | Matching payload function with domain C; specialization declares application-parameters or proposed-semantic-change. |
| E,O,R,Q | Captured source/evidence standing, owner routes or ownership gaps, scoped relationships and unresolved obligations. |
| V | Declared validation profile, subject/input bindings, criteria/outcome scope and evidence ceiling. |
| A | No new semantic admission or action permission is created by the Pack; separately admitted source meanings keep their authority. |
| ResolvedWithStandingAtCapture | Exact resolved reference and declared posture in the frozen source epoch. This does not assert currentness for every later use. |
| ReadyFor(P,u,current_inputs) | Use-specific gate evaluated separately against current inputs and applicable obligations. Reviewable does not mean executable. |
| Candidates(P) | Proposed Definition outputs, possibly none; their exact owner decisions remain separate. |

### Boundary conditions

- The required concept set is declared and bounded; complete handling does not prove exhaustive discovery of every relevant concept.
- An unresolved outcome has an explicit question, reason, affected use, owner route or ownership gap and continuation; it is never an invented answer.
- Reuse binds one exact current admitted meaning at capture and its applicability; a later change in source standing requires separate current-use assessment.
- Specialization within the parent meaning produces an application binding. A new or changed normative meaning produces a complete proposed Definition through the explicit identity/successor route.
- One Pack can yield zero, one or many Definition candidates; it does not own their normative meanings.
- Role/owner routing labels and producer attribution do not establish Role Assignments or action permission.
- A source resolving is distinct from its admission, currentness, truth and permitted use.
- Relationship suggestions are scoped records; they do not create global Typed Relations.
- A changed selected input, intended use, payload, concept set or meaning produces a new frozen revision with lineage; current-use assessments may be separate records and do not rewrite the frozen Pack.
- Validation scope is required even when all selected references resolve.
- Independent review, consumer-use, semantic-owner, capability-adoption and execution decisions retain their own scopes.
- No semantic admission or new action permission is inferred from this bundle or any structural PASS.

### Testable conditions

- Missing, duplicate or undeclared concept dispositions fail well-formedness.
- Every disposition payload matches its exact tag; specialization declares whether normative meaning changes.
- A resolved candidate source cannot be labeled admitted reuse merely because its reference resolves.
- An unresolved source or owner has a visible scoped gap.
- All references resolving with validation scope absent still fails well-formedness.
- A frozen valid record can remain reviewable when its source standing has changed; a new consequential use still requires current-source/owner assessment.
- Partial selection cannot resolve or authorize unselected concepts.
- A Pack with a proposed meaning does not imply an admitted Definition or an authorized agent action.

## Plain-language voice

For one task, the Pack records which concepts the work needs, what can be reused, what is being narrowed or proposed, and what remains unanswered. It keeps the exact sources, context, ownership questions and limits visible so the next person or agent can review the meaning without guessing. A saved Pack preserves what was known then; using it later requires checking what has changed.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

For an agent investigating the Northstar export incident, the Pack can reuse the admitted Incident meaning, specialize Work as a bounded investigation application, propose identifier completeness for a fixed account/filter/snapshot/output, and keep account exclusivity open. The frozen bundle describes the semantic work and its questions. It is not production telemetry, an incident finding, a closure decision or permission to repair data.

### Examples

- INC-1042 proposes identifier completeness for Northstar, status=active, saved snapshot S-1042 and output E-1042.
- The same Pack may be reviewed while the criterion for account exclusivity remains unanswered.
- Applying Work to the incident changes application parameters without redefining Work.
- A later source/meaning update requires current-use assessment; it does not rewrite the earlier captured record.

## Applicability

Shared meaning of a frozen semantic handling bundle for one bounded goal, originating intent, context, named consumer and declared intended use. Captured standing and later-use readiness remain distinct.

### Exclusions

- Canonical definition admission by candidate generation.
- Permission to execute consumer work.
- Authority to change an external organization or production system.

## Boundaries

- The required concept set is declared and bounded; complete handling does not prove exhaustive discovery of every relevant concept.
- An unresolved outcome has an explicit question, reason, affected use, owner route or ownership gap and continuation; it is never an invented answer.
- Reuse binds one exact current admitted meaning at capture and its applicability; a later change in source standing requires separate current-use assessment.
- Specialization within the parent meaning produces an application binding. A new or changed normative meaning produces a complete proposed Definition through the explicit identity/successor route.
- One Pack can yield zero, one or many Definition candidates; it does not own their normative meanings.
- Role/owner routing labels and producer attribution do not establish Role Assignments or action permission.
- A source resolving is distinct from its admission, currentness, truth and permitted use.
- Relationship suggestions are scoped records; they do not create global Typed Relations.
- A changed selected input, intended use, payload, concept set or meaning produces a new frozen revision with lineage; current-use assessments may be separate records and do not rewrite the frozen Pack.
- Validation scope is required even when all selected references resolve.
- Independent review, consumer-use, semantic-owner, capability-adoption and execution decisions retain their own scopes.
- No semantic admission or new action permission is inferred from this bundle or any structural PASS.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.source@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `aefe53df65d0697772ccb565ec9c279927b1ace67bfd770d2dd959309f11d63a` | `admitted` |
| cal.definition.review@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d` | `admitted` |
| cal.definition.decision-scope@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `1bc60f945b301ebede21fd1aae5f3bf12eff021437dc253b6bce1a772223f1f5` | `admitted` |
| cal.definition.typed-connection-extension-rule@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/01-definition-pack/REVIEW.md
- define/proposals/0005-amended-integration-plan/DESIGN.md
- implementation/define-cli/v1/CONTRACT.md

## Lookup and drift

- Index: `candidate:define-m1:DEFINITIONS-INDEX` / `cal.definition.definition-pack`
- Drift owner: `role:definition-owner`
- Audit: `candidate:define-m1:definition-pack:distinction-review`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- candidate:define-m1:source-selection
- candidate:define-m1:definition-pack:example
- candidate:define-m1:definition-pack:interpretation
- candidate:define-m1:definition-pack:distinction-review

## Residue

- reader-meaning-feedback-pending
- required-semantic-fidelity-and-formal-evidence-pending
- v2-evaluation-lifecycle-profile-adoption-pending
- required-consumer-impact-closure-pending
- exact-owner-scope-challenge-evidence-pending
- exact-registry-index-drift-postimages-and-admission-decision-pending

## Claim ceiling

Step 1 authored Definition/v2 candidate and semantic review specimen. All reused sources retain their captured admitted posture. No formal proof, semantic-owner acceptance, live incident finding, consumer permission, Definition admission, or completed M1 CLI preview is claimed.
