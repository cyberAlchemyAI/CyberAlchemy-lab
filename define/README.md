# Define

Define helps people and agents clarify the meaning a piece of work depends on. It keeps the goal, originating intent, context, required concepts, sources, owners and unresolved questions together in a **Definition Pack**. Planning, research, design and implementation can each consume a pack for a stated use.

The source package is an **imported private candidate** from CyberAlchemy v2, captured on **11 October 2026**. Its original identities, owners, fingerprints and receipts are preserved. A separate [Lab-owned candidate CLI](../implementation/define-cli/v1/README.md) now reuses the Lab's context, ontology and review interfaces.

```bash
./define/define doctor
./define/define chat 'Investigate missing rows in an account export'
```

For a model-free workflow and actual Alch/Craft compilation, follow the [incident example](../implementation/define-cli/v1/README.md#prepare-and-compile-an-incident-example).

## Read the package

| Start with | What it explains |
| --- | --- |
| [Define overview](source/cyberAlchemy-v2/define/README.md) | The problem, vocabulary, output and package structure. |
| [Capability](source/cyberAlchemy-v2/define/docs/DEFINE.md) | When Define is useful and where its responsibility ends. |
| [Definition Pack contract](source/cyberAlchemy-v2/define/docs/DEFINITION-PACK.md) | Required content, concept dispositions and acceptance checks. |
| [Authority](source/cyberAlchemy-v2/define/docs/AUTHORITY.md) | Owners, allowed decisions and blocked effects. |
| [Lifecycle](source/cyberAlchemy-v2/define/docs/LIFECYCLE.md) | How clarification, review and reuse develop over time. |
| [Interaction](source/cyberAlchemy-v2/define/docs/INTERACTION.md) | How the agent asks, proposes and preserves human review. |
| [Working Lab CLI](../implementation/define-cli/v1/README.md) | Commands, current dependencies, candidate outputs and verification. |
| [Complete audit](../implementation/define-cli/v1/AUDIT.md) | Source structure, validator findings, dependency resolutions and remaining model boundaries. |
| [Lab integration and remaining gaps](INTEGRATION.md) | What was imported, what already existed and what remains to connect. |

## The workflow

```text
Goal + originating intent + context
                 ↓
Find the concepts and their owned sources
                 ↓
For each concept: reuse / specialize / propose / open
                 ↓
Review the exact meaning, evidence, boundaries and open questions
                 ↓
Definition Pack for one named consumer and intended use
                 ↓
The consumer follows its own review and authority route
```

For example, an incident investigator needs to know what “complete export” means for one account, filter set and source snapshot. Define can locate a suitable definition, narrow an existing definition to that context, propose a missing meaning, or keep the ambiguity open. The resulting pack records which choice was made and who owns it. It does not close the incident, approve a repair or grant execution permission.

For the Lab's own record format and review requirements, follow [Prepare a definition for review](../docs/lab/how-to/prepare-definition.md). The source Define schema and the Lab's Definition contract are separate contracts; copying their files does not establish compatibility.

## What's here

- **260 Define files:** 25 declared parent material files, two ontology children, the capability contracts and obligations, source receipts and supporting review/intake history.
- **763 CLI files:** host adapters, Alch declarations, generated projections, schemas, implementation bindings, documentation, fixtures and existing test sources. Tests were copied as source and were not run during this import.
- **Model:** 13 business concepts / 12 relations; 65 system concepts / 131 relations; two bridge concepts / 13 relations. These are separately owned models, not one globally normalized Lab graph.
- **Meaning registries:** four package-vocabulary proposals, eleven canonical v2 source bindings and twenty handled-definition records. None are newly admitted Lab definitions.

The exact bytes live in `source/cyberAlchemy-v2/`, retaining the source's package-relative layout. [import.json](import.json) provides the machine-readable entry point. The [file manifest](../evidence/migrations/cyberalchemy-v2-to-lab/executions/0080-define-package-import/manifest.json) identifies every copied file and SHA-256 digest. Review/intake history and receipts remain evidence; they are not part of the parent's declared 25-file material set.

## Current standing

Import integrity passes for all **1,023 files**. The separate successor has a verified selected runtime closure and candidate regression evidence. Its [runtime binding](runtime.json) points to current commands and audit artifacts. The source import metadata remains a historical record.

The upstream package validator still reports stale source fingerprints and the system child's wider compilation gap. The successor uses its own exact provider bindings; it does not rewrite those historical claims. Local CLI readiness does not admit a definition or select repository runtime adoption.

[Lab documentation](../docs/lab/README.md) · [Integration report](INTEGRATION.md) · [Import evidence](../evidence/migrations/cyberalchemy-v2-to-lab/executions/0080-define-package-import/README.md)
