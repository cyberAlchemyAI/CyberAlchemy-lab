# Roadmap traceability

| Roadmap layer | Full analysis | Construction and integration tasks | Milestone join |
| --- | --- | --- | --- |
| L0 | [ANALYSIS.md](../../ANALYSIS.md) | B00, B01 | B00 |
| L1 | [ANALYSIS.md](../../ANALYSIS.md) | C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14 | C13 |
| L2 | [ANALYSIS.md](../../ANALYSIS.md) | W01, W02, W03, W04, W05, W06, W07, W08, W09 | W09 |
| L3 | [ANALYSIS.md](../../ANALYSIS.md) | O01, O02, O03, O04, O05, O06, O07 | O07 |
| L4 | [ANALYSIS.md](../../ANALYSIS.md) | R01, R02, R03, R04, R05, R06, R07, R08 | R08 |

Every current carrier and Relation Kind is mapped in [contract-coverage.json](../../contract-coverage.json). Every task maps to one layer and linked contract; every SWU has one parent. Each named rule/negative scenario must be represented by its execution evidence before a node closes. The DAG is a workflow dependency model; its arrows do not declare semantic global relations.
