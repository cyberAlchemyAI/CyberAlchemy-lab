# Full definitions, contracts and work map

Source excerpts retain their exact wording. This generated review collection is explanatory and grants no normative authority. Exact canonical input hashes are in [source bindings](source-bindings.json).

## Definition Pack

[Canonical JSON](../../../steps/01-definition-pack/definition.json) · SHA256 `83bb643b14b48980d85db9bd381c1d4b2ccd27b7bb890c9e24fd2848809dfe76`

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


## CyberAlchemy Define

[Canonical JSON](../../../steps/02-cyberalchemy-define/definition.json) · SHA256 `d4ba6c882cea56e3bc9cc425c356d9fbc34f5de83727f3426cadad1c4326f286`

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


## Definition

[Canonical JSON](../../../steps/03-foundational-definition/definition.json) · SHA256 `37a81341252f331236ff0a260edcc48d57ecae117559f50ebe11876a732abbe8`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `development:define-m1:foundational-definition:authored-unadmitted`

## Scientific/formal voice

A Definition is a versioned, owner-scoped semantic artifact that assigns a term one normative meaning within an exact authority scope. It is structurally complete only when stable identity, applicability, exclusions, a scientific/formal normative voice, explicitly non-normative plain-language and domain-context voices, boundaries, admitted source posture, primary consumers, a synchronized registry postimage, generated index, and a current drift route are declared. Only an exact owner promotion decision can make one exact Definition version canonical authority.

```text
DefinitionComplete(d) iff StableId(d) and ExactScope(d) and FormalVoice(d) and NonNormativePlainVoice(d) and NonNormativeDomainVoice(d) and Boundaries(d) and AdmittedSources(d) and RegistryPostimage(d) and GeneratedIndex(d) and CurrentDriftRoute(d). DefinitionComplete(d) does not imply Admitted(d).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| d | One stable Definition identity at one exact version, evaluated together with its declared review package. |
| StableId; ExactScope | Identity and exact version; authority scope, applicability and exclusions. A filename or classification label cannot supply these silently. |
| FormalVoice | One normative statement with applicable formal expression, notation, boundary conditions and testable conditions. |
| NonNormativePlainVoice; NonNormativeDomainVoice | Explicitly explanatory voices that retain the same scope and meaning; they cannot independently extend the normative statement. |
| Boundaries; AdmittedSources | Declared meaning limits and exact source standing admitted for the applicable target use. Authored candidates can expose unresolved source gaps, but those gaps block promotion readiness. |
| RegistryPostimage; GeneratedIndex | Declared proposed registry and reproducible lookup projection for the exact version. Completeness requires resolved package material, not merely a placeholder reference. |
| CurrentDriftRoute | Accountable owner, audit and challenge route applicable to the selected scope and current review inputs. |
| DefinitionComplete(d); Admitted(d) | Structural/governance completeness of the declared package and separately selected owner admission. Neither a schema pass nor an evaluated example selects admission. |

### Boundary conditions

- A changed normative meaning requires a new Definition version.
- Interpretive voices cannot weaken or expand the normative voice.
- Schema validity and evidence do not perform promotion.
- The successor preserves the admitted normative statement and formal expression. Its applicable-carrier verification rule replaces the v1-only rule; historical bindings remain explicit.
- Carrier, schema, generator and applicable evaluation/lifecycle profile references require exact version, digest, standing and compatibility dispositions. A caller cannot select an arbitrary schema to bypass the applicable contract.
- A shape-valid authored record may have unresolved admission obligations. It is not thereby DefinitionComplete or admission-ready.
- Checking a criterion against example data is distinct from checking the Definition artifact and its semantic fidelity.
- No predecessor connection is silently retyped, copied into a new global relation, removed from history or deemed compatible solely by schema acceptance.

### Testable conditions

- The exact machine record validates against its exact applicable Definition carrier and bound evaluation profile under an explicit version/compatibility disposition; schema, generator and profile standing are resolved for the proposed use.
- The generated projection is byte-identical across two renders and matches the exact bound generator output.
- The candidate appears exactly once in the proposed registry and generated index; live current lookup remains unchanged before the applicable admission/application.
- The three voices preserve one normative meaning and its scope; source, owner and drift routes resolve under their separate standing requirements.
- Each predecessor semantic, carrier and embedded connection binding receives an explicit preservation, compatibility, update or blocking disposition.
- Formal distinction/consistency evidence declares its interpretation, scope and limitations; it does not imply unrestricted consistency or replace owner semantic fidelity review.
- Pre-decision eligibility is assessed separately from the final exact owner decision, so an otherwise eligible candidate need not already be admitted.

## Plain-language voice

A Definition is the owner-scoped record that states what one term means, where that meaning applies and where it stops. Its formal statement governs; the plain-language and domain-context voices explain the same meaning. Its exact representation, sources, consumers and review route are declared. Checks supply evidence, and only the applicable owner decision makes the exact version authoritative.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

The Lab stores Definition JSON as the canonical machine record and generates Markdown from it. This successor keeps the admitted foundational meaning and stable identity while replacing the v1-only verification rule with an exact applicable carrier/profile binding. The admitted Definition/v2 carrier already exists; compatible v2 evaluation and lifecycle successors and consumer dispositions remain pending. The incident example uses an actual repository candidate with illustrative data, without claiming an accepted production finding.

### Examples

- The export identifier completeness candidate states a criterion for fixed snapshot S, account A, filters F and saved output E. Its three voices explain inclusion of required IDs; accuracy and account exclusivity remain separate.
- A required population of 12,000 IDs and 11,800 matched IDs would fail the proposed coverage criterion. This does not invalidate the Definition record structure or admit its meaning.
- An agent can read a generated human view, but authoritative meaning comes from the exact owner-admitted machine record and scoped bindings; neither an ontology label nor the agent output replaces it.
- If this successor is later admitted, the predecessor retains its exact bytes and admission history. Existing consumers do not silently rebind to the successor.

## Applicability

Normative meanings intentionally shared across CyberAlchemy Lab authority and construction surfaces.

### Exclusions

- Context-local expressions that have no shared semantic role.
- Generated summaries, glossary hints, and source quotations.

## Boundaries

- A glossary entry, ontology node, source quotation, generated index row, or narrative explanation is not a Definition by itself.
- Definition identity, artifact type, semantic kind, authority kind, lifecycle posture, owner scope, and bounded-context membership are independent axes.
- One canonical field must never be silently inferred from another; dependent classifications require explicit typed relations; convenience labels are generated projections.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |

## Primary consumers

- authority/definitions/registry.json
- authority/artifact-types/definition/v2
- define/proposals/0005-amended-integration-plan/DESIGN.md
- authority/profiles/definition/v1/evaluation.json
- authority/profiles/definition/v1/lifecycle.json
- docs/lab/how-to/prepare-definition.md

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/03-foundational-definition/compatibility-review.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- proposal:define-amended-integration-plan:source-lineage
- proposal:define-amended-integration-plan:formal-interpretation
- proposal:define-amended-integration-plan:risk-resolution
- define/development/m1-preparation-preview/v1/steps/03-foundational-definition/interpretation.json
- define/development/m1-preparation-preview/v1/steps/03-foundational-definition/compatibility-review.json
- define/development/m1-preparation-preview/v1/steps/03-foundational-definition/example-definition.json

## Residue

- exact-semantic-owner-successor-decision-pending
- v2-evaluation-lifecycle-profiles-pending
- required-consumer-impact-closure-pending
- prior-typed-connection-preservation-disposition-pending
- exact-registry-index-drift-postimages-pending

## Claim ceiling

Authored foundational successor for sequential M1 meaning review. The admitted normative statement and formal expression are preserved; carrier/verification compatibility is proposed explicitly. No source-standing expansion, predecessor connection withdrawal, current lookup change, owner admission, profile adoption, runtime implementation or formal proof is asserted.


## Definition Evaluation Profile

[Canonical JSON](../../../steps/07-profile-formal-source-evidence/definitions/definition-evaluation-profile/definition.json) · SHA256 `5cb480685961c24223e16796eeee0852a22bdf6f31249b379a11ec681d8727b1`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Evaluation Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-evaluation-profile`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1:profile-source-closure-unadmitted`

## Scientific/formal voice

A Definition Evaluation Profile is a reusable, owner-qualified, version-exact contract declaring how an Evaluation assesses one exact Definition version and its declared review package within a named scope and phase. It binds the subject and input selection, applicable governing contracts, required checks, evidence requirements, permitted outcomes, causal blockers, phase-specific aggregation, pre-decision eligibility and claim limits. It specifies the rules for producing and interpreting evaluation evidence; a declared profile does not establish that an Evaluation occurred, that its criteria passed, that an owner selected admission or that an effect was applied.

```text
P=(id,v,T,Sel,C,Omega,B,G,R,A,o,s,L); Omega={PASS,FAIL,NOT_EVALUABLE};
ConformingEvaluation(e,P,S,I,g) implies ExactBinding(e,P,S,I,g) and dom(O_e)=C and BlockersPreserved(e,P).
For g in G, R(P,g) subseteq C; A(P,g,O_e)=FAIL if any c in R(P,g) has O_e(c)=FAIL;
else NOT_EVALUABLE if any required c has O_e(c)=NOT_EVALUABLE; else PASS.
Declaration(P) does not entail Executed(e), A(P,g,O_e)=PASS, Admitted(S), or Applied(S).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P; id,v; T | Exact profile identity/revision and selected Definition subject representation. |
| Sel; S; I; s; g | Exact subject/input selection, one Definition version, input state, authority/applicability scope and named phase. |
| C; Omega; O_e; B | Finite declared check identities, outcome vocabulary, one complete evaluation result map and causal blocker contract. |
| G; R(P,g); A | Declared phases, required aggregation subset for one phase, and its outcome rule. Completeness of check reporting and phase aggregation are different obligations. |
| o; L | Qualified profile owner and explicit coverage/authority claim limits. |
| ConformingEvaluation; ExactBinding | Interpretation of a conforming completed evidence record, not a guarantee that every attempt succeeds. Relevant subject/profile/input versions and scope must match. |

### Boundary conditions

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- Every declared check receives a scoped result or an explicit not-evaluable blocker; only the named phase subset contributes to its aggregate.
- A required check with missing applicable evidence is NOT_EVALUABLE; an established violation is FAIL. Missing evidence is not a proof of violation.
- Admission-selection/application checks can be reported as pending while excluded from pre-decision aggregation.

### Testable conditions

- The semantic record preserves exact identity, scope, three voices and selected carrier/generator bindings.
- Profile declarations, completed evidence, owner selection and confirmed effects have separate identifiers and evidence.
- The incident example retains the account, filters, source snapshot and saved output boundaries.
- No missing review or unperformed effect is reported as completed.

## Plain-language voice

The contract for checking a Definition and understanding the results. It says which evidence is required, which checks contribute to each phase and why other checks are blocked. The results describe only what was actually established; they do not approve the Definition.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This revised semantic binding applies to the proposed v2 profile/carrier. The candidate itself uses admitted Definition/v1 mechanics and current v1 review routes as the explicit bootstrap choice, independent of the meaning’s scope. No v2 self-approval or owner acceptance is claimed.

### Examples

- For the identifier-completeness Definition, schema and projection checks pass while required semantic evidence remains NOT_EVALUABLE.
- The incident’s 200 missing IDs make its proposed coverage predicate false. That is a different subject from whether the Definition record meets its governance contract.

## Applicability

Shared meaning for Lab Definition evaluation contracts and exact phase-scoped review packages.

### Exclusions

- Profiles for unrelated artifact kinds without their own declared extension.
- Automatic owner decisions, lifecycle events, application or machine-agent permission.

## Boundaries

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- Every declared check receives a scoped result or an explicit not-evaluable blocker; only the named phase subset contributes to its aggregate.
- A required check with missing applicable evidence is NOT_EVALUABLE; an established violation is FAIL. Missing evidence is not a proof of violation.
- Admission-selection/application checks can be reported as pending while excluded from pre-decision aggregation.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.evaluation@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `7ca1fc6de116223f93d026856c7780320d600b79e454c0b4ef957bd03dd24a7b` | `admitted` |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /checks | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /admission_rule | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| cal.definition.review@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /outcomes | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /evaluation_mode | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /subject_artifact_type_ref | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /owner_ref | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/2 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/4 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-evaluation-profile/artifact.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-evaluation-profile`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/semantic-binding-review.json
- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/compatibility.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/interpretation.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/example.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-core.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-results.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/correspondence.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json

## Residue

- owner-interpretation-and-semantic-fidelity-decision-pending
- bounded-model-not-whole-natural-language-consistency
- exact-registry-index-review-postimages-pending
- carrier-profile-adoption-pending
- owner-admission-pending

## Claim ceiling

Source-completed candidate with unchanged candidate.2 normative statement and formal expression. Finite model/exhaustive rule evidence applies only to the explicit interpreted core and pinned inputs. It does not establish whole-repository consistency, real-world owner authentication, semantic fidelity acceptance, admission or applied effects.


## Definition Lifecycle Profile

[Canonical JSON](../../../steps/07-profile-formal-source-evidence/definitions/definition-lifecycle-profile/definition.json) · SHA256 `876835497765f255b3de998cf1786d3d5b2196d25a44ba66159e8185520944ac`

<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Lifecycle Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-lifecycle-profile`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1:profile-source-closure-unadmitted`

## Scientific/formal voice

A Definition Lifecycle Profile is a reusable, owner-qualified, version-exact contract declaring the initial posture, permitted states and directed transitions for one exact Definition version under selected governing contracts. It binds each transition to its required evaluation and review evidence, applicable owner authority, intended effect, invalidation conditions and history-preservation rules. It separates satisfied gates, recorded review, selected admission and confirmed application. Declaring the profile or satisfying a gate does not itself record a new state, select an owner Decision, apply an effect or prove that a transition occurred.

```text
P=(id,v,T,Q,q0,E,Gate,Effect,o,s,Invalidate,History); E subseteq Q x Q.
PermittedBy(P,d,a,b,I) iff ExactBinding(P,d,I) and (a,b) in E and Gate(P,d,a,b,I)=PASS.
PermittedBy(P,d,a,b,I) does not entail TransitionRecorded(d,a,b) or EffectApplied(d,Effect(P,a,b)).
ConsistentAdmittedState(d) requires applicable exact owner admission selection and confirmed application; declaration alone provides neither.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P; id,v; T; d | Exact profile identity/revision, selected Definition representation and one exact Definition version. |
| Q; q0; E | Declared states, initial posture and finite directed transition pairs; no transition is inferred from independent state lists. |
| Gate; I | Scoped requirements and exact evidence/authority input state. PASS establishes the gate; unknown or unsupported evidence does not establish permission. |
| Effect; o; s | Declared effect, qualified authority owner and applicability scope. Effect selection and confirmed application remain separate facts. |
| Invalidate; History | Rules for changed epochs, affected evidence invalidation and immutable historical state/receipt preservation. |
| PermittedBy; TransitionRecorded; EffectApplied | Conditions allowing a transition, a separately attributable transition record and separately confirmed effect; none is silently substituted for another. |

### Boundary conditions

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- A permitted directed pair and satisfied gate do not move the subject automatically; each actual transition requires an attributable record and applicable confirmed effect.
- Initial posture is a contract declaration, not evidence of another record’s actual state.
- Pre-decision readiness is an assessment, not an extra lifecycle state. Defer/revise/reject outcomes do not silently create a withdrawal effect.

### Testable conditions

- The semantic record preserves exact identity, scope, three voices and selected carrier/generator bindings.
- Profile declarations, completed evidence, owner selection and confirmed effects have separate identifiers and evidence.
- The incident example retains the account, filters, source snapshot and saved output boundaries.
- No missing review or unperformed effect is reported as completed.

## Plain-language voice

The contract for when a Definition may change state, what evidence and authority are needed, and what history must be kept. A passed check can satisfy a condition; an actual state change still needs its declared record and applicable effect.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This revised semantic binding applies to the proposed v2 profile/carrier. The candidate itself uses admitted Definition/v1 mechanics and current v1 review routes as the explicit bootstrap choice, independent of the meaning’s scope. No v2 self-approval or owner acceptance is claimed.

### Examples

- The completeness Definition stays candidate-authored while semantic review and admission remain pending.
- Even an eligible owner-reviewed Definition stays unadmitted when the admission Decision or its confirmed application is missing.

## Applicability

Shared meaning for Lab Definition lifecycle contracts, transition gates and history-preservation rules.

### Exclusions

- Profiles for unrelated artifact kinds without their own declared extension.
- Automatic owner decisions, lifecycle events, application or machine-agent permission.

## Boundaries

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- A permitted directed pair and satisfied gate do not move the subject automatically; each actual transition requires an attributable record and applicable confirmed effect.
- Initial posture is a contract declaration, not evidence of another record’s actual state.
- Pre-decision readiness is an assessment, not an extra lifecycle state. Defer/revise/reject outcomes do not silently create a withdrawal effect.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.decision@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `514f8a33054508ecd7050ddeb5241e3cd55d7ccf7bfd8677323ebea6318627be` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /transitions | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /separation_invariants | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| cal.definition.admission-transaction@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `af1468a3eaec84c1146a1b570f4154738d586d9691f846fbf56f9fa5228c3b86` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /states | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /initial_state | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /subject_artifact_type_ref | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-LIFECYCLE-DEFINITION-V1 | /owner_ref | `aa81df2baa7be140cfa130723008a122d9aae73815a5cbd07bbcf92dacc64af8` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/2 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/4 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-lifecycle-profile/artifact.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-lifecycle-profile`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/semantic-binding-review.json
- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/compatibility.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/interpretation.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/example.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-core.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-results.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/correspondence.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json

## Residue

- owner-interpretation-and-semantic-fidelity-decision-pending
- bounded-model-not-whole-natural-language-consistency
- exact-registry-index-review-postimages-pending
- carrier-profile-adoption-pending
- owner-admission-pending

## Claim ceiling

Source-completed candidate with unchanged candidate.2 normative statement and formal expression. Finite model/exhaustive rule evidence applies only to the explicit interpreted core and pinned inputs. It does not establish whole-repository consistency, real-world owner authentication, semantic fidelity acceptance, admission or applied effects.


## Evaluation/v2 profile

[Canonical candidate](../../../steps/04-definition-v2-profiles/evaluation.json)

```json
{
  "status": "candidate-unadmitted",
  "authority_effect": "none",
  "subject_artifact_type_ref": "cal.artifact-type.definition/v2",
  "schema_ref": "cal.schema.definition-profiles/v2",
  "schema_digest": "533d6487edd40a3006e9deb73c205ad9ae0f87562f665d9d995ca8cdc5d72d16",
  "binding_contract_ref": "define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/check-contracts.json",
  "binding_contract_sha256": "bedd3309bd4c1c6c079cddcc05a113159f5868c60f432003543062b986c998c7",
  "schema_version": "cyberalchemy-lab-evaluation-profile/v2",
  "record_id": "CAL-EVALUATION-DEFINITION-V2",
  "artifact_type_ref": "cal.artifact-type.evaluation-profile/v2",
  "owner_ref": "role:evidence-conformance-owner",
  "outcomes": [
    "PASS",
    "FAIL",
    "NOT_EVALUABLE"
  ],
  "evaluation_mode": "collect-all",
  "checks": [
    {
      "check_id": "DEF2-01-REPRESENTATION",
      "purpose": "Resolve exact subject type, schema and representation; reject unknown fields and changed digests.",
      "blocked_by": []
    },
    {
      "check_id": "DEF2-02-VOICES",
      "purpose": "Require three present voices with explanatory voices explicitly non-normative.",
      "blocked_by": [
        "DEF2-01-REPRESENTATION"
      ]
    },
    {
      "check_id": "DEF2-03-SOURCES",
      "purpose": "Resolve each exact source, selector, integrity, standing at capture and permitted target use.",
      "blocked_by": [
        "DEF2-01-REPRESENTATION"
      ]
    },
    {
      "check_id": "DEF2-04-OWNER",
      "purpose": "Resolve semantic/drift roles and admitted assignments within the exact scope.",
      "blocked_by": [
        "DEF2-01-REPRESENTATION"
      ]
    },
    {
      "check_id": "DEF2-05-PROJECTION",
      "purpose": "Bind exact generator and require canonical JSON to match deterministic human projection.",
      "blocked_by": [
        "DEF2-01-REPRESENTATION"
      ]
    },
    {
      "check_id": "DEF2-06-CONNECTIONS",
      "purpose": "Close declared dependency and relation obligations, endpoint pairs and carrier roles.",
      "blocked_by": [
        "DEF2-01-REPRESENTATION"
      ]
    },
    {
      "check_id": "DEF2-07-REGISTRY-DRIFT",
      "purpose": "Verify exact proposed registry, unique index entry, generated lookup and accountable drift route.",
      "blocked_by": [
        "DEF2-01-REPRESENTATION"
      ]
    },
    {
      "check_id": "DEF2-08-IMPACT",
      "purpose": "Resolve named consumers, compatibility, source/use gaps and all required current affected bindings.",
      "blocked_by": [
        "DEF2-03-SOURCES",
        "DEF2-06-CONNECTIONS"
      ]
    },
    {
      "check_id": "DEF2-09-SEMANTIC-ASSURANCE",
      "purpose": "Inspect scoped non-collapse and internal-consistency evidence with exact interpretation and coverage.",
      "blocked_by": [
        "DEF2-02-VOICES",
        "DEF2-03-SOURCES"
      ]
    },
    {
      "check_id": "DEF2-10-FIDELITY",
      "purpose": "Record attributable interpretation/voice/source fidelity review of the exact meaning.",
      "blocked_by": [
        "DEF2-08-IMPACT",
        "DEF2-09-SEMANTIC-ASSURANCE"
      ]
    },
    {
      "check_id": "DEF2-11-PROFILE-COMPATIBILITY",
      "purpose": "Resolve applicable profile/carrier standing, exact bindings and foundational compatibility.",
      "blocked_by": [
        "DEF2-01-REPRESENTATION"
      ]
    },
    {
      "check_id": "DEF2-12-REVIEW-COHORT",
      "purpose": "Freeze exact reviewed inputs, requested effects, owner routes and deterministic output recipes.",
      "blocked_by": [
        "DEF2-07-REGISTRY-DRIFT",
        "DEF2-08-IMPACT",
        "DEF2-10-FIDELITY",
        "DEF2-11-PROFILE-COMPATIBILITY"
      ]
    },
    {
      "check_id": "DEF2-13-ADMISSION-DECISION",
      "purpose": "Verify the separate exact owner decision selecting this admission effect.",
      "blocked_by": [
        "DEF2-12-REVIEW-COHORT"
      ]
    },
    {
      "check_id": "DEF2-14-APPLICATION",
      "purpose": "Verify the separate exact admission application and effective lookup visibility.",
      "blocked_by": [
        "DEF2-13-ADMISSION-DECISION"
      ]
    }
  ],
  "admission_rule": "All checks 01-12 PASS on current exact inputs; check 13 is NOT_EVALUABLE solely because owner admission has not been selected; check 14 is excluded before application. If a Decision already exists, assess its binding and application through the later phases rather than treating it as pending. Required phase/check scopes and exact inputs are in the bound check contract. Eligibility is not a lifecycle state or authority grant. Final admission and application are separate checks.",
  "source_direction": {
    "canonical": "evaluation.json",
    "human_projection": "EVALUATION.md",
    "projection_policy": "generated-only",
    "generator_ref": "cal.generator.definition-profile-projections/v2",
    "generator_sha256": "d7cf8ee7f1248a9ffb16cf1719f52954e7ea57d9da2f12a792444939bca701ab"
  },
  "claim_ceiling": "Proposed Definition/v2 evaluation profile and explicit profile-carrier successor. No automatic owner review, semantic truth, profile adoption, Definition admission, current lookup change or runtime implementation."
}
```

## Lifecycle/v2 profile

[Canonical candidate](../../../steps/04-definition-v2-profiles/lifecycle.json)

```json
{
  "status": "candidate-unadmitted",
  "authority_effect": "none",
  "subject_artifact_type_ref": "cal.artifact-type.definition/v2",
  "schema_ref": "cal.schema.definition-profiles/v2",
  "schema_digest": "533d6487edd40a3006e9deb73c205ad9ae0f87562f665d9d995ca8cdc5d72d16",
  "binding_contract_ref": "define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/check-contracts.json",
  "binding_contract_sha256": "bedd3309bd4c1c6c079cddcc05a113159f5868c60f432003543062b986c998c7",
  "schema_version": "cyberalchemy-lab-lifecycle-profile/v2",
  "record_id": "CAL-LIFECYCLE-DEFINITION-V2",
  "artifact_type_ref": "cal.artifact-type.lifecycle-profile/v2",
  "owner_ref": "role:definition-owner",
  "states": [
    "candidate-authored",
    "validated-candidate",
    "owner-reviewed",
    "admitted",
    "superseded",
    "withdrawn"
  ],
  "initial_state": "candidate-authored",
  "transitions": [
    {
      "from": "candidate-authored",
      "to": "validated-candidate",
      "gate": "Exact validation phase in the bound check contract is PASS under adopted applicable profile/carrier bindings; checks 13-14 are excluded. Record a separate attributable transition for this exact candidate epoch.",
      "effect": "Record scoped validation posture; create no semantic authority."
    },
    {
      "from": "validated-candidate",
      "to": "owner-reviewed",
      "gate": "Checks 01-12 PASS; applicable owner review/fidelity record binds the exact candidate and evidence; a separate transition record confirms review completion.",
      "effect": "Record review completion; select no admission effect."
    },
    {
      "from": "owner-reviewed",
      "to": "admitted",
      "gate": "Pre-decision eligibility is established without a prior admission; exact owner Decision passes check 13 and its authorized application passes check 14.",
      "effect": "Only confirmed applicable admission makes the selected exact version authoritative within its scope."
    },
    {
      "from": "admitted",
      "to": "superseded",
      "gate": "Exact owner successor Decision and confirmed coherent application select the admitted replacement and preserve predecessor bytes/history.",
      "effect": "Retire current lookup for this predecessor only after the exact successor becomes effective."
    },
    {
      "from": "candidate-authored",
      "to": "withdrawn",
      "gate": "Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route.",
      "effect": "Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred."
    },
    {
      "from": "validated-candidate",
      "to": "withdrawn",
      "gate": "Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route.",
      "effect": "Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred."
    },
    {
      "from": "owner-reviewed",
      "to": "withdrawn",
      "gate": "Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route.",
      "effect": "Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred."
    },
    {
      "from": "admitted",
      "to": "withdrawn",
      "gate": "Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route.",
      "effect": "Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred."
    },
    {
      "from": "superseded",
      "to": "withdrawn",
      "gate": "Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route.",
      "effect": "Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred."
    }
  ],
  "separation_invariants": [
    "Semantic identity, lifecycle state, source currentness, validation result, authority state, and publication state are independent axes.",
    "A digest change creates a new candidate epoch; it cannot refresh an old admission decision.",
    "PASS does not imply owner review, admission, publication, implementation, or correctness.",
    "Directory placement and generated projections never change lifecycle state.",
    "Representation PASS, full validation, owner review, pre-decision eligibility, selected admission and confirmed application are separately recorded.",
    "No profile or walkthrough executes a transition. No gate requires its own future Decision to already exist.",
    "Changed subject/evidence/profile/source/effect bytes invalidate affected evidence and require a new epoch and applicable review. Historical state/evidence remains preserved; no automatic backward lifecycle rewrite.",
    "Revise, defer and reject are review outcomes, not extra Definition lifecycle states. Defer can preserve the current state; withdrawal requires its explicit selected effect and applicable transition.",
    "Candidate profile use in a preparation preview cannot promote the example to validated-candidate or admitted under an unadopted contract."
  ],
  "source_direction": {
    "canonical": "lifecycle.json",
    "human_projection": "LIFECYCLE.md",
    "projection_policy": "generated-only",
    "generator_ref": "cal.generator.definition-profile-projections/v2",
    "generator_sha256": "d7cf8ee7f1248a9ffb16cf1719f52954e7ea57d9da2f12a792444939bca701ab"
  },
  "claim_ceiling": "Proposed lifecycle successor. Defines gates and effect boundaries; performs no owner review, transition, admission, supersession, withdrawal, lookup update or runtime activation."
}
```

## Fourteen-check contract, phases and evidence requirements

[Canonical candidate](../../../steps/04-definition-v2-profiles/check-contracts.json)

```json
{
  "schema_version": "cal.define-profile-check-contracts/v1",
  "authority_effect": "none",
  "evaluation_profile_id": "CAL-EVALUATION-DEFINITION-V2",
  "lifecycle_profile_id": "CAL-LIFECYCLE-DEFINITION-V2",
  "subject_binding": {
    "admission_decision_ref": "CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION",
    "artifact_path": "authority/artifact-types/definition/v2/artifact.json",
    "artifact_sha256": "f863bd4b09a28c5ca3e82e9008ddc837c1186bad9f35fe9e5cde4ea2ccfac5f7",
    "artifact_type_ref": "cal.artifact-type.definition/v2",
    "instance_discriminator": {
      "path": "/schema_version",
      "value": "cyberalchemy-lab-definition/v2"
    },
    "lifecycle_state": "admitted-current",
    "schema_path": "authority/artifact-types/definition/v2/schema.json",
    "schema_selector": null,
    "schema_sha256": "269591e7f0dd7c1c077579dd874599ba08fa8e17df10fa262d936f8ad5519181",
    "semantic_definition_refs": [
      "cal.definition.definition@1.0.0-candidate.1"
    ],
    "semantic_kind": "definition"
  },
  "subject_generator": {
    "path": "authority/artifact-types/definition/v2/generator.py",
    "sha256": "b3dc43b827a3b509e6afb90336227b2bfedb0854b5bfbda50c053782ea883e8d"
  },
  "outcome_rules": {
    "PASS": "Required predicate is established by applicable evidence for the exact subject and selected scope.",
    "FAIL": "Applicable evidence establishes a violated required predicate, including a known integrity or authority mismatch.",
    "NOT_EVALUABLE": "Required inputs, applicable standing, execution or review evidence are absent, unavailable, unsupported or stale; missing proof is not proof of violation.",
    "collect_all": "Evaluate independent checks even when another fails. A blocked dependent check records NOT_EVALUABLE and the exact reason."
  },
  "phases": {
    "representation": [
      "DEF2-01-REPRESENTATION",
      "DEF2-02-VOICES",
      "DEF2-05-PROJECTION"
    ],
    "validation": [
      "DEF2-01-REPRESENTATION",
      "DEF2-02-VOICES",
      "DEF2-03-SOURCES",
      "DEF2-04-OWNER",
      "DEF2-05-PROJECTION",
      "DEF2-06-CONNECTIONS",
      "DEF2-07-REGISTRY-DRIFT",
      "DEF2-08-IMPACT",
      "DEF2-09-SEMANTIC-ASSURANCE",
      "DEF2-11-PROFILE-COMPATIBILITY"
    ],
    "owner_review": [
      "DEF2-01-REPRESENTATION",
      "DEF2-02-VOICES",
      "DEF2-03-SOURCES",
      "DEF2-04-OWNER",
      "DEF2-05-PROJECTION",
      "DEF2-06-CONNECTIONS",
      "DEF2-07-REGISTRY-DRIFT",
      "DEF2-08-IMPACT",
      "DEF2-09-SEMANTIC-ASSURANCE",
      "DEF2-10-FIDELITY",
      "DEF2-11-PROFILE-COMPATIBILITY",
      "DEF2-12-REVIEW-COHORT"
    ],
    "pre_decision": [
      "DEF2-01-REPRESENTATION",
      "DEF2-02-VOICES",
      "DEF2-03-SOURCES",
      "DEF2-04-OWNER",
      "DEF2-05-PROJECTION",
      "DEF2-06-CONNECTIONS",
      "DEF2-07-REGISTRY-DRIFT",
      "DEF2-08-IMPACT",
      "DEF2-09-SEMANTIC-ASSURANCE",
      "DEF2-10-FIDELITY",
      "DEF2-11-PROFILE-COMPATIBILITY",
      "DEF2-12-REVIEW-COHORT"
    ],
    "decision": [
      "DEF2-13-ADMISSION-DECISION"
    ],
    "application": [
      "DEF2-14-APPLICATION"
    ]
  },
  "aggregation_rule": "For the exact selected phase: FAIL if any required check FAIL; otherwise NOT_EVALUABLE if any required check is NOT_EVALUABLE; otherwise PASS. Do not aggregate all 14 checks into validation or pre-decision eligibility.",
  "eligibility_rule": "All checks 01-12 PASS on current exact inputs; check 13 is NOT_EVALUABLE solely because owner admission has not been selected; check 14 is excluded before application. If a Decision already exists, assess its binding and application through the later phases rather than treating it as pending.",
  "profile_standing_rule": "Candidate profiles and proposed profile carriers support explicitly bounded preview analysis only. Binding digests establishes integrity; separate applicable determinations establish adopted standing.",
  "checks": [
    {
      "check_id": "DEF2-01-REPRESENTATION",
      "phase": "representation",
      "purpose": "Resolve exact subject type, schema and representation; reject unknown fields and changed digests.",
      "depends_on": [],
      "required_inputs": [
        "exact Definition bytes",
        "selected admitted Definition/v2 descriptor and schema"
      ],
      "pass_when": "Exact discriminator, schema identity/digest and closed schema pass; subject identity/version unique.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-02-VOICES",
      "phase": "representation",
      "purpose": "Require three present voices with explanatory voices explicitly non-normative.",
      "depends_on": [
        "DEF2-01-REPRESENTATION"
      ],
      "required_inputs": [
        "scientific/formal voice",
        "plain-language voice",
        "domain-context voice"
      ],
      "pass_when": "All voice fields and notation/boundary/testable declarations satisfy carrier requirements; semantic agreement is assessed separately in DEF2-10.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-03-SOURCES",
      "phase": "validation",
      "purpose": "Resolve each exact source, selector, integrity, standing at capture and permitted target use.",
      "depends_on": [
        "DEF2-01-REPRESENTATION"
      ],
      "required_inputs": [
        "source selection",
        "admission/currentness/target-use evidence"
      ],
      "pass_when": "Every declared governing source resolves at exact digest with applicable standing and use. Missing applicable source evidence is NOT_EVALUABLE; known inadmissibility/mismatch is FAIL.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-04-OWNER",
      "phase": "validation",
      "purpose": "Resolve semantic/drift roles and admitted assignments within the exact scope.",
      "depends_on": [
        "DEF2-01-REPRESENTATION"
      ],
      "required_inputs": [
        "owner registry",
        "scope-specific owner applicability evidence"
      ],
      "pass_when": "Role names resolve to admitted assignments, owner scope is established, and no local key is treated as identity or appointment.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-05-PROJECTION",
      "phase": "representation",
      "purpose": "Bind exact generator and require canonical JSON to match deterministic human projection.",
      "depends_on": [
        "DEF2-01-REPRESENTATION"
      ],
      "required_inputs": [
        "generator bytes/digest",
        "human projection bytes"
      ],
      "pass_when": "Two renders are byte-identical and match the bound human projection; this does not authenticate origin.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-06-CONNECTIONS",
      "phase": "validation",
      "purpose": "Close declared dependency and relation obligations, endpoint pairs and carrier roles.",
      "depends_on": [
        "DEF2-01-REPRESENTATION"
      ],
      "required_inputs": [
        "embedded references",
        "declared coupling obligations",
        "exact Relation Kind/endpoint evidence"
      ],
      "pass_when": "Every declared connection resolves under current contract, with qualifiers where required. An empty embedded list passes only its bounded reference subcheck; absence of undeclared required coupling is not inferred.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-07-REGISTRY-DRIFT",
      "phase": "validation",
      "purpose": "Verify exact proposed registry, unique index entry, generated lookup and accountable drift route.",
      "depends_on": [
        "DEF2-01-REPRESENTATION"
      ],
      "required_inputs": [
        "registry/index/drift postimages",
        "exact baseline identity"
      ],
      "pass_when": "Exactly one selected candidate version is proposed, history preserved, postimages reproducible and drift owner/route current; placeholder strings do not count as resolved material.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-08-IMPACT",
      "phase": "validation",
      "purpose": "Resolve named consumers, compatibility, source/use gaps and all required current affected bindings.",
      "depends_on": [
        "DEF2-03-SOURCES",
        "DEF2-06-CONNECTIONS"
      ],
      "required_inputs": [
        "declared impact inventory",
        "consumer dispositions",
        "compatibility evidence"
      ],
      "pass_when": "All required current bindings have supported compatible/update dispositions; blocking or unsupported deferred obligations remain visible and block readiness.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-09-SEMANTIC-ASSURANCE",
      "phase": "validation",
      "purpose": "Inspect scoped non-collapse and internal-consistency evidence with exact interpretation and coverage.",
      "depends_on": [
        "DEF2-02-VOICES",
        "DEF2-03-SOURCES"
      ],
      "required_inputs": [
        "interpreted-model contracts",
        "formal evidence",
        "selected semantic corpus and obligations"
      ],
      "pass_when": "Required bounded checks have applicable evidence, assumptions, executed coverage and no unresolved required counterexample. Unsupported temporal/deontic/empirical clauses require explicit owner-qualified disposition; they cannot receive a fabricated global PASS.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-10-FIDELITY",
      "phase": "owner-review",
      "purpose": "Record attributable interpretation/voice/source fidelity review of the exact meaning.",
      "depends_on": [
        "DEF2-08-IMPACT",
        "DEF2-09-SEMANTIC-ASSURANCE"
      ],
      "required_inputs": [
        "exact candidate/evidence",
        "applicable owner fidelity record"
      ],
      "pass_when": "Owner review explicitly accepts fidelity to selected meaning and source scope. Author commentary, lexical differences or answering go-next does not satisfy this check.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-11-PROFILE-COMPATIBILITY",
      "phase": "validation",
      "purpose": "Resolve applicable profile/carrier standing, exact bindings and foundational compatibility.",
      "depends_on": [
        "DEF2-01-REPRESENTATION"
      ],
      "required_inputs": [
        "selected evaluation/lifecycle profiles",
        "profile-carrier/schema/generator binding",
        "foundational successor compatibility"
      ],
      "pass_when": "Required profile mechanics/type/evaluation/lifecycle determinations and foundational compatibility are effective for the intended use. Proposed-only schemas/profiles are usable for preview discussion, not assumed admitted enforcement.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-12-REVIEW-COHORT",
      "phase": "owner-review",
      "purpose": "Freeze exact reviewed inputs, requested effects, owner routes and deterministic output recipes.",
      "depends_on": [
        "DEF2-07-REGISTRY-DRIFT",
        "DEF2-08-IMPACT",
        "DEF2-10-FIDELITY",
        "DEF2-11-PROFILE-COMPATIBILITY"
      ],
      "required_inputs": [
        "immutable selected review package",
        "effect declarations",
        "approved output recipe/postimage bindings"
      ],
      "pass_when": "Review material identifies exact candidates, evidence, independent roles, postimages/recipes and invalidation conditions without requiring the future admission Decision or hashing itself.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-13-ADMISSION-DECISION",
      "phase": "decision",
      "purpose": "Verify the separate exact owner decision selecting this admission effect.",
      "depends_on": [
        "DEF2-12-REVIEW-COHORT"
      ],
      "required_inputs": [
        "actual attributable owner Decision",
        "exact reviewed subject/effect bindings"
      ],
      "pass_when": "Applicable owner Decision exists and matches the exact eligible subject, evidence/recipes and selected effect; no Decision is fabricated during preview.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    },
    {
      "check_id": "DEF2-14-APPLICATION",
      "phase": "application",
      "purpose": "Verify the separate exact admission application and effective lookup visibility.",
      "depends_on": [
        "DEF2-13-ADMISSION-DECISION"
      ],
      "required_inputs": [
        "actual application receipt",
        "published immutable epoch",
        "effective current lookup"
      ],
      "pass_when": "Exact authorized application is confirmed, with coherent selected epoch and replay-safe identity; a Decision alone does not prove the effect occurred.",
      "claim_ceiling": "Exact subject and declared use only; grants no new authority."
    }
  ]
}
```

## Final type-registration changes

[Canonical candidate](../../../steps/09-assurance-evidence-closure/registration-delta.json)

```json
{
  "admitted_contracts_added": 0,
  "authority_effect": "none",
  "baseline": {
    "path": "authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json",
    "sha256": "b2a34b5e27d49d94ee41c139ead7f66fcdc5cef163bced4d86d2c2bf03ab3390"
  },
  "current_selections_changed": false,
  "effective_lookup_recipe": "Future exact application after required independent owner effects; delta does not fabricate admitted rows or advance current selections.",
  "historical_lineage_baseline": {
    "path": "authority/admissions/definition-complete-lab-model/v1/artifact-type-registry.json",
    "sha256": "77a4be44316d3292d43d4528020ee4ebe82d2e9126805e5a2730acf93c926e01"
  },
  "promotion_dependencies": [
    {
      "admission_posture": "candidate-unadmitted",
      "bytes": 13673,
      "carrier_ref": "cal.artifact-type.definition/v1",
      "definition_ref": "cal.definition.definition-evaluation-profile@1.0.0-candidate.3",
      "generator": {
        "bytes": 4675,
        "path": "authority/artifact-types/definition/v1/generator.py",
        "sha256": "1bac2e064c11eb4b5e945172a21fe6e1635bc48023269fba6dbbdb11d585167c"
      },
      "human_projection": {
        "bytes": 10143,
        "path": "define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/definitions/definition-evaluation-profile/DEFINITION.md",
        "sha256": "7006e0533f37664f399cc3e2ce31fce32fd26a53f76343247d62100bd00fb1a1"
      },
      "path": "define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/definitions/definition-evaluation-profile/definition.json",
      "schema": {
        "bytes": 7602,
        "path": "authority/artifact-types/definition/v1/schema.json",
        "sha256": "c39a2c6fe7bdc2cd306152c1b8c4c9dc045d784e44e35d9d9da4e1517bd03adf"
      },
      "sha256": "5cb480685961c24223e16796eeee0852a22bdf6f31249b379a11ec681d8727b1"
    },
    {
      "admission_posture": "candidate-unadmitted",
      "bytes": 13660,
      "carrier_ref": "cal.artifact-type.definition/v1",
      "definition_ref": "cal.definition.definition-lifecycle-profile@1.0.0-candidate.3",
      "generator": {
        "bytes": 4675,
        "path": "authority/artifact-types/definition/v1/generator.py",
        "sha256": "1bac2e064c11eb4b5e945172a21fe6e1635bc48023269fba6dbbdb11d585167c"
      },
      "human_projection": {
        "bytes": 10116,
        "path": "define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/definitions/definition-lifecycle-profile/DEFINITION.md",
        "sha256": "b15fb2d6a2731fc6e3491435dd354c7c28ebb84768b445041d200a5743b7e2cb"
      },
      "path": "define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/definitions/definition-lifecycle-profile/definition.json",
      "schema": {
        "bytes": 7602,
        "path": "authority/artifact-types/definition/v1/schema.json",
        "sha256": "c39a2c6fe7bdc2cd306152c1b8c4c9dc045d784e44e35d9d9da4e1517bd03adf"
      },
      "sha256": "876835497765f255b3de998cf1786d3d5b2196d25a44ba66159e8185520944ac"
    },
    {
      "admission_posture": "candidate-unadmitted",
      "bytes": 11430,
      "carrier_ref": "cal.artifact-type.definition/v2",
      "definition_ref": "cal.definition.definition@1.0.0-candidate.3",
      "generator": {
        "bytes": 4672,
        "path": "authority/artifact-types/definition/v2/generator.py",
        "sha256": "b3dc43b827a3b509e6afb90336227b2bfedb0854b5bfbda50c053782ea883e8d"
      },
      "human_projection": {
        "bytes": 9636,
        "path": "define/development/m1-preparation-preview/v1/steps/03-foundational-definition/DEFINITION.md",
        "sha256": "b93b7ab5b324050307a7d65ed660281c5f3ebce098f12c6c4824d4bc6bcc535d"
      },
      "path": "define/development/m1-preparation-preview/v1/steps/03-foundational-definition/definition.json",
      "schema": {
        "bytes": 10760,
        "path": "authority/artifact-types/definition/v2/schema.json",
        "sha256": "269591e7f0dd7c1c077579dd874599ba08fa8e17df10fa262d936f8ad5519181"
      },
      "sha256": "37a81341252f331236ff0a260edcc48d57ecae117559f50ebe11876a732abbe8"
    }
  ],
  "proposed_descriptor_revisions": [
    {
      "artifact_type_ref": "cal.artifact-type.evaluation-profile/v2",
      "bytes": 6558,
      "path": "define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-evaluation-profile/artifact.json",
      "sha256": "d5efe99133477dc381e9b1f0d832c5deac8182fc99dffe1730d929774e3139d7"
    },
    {
      "artifact_type_ref": "cal.artifact-type.lifecycle-profile/v2",
      "bytes": 6550,
      "path": "define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-lifecycle-profile/artifact.json",
      "sha256": "08dcff6fad7d41e263682d3dd689eba4805bc3fe2b6c3c49f4cb06a46a7a69bd"
    },
    {
      "artifact_type_ref": "cal.artifact-type.definition/v2",
      "bytes": 7534,
      "path": "define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/carriers/definition-binding-successor/artifact.json",
      "sha256": "43c2190c2dc8bc4126aeab644f9c2f376d985b05b07e4709ac6c30e4e6fa7a83"
    }
  ],
  "proposed_new_registrations": [
    {
      "artifact_type_ref": "cal.artifact-type.evaluation-profile/v2",
      "distinct_validation_purpose": "Carries the exact owner-qualified Definition evaluation rule contract, its selected subject kind, closed required fields, schema/generator/check-contract bindings and honest evidence/effect limits.",
      "schema_path": "define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/profile-carriers.schema.json",
      "schema_selector": "#/$defs/evaluationProfile",
      "schema_sha256": "533d6487edd40a3006e9deb73c205ad9ae0f87562f665d9d995ca8cdc5d72d16",
      "semantic_definition_refs": [
        "cal.definition.definition-evaluation-profile@1.0.0-candidate.3"
      ],
      "semantic_kind": "evaluation-profile"
    },
    {
      "artifact_type_ref": "cal.artifact-type.lifecycle-profile/v2",
      "distinct_validation_purpose": "Carries the exact owner-qualified Definition lifecycle rule contract, its selected subject kind, closed required fields, schema/generator/check-contract bindings and honest evidence/effect limits.",
      "schema_path": "define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/profile-carriers.schema.json",
      "schema_selector": "#/$defs/lifecycleProfile",
      "schema_sha256": "533d6487edd40a3006e9deb73c205ad9ae0f87562f665d9d995ca8cdc5d72d16",
      "semantic_definition_refs": [
        "cal.definition.definition-lifecycle-profile@1.0.0-candidate.3"
      ],
      "semantic_kind": "lifecycle-profile"
    }
  ],
  "schema_version": "cal.define-profile-carrier-registration-delta/v1",
  "status": "candidate-unadmitted",
  "supersedes_for_this_review_only": {
    "bytes": 4528,
    "path": "define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/registration-delta.json",
    "sha256": "259dcb17ac386d5f0aab5b3cda9ecc087b81c21d695b9359e5c36de74612f6b8"
  }
}
```

## Schemas and generators

- [authority/artifact-types/definition/v1/schema.json](../../../../../../../authority/artifact-types/definition/v1/schema.json) · SHA256 `c39a2c6fe7bdc2cd306152c1b8c4c9dc045d784e44e35d9d9da4e1517bd03adf`
- [authority/artifact-types/definition/v2/schema.json](../../../../../../../authority/artifact-types/definition/v2/schema.json) · SHA256 `269591e7f0dd7c1c077579dd874599ba08fa8e17df10fa262d936f8ad5519181`
- [authority/artifact-types/definition/v1/generator.py](../../../../../../../authority/artifact-types/definition/v1/generator.py) · SHA256 `1bac2e064c11eb4b5e945172a21fe6e1635bc48023269fba6dbbdb11d585167c`
- [authority/artifact-types/definition/v2/generator.py](../../../../../../../authority/artifact-types/definition/v2/generator.py) · SHA256 `b3dc43b827a3b509e6afb90336227b2bfedb0854b5bfbda50c053782ea883e8d`
- [define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/profile-carriers.schema.json](../../../steps/04-definition-v2-profiles/profile-carriers.schema.json) · SHA256 `533d6487edd40a3006e9deb73c205ad9ae0f87562f665d9d995ca8cdc5d72d16`
- [define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/generator.py](../../../steps/04-definition-v2-profiles/generator.py) · SHA256 `d7cf8ee7f1248a9ffb16cf1719f52954e7ea57d9da2f12a792444939bca701ab`
- [authority/foundation/v1/schema.json](../../../../../../../authority/foundation/v1/schema.json) · SHA256 `b09e0dbac01d29e7877b7131cf931334e89a87b9defa24e60a1a0bec59c100f9`
- [authority/foundation/v1/render.py](../../../../../../../authority/foundation/v1/render.py) · SHA256 `ae0f0561fd272121382ae8e077908f735aa31a9686bb2f87057015a5b91b4ac2`

## Registered assurance limits

| ID | Title | Claim ceiling | Future work |
| --- | --- | --- | --- |
| L01 | Pack case universe is bounded | Four declared concepts and the enumerated handling/payload flags; arbitrary concept universes and payload meanings are not exhaustively checked. | Specify variable-size Pack properties, malformed input classes and payload content obligations; select property-based or symbolic coverage with explicit bounds. |
| L02 | Define semantic conditions are interpreted requirements | The 64 outcome cases check interpreted lineage/coverage/source/reviewability conditions, not an actual extractor of those facts from arbitrary input/output. | Bind each condition to exact X/P fields and evidence; define attributable revision checks and negative specimens for silent intent or concept changes. |
| L03 | Full natural-language equivalence is not established | Source correspondence and scoped human acceptance do not prove equivalence of all natural-language statements and all mechanized axioms. | Inventory unmatched clauses and assumptions; choose a decidable formal fragment and exact source-to-formal obligations for owner review. |
| L04 | No mechanized theorem or whole-repository consistency claim | Finite witnesses and reference screens cover selected frames and pairs; source-screened neighboring meanings are not universally formalized. | Select additional warranted comparisons and formalization boundaries; use an appropriate proof/checking backend if a stronger claim is needed. |
| L05 | Source capture and route labels have separate ceilings | Exact source capture does not establish truth, later currentness, actual human credentials, Role Assignment or action permission. | Specify current-use standing assessment and reuse existing owner/review interfaces for independent scope and authority evidence. |
| L06 | Declared concept coverage is not exhaustive discovery | Define accounts for the selected required concept set; unknown requirements and unselected inputs can remain undiscovered. | Define discovery/review heuristics and explicit re-scoping rules; document the selected corpus, exclusions and revision lineage. |
| L07 | Actual Define CLI/provider conformance remains E05 work | The existing saved evidence does not execute or qualify the strict M1 provider/exporter as a complete Lab capability. | Implement the strict preparation boundary, exact result export and governed Context/Ontology/review bindings, then qualify them in a separately authorized verification step. |
| L08 | Interrupted-run, temporal and storage recovery guarantees are unproved | The independent interruption flag model does not establish real persistence, recovery, infinite trace correctness or crash behavior. | Specify saved-result integrity, failure boundaries, lineage and interruption semantics; design concrete recovery scenarios within a declared trace bound. |
| L09 | Unknown/private/external consumers are outside the captured inventory | Current impact evidence is scoped to the selected repository records; universal downstream compatibility is not established. | Maintain explicit source/evidence/subject classifications and discover additional consumers only within authorized scope. |
| L10 | Final cohort and actual compatible adopted standing remain outstanding | Partial conversational fidelity acceptance is not a full phase PASS, owner admission, type/profile adoption or confirmed application. | Finish the remaining sequential reviews, then prepare prerequisite-ordered exact owner material and actual effect evidence only when authorized. |
| L11 | Foundational completeness and compatibility are conditionally interpreted | Completeness conditions and the 96-case carrier model do not prove every real package complete or universally compatible. Criterion outcomes, artifact completeness and authority remain distinct. | Bind completeness predicates to exact owner/source/consumer/registry/index/drift evidence and capture explicit compatibility dispositions for each selected carrier and consumer. |
| L12 | Evaluation rule evidence covers one fixed configuration | The saved 3^14 aggregation and 72 eligibility-guard cases cover the pinned 14-check contract; arbitrary profiles, empty readiness sets and runtime execution are outside the demonstrated claim. | Specify supported profile/check-set configurations and phase validation; preserve the nonempty pinned pre-decision set and pending-selection-only eligibility guard. |
| L13 | Evaluation conditions are necessary, not sufficient conformance proof | ConformingEvaluation implies exact binding, a full result map and preserved causal blockers. The converse is not asserted; shape validity and populated outcomes do not prove evidence adequacy, owner authority or execution. | Map each declared check and blocker to its exact evidence requirements; separately qualify evaluator behavior on mismatched bindings, missing checks, unsupported claims and causal dependencies. |
| L14 | Changed input epochs require scoped re-evaluation | Changed subject/profile/source/evidence epochs invalidate affected evidence; the current correspondence does not establish automatic invalidation, cache correctness or complete temporal history. | Define affected-check dependency selection and revision lineage; qualify stale-evidence handling and preserve old records under their original epochs. |
| L15 | Lifecycle evidence covers finite pair/flag cases, not temporal traces | The saved 576 state-pair/flag cases and 16 admission-support cases cover the pinned six-state profile with abstract exact-binding/gate/record/effect flags; arbitrary lifecycle contracts and infinite traces are unproved. | Define the supported transition/history trace scope and evidence interpretation; select bounded trace, property or theorem checks for warranted stronger claims. |
| L16 | Passing a gate does not establish an actual transition or applied effect | PermittedBy binds the exact profile/subject/inputs, directed pair and PASS gate; actual recording, owner authenticity and confirmed application require independent evidence rather than interpreted flags. | Reuse the existing review/owner/application interfaces to bind transition records, Decision scope and effect receipts; qualify mismatched binding and incomplete-effect scenarios. |
| L17 | Supersession and withdrawal application/history are not runtime-qualified | The profile requires exact successor or withdrawal decisions, coherent current lookup and preserved predecessor history; it does not prove atomic publication, crash/concurrency recovery, or immutable persistence. | Specify the application transaction and replay/recovery behavior for admitted successor, current withdrawal and terminal lookup; preserve historical epochs and explicit consumer dispositions. |

These 17 limits remain open. Their original register is preserved; later preparation acceptances do not retroactively rewrite its historic wording.

## All 79 amended work items

[Original exact planning source](../../../../../../proposals/0005-amended-integration-plan/work-items.json)

The complete planning item declarations follow. They retain historic status labels. Current semantic preparation is separately evidenced; this collection does not automatically mark tasks executed.

```json
[
  {
    "work_id": "G01.01",
    "gap_id": "G01",
    "title": "Freeze the current semantic and contract inputs",
    "status": "planned-not-executed",
    "depends_on": [],
    "planned_outputs": [
      "review/source-selection.json"
    ],
    "actions": [
      "Resolve live current Definition lookup and carrier overlays, not labels inside historical candidate files.",
      "Bind upstream selectors, existing Lab meanings, candidate drafts, schemas and generators to exact hashes.",
      "Record changes from planning snapshot 0002; its integration-doc hash predates the link added during that turn."
    ],
    "completion_criterion": "Every load-bearing input resolves and has a recorded current/historical/candidate posture.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G01.02",
    "gap_id": "G01",
    "title": "Finish the Definition Pack meaning",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.01"
    ],
    "planned_outputs": [
      "review/definitions/definition-pack/definition.json",
      "review/definitions/definition-pack/DEFINITION.md"
    ],
    "actions": [
      "Align formal, plain and domain voices. Declare total single-valued dispositions, matching payloads, explicit gaps and frozen revision lineage.",
      "State that a pack can yield zero or many Definitions and cannot authorize execution.",
      "Keep the semantic tuple independent of a particular CLI wire format."
    ],
    "completion_criterion": "The exact candidate answers what the bundle preserves, with no scope expansion between voices.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G01.03",
    "gap_id": "G01",
    "title": "Finish the CyberAlchemy Define meaning",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.02"
    ],
    "planned_outputs": [
      "review/definitions/cyberalchemy-define/definition.json",
      "review/definitions/cyberalchemy-define/DEFINITION.md"
    ],
    "actions": [
      "State the enabled outcome and bounded concept coverage, goal/intent traceability and unresolved outcomes.",
      "Distinguish capability meaning, Product Capability instance, preparation Method, CLI and agent realization.",
      "Preserve ephemeral machine agents and durable Project State/view boundaries."
    ],
    "completion_criterion": "The exact candidate specifies Define without claiming exhaustive discovery, admission or consumer success.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G01.04",
    "gap_id": "G01",
    "title": "Resolve sources and candidate evidence",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.02",
      "G01.03"
    ],
    "planned_outputs": [
      "review/source-disposition.json",
      "review/source-admission-targets.json"
    ],
    "actions": [
      "Use admitted Lab meanings as governing premises for their exact scopes.",
      "Preserve upstream proposal bytes as hashed candidate lineage/evidence; they are not governing source_refs in the revised drafts.",
      "If a future target requires an upstream selector to govern, add a separate exact source-admission target and review; no whole-package admission is implied."
    ],
    "completion_criterion": "Every source has a clear permitted use; required source admission is prepared before semantic promotion.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G01.05",
    "gap_id": "G01",
    "title": "Prepare distinction, consistency and fidelity obligations",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.02",
      "G01.03",
      "G01.04"
    ],
    "planned_outputs": [
      "review/semantic-obligations.json",
      "review/fidelity-review.md"
    ],
    "actions": [
      "Compare Pack against Definition, Review, Decision Bundle and Generated Output; compare Define against Product Capability, Method and its realizations.",
      "Formalize exact interpreted clauses, variables, assumptions, counterexamples and coverage.",
      "Bind any available formal-assurance candidate by exact version; record unsupported temporal, deontic or empirical clauses without a global PASS."
    ],
    "completion_criterion": "Owner review can see which distinctions are supported, which obligations remain open and what no finite check proves.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G01.06",
    "gap_id": "G01",
    "title": "Prepare semantic registry, index and drift postimages",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.04",
      "G01.05",
      "G03.04"
    ],
    "planned_outputs": [
      "review/registry-postimage.json",
      "review/DEFINITIONS-INDEX.md",
      "review/drift-audit-postimage.json"
    ],
    "actions": [
      "Stage exact new identities and versions with generated Markdown and source digests.",
      "Include a foundational Definition successor only if the compatibility review requires it.",
      "Generate lookup/index and audit consequences without changing the live registry or pretending a future decision already exists.",
      "Include the selected foundational Definition successor alongside the two new meanings in the proposed semantic cohort."
    ],
    "completion_criterion": "Postimages have unique exact identities, reproducible projections and explicit pending decision bindings.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G01.07",
    "gap_id": "G01",
    "title": "Close the semantic review package",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.06",
      "G03.06",
      "R01.01",
      "R10.01"
    ],
    "planned_outputs": [
      "review/semantic-review-package.json",
      "review/semantic-review.md"
    ],
    "actions": [
      "Show final statements, examples, source dispositions, all voices, finite assurance limits and exact proposed effects.",
      "Bind owner roles/scopes and leave accept, revise, defer or reject outcomes undecided.",
      "Keep semantic admission distinct from mapping/profile adoption and later runtime adoption."
    ],
    "completion_criterion": "The human can review exact materials; no implementation or admission is claimed by package preparation.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01",
    "requires_outcomes": [
      "required_semantic_interpretation_and_fidelity_obligations_accounted_for",
      "required_consumer_impact_dispositions_closed"
    ]
  },
  {
    "work_id": "G02.01",
    "gap_id": "G02",
    "title": "Resolve the existing Lab Product and Thesis",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.01"
    ],
    "planned_outputs": [
      "product/product-thesis-selection.json"
    ],
    "actions": [
      "Inspect admitted overlays for product:cyberalchemy-lab and its governed-work Thesis.",
      "Select the exact intended Thesis outcomes and exclusions; retain their source standing.",
      "Reuse this Product identity unless owner review establishes a material anchor change."
    ],
    "completion_criterion": "The capability has exactly one resolvable Product and exact Thesis basis.",
    "review_roles": [
      "Applicable Lab Product owner: resolve exact assignment; foundation route is repository-owner review",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G02.02",
    "gap_id": "G02",
    "title": "Resolve Product, semantic and implementation ownership",
    "status": "planned-not-executed",
    "depends_on": [
      "G02.01"
    ],
    "planned_outputs": [
      "product/owner-selection.json"
    ],
    "actions": [
      "Resolve the Lab Product route and exact applicable role/principal assignments; do not reuse the Craft Product assignment outside its scope.",
      "Keep Product ownership, Definition ownership, mechanics and runtime adoption scopes separate.",
      "Prepare missing assignments or explicit scope bindings only when existing admitted authority does not cover the target."
    ],
    "completion_criterion": "Each proposed effect has its actual authority route; a routing hint never appoints an owner.",
    "review_roles": [
      "Applicable Lab Product owner: resolve exact assignment; foundation route is repository-owner review",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G02.03",
    "gap_id": "G02",
    "title": "Prepare the Define Product Capability candidate",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.03",
      "G02.01",
      "G02.02"
    ],
    "planned_outputs": [
      "product/define-capability.json"
    ],
    "actions": [
      "Use the current Product Capability carrier: Product/Thesis, outcome, participants, consumers, scope, exclusions, context policies, owner routes and acceptance conditions.",
      "Compare the existing Governed Knowledge Lifecycle capability and preserve its identity and scope.",
      "Bind future pack/preparation output contracts as explicit pending references until they exist."
    ],
    "completion_criterion": "A distinct candidate records the Define outcome without selecting a technology or claiming adoption.",
    "review_roles": [
      "Applicable Lab Product owner: resolve exact assignment; foundation route is repository-owner review",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G02.04",
    "gap_id": "G02",
    "title": "Bind named consumers and acceptance conditions",
    "status": "planned-not-executed",
    "depends_on": [
      "G02.03"
    ],
    "planned_outputs": [
      "product/acceptance-profile.json"
    ],
    "actions": [
      "Declare incident-investigator review use and at least one different bounded consumer use.",
      "State what semantic coverage, visible gaps and ergonomic continuity must enable.",
      "Separate inspect/review eligibility, consumer suitability and permission to execute."
    ],
    "completion_criterion": "Acceptance can be evaluated for named uses without treating an open concept as an invented answer.",
    "review_roles": [
      "Applicable Lab Product owner: resolve exact assignment; foundation route is repository-owner review",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G02.05",
    "gap_id": "G02",
    "title": "Freeze the full candidate and its CLI realization binding",
    "status": "planned-not-executed",
    "depends_on": [
      "G02.03",
      "G04.01",
      "G05.06",
      "G09.02",
      "G07.08",
      "G08.06",
      "G09.06"
    ],
    "planned_outputs": [
      "product/cli-implementation.json",
      "product/capability-realization-binding.json",
      "implementation/full-source-selection.json",
      "implementation/full-runtime-manifest.json"
    ],
    "actions": [
      "Bind exact candidate Implementation revision, runtime manifest, roles, contract versions, compatibility, limitations and succession.",
      "Use the current Capability Realization Binding/v2 carrier; candidate conformance and adoption references remain explicit.",
      "Do not mark adopted until relevant evidence and a separate adoption decision exist.",
      "Freeze the complete exporter/review/epoch/state candidate separately from the early preview; bind all provider and output-recipe inputs."
    ],
    "completion_criterion": "The exact full candidate manifest and Capability Realization Binding exist before complete prototype verification.",
    "review_roles": [
      "Applicable Lab Product owner: resolve exact assignment; foundation route is repository-owner review",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02",
    "requires_outcomes": [
      "full_manifest_and_exact_realization_binding_ready"
    ]
  },
  {
    "work_id": "G02.06",
    "gap_id": "G02",
    "title": "Close the Product review inputs",
    "status": "planned-not-executed",
    "depends_on": [
      "G02.04",
      "G02.05",
      "G10.02"
    ],
    "planned_outputs": [
      "product/product-review-package.json"
    ],
    "actions": [
      "Present exact product candidate and current product-test evidence.",
      "Apply the admitted prototype-first construction invariant: product approval precedes a separate authority request for implementation-bearing construction.",
      "Name any accepted residue and stop criteria."
    ],
    "completion_criterion": "A concrete Product candidate is eligible for its owner approval; approval grants no operational authority.",
    "review_roles": [
      "Applicable Lab Product owner: resolve exact assignment; foundation route is repository-owner review",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G03.01",
    "gap_id": "G03",
    "title": "Resolve the foundational v1/v2 discrepancy",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.01"
    ],
    "planned_outputs": [
      "profiles/compatibility-review.json"
    ],
    "actions": [
      "Compare the admitted foundational Definition/v1-specific testable condition with the admitted v2 carrier.",
      "Select an explicit foundational Definition successor candidate that requires its exact applicable carrier/profile binding; preserve the predecessor as admitted history."
    ],
    "completion_criterion": "The exact representation/testable-condition change and affected consumer scope are declared for review.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G03.02",
    "gap_id": "G03",
    "title": "Prepare Definition/v2 evaluation profile",
    "status": "planned-not-executed",
    "depends_on": [
      "G03.01",
      "G01.05"
    ],
    "planned_outputs": [
      "profiles/definition-v2-evaluation.json"
    ],
    "actions": [
      "Bind the exact current v2 schema/generator, three voices, sources, semantic owner/scope, registry/index/drift and typed endpoints.",
      "Declare semantic fidelity/non-collapse obligations and the ceiling of finite evidence.",
      "Separate authored-candidate validation from promotion readiness; missing admitted premises or owner scope block promotion."
    ],
    "completion_criterion": "Every declared check has exact inputs, outcomes and scope; representation PASS cannot stand in for semantic approval.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G03.03",
    "gap_id": "G03",
    "title": "Prepare Definition/v2 lifecycle profile",
    "status": "planned-not-executed",
    "depends_on": [
      "G03.02"
    ],
    "planned_outputs": [
      "profiles/definition-v2-lifecycle.json"
    ],
    "actions": [
      "Preserve authored, validated, reviewed, admitted, superseded and withdrawn distinctions.",
      "Define pre-decision eligibility when only exact owner selection remains pending.",
      "Keep the final exact admission-decision check separate so review does not depend on its own completed admission."
    ],
    "completion_criterion": "No lifecycle transition fabricates authority or creates a circular approval prerequisite.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G03.04",
    "gap_id": "G03",
    "title": "Prepare the foundational Definition successor",
    "status": "planned-not-executed",
    "depends_on": [
      "G03.01",
      "G03.02",
      "G03.03"
    ],
    "planned_outputs": [
      "profiles/foundational-definition-successor.json",
      "profiles/foundational-definition-impact.json"
    ],
    "actions": [
      "Prepare cal.definition.definition@1.0.0-candidate.2 using Definition/v2 and explicitly revise the v1-only testable condition.",
      "Preserve the existing normative meaning, identity and exact predecessor evidence; route its criterion/carrier changes through independent semantic/mechanics review.",
      "Require the C10 impact dispositions before admitting this successor."
    ],
    "completion_criterion": "The foundational successor is complete as a candidate and its dependent bindings have explicit dispositions; no live Definition is replaced.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G03.05",
    "gap_id": "G03",
    "title": "Bind profile generators and deterministic receipts",
    "status": "planned-not-executed",
    "depends_on": [
      "G03.02",
      "G03.03",
      "G03.04"
    ],
    "planned_outputs": [
      "profiles/projection-binding.json",
      "profiles/evaluation-result-contract.json"
    ],
    "actions": [
      "Select existing compatible profile carrier/generator or prepare exact required successors.",
      "Specify reproducible profile projections and outcome aggregation, including pending-decision handling.",
      "Carry amendment, compatibility and enforcement witness obligations under Schema Evolution."
    ],
    "completion_criterion": "Profile mechanics and eligibility can be replayed against exact candidate bytes.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G03.06",
    "gap_id": "G03",
    "title": "Prepare independent profile decision targets",
    "status": "planned-not-executed",
    "depends_on": [
      "G03.05"
    ],
    "planned_outputs": [
      "profiles/review-targets.json"
    ],
    "actions": [
      "Separate mechanics/generator determination, evidence profile adoption and semantic/lifecycle determination.",
      "Preserve independent cores even when one principal holds several roles.",
      "Include profiles and any foundational revision in the exact review checkpoint before later application."
    ],
    "completion_criterion": "All profile decisions have explicit subjects, effects, owners and invalidation conditions.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C01"
  },
  {
    "work_id": "G04.01",
    "gap_id": "G04",
    "title": "Define the closed pack wire contract",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.02",
      "G01.03"
    ],
    "planned_outputs": [
      "contracts/definition-pack.schema.json",
      "contracts/compatibility-amendment.json"
    ],
    "actions": [
      "Close the new Lab pack candidate v2 and preparation-envelope schemas with named use, lineage, standing, gaps, dispositions and scoped readiness.",
      "Implement the explicitly recorded adapter from preserved native legacy pack v1 plus supplementary input; reject unsupported values/unknown fields.",
      "Retain legacy run/chat output and compiler semantics; make v2 compile unsupported as specified by C09."
    ],
    "completion_criterion": "A new contract cannot silently change the old v1 protocol or claim admission from schema validity.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C09"
  },
  {
    "work_id": "G04.02",
    "gap_id": "G04",
    "title": "Define reference resolution and posture records",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01"
    ],
    "planned_outputs": [
      "contracts/reference-standing.schema.json"
    ],
    "actions": [
      "Record exact identity/version/digest/selector where available and admitted/current/historical/candidate/unresolved standing.",
      "Bind source resolution through actual Lab interfaces and exposed source-admission evidence.",
      "Separate provenance from authorization and resolve owner routes versus assignments distinctly."
    ],
    "completion_criterion": "Missing or stale references are visible scoped obligations, not opaque nonempty strings treated as authority.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C09"
  },
  {
    "work_id": "G04.03",
    "gap_id": "G04",
    "title": "Define use-specific readiness",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01",
      "G04.02",
      "G02.04"
    ],
    "planned_outputs": [
      "contracts/readiness-profile.json"
    ],
    "actions": [
      "Separate pack well-formedness, review readiness, preparation completeness, promotion eligibility and named-consumer readiness.",
      "Map each open issue to the use it blocks; allow review of unresolved meaning.",
      "Name the responsible owner and refresh/invalidation rule for each gate."
    ],
    "completion_criterion": "An open question can be reviewed without automatically authorizing or blocking every unrelated use.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C09"
  },
  {
    "work_id": "G04.04",
    "gap_id": "G04",
    "title": "Define supplemental preparation input",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01",
      "G03.02"
    ],
    "planned_outputs": [
      "contracts/preparation-input.schema.json"
    ],
    "actions": [
      "Require explicit stable Definition identity/version, authority scope, semantic owner, domain voice, formalization/notation, boundaries, exact sources, consumers and index/drift routes.",
      "Bind each supplemental record to an exact pack/concept/revision and selected contract.",
      "Reject omitted mandatory values and untraceable semantic changes; never infer a Definition owner from owner_route."
    ],
    "completion_criterion": "Every value absent from the pack is supplied explicitly or reported as a blocking obligation.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C09"
  },
  {
    "work_id": "G04.05",
    "gap_id": "G04",
    "title": "Define revisioned session and handling state",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01",
      "G04.02"
    ],
    "planned_outputs": [
      "contracts/session-state.schema.json",
      "contracts/handled-record.schema.json"
    ],
    "actions": [
      "Retain explicit responses, revisions, idempotency, source state, prior/current dispositions and correction history.",
      "Separate saved workflow state from an ephemeral machine Agent Session and private agent memory.",
      "If using Ledger, specify entry schema, ordering, integrity, correction/reconciliation and retention; otherwise keep these as bounded protocol state."
    ],
    "completion_criterion": "Resume preserves actual user answers and gaps without creating a second canonical Definition registry.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C09"
  },
  {
    "work_id": "G04.06",
    "gap_id": "G04",
    "title": "Select a compatible preparation Method representation",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.03",
      "G04.04"
    ],
    "planned_outputs": [
      "contracts/preparation-method.json",
      "contracts/method-carrier-selection.json"
    ],
    "actions": [
      "Express the preparation Method as a closed candidate contract under admitted CAV2-D32.",
      "Do not claim that specialized Craft Method Binding/v1 carries this method; no new Method Artifact Type is required for M1.",
      "Any later need for independently admitted Method instances must present its own carrier requirement and owner target."
    ],
    "completion_criterion": "The generic Method meaning is reused without falsely claiming its existing specialized carrier fits every use.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C09"
  },
  {
    "work_id": "G04.07",
    "gap_id": "G04",
    "title": "Close contract review and amendment targets",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.03",
      "G04.04",
      "G04.05",
      "G04.06",
      "G06.06"
    ],
    "planned_outputs": [
      "contracts/contract-review-package.json"
    ],
    "actions": [
      "Bind exact versioned schemas, protocol compatibility, affected consumers and rollback routes.",
      "Specify mapping/output/review-package protocols as candidate protocols unless separately registered Artifact Types are required.",
      "Leave independently admitted pack instances and new global kinds outside this first integration."
    ],
    "completion_criterion": "Contract changes have reviewable scope and witnesses without accidental Artifact Type or ontology registration.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C09"
  },
  {
    "work_id": "G05.01",
    "gap_id": "G05",
    "title": "Map semantic kernels and host adapters",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.04",
      "G04.06",
      "G06.06"
    ],
    "planned_outputs": [
      "implementation/construction-map.json"
    ],
    "actions": [
      "Identify deterministic mapping kernels, protocol validation, reference lookup, filesystem publishing and host UI separately.",
      "Reuse selected compiled Define services and Lab Craft pure Calculation where applicable; keep Operation state changing.",
      "Record construction stages, prototype evidence and typed residue for any unformalized host adapter."
    ],
    "completion_criterion": "Every new implementation piece has a specification/binding route and a bounded claim ceiling.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C12"
  },
  {
    "work_id": "G05.02",
    "gap_id": "G05",
    "title": "Implement the candidate prepare entry",
    "status": "planned-not-executed",
    "depends_on": [
      "G05.01"
    ],
    "planned_outputs": [
      "candidate-cli/prepare-entry.mjs"
    ],
    "actions": [
      "Add a proposed prepare command using exact pack and explicit supplement files; choose target directory and optional provisioned store explicitly.",
      "Use existing context/freshness/inspection interfaces and return readable blockers.",
      "Preparation must not call authorize/apply or create operator keys."
    ],
    "completion_criterion": "The command can prepare review material without mutating admitted state.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C12"
  },
  {
    "work_id": "G05.03",
    "gap_id": "G05",
    "title": "Implement complete Definition/v2 emission",
    "status": "planned-not-executed",
    "depends_on": [
      "G05.02",
      "G03.05",
      "G04.04",
      "G06.06"
    ],
    "planned_outputs": [
      "candidate-cli/definition-exporter.mjs"
    ],
    "actions": [
      "Build each selected complete Definition using the bound v2 schema and generator.",
      "Validate all voices, sources, consumers and exact scope; emit a clear partial preparation report when values are missing.",
      "Never mark a skeleton as a complete admission candidate."
    ],
    "completion_criterion": "Each emitted complete record satisfies the exact carrier; incomplete targets remain explicit unresolved obligations.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C12"
  },
  {
    "work_id": "G05.04",
    "gap_id": "G05",
    "title": "Implement field lineage and semantic-change visibility",
    "status": "planned-not-executed",
    "depends_on": [
      "G05.03"
    ],
    "planned_outputs": [
      "candidate-cli/field-lineage.mjs",
      "example/preparation-field-lineage.json"
    ],
    "actions": [
      "Trace each output field to a pack field, supplementary input, exact current source, or explicitly proposed semantic revision.",
      "Show renamed terms, changed normative wording, new formal expressions and parent relationships for owner review.",
      "Bind pack/supplement/contract digests so reviewers can reconstruct the transformation."
    ],
    "completion_criterion": "No materially new meaning is hidden inside automatic formatting or normalization.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C12"
  },
  {
    "work_id": "G05.05",
    "gap_id": "G05",
    "title": "Implement safe package publication",
    "status": "planned-not-executed",
    "depends_on": [
      "G05.04"
    ],
    "planned_outputs": [
      "candidate-cli/preparation-publisher.mjs"
    ],
    "actions": [
      "Reuse no-overwrite candidate publishing and atomic staged-directory publication.",
      "Handle existing files, directories, symlinks and races; report unsupported guarantees visibly.",
      "Include records, generated Markdown, lineage and blockers as one exact preparation package."
    ],
    "completion_criterion": "Failure cannot replace existing work or leave a partial output presented as completed.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C12"
  },
  {
    "work_id": "G05.06",
    "gap_id": "G05",
    "title": "Freeze the read-only preparation preview",
    "status": "planned-not-executed",
    "depends_on": [
      "G05.05",
      "R01.01",
      "R03.01",
      "R06.01",
      "R09.01",
      "R10.01",
      "R11.01",
      "R12.01"
    ],
    "planned_outputs": [
      "implementation/preview-source-selection.json",
      "implementation/preview-runtime-manifest.json",
      "implementation/preview-obligations.json"
    ],
    "actions": [
      "Freeze the candidate exporter, strict current-epoch source provider, pack adapter, v2 checks and safe package publisher.",
      "Exclude signing, store provisioning, current-pointer/registry mutation and automatic admission from this preview.",
      "Show complete candidates and blockers with exact lineage; preserve immutable imported and admitted runtime bytes."
    ],
    "completion_criterion": "A separately bounded M1 preview is reproducible and reviewable without the full governance/application implementation.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C12",
    "requires_outcomes": [
      "preview_manifest_exact",
      "no_authorize_apply_or_registry_effect"
    ]
  },
  {
    "work_id": "G06.01",
    "gap_id": "G06",
    "title": "Map exact current reuse",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01",
      "G04.02"
    ],
    "planned_outputs": [
      "mapping/reuse-policy.json"
    ],
    "actions": [
      "Resolve exact selected current Lab Definition versions and their scope/source standing.",
      "Emit a reference/application binding, not a duplicate Definition admission target.",
      "Preserve historical references for traceability without labeling them current reuse."
    ],
    "completion_criterion": "Reusing an existing admitted meaning grants no new semantic or action authority.",
    "review_roles": [
      "role:definition-owner",
      "Applicable next-use owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C10"
  },
  {
    "work_id": "G06.02",
    "gap_id": "G06",
    "title": "Map unchanged-meaning parameter specialization",
    "status": "planned-not-executed",
    "depends_on": [
      "G06.01"
    ],
    "planned_outputs": [
      "mapping/application-binding-policy.json"
    ],
    "actions": [
      "Identify parameters already permitted by the governing meaning, such as fixed snapshot, account and filters.",
      "Prepare an exact application binding with context/evidence, retaining the parent meaning.",
      "Do not create a new global specializes relation or overwrite the parent."
    ],
    "completion_criterion": "Narrowing an allowed application is distinguishable from changing normative meaning.",
    "review_roles": [
      "role:definition-owner",
      "Applicable next-use owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C10"
  },
  {
    "work_id": "G06.03",
    "gap_id": "G06",
    "title": "Map new meanings and semantic revisions",
    "status": "planned-not-executed",
    "depends_on": [
      "G06.02",
      "G04.04"
    ],
    "planned_outputs": [
      "mapping/semantic-change-policy.json"
    ],
    "actions": [
      "Require an explicit owner-review classification when normative meaning changes: new identity or successor of the same identity.",
      "Bind exact current predecessor for revision and preserve history, applicability and affected consumers.",
      "Treat automated suggestions as candidate analysis; do not infer stable identity or ownership from concept_id."
    ],
    "completion_criterion": "Changed meaning follows an explicit version/identity route and complete Definition preparation.",
    "review_roles": [
      "role:definition-owner",
      "Applicable next-use owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C10"
  },
  {
    "work_id": "G06.04",
    "gap_id": "G06",
    "title": "Map new proposals and unresolved outcomes",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.03",
      "G04.04"
    ],
    "planned_outputs": [
      "mapping/propose-open-policy.json"
    ],
    "actions": [
      "Map propose to a complete candidate or explicit missing preparation obligations.",
      "Map open to an unresolved question, owner route, affected use, source conflict and next action.",
      "Preserve omitted answers and non-answers without treating them as user-confirmed meanings."
    ],
    "completion_criterion": "Unresolved concepts remain visible and can never become invented Definitions.",
    "review_roles": [
      "role:definition-owner",
      "Applicable next-use owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C10"
  },
  {
    "work_id": "G06.05",
    "gap_id": "G06",
    "title": "Map partial selection and dependency closure",
    "status": "planned-not-executed",
    "depends_on": [
      "G06.01",
      "G06.03",
      "G06.04"
    ],
    "planned_outputs": [
      "mapping/selection-closure-policy.json"
    ],
    "actions": [
      "Permit explicit selection of zero/one/many prepared targets.",
      "Check selected targets dependencies and preserve excluded/rejected/open concept standing.",
      "Do not mark the entire pack resolved because one Definition is selected or admitted."
    ],
    "completion_criterion": "Every selected effect is closed over its required dependencies; unselected members receive no inferred authority.",
    "review_roles": [
      "role:definition-owner",
      "Applicable next-use owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C10"
  },
  {
    "work_id": "G06.06",
    "gap_id": "G06",
    "title": "Prepare the complete disposition matrix",
    "status": "planned-not-executed",
    "depends_on": [
      "G06.02",
      "G06.03",
      "G06.04",
      "G06.05"
    ],
    "planned_outputs": [
      "mapping/disposition-matrix.json",
      "mapping/incident-example.json"
    ],
    "actions": [
      "Map all four dispositions and both specialization forms to exact output kinds, required inputs, owner gates and failure behavior.",
      "Extend the INC-1042 example with reuse, proposed identifier coverage and an open account-exclusivity question.",
      "Define expected outcomes as future fixture obligations, not production observations."
    ],
    "completion_criterion": "One matrix covers all routes and supplies explicit examples for implementation and review.",
    "review_roles": [
      "role:definition-owner",
      "Applicable next-use owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C10"
  },
  {
    "work_id": "G07.01",
    "gap_id": "G07",
    "title": "Specify Definition-specific authority evidence",
    "status": "planned-not-executed",
    "depends_on": [
      "G02.02",
      "G03.06"
    ],
    "planned_outputs": [
      "authorization/semantic-authority-contract.json"
    ],
    "actions": [
      "Bind exact target, semantic-owner role, accountable principal, assignment evidence, authority scope, permitted effect and effective period.",
      "Resolve free-text owner assignment scopes through an explicit reviewed policy mapping; do not infer a wildcard grant.",
      "Retain provisioned operator authority separately.",
      "Repository semantic promotion uses C02 human-owner evidence; local operator identity cannot establish that event."
    ],
    "completion_criterion": "Every semantic effect has explicit machine-checkable evidence or a visible unresolved authorization gap.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G07.02",
    "gap_id": "G07",
    "title": "Resolve owner-assignment sources and lifecycle",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.01",
      "G04.02"
    ],
    "planned_outputs": [
      "authorization/assignment-source-selection.json"
    ],
    "actions": [
      "Select exact admitted assignments and scope determinations from their actual registries/admission records.",
      "Ensure those sources are available to the reader; a matching owner label is insufficient.",
      "Handle current expiry/revocation for new effects while preserving historical authorization evidence for replay."
    ],
    "completion_criterion": "New approvals use current applicable standing; historical replay does not fabricate retroactive authority.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G07.03",
    "gap_id": "G07",
    "title": "Enforce nested Definition scope",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.01",
      "G07.02"
    ],
    "planned_outputs": [
      "candidate-runtime/definition-scope-validation.py"
    ],
    "actions": [
      "Check scope.authority_scope_ref against the applicable semantic boundary and exact decision, not only top-level proposal.scope_ref.",
      "Declare any cross-scope relation between the shared Definition boundary and the local operational store boundary explicitly.",
      "Reject unsupported scope mappings and broadened effects.",
      "Reject shared-scope repository effects from a merely provisioned local key; an exact human-owned effect and scope reconciliation are mandatory."
    ],
    "completion_criterion": "A shared-scope Definition cannot be admitted merely because a narrower local operator signed it.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G07.04",
    "gap_id": "G07",
    "title": "Bind an applicable Policy and Challenge Contract",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.01",
      "G02.01"
    ],
    "planned_outputs": [
      "authorization/policy-challenge-selection.json",
      "authorization/policy-successor-if-required.json",
      "authorization/challenge-successor-if-required.json"
    ],
    "actions": [
      "Prepare explicit operational Policy and Challenge Contract successor candidates extending their exact subjects/scopes to this Definition integration.",
      "Bind Definition challenge grounds, evidence, response, role/principal route and unresolved residue; preserve the existing admitted versions.",
      "Include their own owner decisions in the final cohort; a route string does not satisfy the contract."
    ],
    "completion_criterion": "The exact semantic targets have a valid policy/challenge mechanism without silently expanding existing subjects.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G07.05",
    "gap_id": "G07",
    "title": "Validate Definition sources, consumers and typed relations",
    "status": "planned-not-executed",
    "depends_on": [
      "G03.02",
      "G04.02",
      "G06.06"
    ],
    "planned_outputs": [
      "candidate-runtime/definition-reference-validation.py"
    ],
    "actions": [
      "Validate source_refs and primary consumers with admission/currentness standing under the selected evaluation contract.",
      "Inspect typed_relations separately from the generic runtime relation_refs path; enforce allowed carrier roles and exact global endpoint pairs.",
      "Keep provenance pointers and ontology-local projections separate from global relations; missing endpoints require explicit gaps or an extension decision."
    ],
    "completion_criterion": "Schema-only validation cannot admit unresolved semantic sources or undeclared Definition connections.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G07.06",
    "gap_id": "G07",
    "title": "Apply the same checks at all consequential boundaries",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.02",
      "G07.03",
      "G07.04",
      "G07.05"
    ],
    "planned_outputs": [
      "candidate-runtime/authorization-enforcement.py"
    ],
    "actions": [
      "Check semantic authority during preview/preparation, review, authorize and apply immediately before commit.",
      "Bind current HEAD, source/profile/assignment digests and exact targets; reject changes after review.",
      "Replay recorded transactions against their historical authorization basis; verify new effects against current standing."
    ],
    "completion_criterion": "Neither a bypassed CLI nor an old preflight receipt can skip the applicable semantic checks.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G07.07",
    "gap_id": "G07",
    "title": "Prepare compatible decision-core and approval protocols",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.01",
      "G07.06",
      "R02.01",
      "R06.01"
    ],
    "planned_outputs": [
      "authorization/decision-core-contract.json",
      "authorization/approval-contract.json",
      "authorization/protocol-amendment.json"
    ],
    "actions": [
      "Existing cores carry target/category/operation/digest and existing approval carries one operator owner/scope.",
      "Bind semantic role, principal, assignment, evidence/profile digests and applicable effect boundaries explicitly.",
      "Version any closed-protocol changes; do not silently append fields to v1 or treat one key as every owner role."
    ],
    "completion_criterion": "Exact signed/selected decisions cover the necessary semantic authority evidence and retain legacy compatibility boundaries.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G07.08",
    "gap_id": "G07",
    "title": "Preserve independent governance records",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.07"
    ],
    "planned_outputs": [
      "candidate-runtime/governance-record-bindings.py"
    ],
    "actions": [
      "Existing governance templates use one approval owner as owner role and accountable principal for one local boundary.",
      "Generate role/principal/scope bindings from actual member decision evidence; keep Product, semantic, mechanics and repository effects separate.",
      "A single principal may approve several roles only through separately scoped member determinations."
    ],
    "completion_criterion": "Bundling reduces interaction count without collapsing authority boundaries or selected outcomes.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C02"
  },
  {
    "work_id": "G08.01",
    "gap_id": "G08",
    "title": "Specify the preparation and Review package",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.07",
      "G04.07",
      "G07.01"
    ],
    "planned_outputs": [
      "review/preparation-package.schema.json",
      "review/review-profile.json"
    ],
    "actions": [
      "Package exact pack, supplement, candidates, lineage, checks, findings, options and planned effects.",
      "Use Review/v1 within its exact carrier obligations when emitting a Review record; a preview bundle is not automatically a Review or new Artifact Type.",
      "Do not substitute the specialized thirteen-member C10 successor reviewer."
    ],
    "completion_criterion": "A reviewer can understand every target, blocker and consequence without reconstructing the session.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C04"
  },
  {
    "work_id": "G08.02",
    "gap_id": "G08",
    "title": "Build exact runtime proposal targets",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.01",
      "G06.05",
      "G07.07"
    ],
    "planned_outputs": [
      "candidate-cli/review-proposal-adapter.mjs"
    ],
    "actions": [
      "Emit existing or explicitly versioned proposal contracts with category/operation/carrier/record/predecessor/core references.",
      "Resolve exact new admission versus revision/withdrawal behavior and schemas against the proposed closure.",
      "Block unresolved dependencies and wrong current carriers; explicitly selected zero-target packs remain reviewable but do not create empty admission transactions."
    ],
    "completion_criterion": "Each effect points to one immutable target and the correct current carrier.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C04"
  },
  {
    "work_id": "G08.03",
    "gap_id": "G08",
    "title": "Build exact postimages and consequences",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.02",
      "G01.06"
    ],
    "planned_outputs": [
      "review/transaction-postimages.json"
    ],
    "actions": [
      "Generate registry/current lookup/index/drift changes and required Project State/history/receipt consequences.",
      "Bind selected source, policy, challenge and independent decision cores without future authorizations masquerading as evidence.",
      "Keep accepted source posture, definition admission and consumer adoption effects distinct."
    ],
    "completion_criterion": "Review shows all intended mutations and nothing outside the selected target set.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C04"
  },
  {
    "work_id": "G08.04",
    "gap_id": "G08",
    "title": "Integrate the existing structural review interface",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.03",
      "G07.08"
    ],
    "planned_outputs": [
      "candidate-cli/review-bridge.mjs"
    ],
    "actions": [
      "Call Store.review only on an explicitly provisioned store and exact candidate runtime binding.",
      "Present structural preflight, semantic evidence and independent requested decisions separately.",
      "Report local planned consequences and the absence of repository authority until a separate repository route is selected."
    ],
    "completion_criterion": "Review remains non-mutating and never labels structural preflight as semantic-owner approval.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C04"
  },
  {
    "work_id": "G08.05",
    "gap_id": "G08",
    "title": "Specify local and repository application routes",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.04",
      "G09.02"
    ],
    "planned_outputs": [
      "review/application-route-contract.json"
    ],
    "actions": [
      "The Define CLI stays a prepare/inspect/review interface; the first repository application route is a separately authorized attended action under trusted human-owner decision evidence.",
      "Keep local generic transaction effects within the provisioned branch; no local signature implies repository authority.",
      "Constrain the repository writer to this cohort and the C04/C05 commit/recipe protocol."
    ],
    "completion_criterion": "The route and its authority boundary are explicit; a local signature cannot imply repository publication/admission.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C04"
  },
  {
    "work_id": "G08.06",
    "gap_id": "G08",
    "title": "Prepare atomicity, recovery and compatibility",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.05",
      "G09.03",
      "R04.01",
      "R05.01",
      "R08.01"
    ],
    "planned_outputs": [
      "candidate-runtime/transaction-compatibility.py",
      "review/recovery-plan.json"
    ],
    "actions": [
      "Extend exact staged-transaction behavior with new semantic checks and source-profile compatibility.",
      "Declare repository preimages/postimages, receipt/state consequences and recoverable publication boundary.",
      "Specify failure recovery, same-byte idempotency, changed-byte rejection and backward replay without replacing historical approvals."
    ],
    "completion_criterion": "The transaction is a recoverable all-or-nothing effect under its declared scope, with exact rollback residue.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C04"
  },
  {
    "work_id": "G08.07",
    "gap_id": "G08",
    "title": "Define first end-to-end review scenarios",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.06",
      "G06.06",
      "G09.05"
    ],
    "planned_outputs": [
      "verification/incident-review-scenarios.json"
    ],
    "actions": [
      "Describe inspect, prepare, review, revise, partial selection, rejection, authorized local fixture application and repository package preparation.",
      "Use the synthetic incident and exact state/source bindings.",
      "Keep scenario expectations separate from test results and production incident facts."
    ],
    "completion_criterion": "The scenario matrix covers one continuous journey and its failure paths; execution remains a later verification task.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C04"
  },
  {
    "work_id": "G09.01",
    "gap_id": "G09",
    "title": "Extend stale-input rules to preparation and review",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.02",
      "G04.03",
      "G07.02"
    ],
    "planned_outputs": [
      "contracts/preparation-freshness.json"
    ],
    "actions": [
      "Bind pack, supplement, source epoch, HEAD, TTL, current carrier and semantic-owner assignments.",
      "Distinguish expired context evidence retained for history from valid context for a new consequential decision.",
      "Require rebuilding exact preparation when selected inputs materially change."
    ],
    "completion_criterion": "Expired or stale input cannot retain current promotion/readiness status by timestamp relabeling.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C05"
  },
  {
    "work_id": "G09.02",
    "gap_id": "G09",
    "title": "Prepare an explicit successor source epoch",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.06",
      "G03.06",
      "G04.07",
      "G07.04",
      "R03.01",
      "R05.01"
    ],
    "planned_outputs": [
      "candidate-runtime/profile-successor.json",
      "candidate-runtime/source-reader-epoch-binding.py"
    ],
    "actions": [
      "Prepare the reviewed reader/profile recipe for the selected immutable epoch, using the existing current Project State lookup as derived selector.",
      "Generate its final instantiated profile only after actual authorized decision evidence exists; validate against fixed reviewed inputs and the C05 output recipe.",
      "Include the representation/source-direction amendment and exact declared consumer compatibility; do not disable integrity checks or retain hardcoded old vocabulary as current."
    ],
    "completion_criterion": "An exact successor epoch can be read while prior immutable evidence and compatibility boundaries remain preserved.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C05"
  },
  {
    "work_id": "G09.03",
    "gap_id": "G09",
    "title": "Map existing-store baseline compatibility",
    "status": "planned-not-executed",
    "depends_on": [
      "G09.02",
      "G09.01"
    ],
    "planned_outputs": [
      "compatibility/store-baseline-policy.json"
    ],
    "actions": [
      "Keep existing local stores pinned to their original exact baselines and explicit historical/stale standing.",
      "Use a newly explicitly provisioned branch for successor operational work when needed; automatic rebase/in-place store migration is outside this first release.",
      "Preserve identities, signing keys and historical replay, and require explicit selection of the supported source baseline."
    ],
    "completion_criterion": "Old stores remain inspectable under their declared standing; new work has an explicit supported source baseline.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C05"
  },
  {
    "work_id": "G09.04",
    "gap_id": "G09",
    "title": "Map ontology visibility and supported connections",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.05",
      "G09.02"
    ],
    "planned_outputs": [
      "candidate-runtime/definition-graph-projection.py",
      "contracts/ontology-local-signatures.json"
    ],
    "actions": [
      "Expose accepted Definitions, sources, current carriers, owner evidence and decisions through existing graph posture.",
      "Current global links require admitted exact relation instances; local graph signatures are separately scoped and bound.",
      "Register a needed pair only through the extension rule, or preserve it as unresolved/candidate local evidence."
    ],
    "completion_criterion": "No graph suggestion or added node becomes an undeclared global connection or second writable authority.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C05"
  },
  {
    "work_id": "G09.05",
    "gap_id": "G09",
    "title": "Map Project State and history consequences",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.03",
      "G09.02"
    ],
    "planned_outputs": [
      "compatibility/project-state-history-map.json"
    ],
    "actions": [
      "Bind semantic events and governance events separately to selected exact member effects.",
      "Advance Project State, current lookup and deterministic receipts through the authorized transaction.",
      "Retain pack provenance and declined/open state without recording unselected meanings as admitted."
    ],
    "completion_criterion": "Current state can be reconstructed from exact authorized consequences and preserved history.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C05"
  },
  {
    "work_id": "G09.06",
    "gap_id": "G09",
    "title": "Refresh bounded Agent context",
    "status": "planned-not-executed",
    "depends_on": [
      "G09.04",
      "G09.05",
      "G09.01"
    ],
    "planned_outputs": [
      "candidate-cli/context-selection.mjs"
    ],
    "actions": [
      "Select the new admitted Define/Pack meanings when applicable, plus the exact use-relevant meanings.",
      "Preserve context budgets, TTL, diagnostics, source posture and explicit inclusion choices.",
      "Close machine sessions and keep saved Define workflow state distinct from private long-term agent memory."
    ],
    "completion_criterion": "A new ephemeral agent gets durable project knowledge through views without claiming global context completeness.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C05"
  },
  {
    "work_id": "G09.07",
    "gap_id": "G09",
    "title": "Specify observable read-back criteria",
    "status": "planned-not-executed",
    "depends_on": [
      "G09.06",
      "G08.07"
    ],
    "planned_outputs": [
      "verification/read-back-criteria.json"
    ],
    "actions": [
      "Check exact accepted meaning, source standing, owner decision, current state and supported graph links.",
      "Check that open/rejected/unselected meanings remain candidate or unresolved and that old epochs are explicitly historical.",
      "Add useful diagnostics for source mismatch, missing ownership, unsupported relation and stale preparation."
    ],
    "completion_criterion": "A user can inspect why a target counts as accepted and why another does not.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C05"
  },
  {
    "work_id": "G10.01",
    "gap_id": "G10",
    "title": "Prepare the complete verification matrix",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.07",
      "G09.07",
      "G02.04",
      "G03.05",
      "G07.08",
      "G02.05",
      "R01.01",
      "R02.01",
      "R03.01",
      "R04.01",
      "R05.01",
      "R06.01",
      "R08.01",
      "R09.01",
      "R10.01",
      "R11.01",
      "R12.01"
    ],
    "planned_outputs": [
      "verification/matrix.json"
    ],
    "actions": [
      "Trace every work item requirement to an exact planned fixture, schema/link check, browser/CLI journey, semantic review or owner decision.",
      "Include all dispositions, missing supplements, wrong owner/nested scope, tampering, stale inputs, bad typed endpoints, partial selection, recovery and replay.",
      "Include numeric and boolean Calculation regressions and existing context/ontology/review behaviors."
    ],
    "completion_criterion": "Every promised behavior has a verification surface; no result is invented by listing a case.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C07"
  },
  {
    "work_id": "G10.02",
    "gap_id": "G10",
    "title": "Verify the frozen candidate prototype",
    "status": "planned-not-executed",
    "depends_on": [
      "G10.01",
      "G05.06"
    ],
    "planned_outputs": [
      "verification/candidate-results.json",
      "verification/semantic-assurance-report.json"
    ],
    "actions": [
      "When implementation verification is authorized, execute the matrix against exact candidate bytes in isolated fixtures.",
      "Bind actual source/runtime manifests and formal interpretation/fidelity coverage; report failures and unsupported obligations.",
      "Native host initialization does not prove live-model completion; exercise a model turn only when that scope is selected."
    ],
    "completion_criterion": "Current recorded evidence covers the exact release candidate and preserves all claim ceilings.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C07",
    "requires_outcomes": [
      "verification_matrix_bound_to_full_manifest_and_realization",
      "all_required_checks_pass_or_declared_block"
    ]
  },
  {
    "work_id": "G10.03",
    "gap_id": "G10",
    "title": "Obtain the exact Product approval outcome",
    "status": "planned-not-executed",
    "depends_on": [
      "G02.06",
      "G10.02",
      "R07.01"
    ],
    "planned_outputs": [
      "adoption/product-approval-request.json",
      "adoption/product-approval-outcome.json"
    ],
    "actions": [
      "Present frozen Product capability/realization candidates, tests, limitations and residue.",
      "Record the appropriate Product owner outcome after the prototype evidence exists.",
      "Treat that outcome as Product approval only; it does not grant semantic admission, runtime activation or external action."
    ],
    "completion_criterion": "A concrete tested product candidate has an attributable scoped approval/revision/defer/reject outcome.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C07",
    "requires_outcomes": [
      "current_product_evidence_matches_frozen_candidate",
      "final_documentation_check_passed"
    ]
  },
  {
    "work_id": "G10.04",
    "gap_id": "G10",
    "title": "Update the repository documentation candidate",
    "status": "planned-not-executed",
    "depends_on": [
      "G10.02",
      "G08.05"
    ],
    "planned_outputs": [
      "documentation/README-postimage.md",
      "documentation/use-define-postimage.md",
      "documentation/prepare-definition-postimage.md",
      "documentation/interface-contract-postimage.md"
    ],
    "actions": [
      "Document inspect -> run -> prepare -> review -> exact owner decision -> applicable apply -> refreshed views.",
      "Explain missing-field blockers, all four dispositions, parameter specialization versus meaning revision, and local versus repository standing.",
      "Keep command examples matched to actual behavior; include source/profile compatibility and no live completion claim unless observed."
    ],
    "completion_criterion": "All linked documentation explains the same candidate contracts and behaviors.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C07"
  },
  {
    "work_id": "G10.05",
    "gap_id": "G10",
    "title": "Prepare and obtain independent adoption decisions",
    "status": "planned-not-executed",
    "depends_on": [
      "G10.03",
      "G10.04",
      "G01.07",
      "G03.06",
      "G07.08",
      "G09.02",
      "R07.01"
    ],
    "planned_outputs": [
      "adoption/exact-target-manifest.json",
      "adoption/decision-cores.json",
      "adoption/authorization-evidence.json"
    ],
    "actions": [
      "Bind exact semantic targets, required source dispositions, evaluation/lifecycle profiles, policy/challenge amendments, runtime code and source profile with independent owner scopes.",
      "Present one checkpoint only after all exact reviewable bytes exist; preserve partial or rejected outcomes and rebuild dependent closure.",
      "Separate runtime adoption, capability realization adoption, semantic admission and repository application authorization."
    ],
    "completion_criterion": "Every admitted effect has its applicable exact owner decision; no member outcome authorizes another by implication.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C07",
    "requires_outcomes": [
      "product_outcome_qualifies_as_approval",
      "all_reviewed_input_and_recipe_hashes_match",
      "each_requested_effect_has_separate_applicable_owner_scope"
    ]
  },
  {
    "work_id": "G10.06",
    "gap_id": "G10",
    "title": "Apply only the authorized coherent target set",
    "status": "planned-not-executed",
    "depends_on": [
      "G10.05",
      "G08.06"
    ],
    "planned_outputs": [
      "adoption/application-receipt.json",
      "adoption/registry-index-state-consequences.json"
    ],
    "actions": [
      "Verify exact preconditions and apply only the closed authorized target set through the selected route.",
      "Publish matching registry/profile/state/view consequences so the source reader stays compatible.",
      "Recover failure under the declared rollback boundary; no remote publication, hosting, deployment or external effects are implied."
    ],
    "completion_criterion": "The authorized repository/local effects and receipts agree; unselected or rejected targets remain unchanged.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C07",
    "requires_outcomes": [
      "selected_effect_set_is_dependency_closed",
      "each_selected_effect_is_exactly_authorized",
      "current_preconditions_and_expected_selection_match",
      "generated_outputs_match_authorized_recipe",
      "required_representation_and_profile_amendments_accepted"
    ]
  },
  {
    "work_id": "G10.07",
    "gap_id": "G10",
    "title": "Inspect the final integrated state",
    "status": "planned-not-executed",
    "depends_on": [
      "G10.06",
      "G09.07"
    ],
    "planned_outputs": [
      "adoption/final-integration-report.json"
    ],
    "actions": [
      "Read back exact accepted Definitions, active contract/profile selection, Project State, source epochs and agent views.",
      "Compare actual outcomes with the documentation and matrix; record remaining bounded residue.",
      "Keep historical upstream BLOCK/FLAG evidence and deferred ontology/handled-record migration visible."
    ],
    "completion_criterion": "The selected Define integration is complete within its declared scope, with actual final-state evidence and explicit deferred work.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "design_choice_ref": "C07",
    "requires_outcomes": [
      "committed_selection_and_receipts_verified",
      "accepted_and_unselected_postures_match",
      "final_read_back_checks_passed"
    ]
  },
  {
    "work_id": "R01.01",
    "gap_id": "G01",
    "title": "The proposed formal meaning needs an unambiguous interpretation",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.02",
      "G01.05"
    ],
    "planned_outputs": [
      "implementation-evidence/r01-closure.json"
    ],
    "actions": [
      "Implement the explicit grouped Pack predicate/signature interpretation in C01 and formal-interpretation.json.",
      "Reject duplicate disposition rows before constructing the total function; bind required finite/operational and fidelity assurance outcomes to exact sources and consumers."
    ],
    "completion_criterion": "Implement the selected C01 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner",
      "role:artifact-mechanics-owner"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R01",
    "design_choice_ref": "C01",
    "planned_verification": [
      "Counterexamples: all references resolved with validation scope absent; unresolved reference without a declared gap; two differently worded statements with the same meaning.",
      "Check interpretation against all three voices and declared neighboring/current definitions; record unsupported source clauses."
    ]
  },
  {
    "work_id": "R02.01",
    "gap_id": "G07",
    "title": "Key possession is not yet bound to the semantic principal",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.01",
      "G07.02"
    ],
    "planned_outputs": [
      "implementation-evidence/r02-closure.json"
    ],
    "actions": [
      "Use the existing trusted human-owner conversation decision route for repository semantic admission; local key possession is not a substitute.",
      "Implement the declared role/principal/source reconciliation and prevent the CLI from manufacturing human evidence or automating shared-scope promotion."
    ],
    "completion_criterion": "Implement the selected C02 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R02",
    "design_choice_ref": "C02",
    "planned_verification": [
      "A valid local key with a copied definition-owner label is rejected for semantic promotion.",
      "Unbound, rotated or revoked keys cannot make new effects; historical approved effects retain their exact recorded basis."
    ]
  },
  {
    "work_id": "R03.01",
    "gap_id": "G09",
    "title": "Source parsing can use different bytes from the recorded digest",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.01"
    ],
    "planned_outputs": [
      "implementation-evidence/r03-closure.json"
    ],
    "actions": [
      "Read each selected file once, hash and strictly parse that same bounded byte buffer.",
      "Pin immutable material selection; implement duplicate-key, finite-number, precision and depth checks and source-change diagnostics."
    ],
    "completion_criterion": "Implement the selected C03 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner",
      "role:artifact-mechanics-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R03",
    "design_choice_ref": "C03",
    "planned_verification": [
      "Planned controlled writer-interleaving case checks that parsed content always corresponds to the captured digest.",
      "Persistent and transient source changes must cause a clean retry/failure or remain outside the pinned immutable snapshot."
    ]
  },
  {
    "work_id": "R04.01",
    "gap_id": "G08",
    "title": "Repository publication has no chosen coherent commit boundary",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.05",
      "G09.03"
    ],
    "planned_outputs": [
      "implementation-evidence/r04-closure.json"
    ],
    "actions": [
      "Implement immutable staged admission bundles with one current Project State lookup visibility commit, validated through the admitted bundle.",
      "Implement cooperative writer lock, expected-lookup comparison, no-overwrite immutable publication, fsync and atomic lookup replacement; make legacy compatibility projections derivative under an explicit representation amendment."
    ],
    "completion_criterion": "Implement the selected C04 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment",
      "Applicable source-profile, Project State and ontology owners: resolve assignments",
      "Applicable Product approval owner: resolve assignment",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R04",
    "design_choice_ref": "C04",
    "planned_verification": [
      "Planned reader-during-cutover, competing writer, stale preimage and crash-at-each-publication-step cases.",
      "After recovery, readers see a complete old or complete new selected epoch, or an explicit unavailable state; no mixed state is labeled current."
    ]
  },
  {
    "work_id": "R05.01",
    "gap_id": "G08",
    "title": "The future source epoch depends on records not yet created",
    "status": "planned-not-executed",
    "depends_on": [
      "G08.03",
      "G07.07"
    ],
    "planned_outputs": [
      "implementation-evidence/r05-closure.json"
    ],
    "actions": [
      "Implement separate reviewed-input, actual-decision and observed-consequence manifests.",
      "Generate the final epoch descriptor from the authorized exact recipe after decision evidence exists; reject self-hashing, fixture substitution and undeclared outputs."
    ],
    "completion_criterion": "Implement the selected C05 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner",
      "role:artifact-mechanics-owner",
      "Applicable repository admission owner: resolve assignment",
      "Applicable source-profile, Project State and ontology owners: resolve assignments",
      "Applicable Product approval owner: resolve assignment",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R05",
    "design_choice_ref": "C05",
    "planned_verification": [
      "Fixture-dependent, predicted and observed digests cannot be substituted for each other.",
      "A content-dependency graph distinguishes reviewed inputs, decision evidence and generated outputs; no output must hash itself."
    ]
  },
  {
    "work_id": "R06.01",
    "gap_id": "G04",
    "title": "Cross-runtime parsing and hash rules remain unspecified",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01",
      "G07.01"
    ],
    "planned_outputs": [
      "implementation-evidence/r06-closure.json"
    ],
    "actions": [
      "Let the pinned Python strict boundary own new authority-record hashes and signature bytes.",
      "Keep raw-file, Python authority and legacy Node pack digest kinds separate; Node transports original bytes/references without authority hash recomputation."
    ],
    "completion_criterion": "Implement the selected C06 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment",
      "role:evidence-conformance-owner",
      "Applicable repository admission owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R06",
    "design_choice_ref": "C06",
    "planned_verification": [
      "Planned cross-runtime cases: 1 versus 1.0, exponent forms, negative zero, unsafe integers, Unicode and numeric-looking keys.",
      "Duplicate keys and unsupported nonfinite/precision values fail before review; source text and normalized content remain traceable."
    ]
  },
  {
    "work_id": "R07.01",
    "gap_id": "G10",
    "title": "Verification can precede a required binding and late documentation",
    "status": "planned-not-executed",
    "depends_on": [
      "G10.04",
      "G02.05",
      "G10.02"
    ],
    "planned_outputs": [
      "implementation-evidence/r07-closure.json"
    ],
    "actions": [
      "Run the final documentation/example/adoption-closure check on the full tested runtime and exact realization binding.",
      "Create a new candidate revision and reopen impacted checks when governing bytes/behavior change; record documentation-only checks separately."
    ],
    "completion_criterion": "Implement the selected C07 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "Applicable Lab Product owner: resolve exact assignment; foundation route is repository-owner review",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R07",
    "design_choice_ref": "C07",
    "planned_verification": [
      "Prototype verification cannot be ready while the realization binding is pending.",
      "Exact documented CLI commands, relative links and stated behavior are checked on final selected bytes."
    ]
  },
  {
    "work_id": "R08.01",
    "gap_id": "G07",
    "title": "A completed decision task does not mean its outcome permits continuation",
    "status": "planned-not-executed",
    "depends_on": [
      "G07.07",
      "G06.05"
    ],
    "planned_outputs": [
      "implementation-evidence/r08-closure.json"
    ],
    "actions": [
      "Implement approve/revise/defer/reject guards and accepted-subset dependency closure.",
      "Bind retries to exact proposal/authorization; changed bytes or uncertain outcomes require inspection/recomposition and fresh qualifying decisions as specified by C08."
    ],
    "completion_criterion": "Implement the selected C08 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "role:definition-owner",
      "role:artifact-mechanics-owner",
      "Applicable runtime adoption owner: resolve assignment",
      "Applicable next-use owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R08",
    "design_choice_ref": "C08",
    "planned_verification": [
      "Rejected/deferred Product or semantic outcomes never reach their dependent apply effect.",
      "Partial selection preserves unselected targets; changed-byte requests cannot reuse an old decision/core/bundle."
    ]
  },
  {
    "work_id": "R09.01",
    "gap_id": "G04",
    "title": "Legacy compile and durable-session consumers need explicit adapters",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01",
      "G04.03",
      "G04.05"
    ],
    "planned_outputs": [
      "implementation-evidence/r09-closure.json"
    ],
    "actions": [
      "Preserve legacy v1 run/chat/compile/session contracts; implement explicit v1-plus-supplement adaptation into the new Lab pack v2 preparation envelope.",
      "Expose v2 compile as unsupported in this release, retain no-open-question compile readiness, and never migrate old sessions implicitly."
    ],
    "completion_criterion": "Implement the selected C09 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner",
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R09",
    "design_choice_ref": "C09",
    "planned_verification": [
      "Planned old/new pack x prepare/compile/resume compatibility cases.",
      "Open questions may be reviewable while unsupported compilation remains blocked; numeric/boolean Calculation regressions still run on the selected compiler."
    ]
  },
  {
    "work_id": "R10.01",
    "gap_id": "G01",
    "title": "Semantic revision impact is not closed over declared consumers",
    "status": "planned-not-executed",
    "depends_on": [
      "G01.05",
      "G03.01"
    ],
    "planned_outputs": [
      "implementation-evidence/r10-closure.json"
    ],
    "actions": [
      "Build the exact declared consumer/dependency impact closure and compare new meanings with every current registered meaning under the stated assurance scope.",
      "Classify each affected reference as historical, compatible, updated, deprecated, blocked or owner-qualified residue; block unresolved incompatible required consumers."
    ],
    "completion_criterion": "Implement the selected C10 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:definition-owner",
      "role:source-admission-owner",
      "role:evidence-conformance-owner",
      "role:artifact-mechanics-owner",
      "Applicable next-use owner: resolve assignment",
      "Applicable Policy and Challenge Contract owner: resolve assignment",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R10",
    "design_choice_ref": "C10",
    "planned_verification": [
      "An incompatible declared dependent blocks current promotion/adoption until repaired or explicitly governed.",
      "A preserved historical binding stays exact; it is not silently rewritten to the new current version."
    ]
  },
  {
    "work_id": "R11.01",
    "gap_id": "G04",
    "title": "Pack and assurance work has no declared resource bounds",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.01"
    ],
    "planned_outputs": [
      "implementation-evidence/r11-closure.json"
    ],
    "actions": [
      "Enforce the initial C11 limits before expensive parsing/pair work; distinguish timeout/over-limit from complete success.",
      "Implement explicit batch identity, coverage and continuation for larger sets without silently dropping cross-batch dependencies."
    ],
    "completion_criterion": "Implement the selected C11 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:definition-owner",
      "role:evidence-conformance-owner",
      "Applicable Product approval owner: resolve assignment",
      "Applicable runtime adoption owner: resolve assignment"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R11",
    "design_choice_ref": "C11",
    "planned_verification": [
      "Boundary and over-limit inputs produce clear bounded outcomes.",
      "Batch recomposition preserves full declared required-set identity and unresolved residue."
    ]
  },
  {
    "work_id": "R12.01",
    "gap_id": "G05",
    "title": "The first useful preview is tied to the entire authority implementation",
    "status": "planned-not-executed",
    "depends_on": [
      "G04.06",
      "G06.06"
    ],
    "planned_outputs": [
      "implementation-evidence/r12-closure.json"
    ],
    "actions": [
      "Deliver separately frozen M1 preparation preview, M2 guarded review and M3 authorized application/visibility.",
      "Limit the writer to this Definition cohort and its reviewed profile/representation/state consequences; preserve one final exact owner checkpoint if selected."
    ],
    "completion_criterion": "Implement the selected C12 design and satisfy all bound verification obligations; owner adoption remains separate.",
    "review_roles": [
      "role:artifact-mechanics-owner",
      "role:evidence-conformance-owner",
      "role:definition-owner",
      "Applicable Policy and Challenge Contract owner: resolve assignment",
      "Applicable repository admission owner: resolve assignment",
      "Applicable source-profile, Project State and ontology owners: resolve assignments"
    ],
    "execution_authorization": "Planning choices applied; implementation is not started. Applicable verification and exact owner effect gates remain mandatory.",
    "audit_finding_ref": "R12",
    "design_choice_ref": "C12",
    "planned_verification": [
      "The preview can be demonstrated without signing, stores, repository mutation or new authority.",
      "Every milestone has a bounded accepted/deferred scope; partial delivery is never reported as full integration."
    ]
  }
]
```
