---
node_type: ontology-review
status: review-candidate
authority_effect: none
review_date: 2026-10-05
---

# Actor and Agent model review

## Conclusion

The Lab currently models Person, Person Reference, Team, Role, Role Assignment, Capability Instance, owners, implementations, and runtime activity, but it has no governed Actor or Agent model joining them.

This is a structural gap. A complete Lab needs an Agent as the attributable actor that receives bounded context and assignments, uses declared capabilities and tools, performs actions, produces artifacts and evidence, and remains constrained by Roles, Policies, Authority Claims, delegations, and owner decisions.

No Definition or Artifact Type is admitted by this review.

## Existing evidence

1. `cal.definition.person` explicitly keeps Person distinct from agent, account, role, permission, model, session, and Team.
2. The imported Ontology Product already contains four local actor nodes: Human Participant, Work Owner, Machine Collaborator, and Ontology Steward.
3. The local Product ontology defines `serves` and `participates_in`, including Machine Collaborator participation in validation.
4. The global Relation Kind candidate has no `actor` or `agent` endpoint kind.
5. The admitted Definition registry has no Actor, Agent, Agent Instance, Agent Session, Agent Action, Agent Capability, or Delegation Definition.

## Semantic model

```text
Actor
  abstract governed participant classification

Agent
  abstract operational Actor classification for bounded attributable action

Agent Profile
  reusable behavior, input, output, policy, and stop contract

Agent Capability
  bounded class of action or interpretation the Agent can perform

Agent Instance
  time-bounded concrete Actor realization; a Machine Agent is always ephemeral

Agent Session
  time-bounded execution scope with Project State views, authority, assignment, budgets, and short-term memory

Agent Action
  immutable attributable proposal, attempt, or execution record

Agent Assignment
  time-bounded binding of an Agent to Intent, Goal, Project, Work, Role, or Responsibility

Delegation
  explicit scope- and time-bounded authorization for an Agent to act for a Principal

Project State
  durable external state that supplies machine-agent long-term memory through Context and Ontology Views

Session Memory
  ephemeral working state owned by one Agent Session

Operational Learning Records
  durable governed Project State derived from attributable Agent work;
  selected for later Sessions only through Context and Ontology Views
```

## Proposed Definitions

### Actor

**Candidate identity:** `cal.definition.actor`

An Actor is a governed participant identity that may be attributed participation in an Intent, Product, Project, Research activity, Experiment, work item, request, artifact, relation, review, or decision. Actor classification alone establishes no personhood, agency, ownership, capability, role, permission, authority, or successful action.

```text
Actor(a)
  => attributable_participant(a)

Actor(a)
  =/=> Agent(a)
  =/=> Person(a)
  =/=> authorized(a)
  =/=> owner(a)
```

Actor is an abstract semantic classification. It does not require a standalone root Artifact Type if every concrete actor kind has a governed carrier.

### Agent

**Candidate identity:** `cal.definition.agent`

An Agent is an Actor operating within an explicit Session, Context, Assignment, Policy, and Authority boundary that may interpret inputs, select or perform Actions using declared Capabilities and Tools, and produce attributable outputs, evidence, or proposed effects. Agent capability does not grant authority, and Agent output does not become owner meaning, fact, decision, admission, Project State, or external effect without the required validation and governance.

```text
Agent(a)
  => Actor(a)
  and bounded_operational_identity(a)
  and declared_capabilities(a)
  and owner_route(a)
  and challenge_route(a)

may_perform(a, action, scope)
  requires active_instance(a)
  and active_assignment(a, scope)
  and valid_context(a, action)
  and valid_authority(a, action, scope)
  and policy_allows(a, action)

output_of(a, artifact)
  =/=> admitted(artifact)
  =/=> accepted_as_fact(artifact)
  =/=> authority_effect(artifact)
```

`Agent` is a semantic classification rather than a durable machine identity. A concrete Agent is represented by an Agent Instance. A Machine Agent Instance is created for one Agent Session and expires with that Session.

### Principal

**Candidate identity:** `cal.definition.principal`

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary. A Principal may correspond to a Person Reference, Team, service identity, or Agent Instance, but Principal identity does not prove Person identity, Agent capability, Role assignment, or authority outside exact grants.

### Agent Profile

**Candidate identity:** `cal.definition.agent-profile`

An Agent Profile is a reusable, versioned contract describing allowed input kinds, output kinds, behavior constraints, required Policies, Context requirements, tool classes, evidence obligations, escalation rules, and stop conditions independently of any active Agent Instance or Session.

### Agent Capability

**Candidate identity:** `cal.definition.agent-capability`

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to perform under an exact input, output, evidence, and failure contract. It remains distinct from Product Capability, authority, Role, Tool, Implementation, and successful performance.

```text
Agent Capability = what an Agent can attempt
Product Capability = durable outcome a Product offers
Implementation = technical realization
Authority Claim = what an Agent may do in scope
```

### Agent Instance

**Candidate identity:** `cal.definition.agent-instance`

An Agent Instance is one time-bounded concrete realization of the Agent classification, bound to an Agent Profile, implementation version, capability set, accountable Principal, owner route, and lifecycle posture. It is not a Person, model, implementation, session, or authority grant. A Machine Agent Instance is ephemeral: it is created for one Agent Session, cannot predate or outlive that Session, and cannot claim identity continuity with an instance from another Session.

### Agent Session

**Candidate identity:** `cal.definition.agent-session`

An Agent Session is a time-bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, Authority envelope, input set, budgets, event cursor, short-term Session Memory, and termination state. For a Machine Agent, Session termination also terminates the Agent Instance.

### Project State and long-term memory

**Candidate identity:** `cal.definition.project-state`

Project State is the durable governed external state of a Project: its admitted and candidate artifacts, Definitions, Product and Project records, decisions, evidence, semantic and governance event histories, relation instances, and other versioned records. Project State is not owned by an Agent.

For a Machine Agent, long-term memory is Project State selected and presented through exact Context Views and Ontology Views:

```text
machine_agent_long_term_memory(session)
  := project_state
     projected_through context_view(session)
     and ontology_view(session)

hidden_cross_session_machine_memory = forbidden
```

A Context View supplies purpose-bounded project material. An Ontology View supplies a graph-shaped projection of one exact consistent Ontology cut. Both bind source versions, cursors, digests, exclusions, freshness, expiry, allowed readings, and forbidden moves. They are read surfaces over Project State, not memory owned by the Machine Agent and not competing canonical stores.

### Session Memory

**Candidate identity:** `cal.definition.session-memory`

Session Memory is ephemeral working state owned by one Agent Session. It may contain selected inputs, temporary working records, recent Agent Actions, tool results, unresolved questions, and short-lived caches needed to continue the Session. It has no authority effect, cannot serve as canonical Project State, and expires when the Session terminates.

Material survives a Session only when an Agent Action explicitly writes an artifact, event, receipt, evidence record, or proposed change through the Project's validation and governance path. A later Machine Agent is a new instance that reconstructs its working state from new Context and Ontology Views.

Operational learning follows this same persistence rule. Agent Reflection, Operational Lesson, Lesson Application, Lesson Outcome Assessment, and Improvement Target records are durable only as governed Project State. They are never copied forward as hidden Machine Agent memory. Their complete candidate semantics are reviewed in `2026-10-05-agent-operational-learning-model-review.md`.

### Ontology View

**Candidate identity:** `cal.definition.ontology-view`

An Ontology View is an immutable, purpose-bounded projection of one exact consistent Ontology cut for a named consumer or Agent Session. It carries the Ontology identity, semantic cursor, event-set digest, governance cut, selected nodes and edges, exclusions, expiry, and claim ceiling. It is derived Project State and never a replay source.

### Agent Action

**Candidate identity:** `cal.definition.agent-action`

An Agent Action is an immutable attributable record of one proposed, attempted, completed, rejected, or failed operation by an Agent Instance inside one Session. It records exact inputs, output references, tool uses, policies, authority evidence, approvals, effects, residue, and receipts. The action record does not prove that the claimed effect occurred.

### Agent Assignment

**Candidate identity:** `cal.definition.agent-assignment`

An Agent Assignment is a time-bounded, owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Research Run, Experiment Run, Role, or Responsibility. Assignment establishes expected participation and scope; it grants no authority unless an exact Authority Claim or Delegation says so.

### Delegation

**Candidate identity:** `cal.definition.delegation`

A Delegation is an explicit, scope-bounded, time-bounded authorization from one Principal or Authority owner to an Agent or Agent Instance to perform named action kinds under exact Policies, approval gates, evidence obligations, revocation rules, and claim ceilings. Delegation does not transfer identity, ownership, or authority outside its envelope.

## Proposed Artifact Types

| Artifact Type | Identity and responsibility |
| --- | --- |
| Agent Profile | Reusable behavior, Context, Policy, input/output, tool, evidence, escalation, and stop contract |
| Agent Capability | Bounded technical ability with inputs, outputs, failure modes, evidence, and implementation bindings |
| Agent Instance | Time-bounded concrete Agent with actor kind, Profile, capabilities, implementation, model, runtime, accountable Principal, owner, and lifecycle; mandatory ephemeral posture for Machine Agents |
| Agent Session | Bounded Assignment, Context View, Ontology View, authority, Policy, inputs, budgets, cursor, Session Memory, and termination record |
| Session Memory | Ephemeral working state owned by one Session, with expiry and no authority effect |
| Agent Action | Immutable proposed/attempted/completed action, tool use, outputs, effects, evidence, receipt, and residue |
| Agent Assignment | Exact Agent-to-Intent/Goal/Project/Work/Run/Role/Responsibility participation contract |
| Principal Reference | Minimal governed reference to the accountability or authorization Principal |
| Delegation | Exact delegator, eligible Agent Profile or concrete Agent Instance, scope, action kinds, Policies, gates, evidence, period, and revocation |
| Ontology View | Immutable graph projection of one exact consistent Ontology cut for a Session or consumer |
| Agent Reflection | Evidence-bounded diagnostic interpretation of exact Sessions, Actions, observations, feedback, and residue |
| Operational Lesson | Scoped, versioned candidate behavior or interpretation retained in Project State |
| Lesson Application | Immutable record that one exact lesson revision was selected and actually used or deliberately not used |
| Lesson Outcome Assessment | Supported, contradicted, or inconclusive evidence assessment of one application |
| Improvement Target | Owner-reviewed routing record from recurring operational evidence into Research, Experiment, Profile, Policy, validation, or Implementation work |
| Classification Scheme | Cross-cutting versioned axes and values for actor kind, action kind, lesson routing, and other governed classifications |
| Classification Assignment | Attributable binding of an exact Agent or Agent-work subject revision to one Scheme axis and value |
| Failure Mode | Reusable contract for one way an Agent, Action, Profile, Capability, Tool, Implementation, workflow, or runtime may violate an exact boundary |
| Failure Occurrence | Immutable episode binding exact Agent work, conditions, boundary, evidence, impact, response, uncertainty, and residue |
| Failure Assessment | Evidence-bounded interpretation of occurrence, mode, cause hypotheses, impact, containment, and recovery |
| Failure Control Binding | Exact preventive, detective, containment, recovery, or compensation control associated with one Failure Mode |

`Actor` and `Agent` remain abstract Definitions. Concrete participation is carried by Person Reference, Team, or a time-bounded Agent Instance. No durable Machine Agent carrier is allowed.

## Actor kinds

| Actor kind | Underlying subject | Required boundary |
| --- | --- | --- |
| Human Agent | Person Reference | Person remains distinct; Agent record carries operational participation only |
| Team Agent | Team | Every consequential action retains an accountable Principal or Agent Instance |
| Machine Agent | Ephemeral Agent Instance bound to one Session | Cannot outlive the Session, retain hidden cross-session memory, or claim owner or decision authority |
| Service Agent | Ephemeral Agent Instance bound to one invocation or Session | Exact API, Profile, capability, Policy, authority envelope, and expiry |
| Hybrid Agent | Multiple declared actor subjects | Human and machine contributions remain separately attributable |

## Core non-collapse rules

```text
Person != Person Reference != Principal != Actor != Agent

Agent != Role != Role Assignment != Team != Team Membership

Agent classification != Agent Profile != Agent Instance != Agent Session != Agent Action

Agent Capability != Product Capability != Capability Instance

Agent Capability != Authority Claim != Delegation

Agent != model != Implementation != Tool

Actor kind classification != Role != Agent Profile != Agent Capability

Agent output != evidence acceptance != Finding != Decision != admission

failure signal != Failure Occurrence != Failure Assessment != Operational Lesson

Machine Agent Instance lifetime = Agent Session lifetime

Session Memory != Project State != Context View != Ontology View

Machine Agent long-term memory = Project State accessed through Context and Ontology Views

Operational Lesson != Session Memory != Agent Profile != Policy != Definition

lesson selection != lesson application != successful outcome
```

## Proposed relation axes and exact starting pairs

These are review candidates. Each requires the Typed Connection Extension Rule and a closed qualifier schema.

### `relation.acts-for`

Unique question: which Principal is this Agent explicitly acting for within a bounded delegation?

- `agent-instance -> principal`

Required qualifiers: delegation reference, scope, allowed action kinds, period, revocation state.

Forbidden inference: identity equivalence, ownership transfer, unrestricted authority.

### `relation.has-capability`

Unique question: which Agent Capability is declared for this Agent Profile or concrete Agent Instance?

- `agent-profile -> agent-capability`
- `agent-instance -> agent-capability`

Forbidden inference: authority, successful performance, Product value.

### `relation.performs`

Unique question: which attributable activity is performed or attempted by this Agent Instance?

- `agent-instance -> agent-action`
- `agent-instance -> work`
- `agent-instance -> research-run`
- `agent-instance -> experiment-run`
- `agent-instance -> review`

Required qualifiers: participation role, action posture, session reference.

Forbidden inference: ownership, approval, admission, successful effect.

### `relation.uses-tool`

Unique question: which Tool or Implementation does this Agent Session use to perform its bounded work?

- `agent-session -> implementation`
- `agent-action -> implementation`

Forbidden inference: realization, conformance, ownership, authority.

### `relation.produces`

Unique question: which attributable output was produced by this Agent Action?

- `agent-action -> generated-output`
- `agent-action -> observation`
- `agent-action -> measurement-result`
- `agent-action -> evidence-set`
- `agent-action -> finding`
- `agent-action -> definition`
- `agent-action -> typed-relation`

Required qualifiers: production role, output posture, exact action receipt.

Forbidden inference: acceptance, correctness, admission, authority effect.

### Extensions to existing axes

- `agent-instance -> role` and `agent-instance -> responsibility` under `relation.assigned-to`.
- `agent-instance -> agent-profile` under a reviewed profile binding; Agent remains an abstract classification.
- `agent-profile`, `agent-instance`, `agent-session`, and `agent-action` to Policy under `relation.governed-by`.
- `agent-assignment -> intent` under `relation.addresses-intent`.
- `agent-assignment -> project` under `relation.member-of` only when the assignment is structurally part of that Project.
- `agent-action -> goal` or Product under `relation.contributes-to` only when intended contribution is separately declared.
- `agent-session -> context-view` through a dedicated Context consumption binding; fulfilling a Context Request remains separate.

### Operational learning connections

- Agent Action `produces` Agent Reflection, Operational Lesson, or Lesson Application without implying acceptance.
- Agent Reflection and Operational Lesson `derive-from` exact Actions, Observations, Findings, Evidence Sets, feedback, Residue, or earlier assessments.
- Lesson Application `applies-lesson` to one exact Operational Lesson revision. This is an independent axis because applying guidance is semantically different from using a Method, executing Work, testing a Hypothesis, or belonging to a Project.
- Lesson Outcome Assessment `evaluates` one Lesson Application.
- Improvement Target `derives-from` Operational Lessons and Outcome Assessments, then is addressed through Research or Experiment.
- Owner Decision `declares-effect-on` the lesson or a separate target-specific promotion candidate.

Each new pair must pass the Typed Connection Extension Rule. Selection in a View, application, compliance, outcome, and causal benefit remain separate facts.

## How Agent interacts with the Lab

### Intent

An Actor may propose an Intent. An Agent works toward it only through an Agent Assignment and exact Authority boundary. An Agent Action may contribute evidence; only an owner Decision can mark the Intent satisfied.

### Product

A Product serves Actors. Agents may consume Product Capabilities or help realize them. Agent Capability and Product Capability remain separate.

### Project and Work

An Agent Assignment places an Agent in a Project, Goal, or Work scope. Project membership does not grant authority. Every action is attributed to an Agent Instance and Session.

### Research and Experiment

Agents may perform Research Runs or Experiment Runs under exact methods and designs. Observations and Measurements name their producing Agent Action and Run. Findings remain evidence-bounded conclusions.

### Definitions

Agents may read admitted Definitions, use them for validation, and produce Definition candidates. A Definition candidate remains the Agent's attributable output. Admission belongs to the Definition owner and exact decision route.

### Artifact Types and instances

An Agent uses an admitted Artifact Type to construct or validate an instance. Schema conformance proves structure only. The Agent Action records the exact type version, input digest, output digest, validator, and receipt.

### Relations

An Agent may propose Typed Relations only when the exact Relation Kind, endpoint pair, and qualifiers are admitted. The producing Agent and action are provenance; they are not automatically endpoints of the proposed domain relation.

### Ontology

An Agent reads an exact Ontology View or Ontology Package, then proposes node or edge changes through Agent Actions. The Ontology runtime appends events only after validation and required governance. Agent output never silently rewrites canonical history. The Ontology View is one source of the Agent Session's long-term project memory and remains derived from canonical event histories.

### Context

An Agent Session issues a Context Request. The resolver returns an immutable Context View bound to the request, Agent Session, purpose, cursor, event-set digest, exclusions, expiry, allowed readings, and forbidden moves. The Context View is the other source of long-term Project State presented to the Machine Agent.

### Classifications

Agent Instance, Agent Action, Operational Lesson, and related Project State may carry governed Classification Assignments. A Classification Scheme owns each axis, its values, cardinality, Definition bindings, compatibility, and challenge rules.

For Agents, the initial actor-kind values are Human Agent, Team Agent, Machine Agent, Service Agent, and Hybrid Agent. Assigning `machine-agent` classifies one ephemeral Agent Instance; it does not establish Role, Profile, Capability, Assignment, Delegation, authority, memory, or continuity. Agent Action kind, result posture, and effect class remain independent axes.

The assigning classifier is the role played by an attributable Agent Action, Method, or Implementation. It is not a new durable actor. Owner confirmation or rejection remains a separate Decision.

The detailed Scheme, Assignment, taxonomy, `instance-of`, and orthogonality rules are in `2026-10-05-classification-model-review.md`.

### Memory

A Machine Agent owns no durable memory. Long-term memory belongs to Project State and is reconstructed for each new Session through exact Context and Ontology Views. Short-term memory belongs only to the Agent Session and expires with it.

```text
Before Session
  Project State
    -> Context View
    -> Ontology View

During Session
  new ephemeral Machine Agent Instance
    -> Session Memory
    -> Agent Actions

After Session
  Agent Instance expires
  Session Memory expires
  explicitly persisted artifacts/events/receipts return to Project State
```

No model state, hidden cache, previous-session narrative, or Agent identity may be treated as Project memory unless it was explicitly persisted through a governed Project artifact or event.

Operational lessons are one permitted durable form, but persistence does not make them true or authoritative. A lesson must retain provenance, scope, exclusions, expected benefit, falsifier, counterevidence, retention policy, expiry, owner, and challenge route. A later Context View may select an eligible exact revision; a separate Lesson Application records actual use; a Lesson Outcome Assessment records supported, contradicted, or inconclusive evidence. Silence, dispatch, Agent self-report, or successful task completion alone does not prove that a lesson helped.

### Governance and challenge

Roles state expected functions. Role Assignment binds the Agent to a Role. Authority Claim or Delegation authorizes exact actions. Policy constrains them. Contestability permits challenges. These records remain independent.

### Implementation and tools

A Machine Agent is realized through exact Implementation, model, runtime, Agent Profile, capability, and Tool bindings for one Session. Every later Session creates a new Machine Agent Instance even when all bindings are identical. Continuity belongs to the durable Project State and Agent Profile, not to the expired Machine Agent.

### Evidence and decisions

Agent Actions produce receipts, outputs, observations, measurements, and evidence. Evidence may support a Finding or Decision. The Agent that produced evidence cannot infer its acceptance or grant itself authority.

### Failure modes and recovery

An Agent Capability and Agent Profile declare relevant Failure Modes and control obligations. When a signal appears, the Agent records an Observation. A Failure Occurrence is created only when evidence indicates that an exact Action, Session, Tool, Implementation, Context/Ontology View, persistence boundary, or authority obligation was violated or could not be satisfied.

A Failure Assessment separately records occurrence posture, mode assignment, causal hypotheses, impact, containment, recovery, and uncertainty. The Agent may propose it, but cannot confirm its own causal explanation, grant itself retry authority, remove contradictory evidence, close an Incident, or change its Profile or Implementation.

The Machine Agent still expires with the Session. Failure Occurrences, Assessments, controls, response Actions, recovery evidence, and residue survive only as governed Project State. Operational Lessons may derive from assessed failures, but a failure does not prove a lesson or an improvement.

The complete candidate vocabulary, classification axes, control roles, relation extensions, and recovered-with-residue example are in `2026-10-05-failure-mode-model-review.md`.

## End-to-end example

```text
Person Reference: person:vlad
  -> Principal: principal:lab-owner
  -> creates Intent: intent:complete-lab-model
  -> authorizes Profile: profile:repository-model-review for bounded repository review

Durable Project State
  -> Context View: context-view:complete-model-evidence/cursor-120
  -> Ontology View: ontology-view:lab-model/cursor-120

New ephemeral Machine Agent Instance: agent-instance:session-42
  -> uses Profile: profile:repository-model-review
  -> has Capability: agent-capability:read-and-model-repository
  -> is assigned Role: role:model-reviewer
  -> realized by Implementation: implementation:codex-runtime/version-x

Agent Session: session:complete-model-audit
  -> owns short-term Session Memory
  -> reads the exact Context View and Ontology View
  -> performs Action: action:audit-definitions
  -> performs Action: action:audit-relations
  -> produces candidate report and evidence receipts
  -> explicitly persists approved outputs to Project State
  -> terminates Session Memory and agent-instance:session-42

Next Session
  -> creates a different Machine Agent Instance
  -> reconstructs long-term memory from new Context and Ontology Views
  -> may receive lesson:complete-model-coverage@1 through those Views
  -> records a separate Lesson Application if it actually uses the lesson
  -> records a supported, contradicted, or inconclusive Outcome Assessment

Definition owner
  -> reviews candidate output
  -> challenges or accepts evidence
  -> records Decision
  -> admission occurs only if that Decision declares the exact authority effect
```

## Required admission order

1. Admit positive Actor, Agent, Principal, Agent Profile, Agent Capability, Agent Instance, Agent Session, Session Memory, Project State, Ontology View, Agent Action, Agent Assignment, and Delegation Definitions.
2. Keep Actor and Agent abstract, require Machine Agent Instance lifetime to equal Session lifetime, and decide whether Delegation specializes Authority Claim.
3. Admit Classification Scheme and Classification Assignment and define the exact Agent actor-kind Scheme without creating a durable Machine Agent identity.
4. Admit the Failure Mode, Failure Occurrence, Failure Assessment, and Failure Control Binding foundations and decide the optional Incident carrier.
5. Decide whether Agent Reflection specializes the imported Intent Reflection concept or receives one general carrier; prohibit dual writable copies.
6. Admit the operational learning Definitions and materialize the Agent and learning Artifact Types.
7. Add `principal`, `agent-profile`, `agent-capability`, `agent-instance`, `agent-session`, `session-memory`, `agent-action`, `agent-assignment`, `delegation`, `ontology-view`, classification, failure, and operational-learning endpoint kinds. Do not add a durable Machine Agent endpoint.
8. Review and admit the five Agent relation axes, exact extensions to existing axes, semantic-class projections through `instance-of`, failure occurrence/control axes, and the independent `applies-lesson` axis.
9. Add Agent attribution, Context, classification, failure, recovery, event, evidence, lesson selection/application/outcome, and challenge adapters.
10. Admit a representative Human Agent participation record, an ephemeral Machine Agent Session with one assessed failure/recovery cycle, and one complete operational lesson cycle only after their Person/Implementation, Principal, Role, Assignment, Context View, Ontology View, Classification Scheme, Policy, authority, evidence, residue, expiry, and challenge references resolve.

## Gap register

1. No admitted Actor or Agent Definition.
2. No ephemeral Agent operational Artifact Type family or memory boundary.
3. No Agent, Principal, Session, or Action endpoint kinds.
4. No global `acts-for`, `has-capability`, `performs`, `uses-tool`, or `produces` axes.
5. No governed Principal or general Authority Claim carrier in current root authority.
6. No typed link from Context Request/View to an Agent Session.
7. No uniform attribution from Research Runs, Experiment Runs, Observations, Findings, Typed Relations, Definitions, or Decisions to Agent Actions.
8. Local Ontology Product actor meanings are not mapped into the Lab's global model.
9. Machine agent implementations and current Agent Reasoning Engine migration evidence have no shared ephemeral Agent Session contract.
10. No rule states that long-term memory is Project State accessed through Context and Ontology Views or that short-term memory belongs only to the Session.
11. No admitted operational learning carrier separates Reflection, Lesson, Application, Outcome Assessment, and Improvement Target or prevents those records from becoming hidden memory or self-upgrade authority.
12. Actor kind and Agent-work classifications have no governed Scheme or attributable Assignment carrier, so labels cannot yet be versioned, challenged, or kept orthogonal to Role, Profile, Capability, lifecycle, and authority.
13. Agent Profiles and Capabilities mention failure contracts, but no admitted Failure Mode, Occurrence, Assessment, Control, or recovery model makes those contracts attributable and reusable.

## Decision posture

The revised model makes Actor and Agent abstract semantic classifications. Concrete participation is carried by time-bounded Agent Instances, Sessions, and Actions. Every Machine Agent is ephemeral and dies with its Session. Durable continuity belongs to Project State, Agent Profiles, implementations, policies, Definitions, event histories, and other governed artifacts. Long-term memory reaches each new Machine Agent through exact Context and Ontology Views; short-term memory belongs exclusively to the Session. Operational learning persists only as evidence-bounded Project State: exact lesson revisions are selected through Views, actual use and outcomes are separately recorded, and any change to a Profile, Policy, Definition, validator, or Implementation requires its own owner decision.
