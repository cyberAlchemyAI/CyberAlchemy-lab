# L1 Residue Map

Status: pass

## Residue Table

| ID | Residue | Why it matters | Current owner | Decision | Next route |
| --- | --- | --- | --- | --- | --- |
| R1 | Alloy example is unvalidated | A model sketch is not useful evidence until the Analyzer accepts it and produces expected behavior. | future task-session | open | Install/run Alloy and capture result. |
| R2 | TLA+ example is unvalidated | TLC result is needed before the tower can claim even finite-model confidence. | future task-session | open | Install/run `tla2tools.jar` and capture result. |
| R3 | `orchestrates` signature is strained for Saga | Current relationship vocabulary says Workflow -> Operation[], but the saga pilot needs Saga coordination. | definitions-governance | open | Decide whether Saga specializes Workflow or needs an explicit edge. |
| R4 | No generated fixture contract exists | Manual Alloy/TLA sketches can drift from DomainSpec data. | implementation-readiness | open | Define JSON shape emitted from TypeScript `SagaSpec`. |
| R5 | Fairness/liveness boundary is not chosen | Some retry/dead-letter obligations may need liveness, not only safety. | TLA+ validation task | open | Start with safety, add fairness only when needed. |
| R6 | DCB freshness around formal results needs receipt shape | Formal runs need version, scope/config, input hash, result hash, and read-set linkage. | research-evidence-harness | future-work | Define formal-result receipt schema. |

## Closed Or Downgraded Residue

| ID | Residue | Closure |
| --- | --- |
| CR1 | Which language should replace TypeScript first? | None should replace it; TypeScript remains extraction/witness layer. |
| CR2 | Should Alloy and TLA be merged into one formal lane? | No. Split by graph completeness vs temporal behavior. |
| CR3 | Should DCB prove saga behavior? | No. DCB guards evidence freshness and acceptance. |
