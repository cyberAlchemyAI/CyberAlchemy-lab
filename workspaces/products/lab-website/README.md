# CyberAlchemy Lab website workspace

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

Shared operations and execution are selected from the Lab; no runtime is installed or copied into this workspace. Old names at the workspace root are compatibility links, not additional source homes.


This Product has one home containing Product records, Project coordination, Work, authority selections, ontology, architecture, implementation and docs. WORKSPACE.json records the physical location and shared Lab references. Original candidate/source standing and historical evidence are preserved.

Current application source is in [implementation/site](implementation/site/). Its existing Python environment is shared at the Lab root .local/shared-environments/lab-website/venv and linked from the site; it was moved, not copied.
