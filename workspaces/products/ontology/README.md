# Ontology workspace

## Current workspace layout

This Product has one canonical home. Its Project coordination and Work stay here. The current profile is [WORKSPACE.json](WORKSPACE.json); model selection is [authority/workspace-model-binding.json](authority/workspace-model-binding.json).

 | Area | Responsibility |
 | --- | --- |
 | [product/](product/) | Product identity, capabilities and features |
 | [project/](project/) | Project coordination records |
 | [work/](work/) | Goals, plans, tasks, research and outcomes |
 | [authority/](authority/) | Local contracts, bindings and retained authority records |
 | [ontology/](ontology/) | Product-owned meanings and models |
 | [architecture/](architecture/) | Design, patterns and constraints |
 | [implementation/](implementation/) | Product-owned executable source |
 | [docs/](docs/) | Explanations and reference documentation |

Shared operations and execution are selected from the Lab; no runtime is installed or copied into this workspace. Use this workspace path directly.


This Product has one home containing Product records, Project coordination, Work, authority selections, ontology, architecture, implementation and docs. WORKSPACE.json records the physical location and shared Lab references. Original candidate/source standing and historical evidence are preserved.

Implementation packages are [ontology-package](implementation/ontology-package/) and [ontology-lifecycle](implementation/ontology-lifecycle/). The Project identity stays in its upstream carrier, selected by [reference](project/lifecycle-project.ref.json). Both packages use existing shared Rust tools; their historical validation receipts remain historical.
