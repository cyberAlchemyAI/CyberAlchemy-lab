<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# CyberAlchemy Define

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.cyberalchemy-define`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `development:define-m1:cyberalchemy-define:authored-unadmitted`

## Scientific/formal voice

CyberAlchemy Define is the Lab capability to make the meaning required for one bounded Goal and its originating Intent explicit for a named consumer and intended use. It examines selected existing meanings and their source standing, identifies the declared required concepts, exposes ambiguous or missing meaning and ownership gaps, and prepares a reviewable Definition Pack with exactly one current disposition—reuse, specialize, propose or open—for each declared required concept. The result preserves the originating Intent, explicit Goal and concept-set revisions, exact source bindings and unresolved obligations. It establishes coverage of the declared concept set, not exhaustive discovery of every relevant concept. A recorded open question may be part of a conforming result; an interrupted or failed attempt does not by itself produce one. Define does not select the consumer solution, appoint an owner, admit a Definition, achieve the Goal or grant execution authority. Its Product Capability instance separately binds exactly one Product, scope, owner and outcome contract; a Method specifies the governed transformation, and CLI or agent-based implementations may realize the capability.

```text
X=(g,i,k,u,E,C0); D={reuse,specialize,propose,open};
ConformingDefineResult(X,P) iff WellFormedPack(P)
  and PreservesIntentAndGoalLineage(X,P)
  and AccountsForDeclaredConcepts(C0,C(P),P)
  and (delta_P in Functions(C(P),D))
  and RecordsSourceStandingAndGaps(X,P)
  and ReviewableFor(P,u) and NoNewAuthorityFromPreparation(P).
ConformingDefineResult(X,P) does not entail ExhaustiveDiscovery(X),
  ReadyForConsumerAction(P,u), Admitted(Candidates(P)),
  GoalAchieved(g), or MayExecute(u).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| X; g,i,k,u,E,C0 | Selected input: Goal (with its Project link), originating Intent, context, named consumer plus intended use, exact selected sources/evidence and initial required concept set. |
| P; C(P); delta_P; D | Resulting Definition Pack, its declared required concept set, its single-valued total disposition function and the four closed handling tags. |
| WellFormedPack(P) | The Pack contract proposed in step 1, exact candidate.3. This remains a coupled candidate dependency until its applicable admission. |
| PreservesIntentAndGoalLineage | Attributable Intent and Goal are retained; explicit refinements or replacements keep their reasons and prior lineage. No silent satisfaction or lifecycle transition. |
| AccountsForDeclaredConcepts | All initially required concepts remain handled or have explicit scoped revision evidence. Newly required concepts enter the resulting set; omissions cannot be silently relabeled as completeness. |
| RecordsSourceStandingAndGaps | Exact selected source standing at capture, ownership routes or gaps, unanswered questions, and affected next uses remain visible; capture is not a perpetual-currentness guarantee. |
| ReviewableFor | Consumer, use, boundaries, exact references and unresolved obligations are inspectable. This does not mean that the consumer approved the Pack or may act on it. |
| NoNewAuthorityFromPreparation | Preparing a Pack grants no new semantic admission or action permission; existing admitted meanings retain their separately scoped authority. |

### Boundary conditions

- Capability meaning, owner-qualified Product Capability instance, governed Method, Implementation, Agent and Definition Pack remain separately identifiable; each answers a different declared question.
- One Goal retains its Project and owner routes. A Define result is not evidence that all Goal success conditions are satisfied or that its owner recorded achievement.
- Intent, Goal and required-concept changes are explicit and attributable. A consumer solution or convenient output shape cannot silently replace them.
- Coverage is relative to the declared required set and selected sources. Undiscovered requirements and unselected repository content are not claimed covered.
- An open disposition can be reviewed while blocking a named next use. Unanswered questions and unavailable owners are not fabricated resolutions.
- Specialization distinguishes application parameters under an existing meaning from a proposed normative change. Proposed changes require their own applicable review and admission.
- Source standing is recorded at capture. A later consequential use requires its own relevant source, owner and contract currentness checks.
- A structurally invalid output, provider failure or interrupted attempt is not a conforming result. No particular CLI exit code or future protocol schema is defined by this capability meaning.
- The Product Capability owner, Definition semantic owner and incident investigation owner are separate roles. Naming a route or possessing local signing keys does not appoint any of them.
- Machine Agent Instances cannot outlive or span Sessions. Long-term context comes from governed Project State through Context and Ontology Views; Session Memory remains session-bound. Saved Define work records become Project State only through the applicable governance route.

### Testable conditions

- The result retains the selected Intent/Goal or records an attributable revision and rationale instead of silently dropping the original requirement.
- Each distinct required concept has one matching disposition payload; duplicate, missing or undeclared rows fail the selected Pack contract.
- An unanswered exclusivity criterion remains open and names the next use it blocks; it is not reported as accepted or resolved.
- A tool failure without a conforming Pack remains an unsuccessful attempt even when a process exits or an agent reports completion.
- Reusing an admitted Definition preserves its exact version and captured standing; a generated proposal remains candidate.
- CLI and agent-based realizations can satisfy the same outcome contract without sharing implementation identity or gaining authority from that equivalence.
- Producing the Pack does not change the incident, admit a candidate, mark its Goal achieved or permit a production repair.

## Plain-language voice

Define helps a person or agent establish what the next task depends on: which meanings already apply, what needs a proposal, and which questions remain unanswered. It leaves that work in a reviewable Definition Pack. The Pack covers the concepts explicitly selected for the task; it does not claim to know everything or approve the next action.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

For the Lab integration, Define is the enabled outcome; its owner-qualified Product Capability instance, preparation Method and exact realization binding are separate pending work. The existing CLI candidate reads selected Project State, Context Views and Ontology Views, but its legacy output is not yet the M1 Lab preparation preview. The incident illustration explains the desired outcome without claiming a live agent run or an admitted incident assessment.

### Examples

- For INC-1042, Define clarifies the meanings needed to investigate saved Northstar export evidence with status=active, snapshot S-1042 and output E-1042. The Goal is linked to one illustrative investigation Project; no Project or Goal record is created by the illustration.
- The Pack reuses Incident, applies Work through explicit investigation parameters, proposes identifier completeness and leaves account exclusivity open. Required-ID coverage and exclusion of unrelated records remain separate questions.
- The illustrative 12,000 required IDs and 11,800 matched required IDs show the proposed completeness criterion would fail by 200 IDs; this is a conditional fixture interpretation, not a production finding or Define execution.
- A CLI workflow or ephemeral machine-agent Session can realize Define. A saved Pack supports later review; it is not private long-term machine-agent memory, owner acceptance or a production repair.

## Applicability

Shared meaning for the Lab-owned Define capability and its named consumers. A canonical Product Capability instance separately binds one Product, scope, accountable owner and outcome contract; this Definition does not create that instance or adopt a runtime.

### Exclusions

- Canonical definition admission by candidate generation.
- Permission to execute consumer work.
- Authority to change an external organization or production system.

## Boundaries

- Capability meaning, owner-qualified Product Capability instance, governed Method, Implementation, Agent and Definition Pack remain separately identifiable; each answers a different declared question.
- One Goal retains its Project and owner routes. A Define result is not evidence that all Goal success conditions are satisfied or that its owner recorded achievement.
- Intent, Goal and required-concept changes are explicit and attributable. A consumer solution or convenient output shape cannot silently replace them.
- Coverage is relative to the declared required set and selected sources. Undiscovered requirements and unselected repository content are not claimed covered.
- An open disposition can be reviewed while blocking a named next use. Unanswered questions and unavailable owners are not fabricated resolutions.
- Specialization distinguishes application parameters under an existing meaning from a proposed normative change. Proposed changes require their own applicable review and admission.
- Source standing is recorded at capture. A later consequential use requires its own relevant source, owner and contract currentness checks.
- A structurally invalid output, provider failure or interrupted attempt is not a conforming result. No particular CLI exit code or future protocol schema is defined by this capability meaning.
- The Product Capability owner, Definition semantic owner and incident investigation owner are separate roles. Naming a route or possessing local signing keys does not appoint any of them.
- Machine Agent Instances cannot outlive or span Sessions. Long-term context comes from governed Project State through Context and Ontology Views; Session Memory remains session-bound. Saved Define work records become Project State only through the applicable governance route.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.product-capability@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `446a5357c0dd1337c7345e9c5b14a8ff9b7c03d4ad1162384c491e3400f05431` | `admitted` |
| CAV2-D32@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `82743cbbac7b9ad9f393c56a9efa90aae4acc0d6dff769ddb40fd9b5face1c39` | `admitted` |
| cal.definition.intent@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `cce7b46ddc9bf4f7b42038c15da1380573e58d9bb2919d86b94a7c1738325c0b` | `admitted` |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.context-view@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `0dc6fb05c40d51d0ae746f1177797766861b353844167771c4fb6a793996a7d2` | `admitted` |
| cal.definition.ontology-view@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `1fcc7fa38a6a77e67258ae56c49719ea35f1c853868060ab58200343fde2f81e` | `admitted` |
| cal.definition.agent-session@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `71fbd822757e8e83e4072faf16e2d14c96148e6f24adbed4f225d03c4c48d9e7` | `admitted` |
| CAV2-D59@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `f43a539e5f0f4db26dab0df0cb30c523868c6fef3dbb3d061614a4d288c5ae19` | `admitted` |
| cal.definition.agent-instance@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `21d331a24a6fb7420c2bc59fe504c0701708bd6685925d7dba1a92791070adcd` | `admitted` |
| cal.definition.project-state@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `40e00c926c7ca2a9143c321e1681ebb7df480c71d4b8950e5524849758b4e784` | `admitted` |
| cal.definition.capability-realization-binding@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `8a0f907bb854371b8946e071c9d01702de3f35799405cb8b0ee66e546990b1bd` | `admitted` |

## Primary consumers

- define/INTEGRATION.md
- implementation/define-cli/v1/CONTRACT.md
- define/proposals/0005-amended-integration-plan/DESIGN.md

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.cyberalchemy-define`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/02-cyberalchemy-define/distinction-review.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- proposal:define-amended-integration-plan:source-lineage
- proposal:define-amended-integration-plan:formal-interpretation
- proposal:define-amended-integration-plan:risk-resolution
- define/development/m1-preparation-preview/v1/steps/01-definition-pack/definition.json
- define/development/m1-preparation-preview/v1/steps/02-cyberalchemy-define/interpretation.json
- define/development/m1-preparation-preview/v1/steps/02-cyberalchemy-define/example.json

## Residue

- exact-semantic-owner-decision-pending
- v2-profiles-and-required-representation-amendment-pending
- required-formal-and-fidelity-evidence-pending
- declared-consumer-impact-closure-pending
- exact-admission-postimages-pending
- definition-pack-exact-candidate-dependency-admission-pending
- owner-qualified-product-capability-and-realization-binding-pending

## Claim ceiling

Revised authored Definition/v2 candidate for sequential M1 meaning review. Only exact admitted meanings govern source premises; the revised Pack is a candidate dependency. Schema/projection/source checks do not prove semantic fidelity or non-collapse. No owner acceptance, admission, runtime implementation, live agent outcome or new action authority.
