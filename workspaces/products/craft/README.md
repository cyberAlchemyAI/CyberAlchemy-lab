# Craft

Craft helps people turn a business decision into a checked application. The team writes the facts and rules, selects a supported way to build, and reads the result of focused checks. Craft is a CyberAlchemy Product still in development.

The [step-by-step Craft guide](COMPLETE-GUIDE.html) makes this concrete. It follows one Customer Success renewal review from its input and meta types through AlchLang, profiles, a generated application, and a local result. A [Markdown version](COMPLETE-GUIDE.md) is available too.

## Start here

Read the [guide](COMPLETE-GUIDE.html) first. It introduces each term when the example needs it. Then use the [documentation index](docs/README.md) to find the syntax reference, profile authoring, other applications, and contributor commands.

The [capability catalog](product/capabilities/README.md) currently has **proposal-only** standing. Core and AlchLang have local build and focused check paths, while [broader verification](work/outcomes/current-verification/broader-qualification.json) still has failures and pending cases in the wider test derivation suite. The full Craft construction and feedback promise is not yet qualified.

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

Shared operations and execution are selected from the Lab; no runtime is installed or copied into this workspace. Old executable and directory names at the workspace root are compatibility links, not additional source homes. The root guides below are regular files so they can be opened from Windows through the WSL share.

Current executable code is under implementation/. Superseded implementation and formalization trees have been removed. Current research and discovery belong under work/. The pinned Project identity package remains a required shared-runtime input; no older Craft compiler or runtime is retained.


Craft is a Lab subset whose Product, Project, Work, Authority and Ontology follow the Lab model. Current functional source and work definitions are imported; only selected current verification reports are retained.

- [Product](product/README.md)
- [Project](project/README.md)
- [Work](work/README.md)
- [Authority](authority/README.md)
- [Ontology](ontology/README.md)
- [Architecture](architecture/README.md)
- [Implementation](implementation/README.md)
- [Documentation](docs/README.md)

The [documentation index](docs/README.md) is the reader path. The [Markdown guide](COMPLETE-GUIDE.md) follows the same application story. Older imported source records remain available for provenance; their original status labels do not establish current Craft support.

The top-level `craft` path is a Linux compatibility symlink to this directory, not another copy. Current runtime imports and the [workspace migration verifier](../../../tooling/verify_workspace_migration.py) still depend on it. Windows tools that cannot open WSL symlinks should use the real `workspaces/products/craft` path. Dependency links under `implementation/` and `node_modules/` serve the local build and are not documentation copies.

To build or check the relocated source, use the [implementation guide](implementation/README.md). [Current work](work/CURRENT.json) tracks the product's active tasks.

## Existing Lab entry points

The relocated implementation is selected explicitly through `node workspaces/products/craft/implementation/run.mjs` from the Lab root. The shorter `craft/` route is the Linux compatibility symlink; it is not a second Product home. The existing [runtime binding](RUNTIME.json), [runtime validator](validate-runtime.mjs), [legacy implementation](impl) and [formalization](formalization) remain accessible. No global consumer switch or production activation has run.

## Open questions

Production providers and broader runtime qualification remain separate from the local journey. [Ontology source reconciliation](ontology/sources/reconciliation.json) checks the current reviewed functional source selections. Body War is a [reference application](work/experiments/body-war-reference/README.md).

## Workspace location

Canonical Product home: workspaces/products/craft/. Product coordination and Work stay here. Shared operations remain at the Lab root implementation/. Legacy locations are compatibility links, not additional copies. Native definition/admission standing is unchanged.
