# Source-reader realization proposal

Candidate for the single final review package. No admission or adoption effect.

## What is bound

| Item | Exact subject |
| --- | --- |
| Product capability | `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle@foundation.1` |
| Implementation | `implementation:R03-current-episode-0002-source-reader@1.0.0-candidate.1` |
| Agent Capability | `agent-capability:R03-current-episode-0002@1.0.0-candidate.1` |
| Entry point | `current-source-adapter-v2/reader.py#SelectedReader.open_signed` |
| Input | Independently pinned signed source branch and exact original artifact references |
| Output | Original records with byte, selector and revision witnesses |

This is one semantic source-reading unit. The Implementation and Agent Capability belong to the same binding; supporting code files do not become separate realization bindings.

## What the assessment proves

The binding passes the v2 schema. Exact original subjects, input/output protocol references, code and environment selection match retained signed-source evidence. The 17 reader cases and 94 independent checks remain passing and every retained input digest was checked again. The independent audit actually called the declared reader, resolved original bodies and disposed its owned read workspace.

The scoped conformance profile covers six obligations: exact original endpoints, actual code/environment selection, declared input/output contracts, authentic cold-source use, reader regression boundaries and current retained input bytes. All six passed for this scope.

## What remains open

The reader is a subset of Governed Knowledge Lifecycle. Complete Project State, bounded Agent context, evidence lineage and ontology projection contract fulfillment require their own complete assessments. The first current Agent lifecycle observation failed at session.open and its diagnostic is still running; reader evidence does not qualify that lifecycle.

W09 supplies authentic engineering/research workflow evidence. O07 supplies authentic scoped ontology reconstruction/coherence evidence. Their exact semantic realization declarations and contract correspondence still need to be materialized in R04. The broader task is in progress.

## Effects and owners

The binding is candidate-unadmitted and its adoption Decision is null. Declared owners and routes are retained as references; no current governing owner authority is inferred. No Capability Instance requiring an adoption Decision is fabricated. No new global realizes relation is added. Actual binding admission and owner-local adoption follow the represented R08/A03 authority.

Historical isolated use, current service liveness and human value are independent. Current liveness and human value are NOT_EVALUABLE.

## Review files

- `binding.json`: exact candidate realization binding.
- `conformance-profile.json`: bounded obligations and evidence sufficiency rule.
- `conformance.json`: endpoint/body/code witnesses, findings, unknowns and effects.
- `receipts/R04-0002.json`: verified input/output/terminal closure.
