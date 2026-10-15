[Documentation home](../README.md)

# Agent work and memory

<a id="agent"></a>

06

<a id="agent-title"></a>

## Give the agent a task, limits and a temporary session

 [Explore this in the system map ↑](system-map.md#system-map) 

<a id="docs-agent-heading-2"></a>

### Establish the job and permissions

The Work item names the investigation and expected result. An **Agent Assignment** binds participation to that job, including owner, scope, period and stop conditions. An **Agent Profile** supplies reusable behavior and tool rules.

An **Agent Capability** describes an ability such as comparing identifiers. The Product Capability describes the useful outcome the platform must provide.

A **Principal** is the identity recognized for authorization or accountability at a particular boundary. **Delegation** grants permission from an authorized owner or principal for named actions within limits.

For INC-0241, the service owner permits saved-material inspection, comparison, candidate recording and a proposal during the 30-minute window. Source-data changes, activation and closure need their own authority.

<a id="docs-agent-heading-3"></a>

### Prepare a temporary session

Session 12 brings one temporary machine-agent instance together with its assignment, policies, permissions, views and working memory. Its **Context View** selects the governing definition, S1, E12, account, filters and investigation records. An Ontology View supplies relevant concepts and connections, including the observation’s trail. Both identify exact source versions and use conditions.

The Coordination Context gives that selection a purpose: one product, the repair project and its primary goal. Definitions, record contracts and current delegation then govern how the agent uses the material.

<a id="figure-agent-session"></a>

![The Northstar agent session and its durable project records](../assets/diagram-37f7c62c3136.svg)

**Diagram labels:** PROJECT STATE · saved outside the agent · Northstar observation · candidate revision 8 · decisions · evidence · Separate histories of changes and their acceptance · Context View 3 · Snapshot S1 · output E12 · rules Usable at start; later expired · Ontology View · Investigation records and source trail from a consistent ontology cut · MACHINE AGENT SESSION 12 · temporary · Agent instance · Investigation assignment Separate delegation · Actions and tools · Compare identifiers Record result and limits · Session Memory · Working notes only Cleared on termination · Useful output → authorized recording → project records with their own standing

### Read this diagram as text

Project State keeps the observation, candidate revision 8, decisions and evidence. Context View 3 and an Ontology View select exact information for session 12. The session binds a temporary agent instance to its assignment, delegation, actions and working memory. When view 3 expires, the agent needs a checked replacement and current permission before continuing.

- PROJECT STATE · saved outside the agent
- Northstar observation · candidate revision 8 · decisions · evidence
- Separate histories of changes and their acceptance
- Context View 3
- Snapshot S1 · output E12 · rules Usable at start; later expired
- Ontology View
- Investigation records and source trail from a consistent ontology cut
- MACHINE AGENT SESSION 12 · temporary
- Agent instance
- Investigation assignment Separate delegation
- Actions and tools
- Compare identifiers Record result and limits
- Session Memory
- Working notes only Cleared on termination

Figure 06 The instance and working memory end with the session. The recorded investigation survives with its own standing, and later sessions obtain new checked views.

Future sessions recover knowledge from saved Project State and its views. Working memory belongs to one session.

<a id="docs-agent-heading-4"></a>

### Follow the same session through time

Agent · Session 12

1. 09:45

   **Prepare session 12**

   The assignment identifies the investigation Work item. At this point, task view 3 is usable and the owner’s 30-minute delegation is current.
2. 09:55

   **Record what the comparison establishes**

   Method 2 finds 200 required identifiers missing from E12. The agent saves the observation, the sources used and the limits of the result.
3. 10:03

   **Retain the proposed change as a candidate**

   Revision 8 is ready for assessment. We still need evidence of its efficacy and the separate decisions for adoption and activation.
4. 10:10

   **Pause when task view 3 expires**

   The agent needs a newly checked view and current delegation to continue. Keep the expired view in the history so the earlier work stays inspectable.

The next session starts with a new machine-agent instance and empty working memory. Bind its assignment and current permission, then recover the saved investigation through new Context and Ontology Views.

### What survives when the session ends?

Session Memory

<a id="session-note"></a>

Working note: “Compare E12 with the required identifiers for Northstar in snapshot S1, keeping the filters explicit.”

<a id="session-status"></a>

Temporary · current session only

Project State

Saved observation, evidence, candidate revision 8, decisions and histories.

Saved outside the agent · available to later sessions

<a id="session-explanation"></a>

This demonstration clears only the example note on this page. It does not close a real Lab session.

<a id="docs-agent-heading-5"></a>

### Carry knowledge into the next session

When the machine-agent session ends, the instance ends and working memory clears. Useful outputs enter the authorized recording route with their own standing. The observation, candidate assessment and proposed revision 8 survive there as recorded work, without becoming an accepted repair.

A later instance starts with empty working memory and new Context and Ontology Views of saved Project State.

At the latest checkpoint, view 3 has expired. Continuing needs a newly checked selection and current permission. The replacement preserves the earlier view’s history and leaves the delegation window unchanged. Meaning, sources, state and permission still answer separate questions.

### Definitions and sources

[Actor](../reference/records/def-cal-definition-actor.md#def-cal-definition-actor) · [Principal](../reference/records/def-cal-definition-principal.md#def-cal-definition-principal) · [Role](../reference/records/def-cal-definition-role.md#def-cal-definition-role) · [Agent Profile](../reference/records/def-cal-definition-agent-profile.md#def-cal-definition-agent-profile) · [Agent Instance](../reference/records/def-cal-definition-agent-instance.md#def-cal-definition-agent-instance) · [Delegation](../reference/records/def-cal-definition-delegation.md#def-cal-definition-delegation) · [Agent Session](../reference/records/def-cal-definition-agent-session.md#def-cal-definition-agent-session) · [Session Memory](../reference/records/def-cal-definition-session-memory.md#def-cal-definition-session-memory) · [Tool](../reference/records/def-cal-definition-tool.md#def-cal-definition-tool)

- [Local runtime implementation overview](../assets/78623efb7024-README.md)
- [Local runtime: temporary agent sessions](../assets/9e96494cfe22-session.py)
