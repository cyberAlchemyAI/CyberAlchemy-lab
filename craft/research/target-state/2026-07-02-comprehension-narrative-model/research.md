---
node_type: research
is_session: false
status: candidate
created: 2026-07-02
authored_by: domainspec-subagents-strategy
dispatch: 2026-07-02-spec-comprehension-model
promotion_boundary: local research only.
---

# Research method & provenance — Spec Comprehension Model

## Dispatch shape
- **Type:** research. **Groups:** 2 (explorers → skeptics), sequential edge (skeptics attack the merged
  explorer candidate). **final_approver:** parent.
- **Composite tension axis** (declared at propose): *methodology × source-corpus* — three comprehension
  methodologies (narrative, example, distillation) each grounded in a distinct primary corpus
  (Alexander/OCM · Polanyi/tacit-knowledge · Evans/DDD). Passed the check-tension gate first-pass.

## Roster
| Group | Agent (lens) | Terminal position | Deliverable |
|---|---|---|---|
| 1 explorers | Alexander — narrative/OCM | minimal "comprehension contract", forms *projected* not authored | `lens-narrative.md` |
| 1 explorers | Polanyi — example/tacit | example-first (pos + discriminating neg + axis) | `lens-example.md` |
| 1 explorers | Wittgenstein — DDD distillation | distill to core; adding forms = anti-Evans | `lens-distillation.md` |
| (merge) | strategist | 4-move merged candidate | `candidate-model.md` |
| 2 skeptics | Feyerabend — anti-ceremony | STILL TOO MUCH — cut further, author zero | `skeptic-feyerabend.md` |
| 2 skeptics | Gigerenzer — completeness | REDUCTION LOSES COMPLETENESS — verify novice | `skeptic-gigerenzer.md` |

Genuine tension confirmed at close: the two skeptics rendered **opposite terminal verdicts** on the *same*
candidate; the synthesis is a partition (findings.md §"4-region partition"), not a coin-flip.

## P8 verification log (strategist re-checked every load-bearing claim on disk)
| Claim (by whom) | Check | Result |
|---|---|---|
| Crossed Money pair exists (Polanyi) | read `entity-bad.md` + `value-object-ok.md` | ✅ same concept, two verdicts |
| 5 UI types are declared backend shadows (Wittgenstein) | `TAXONOMY.md:28,33,37,38,39,40` | ✅ "Backend Counterpart" column |
| `entity.md` projects `entity.schema.yml` (Feyerabend) | header↔key diff | ✅ near-total projection |
| All 14 backend schemas carry `distinguisher.vs` (Feyerabend) | scan all 14 `.schema.yml` | ✅ 14/14 (single-valued) |
| No UI schema exists (Feyerabend, shared residue) | `find meta-types` | ✅ none |
| 5 weak fixtures (Gigerenzer): Enum/Interface/Mapping malformed-only, Event/State-Machine intent-flip | read all 5 `-bad.md` | ✅ confirmed classification |
| Shadow-collapse loses edges (Gigerenzer) | `RELATIONSHIPS.md:39,51` | ✅ Guard sources `protects`/`mirrors`, ≠ Rule's `enforces` |

## Corrections surfaced during synthesis (claim ≤ proof)
- The **candidate's own R2 was refuted** by disk: it guessed behavioral/lifecycle would lack pairs;
  behavioral is 7/7. The real gap is connective (0/3) + lifecycle (0/1) + Enum.
- Primary sources were **not reachable**: DDD Reference PDF 403'd; narrativedriven.org / NDD primary URLs
  dead. All external quotes are **secondary** (Fowler, herbertograca 2016, Wikipedia, Vaadin/DevIQ) and
  labelled as such in the lenses. The DomainSpec disk facts are primary and were all re-verified here.

## Boundary
No engine `src/rules` touched or referenced. All work is spec-surface comprehension. Outputs are local
research; promotion to `domainspec-v2` awaits owner confirmation.
