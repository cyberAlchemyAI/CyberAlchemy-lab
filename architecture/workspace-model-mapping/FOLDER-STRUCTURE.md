<!-- GENERATED from inventory/workspace-catalog.json by inventory/check_workspaces.py --render. -->

# Current folder structure

One Product has one operating home containing Product records, Project coordination, Work and the other five responsibilities. The physical directory migration is applied. Old paths are compatibility links to these homes; they contain no duplicate source trees.

```text
CyberAlchemy-lab/                       # Lab Product Workspace
├── product/
├── project/
│   └── definition-formal-assurance/     # Existing Project records
├── work/
│   ├── goals/
│   ├── plans/
│   │   ├── definition-formal-assurance/
│   │   └── relational-theorem-checker/   # Workstream; no invented Project
│   ├── tasks/
│   ├── research/
│   ├── experiments/
│   ├── blockers/
│   └── outcomes/
├── authority/
├── ontology/
├── architecture/
├── implementation/                     # SHARED LAB OPERATIONS
│   ├── lab-bootstrap/
│   ├── lab-provisioning/
│   ├── lab-runtime/
│   ├── lab-context/
│   ├── lab-work/
│   ├── lab-workflows/
│   ├── lab-review/
│   ├── lab-continuity/
│   ├── lab-ontology/
│   ├── lab-integration/
│   └── lab-workspaces/
├── docs/
├── workspaces/
│   ├── products/
│   │   ├── craft/
│   │   │   ├── product/
│   │   │   ├── project/  # Craft Project stays here
│   │   │   ├── work/
│   │   │   ├── authority/
│   │   │   ├── ontology/
│   │   │   ├── architecture/
│   │   │   ├── implementation/
│   │   │   └── docs/
│   │   ├── define/
│   │   │   ├── product/
│   │   │   ├── project/
│   │   │   ├── work/
│   │   │   ├── authority/
│   │   │   ├── ontology/
│   │   │   ├── architecture/
│   │   │   ├── implementation/
│   │   │   └── docs/
│   │   ├── ontology/
│   │   │   ├── product/
│   │   │   ├── project/  # Ontology Lifecycle Project stays here
│   │   │   ├── work/
│   │   │   ├── authority/
│   │   │   ├── ontology/
│   │   │   ├── architecture/
│   │   │   ├── implementation/
│   │   │   │   ├── ontology-package/
│   │   │   │   └── ontology-lifecycle/
│   │   │   └── docs/
│   │   ├── people-and-teams/
│   │   │   ├── product/
│   │   │   ├── project/
│   │   │   ├── work/
│   │   │   ├── authority/
│   │   │   ├── ontology/
│   │   │   ├── architecture/
│   │   │   ├── implementation/
│   │   │   └── docs/
│   │   ├── lab-website/
│   │   │   ├── product/
│   │   │   ├── project/
│   │   │   ├── work/
│   │   │   ├── authority/
│   │   │   ├── ontology/
│   │   │   ├── architecture/
│   │   │   ├── implementation/
│   │   │   └── docs/
│   │   └── trusted-dataset-materialization/
│   │       ├── product/
│   │       ├── project/
│   │       ├── work/
│   │       ├── authority/
│   │       ├── ontology/
│   │       ├── architecture/
│   │       ├── implementation/
│   │       └── docs/
│   └── projects/                        # Reserved; no standalone workspace selected
├── evidence/                            # Retained exact history and source evidence
├── tooling/
├── tests/
└── .local/                              # Private selected execution state
```

The root is the CyberAlchemy Lab Product Workspace. The six nested Product homes plus the referenced Agent Reasoning Engine scope give eight Product catalog entries in total. ARE is a catalog reference to upstream implementation; no copied local ARE directory is proposed.

Shared operations live in the root implementation directory. Product-owned capability code stays in its owning Product implementation directory and is consumed through selected bindings. Central execution does not require duplicating that code or installing a runtime in every workspace.

Each Work area can contain goals, plans, tasks, research, experiments, blockers and outcomes. A Project-owned Goal keeps its existing Project reference even when all these records share one Product workspace.

No standalone Project Workspace is currently selected. Craft coordination stays in Craft; lifecycle coordination stays in Ontology; Definition Formal Assurance stays in Lab. The relational theorem-checker plan stays Lab Work, referencing existing Craft formalization source without transferring its ownership.

The existing external homes stay separate:

```text
projects/
├── CyberAlchemy-lab/
├── body-war/                 # TROQAR Product, coordination and Work
├── engineer-assessment/      # Product and research Project/Work
└── agentic-research-network/ # Product and modelling Project/Work
```

Definition NFT and Lab migration remain removed from active workspace planning. Historical evidence stays retained. The current typed successor is lab-workspace-model/v2, selected by implementation/lab-workspaces/CURRENT.json and executed through implementation/lab-runtime/lab.py. The older Project-only candidate remains exact historical evidence.

- [Current workspace catalog](WORKSPACES.md)
- [One Product home rule and exact record placement](PRODUCT-COLOCATION.md)
