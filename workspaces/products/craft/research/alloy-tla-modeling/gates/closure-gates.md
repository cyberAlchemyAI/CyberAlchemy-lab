# Closure Gates

Status: pass for research orientation and executable surface; partial for formal proof readiness

## Gate Table

| Gate | Expected | Actual | Status |
| --- | --- | --- | --- |
| Source record exists | `SOURCE-RECORD.md` lists URLs/paths, version/freshness, date checked, and source boundary. | Present. | pass |
| Source claims labeled | `CLAIM-LEDGER.md` separates primary-source, local-inference, operator-reading, and open residue. | Present. | pass |
| Notation bridge exists | Symbols needed to read examples are explained before examples. | Present. | pass |
| Glossary and definitions exist | Local terms have source kind, operator reading, and misuse warning. | Present. | pass |
| Related work bounded | Crosswalk only includes frameworks needed for named residue. | Present. | pass |
| Two-lane discipline honored | Lane Z builds out formal promotion; Lane A challenges with alternatives. | Present in `TOWER.md`. | pass |
| `/domainspec-subagents-strategy` honored | Proposed dispatch recorded; actual fan-out not run without human confirm. | Present in `subagents/PROPOSED-DISPATCH.md` and `SUBAGENT-CLOSEOUT.md`. | pass |
| Promotion boundary explicit | No taxonomy/relationship mutation from this tower. | Present. | pass |
| Final learning pack exists | Operator-readable synthesis exists and reflects tool-run evidence. | Present and updated after tool execution. | pass |
| Local toolchain | Java, TLA+, and Alloy are available without tracked binaries. | Portable JRE, TLA+ jar, and Alloy jar installed under ignored `.formal-tools/`; receipts captured. | pass |
| Wrapper surface | Future agents can run stable commands without rediscovering paths. | `tooling/` scripts parse and wrapper smoke checks pass. | pass |
| Alloy validation | Alloy tool run produces bounded result and receipt. | Alloy 6.2.0 listed commands and executed all declared commands after reserved-word syntax repair; no counterexample found for completeness in scope 8. | pass-bounded |
| TLA+ validation | SANY/TLC run produces accepted result or exact counterexample. | SANY parses; TLC runs and finds `FreshnessSafety` counterexample after acceptance followed by waiver change. | flag-counterexample |
| Fixture contract | TypeScript witness has a reviewable formal fixture shape. | JSON Schema, example fixture, and README exist; JSON validation passes. | pass |

## Gate Verdict

This tower passes as a research, route-selection, and local executable-surface artifact.

It does not pass as a proof artifact. Alloy currently provides bounded graph evidence in scope 8. TLA+ currently provides a useful freshness counterexample that must be repaired or reframed before any saga-correctness claim can be accepted.
