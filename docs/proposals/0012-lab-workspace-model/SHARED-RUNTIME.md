# Shared operations and workspace selection

Status: operating-model candidate `1.0.0-candidate.2`, prepared in Define Pack revision 3. Authority effect: none.

The user's correction selects shared capability operations by default. Creating a Lab Workspace creates or binds its scoped records and configuration; it does not require another runtime installation, copied capability implementation or separate storage backend.

| Concern | Shared default | Workspace choice |
| --- | --- | --- |
| Capability operations | Use the central capability implementation | Select a compatible specialized implementation/profile when needed |
| Behavior | Inherit selected shared behavior | Select a workspace specialization; shared execution remains available |
| Execution placement | Use a shared runtime target | Explicitly select a compatible dedicated target |
| Product, Project, Goals and Work | Keep attributable workspace references and records | Evolve local records under their own owners |
| State storage | A common backend may hold multiple workspace scopes | Select separate storage when an operational requirement warrants it |
| Authority | Each operation resolves applicable workspace/action permission | A runtime selection grants no additional permission |

Behavior and placement are independent choices. A specialized profile can run centrally. A dedicated runtime can retain inherited behavior. This first fixture exercises only context budget and operator note specialization; it does not implement arbitrary replacement capability code.

```text
Craft workspace ----------+
Define workspace ---------+--> shared Lab capability operations / runtime
People and Teams workspace+
       |
       +--> optional workspace specialization (can still run centrally)
       +--> optional explicitly selected dedicated runtime
```

The lines illustrate proposed consumers, not actual deployment bindings. Workspace development source may remain in its own implementation area; consuming a capability does not copy that source into each workspace. Root Lab Work evolves shared capabilities, while a workspace's Work evolves its own Product, Project and selected specializations.

## Candidate artifacts

- [Runtime policy](model/runtime-policy.json): shared/inherited defaults and independent optional choices.
- [Selection schema](model/runtime-selection.schema.json): local candidate contract, not an admitted Artifact Type.
- [Craft selection](craft/runtime-selection.json): proposed shared default; no concrete runtime target is selected or provisioned.
- [Reference resolver](runtime_selection.py): configuration checks only, with an explicitly supplied catalog and workspace/Project/scope/revision context.
- [Validation receipt](receipts/validation.json): two workspace scopes select one synthetic shared target; specialization can retain that target; dedicated placement is optional; invalid selections are refused.

The second workspace and runtime catalog are fixture data. Distinct namespace references demonstrate routing intent, not live storage isolation or multi-tenant security. The selected host must enforce actual authorization, state partitioning, concurrency and effect handling before operations can run.

## Evolution and history

The operating model and Craft binding advance to candidate revision 2. The [predecessor records](history/model-r1/INDEX.json), earlier validation receipts and frozen Define Packs remain available. The Workspace Definition remains byte-identical: its durable-scope meaning already separates a workspace from execution. Its original consumer-reference list records the first draft consumers; current consumption is declared by the successor operating model and binding.

Define prepared 16 reused meanings, three local proposals and two open concepts. Formal-symbol fit and semantic-owner acceptance remain open; native owner-review use remains blocked by local-snapshot/current-authority obligations. This update authors the candidate policy and fixture. It does not deploy the central runtime or change existing runtime consumers.
