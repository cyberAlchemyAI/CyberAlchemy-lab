# Complete task DAG

Status: proposed dependencies; authority effect: none. [dag.json](dag.json) is the machine dependency source. Edges mean accepted upstream evidence, not global semantic Relation Kinds. Owner nodes require actual exact dispositions; no simulated approval.

```mermaid
flowchart TD
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
  C10["C10: Exact successor admission decision"]
  C11["C11: Explicit operational branch provisioning"]
  C12["C12: First real Work with selected durable evidence"]
  C13["C13: Repeatable-operation milestone closure"]
  C14["C14: Complete typed extension admissibility"]
  W01["W01: Integrated workflow transition contracts"]
  W02["W02: Bounded actor authority and tool dispatch"]
  W03["W03: Engineering workflow implementation"]
  W04["W04: Research and experiment workflow implementation"]
  W05["W05: Evidence, classification, failure and challenge"]
  W06["W06: Operational lesson selection and application"]
  W07["W07: Integrated workflow validation"]
  W08["W08: Exact integrated workflow review"]
  W09["W09: Real integrated work and learning closure"]
  O01["O01: Lab ontology mapping and coverage contract"]
  O02["O02: Lab ontology lifecycle adapter"]
  O03["O03: Three-lens queries, freshness and coverage"]
  O04["O04: Selected source migration inventory and disposition"]
  O05["O05: Selected import and adaptation construction"]
  O06["O06: Exact ontology and selected migration review"]
  O07["O07: Selected ontology and migration coherence closure"]
  R01["R01: Lab Product acceptance and release scope"]
  R02["R02: Install, upgrade, export and recovery packaging"]
  R03["R03: Coherent operator inspection and review surface"]
  R04["R04: Capability realization, adoption and conformance"]
  R05["R05: Bounded real Product pilot"]
  R06["R06: Exact private/public boundary review"]
  R07["R07: Stable candidate validation and final audits"]
  R08["R08: Exact stable v1.0.0 release decision"]
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
  C09 --> C10
  C10 --> C11
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
  R07 --> R08
```
