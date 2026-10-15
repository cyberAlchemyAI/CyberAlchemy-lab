[Documentation home](../README.md)

<a id="essay-6"></a>

Part II · The Lab model Essay 06 · 4 minute read

<a id="essay-6-title"></a>

## An agent’s working session

A new agent starts the export investigation on Monday. Last week’s review is unavailable as private recollection. The agent needs selected software, current evidence, the project goal and tool permission. The Lab prepares an explicit session for one temporary machine instance and saves useful knowledge outside it.

Actor classifies identifiable participants. Person, Team and Principal identify a human, continuing group and boundary-recognized identity respectively. Principals support authentication, authorization, ownership or accountability. Role describes a position; Responsibility describes what someone answers for. Team Membership and Role Assignment record separate facts. A reference leaves person, account and role identities distinct.

Agent classifies an operational actor. Its Profile supplies reusable behavior, inputs, outputs, tools, evidence, escalation and stop conditions. An Agent Capability describes technically possible attempts and their input, output and failure requirements. An Instance identifies a concrete realization and accountability. Concrete participant kinds use their own records without requiring a duplicate universal Actor record.

Assignment identifies expected participation in work, intent, project, goal, run, role or responsibility, with limits and deliverables. Delegation separately grants scoped permission. Diagnosing an export might permit reading selected material and proposing a fix while excluding customer communication and production changes. The job and permission need separate records.

Saltzer and Schroeder describe least privilege and complete mediation: limit permissions to the work and check authorization whenever access occurs, including relevant changes to earlier grants. Those principles help explain why an old instruction has limits. They provide design guidance rather than evidence of enforcement on every Lab path. [Basic Principles of Information Protection](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)

A Session binds one instance and assignment to Context and Ontology Views, policies, permissions, inputs, budgets and termination conditions. The machine instance belongs to that session and ends with it. Profiles and historical session records can persist. The operating worker and its working memory are temporary.

Project State supplies saved knowledge with each record’s standing intact. Including a proposal in an accepted state does not accept the proposal. A Context Request identifies session needs; a Context View gives a fixed source selection with versions and use conditions. An Ontology View supplies a connected selection from a consistent cut. Both retain source authority limits.

Session Memory holds temporary notes, alternatives and reminders, then ends with the session. Useful material can enter the applicable reflection, evidence or lesson route. A private note has to follow the recording process before becoming Project State. Later agents recover their position through saved records and fresh views.

The inspected local runtime keeps bounded notes in process memory and clears them on closure. A session records accepted-state reference, source selection and expiry. Changed state reference, changed source digest or expiry invalidates continued context use. The agent needs current checked context through the applicable route.

A saved context packet is an output of preparation. The runtime’s context-only export closes its session after preparing that packet. A later consumer needs its own freshness and permission checks. Keeping the file preserves neither the earlier machine instance nor expired grants.

Agent Action records attributable proposals, attempts, completion, rejection or failure, with session and inputs. A Tool supplies a versioned invocation interface. Availability, ability, action and observed effect are different facts. A Work Outcome Assessment compares expected and observed results within its scope.

The agent can recover current information, inspect assignment and permission, choose allowed tools and record actions, evidence and unresolved work. Proposed Project State changes follow review and authorization. After closure, another agent recovers accepted results through new views without inheriting private memory or unrestricted grants.

### Definitions and sources

[Actor](../reference/records/def-cal-definition-actor.md#def-cal-definition-actor) · [Principal](../reference/records/def-cal-definition-principal.md#def-cal-definition-principal) · [Role](../reference/records/def-cal-definition-role.md#def-cal-definition-role) · [Agent](../reference/records/def-cal-definition-agent.md#def-cal-definition-agent) · [Agent Profile](../reference/records/def-cal-definition-agent-profile.md#def-cal-definition-agent-profile) · [Agent Capability](../reference/records/def-cal-definition-agent-capability.md#def-cal-definition-agent-capability) · [Agent Instance](../reference/records/def-cal-definition-agent-instance.md#def-cal-definition-agent-instance) · [Agent Assignment](../reference/records/def-cal-definition-agent-assignment.md#def-cal-definition-agent-assignment) · [Delegation](../reference/records/def-cal-definition-delegation.md#def-cal-definition-delegation) · [Agent Session](../reference/records/def-cal-definition-agent-session.md#def-cal-definition-agent-session) · [Session Memory](../reference/records/def-cal-definition-session-memory.md#def-cal-definition-session-memory) · [Agent Action](../reference/records/def-cal-definition-agent-action.md#def-cal-definition-agent-action) · [Tool](../reference/records/def-cal-definition-tool.md#def-cal-definition-tool) · [Project State](../reference/records/def-cal-definition-project-state.md#def-cal-definition-project-state)

- [Local runtime implementation overview](../assets/78623efb7024-README.md)
- [Local runtime: temporary agent sessions](../assets/9e96494cfe22-session.py)

Follow these links to the exact sources used by the essay. An older draft label leaves standing to the acceptance recorded for that version.

[Continue to essay 07 **How experience becomes useful →**](07-how-experience-becomes-useful.md#essay-7)
