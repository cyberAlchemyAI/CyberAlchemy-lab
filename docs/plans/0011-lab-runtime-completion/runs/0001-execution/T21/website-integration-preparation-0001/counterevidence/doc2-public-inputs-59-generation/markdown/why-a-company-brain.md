[Documentation home](README.md)

<a id="company-brain"></a>

CyberAlchemy Lab / Why we are building it

# A company brain for work with AI.

Keep the meanings, evidence and decisions behind work available to whoever continues it, including the next agent.

6 minute read

[Explore the documentation](start-here.md)

<a id="continuity"></a>

<a id="continuity-title"></a>

## The work continues. The context has to continue too.

A customer reports a problem. Someone reads logs, forms a hypothesis and proposes a change. A colleague returns the following morning and needs to recover the basis: the data examined, what “fixed” means, why the proposal exists and who can approve it. That recovery is work in its own right.

An agent session can leave code, an assessment or a plan. The next session needs an account of its meaning and status. A connected record lets a reviewer examine the basis of the explanation, rather than depend on how convincing it sounds.

We’re building the Lab for software, research and operations teams coordinating people and agents across projects. Continuity is part of their work.

<a id="company-knowledge"></a>

<a id="company-knowledge-title"></a>

## Give the company’s knowledge a structure it can use.

We call the Lab an **open-source company brain system**. The ambition is practical: connect knowledge to the work it informs with enough structure for people and machines to inspect it.

That knowledge includes important meanings, project intentions, evidence gathered and decisions changing what is accepted. Records and declared connections give those facts identifiable places.

When reading a saved explanation, we still need to understand its role. Is it defining a meaning, recording an observation, proposing a change or authorizing an effect? Those roles have different requirements and limits on use.

<a id="governed-work"></a>

<a id="governed-work-title"></a>

## Knowledge that can guide work.

The Lab starts with definitions. “Complete,” “valid” and “recovered” need boundaries when work depends on them. An accountable owner accepts an exact meaning within scope; the associated record format governs its representation.

**Authority**

Which accepted meanings and rules apply, and who may act within which scope?

**Provenance**

Where did this information come from, and how was it produced?

**Lifecycle**

What state is this record in, and what conditions allow it to change?

Now a team has a basis for examining the claim and response. Evidence supports the assessment. An accountable decision authorizes a change. A proposed fix stays proposed until its applicable route is completed.

Intent gives the work a purpose. Product identifies a continuing offering, Project coordinates a bounded effort, and Work records its attempts. Individual tasks can then move ahead while their purpose remains recoverable.

<a id="incident"></a>

<a id="incident-title"></a>

## An incident, examined.

In the fictional Northstar case, a customer reports missing export records. The agent’s bounded investigation covers saved sources, output and logs, identifier comparison, candidate assessment material and a proposal.

Declared input**10,000** required identifiers 

Account Northstar,
status = active, fixed snapshot S1.

Saved output**9,800** identifiers present 

Inspect the saved export
E12, from run 12.

Observed difference**200** required identifiers missing 

Enough to establish an omission
in this output.

A fictional comparison, used to explain the model. The source and output identities stay attached to the assessment.

The completeness definition fixes account, filters and snapshot. That lets the comparison establish a scoped omission. Cause, wider impact and recovery still need investigation.

The assignment identifies investigation. Permission to change source data, deploy a fix, accept a definition or close the incident has to come from the relevant authority route.

A reviewer can follow the criterion, inputs, comparison and proposal. Each part has a basis to examine. The [full walkthrough](tutorials/incident-walkthrough.md) follows that account.

<a id="agent-memory"></a>

<a id="agent-memory-title"></a>

## What the next agent inherits.

A machine agent is temporary, with working memory belonging to its session. Project State retains the meanings, work, evidence and decisions another session needs.

Session A**Investigate & record** Short-term session memory

Project state**Continuing knowledge** Recorded work, evidence & decisions

Session B**Recover & continue** Fresh context, checked permissions

A session handoff. Records persist; a new session obtains the relevant context rather than inheriting an agent’s private memory.

Each session gets a task-specific Context View and a relevant Ontology View. Both derive from Project State and declare use conditions. If a view expires, the agent refreshes or pauses. Continuing needs usable information and current permission.

Learning is another question to examine. A saved lesson can be tried in later work. To claim improvement, we need evidence of actual use and an assessment of the resulting benefit.

<a id="alignment"></a>

<a id="alignment-title"></a>

## A practical setting for the alignment question.

AI alignment examines whether behavior follows human intentions and values. Expressing those fully is difficult, and people disagree. Training, evaluation and control are parts of that research. [Ji et al., AI Alignment: A Comprehensive Survey](https://arxiv.org/abs/2310.19852)

The Lab gives us a setting for some of those questions. Do clearer meanings reduce misunderstandings? Would bounded permissions and visible evidence help expose a bad action sooner? Can Project State preserve corrections as agents change?

We can formulate and test those questions. Governance records make intentions and decisions inspectable. Actual behavior needs evaluation under changing conditions, adversarial exercises and oversight. These are complementary lines of research. [Anthropic’s alignment research](https://www.anthropic.com/research/team/alignment)

More general intelligence is part of the ambition. As capabilities grow, we need better ways to express direction, examine behavior and change course.

<a id="begin"></a>

<a id="begin-title"></a>

## Begin with one piece of work.

Choose a project where people keep rebuilding context. Ask what its important words mean, what supports current claims and who is allowed to make the next change. That gives us a concrete place to begin.

The incident, system map and reference library provide routes into the model. For software behavior, the Craft article follows explicit design within the wider Lab.

[Start with the Lab](start-here.md)[Explore the system map](guide/system-map.md#system-map)
