# CyberAlchemy Lab documentation

CyberAlchemy is a system for organizing knowledge and work. Definitions give us a starting point. The Lab connects those meanings to projects, work, evidence and decisions, so people and temporary AI agents can recover what applies and continue from saved project knowledge.

You can read this edition in a checkout, an editor or a Git repository viewer. Open the documents directly. Reading requires no website or build step.

## Start here

1. [Understand the Lab](start-here.md): definitions, the three governance questions, purpose, work and agents.
2. [Follow an incident](tutorials/incident-walkthrough.md): a concrete investigation from reported omission to proposed assessment and owner review.
3. [Compare the concepts](concepts/comparisons.md): distinguish meanings, records, evidence, work, views and permissions.
4. [Read the complete guide](guide/README.md): the governance model and the rest of the Lab model.

The incident is fictional. Its examples help explain the records and their responsibilities. They have not been admitted into Project State.

## Understand the model

| Question | Read |
| --- | --- |
| What is the company brain? | [Knowledge, work, decisions, people and agents](company-brain.md) |
| Why build it? | [The product's purpose and its connection to alignment research](why-a-company-brain.md) |
| What governs meaning and action? | [Authority](guide/authority.md) |
| Where did a claim come from? | [Provenance](guide/provenance.md) |
| What can change from here? | [Lifecycle](guide/lifecycle.md) |
| How do intent, product, project and work fit together? | [Purpose and work](guide/intent-product-project.md) |
| How are records connected? | [Definitions, formats and declared connections](guide/records-and-connections.md) |
| What does an agent remember? | [Temporary sessions and durable Project State](guide/agents-and-memory.md) |
| How can experience improve later work? | [Operational learning](guide/operational-learning.md) |
| What does the inspected implementation establish? | [Operational scope](guide/operational-scope.md) |

[Explore the diagrams](guide/system-map.md), [read the eight expanded essays](essays/README.md), or [read about the research lab and its culture](research-and-culture.md).

## Follow a practical task

- [Read a record and establish its standing](how-to/read-a-record.md).
- [Prepare an incident assessment](how-to/prepare-incident-assessment.md).
- [Prepare a definition for owner review](how-to/prepare-definition.md).
- [Recover context and resume agent work](how-to/resume-agent-work.md).
- [Inspect complete record and connection examples](reference/record-examples.md).

The [Define package](../../define/README.md) provides the preserved source model
and a [working candidate CLI](../../implementation/define-cli/v1/README.md) for
clarifying the meanings needed by work. Follow [Use Define](how-to/use-define.md)
for commands. The [integration audit](../../implementation/define-cli/v1/AUDIT.md)
separates verified local behavior from meaning acceptance and runtime adoption.

These guides help you prepare material and inspect its basis. Acceptance and permission still come from the authorized owner and applicable contracts.

## Find an exact meaning or contract

The [reference library](reference/README.md) contains the reviewed explanations, governing statements, boundaries, required fields and declared connection patterns from the documentation's selected source snapshot. Entries link to the repository's original records and schemas.

For the repository's current authority selection, begin with the [canonical Definition index](../../authority/definitions/DEFINITIONS-INDEX.md), [governance module index](../../authority/governance/README.md), and [current Project State lookup](../../authority/project-state-transitions/current.json). Authored candidate labels, effective acceptance and current selection are separate facts.

## Craft within the Lab

[Craft's model](craft/model.md) explains software design within the wider Lab: Rules evaluate conditions, Calculations derive values, Queries retrieve information and Operations change business state. The capacity Calculation and capacity-reservation Operation preserve those separate responsibilities.

For implementation instructions, use the repository's [Craft entry point](../../craft/README.md) and [CLI documentation](../../craft/impl/cli/README.md).

## Documentation and current operation

This explanatory edition was refreshed on **12 October 2026**, using the adopted natural editorial voice. The reference catalog and source-based operational discussion retain their **8 October 2026** capture scope. The prose update changes no admitted definition, schema, decision or runtime profile.

For current planning and operation, consult the [roadmap](../ROADMAP.md), [admitted local runtime instructions](../../implementation/lab-runtime/v1/README.md), and [candidate runtime review](../../implementation/lab-runtime/v2/REVIEW.md).

[Sources and research](sources.md) · [Maintaining this edition](MAINTENANCE.md) · [Import manifest](IMPORT-MANIFEST.json)
