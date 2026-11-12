# CyberAlchemy Lab

The current [workspace model](implementation/lab-workspaces/v2/README.md) uses one canonical home per Product and shared Lab operations. See the [folder structure](architecture/workspace-model-mapping/FOLDER-STRUCTURE.md) and [migration verification](docs/migration-plans/0009-complete-workspace-migration-20261108/REPORT.md).

Run python3 implementation/lab-runtime/lab.py workspace verify to check the selected Product/Project profiles, and python3 tooling/verify_workspace_migration.py to check physical ownership and shared dependency links.


Status: **admitted operational foundation and local runtime v1**
Repository lifecycle: **clean-history successor line**
First stable release target: **v1.0.0**

CyberAlchemy Lab is the new repository in which the first stable CyberAlchemy
line is being developed. It has independent Git history and admits
material deliberately through exact source inventories and owner Decisions.

## Read the documentation

Start with the [Lab documentation](docs/lab/README.md) for a repository-readable
introduction, complete model guide, practical walkthroughs, expanded essays,
reference contracts and Craft's place in the Lab. No website or build step is
required to follow it.

For Craft, start with the [step-by-step application guide](workspaces/products/craft/COMPLETE-GUIDE.html)
through its workspace path. The [documentation index](workspaces/products/craft/docs/README.md)
has the follow-on references.

The [complete documentation website](workspaces/products/lab-website/implementation/site/README.md) is maintained in this
repository with its templates, assets, Craft article and shared search. Build
it with `python3 workspaces/products/lab-website/implementation/site/build.py` after installing
`workspaces/products/lab-website/implementation/site/requirements.txt`.
The result is a portable static site in `workspaces/products/lab-website/implementation/site/dist/`; see the
[deployment instructions](workspaces/products/lab-website/implementation/site/DEPLOYMENT.md) for hosting and the optional
manual GitHub Pages workflow.

The [Define package](workspaces/products/define/README.md) includes a
[working candidate CLI](workspaces/products/define/implementation/cli/alchlang/README.md). Run
`./workspaces/products/define/define doctor` to inspect its selected dependencies and current Lab
context. Its [current implementation guide](workspaces/products/define/implementation/cli/alchlang/README.md) describes verification and the boundary between candidate preparation and admission.

## Foundation boundary

- The repository has a configured `origin` remote and a published checkpoint.
- The initial empty foundation has evolved through admitted imports, semantic
  contracts, operational records, and Project State through Decision 0075.
- `cyberAlchemy-v2` remains an external source and evidence ledger. Its names,
  paths, history, and semantic identities are not renamed by this repository.
- Source evidence does not become CyberAlchemy Lab authority merely by being
  referenced or imported.
- Every future import must have an explicit source, boundary classification,
  selected byte inventory, validation, and owner decision.

## Repository index

Generate the local repository file index and path/digest manifest with
`python3 tooling/inventory/build_inventory.py`. The generated files under
`.arcanum/inventory/` are local navigation outputs and are excluded from Git.
`python3 tooling/inventory/build_content_map.py` also builds content outlines
and the SQLite full-text index. Source navigation and retention are described
in [.arcanum/inventory/README.md](.arcanum/inventory/README.md).

## Stability claim

This initial foundation is **not yet a stable release**. `v1.0.0` is the first
stable release target. That target requires, at minimum:

1. an accepted product and architecture boundary;
2. an accepted authority model and source-admission policy;
3. a completed private/public boundary review;
4. deterministic validation of every admitted release artifact; and
5. an explicit owner release decision for the exact candidate bytes.

Preparation, import, validation, or a release candidate does not by itself
authorize promotion, publication, deployment, or a stable-release claim.

## Next gate

See the [proposed whole-Lab roadmap](docs/ROADMAP.md) for the current state,
five milestones, and the next repeatable-operation milestone.
The [integrated analysis and DAG plan](docs/plans/0009-lab-integrated-roadmap/PLAN.md)
provides implementation reuse analysis, exact task dependencies and work units.

An exact earlier version of the [local operational runtime v1](implementation/lab-runtime/ADMISSION.md)
was admitted by [Decision 0075](docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md).
The symlink-free source resolver in this checkout changes v1 implementation
bytes. That maintenance change is not covered by the earlier admission.

The current repository state is [D75](authority/project-state-transitions/current.json).
A [v2 source-profile candidate](implementation/lab-runtime/v2/REVIEW.md) now
integrates D75 for review, with its own source inspection and
transaction/recovery regression evidence. The v1 profile retains its D74
scope. Both profiles preserve their recorded source names and verify the same
source bytes through the canonical workspace paths. Their `status` commands
report current source freshness; this read does not grant runtime admission.

Inspect the v1 D74 source profile from repository root:

```bash
python3 implementation/lab-runtime/v1/lab.py status
python3 implementation/lab-runtime/v1/lab.py query Lifecycle
```

Inspect the v2 source-profile candidate:

```bash
python3 implementation/lab-runtime/v2/lab.py status
python3 implementation/lab-runtime/v2/lab.py inspect implementation:cyberalchemy-lab:operational-runtime:v1 --record
```

## Product workspaces

The Lab is the root workspace. Each Product has one home under [workspaces/products](workspaces/products/); its Project coordination and Work remain there. Shared operations stay in [implementation](implementation/). Use these canonical workspace paths for source and commands. See the [current folder structure](architecture/workspace-model-mapping/FOLDER-STRUCTURE.md) and [migration report](docs/migration-plans/0008-product-workspaces-20261107/REPORT.md).
