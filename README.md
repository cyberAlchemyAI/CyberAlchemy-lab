# CyberAlchemy Lab

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

The [complete documentation website](website/README.md) is maintained in this
repository with its templates, assets, Craft article and shared search. Build
it with `python3 website/build.py` after installing `website/requirements.txt`.
The result is a portable static site in `website/dist/`; see the
[deployment instructions](website/DEPLOYMENT.md) for hosting and the optional
manual GitHub Pages workflow.

The [Define package](define/README.md) includes an unchanged source snapshot and
a [working candidate CLI](implementation/define-cli/v1/README.md). Run
`./define/define doctor` to inspect its selected dependencies and current Lab
context. See [the integration audit](implementation/define-cli/v1/AUDIT.md) for
verification and the boundary between candidate preparation and admission.

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

See the [complete repository file index](.arcanum/inventory/index.md) and its
[path and digest manifest](.arcanum/inventory/inventory.json). The [content
map](.arcanum/inventory/content-map.jsonl.gz) outlines each file's internal
structure, and the generated SQLite index supports full-text search. Refresh
or validate the path index with `python3 tooling/inventory/build_inventory.py`.

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

The [local operational runtime v1 is admitted](implementation/lab-runtime/ADMISSION.md)
by [Decision 0075](docs/decisions/0075-lab-operational-runtime-v1-admission/DECISION.md).
It reads its frozen D74 repository foundation, manages exact authorized
transactions in a separately identified local store, and prepares ephemeral
Agent context. Its reviewed files and evidence remain unchanged.

The current repository state is [D75](authority/project-state-transitions/current.json).
A [v2 source-profile candidate](implementation/lab-runtime/v2/REVIEW.md) now
integrates D75 for review, with its own source inspection and
transaction/recovery regression evidence. The frozen admitted v1 profile
continues to report its D74 scope.

Inspect the executable's D74 foundation from repository root:

```bash
python3 implementation/lab-runtime/v1/lab.py status
python3 implementation/lab-runtime/v1/lab.py query Lifecycle
```

Inspect the candidate's D75 foundation:

```bash
python3 implementation/lab-runtime/v2/lab.py status
python3 implementation/lab-runtime/v2/lab.py inspect implementation:cyberalchemy-lab:operational-runtime:v1 --record
```
