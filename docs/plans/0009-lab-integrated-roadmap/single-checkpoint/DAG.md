# Proposed single-checkpoint DAG

Status: proposed analysis variant; no execution authority. Original roadmap remains preserved. **One human checkpoint at R08; application and operational verification follow it.**

```mermaid
flowchart TD
  subgraph preparation["Preparation"]
    B00["B00: Scoped foundation proof"]
    B01["B01: Whole-Lab source and contract analysis"]
    C01["C01: Independent source-profile contract"]
    C02["C02: Contract and reference impact matrix"]
    C03["C03: Replay and context measurements"]
    C04["C04: Explicit profile selection and capture"]
    C05["C05: Successor-branch transition"]
    C06["C06: Measured replay reuse with full verifier"]
    C07["C07: Local-result promotion and repository publisher"]
    C08["C08: Exact context and generator provenance"]
    C09["C09: Successor integration validation and example"]
    C10["C10: Prepare exact successor admission members"]
    C11["C11: Rehearse candidate provisioning; prepare operational scope"]
    C12["C12: Perform genuine bounded candidate Work"]
    C13["C13: Verify candidate continuity and fresh session"]
    C14["C14: Complete typed extension admissibility"]
    W01["W01: Integrated workflow transition contracts"]
    W02["W02: Bounded actor authority and tool dispatch"]
    W03["W03: Engineering workflow implementation"]
    W04["W04: Research and experiment workflow implementation"]
    W05["W05: Evidence, classification, failure and challenge"]
    W06["W06: Operational lesson selection and application"]
    W07["W07: Integrated workflow validation"]
    W08["W08: Prepare workflow admission members"]
    W09["W09: Exercise candidate workflows and later lesson application"]
    O01["O01: Lab ontology mapping and coverage contract"]
    O02["O02: Lab ontology lifecycle adapter"]
    O03["O03: Three-lens queries, freshness and coverage"]
    O04["O04: Selected source migration inventory and disposition"]
    O05["O05: Selected import and adaptation construction"]
    O06["O06: Prepare ontology and selected import admission members"]
    O07["O07: Verify candidate ontology and selected migration coherence"]
    R01["R01: Lab Product acceptance and release scope"]
    R02["R02: Install, upgrade, export and recovery packaging"]
    R03["R03: Coherent operator inspection and review surface"]
    R04["R04: Assess candidate realization/adoption/conformance"]
    R05["R05: Run authorized genuine candidate Product pilot"]
    R06["R06: Exact private/public boundary review"]
    R07["R07: Validate exact candidate release and all-member review closure"]
    S01["S01: Candidate closure composer and bootstrap proof"]
    S02["S02: Freeze package and verify final review readiness"]
  end
  subgraph checkpoint["Checkpoint"]
    R08["R08: One final owner checkpoint for the exact complete package"]
  end
  subgraph application["Application"]
    A01["A01: Apply exact authorized repository admission"]
    A02["A02: Execute independently scoped local operational instructions"]
    A03["A03: Verify original admitted operational milestone obligations"]
    A04["A04: Complete selected release effects or report blocked release"]
  end
  B00 --> B01
  B01 --> C01
  B01 --> C02
  B01 --> C03
  C01 --> C04
  C02 --> C04
  C04 --> C05
  C03 --> C06
  C04 --> C06
  C02 --> C07
  C04 --> C07
  C14 --> C07
  C02 --> C08
  C04 --> C08
  C05 --> C09
  C06 --> C09
  C07 --> C09
  C08 --> C09
  C14 --> C09
  S01 --> C09
  C09 --> C10
  C10 --> C11
  S01 --> C11
  C11 --> C12
  C12 --> C13
  C02 --> C14
  C04 --> C14
  C02 --> W01
  W01 --> W02
  C13 --> W02
  W01 --> W03
  W02 --> W03
  W01 --> W04
  W02 --> W04
  W01 --> W05
  W02 --> W05
  W05 --> W06
  C08 --> W06
  W03 --> W07
  W04 --> W07
  W06 --> W07
  W07 --> W08
  W08 --> W09
  C13 --> W09
  B01 --> O01
  C02 --> O01
  O01 --> O02
  C13 --> O02
  W05 --> O02
  O01 --> O03
  C08 --> O03
  O01 --> O04
  C07 --> O04
  O04 --> O05
  O02 --> O05
  O05 --> O06
  O03 --> O06
  W09 --> O06
  O06 --> O07
  W09 --> O07
  B01 --> R01
  R01 --> R02
  C13 --> R02
  R01 --> R03
  C13 --> R03
  W01 --> R03
  R01 --> R04
  W09 --> R04
  O07 --> R04
  R02 --> R05
  R03 --> R05
  R04 --> R05
  O07 --> R05
  R01 --> R06
  R02 --> R06
  O04 --> R06
  R05 --> R07
  R06 --> R07
  S02 --> R08
  C02 --> S01
  C04 --> S01
  C14 --> S01
  C10 --> S02
  W08 --> S02
  O06 --> S02
  R07 --> S02
  R08 --> A01
  A01 --> A02
  A02 --> A03
  A03 --> A04
  classDef approval fill:#ffe6a7,stroke:#835b00,stroke-width:3px
  class R08 approval
```

## Reading the graph

C10, W08 and O06 prepare exact member Decisions. They confer no authority on downstream candidate work. C11–C13, W09, O07 and R04–R05 supply candidate evidence in the pre-approval branch; actual admitted obligations remain at A02/A03. S01 supplies the missing isolated candidate bootstrap. S02 closes final targets, carrier fit and evidence.

A04 is a guarded selected release disposition: a required new semantic Decision, missing admitted pilot evidence or unrepresentable conditional authorization blocks full release. Internal quality gates and all original semantic/evidence criteria remain.

The [machine graph](dag.json) maps all 40 original tasks and adds six explicitly scoped integration nodes (46 total). The [transformation matrix](task-transformation.json) retains each original acceptance criterion. Original SWUs need phase reconciliation before execution; this is not an authorized execution pack.
