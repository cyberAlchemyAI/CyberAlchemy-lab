# Open Residue

Status: active

## Open Items

| ID | Residue | Current risk | Owner route | Priority |
| --- | --- | --- | --- | --- |
| R1 | Validate Alloy syntax and Analyzer behavior. | Example could be misleading if syntactically wrong. | task-session | high |
| R2 | Validate TLA+ syntax and TLC behavior. | Example could be misleading if the state model is wrong. | task-session | high |
| R3 | Decide Saga-vs-Workflow `orchestrates` representation. | Graph lane may keep flagging the same signature gap. | definitions-governance | medium |
| R4 | Define TypeScript-to-formal fixture contract. | Manual examples will drift from actual DomainSpec artifacts. | implementation-readiness | high |
| R5 | Define formal-result receipt shape for DCB acceptance. | Freshness layer cannot safely accept model results without stable metadata. | research-evidence-harness | medium |
| R6 | Decide when to introduce liveness/fairness. | First TLA+ model may overfit safety only. | TLA+ validation task | medium |

## Not Open

| Question | Closure |
| --- | --- |
| Should DCB be the proof engine? | No. It is the freshness/acceptance guard. |
| Should TypeScript be discarded? | No. It is the extraction and bounded-witness layer. |
| Should Alloy and TLA+ be one lane? | No. Split by graph completeness vs temporal behavior. |
