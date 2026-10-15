# Execution schedule: integrated Lab

Status: proposed; authority effect: none. [Work pack](WORK-PACK.md) owns task/SWU contracts; [DAG](dag.json) owns dependencies. This file schedules them without redefining their meaning.

Planning gate: structurally complete planning contracts. Implementation execution is not authorized by the present analysis request. Exact upstream design, scope and authority gates apply task by task. Complexity: high; baseline wave: W00; active layer: L1; next unit: SWU-C01-01.

## Waves

| Wave | Tasks | Entry | Exit |
| --- | --- | --- | --- |
| [W00](work-pack/waves/W00.md) | B00 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W01](work-pack/waves/W01.md) | B01 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W02](work-pack/waves/W02.md) | C01, C02, C03, R01 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W03](work-pack/waves/W03.md) | C04, W01, O01 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W04](work-pack/waves/W04.md) | C05, C06, C08, C14 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W05](work-pack/waves/W05.md) | C07, O03 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W06](work-pack/waves/W06.md) | C09, O04 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W07](work-pack/waves/W07.md) | C10 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W08](work-pack/waves/W08.md) | C11 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W09](work-pack/waves/W09.md) | C12 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W10](work-pack/waves/W10.md) | C13 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W11](work-pack/waves/W11.md) | W02, R02, R03 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W12](work-pack/waves/W12.md) | W03, W04, W05, R06 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W13](work-pack/waves/W13.md) | W06, O02 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W14](work-pack/waves/W14.md) | W07, O05 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W15](work-pack/waves/W15.md) | W08 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W16](work-pack/waves/W16.md) | W09 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W17](work-pack/waves/W17.md) | O06 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W18](work-pack/waves/W18.md) | O07 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W19](work-pack/waves/W19.md) | R04 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W20](work-pack/waves/W20.md) | R05 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W21](work-pack/waves/W21.md) | R07 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |
| [W22](work-pack/waves/W22.md) | R08 | Upstream accepted evidence and exact task gates | All scheduled SWUs evidenced for their scoped outcomes |

Dependency-independent tasks may be worked in parallel only with disjoint writes or serialized integration. C04/C06/C08 share successor runtime concerns: integrate sequentially before C09. W03/W04/W05 may build separate adapters after W02, then join through W06/W07. O01 and R01 can begin early; O02/O06 and R04/R05 wait for their operational inputs. Wave membership is not permission to spawn agents.

## Delivery stage coverage

| Stage | Planned tasks / evidence |
| --- | --- |
| discover | B00/B01 existing proof and current source/contract analysis |
| design-baseline / specification | C01/C02/W01/O01/O04/R01 |
| scenarios | Each task's negative/edge cases; C09/W07/O07/R07 integrated examples |
| tests | Future authorized validation nodes; none run in this planning request |
| implementation | C04–C08, W02–W06, O02/O03/O05, R02/R03 |
| interface-experience | R03 selected interface and operator journeys |
| telemetry-spec / instrument / verify | C03 per-operation measurement; W02 action receipts; O03 coverage/freshness; R05 declared pilot outcomes |
| deployment | Deferred unless exact selected release/pilot effects require it; no automatic service |
| concept-index-sync | B01 planning coverage/indexes; each future package's closure evidence |
| readiness-review | C09/C10, W07/W08, O06/O07, R07/R08 |
| completion-verify | C13, W09, O07, R07 |
| audit-alignment | Exact contract/reference/typed-axis non-collapse checks at each milestone join |
| audit-layering | Preserved guarantees and explicit deferrals at each milestone join |

All alignment/layering obligations are included in the closure tasks, not waived. Findings add remediation dependencies and invalidate the affected review target; original obligations remain visible. Execution-time sources, task status, wave evidence and SWU results must be synchronized before promotion.
