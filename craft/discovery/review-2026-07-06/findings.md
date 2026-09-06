# Discovery Review — `domainspec-v2-discovery.md` (repo-fidelity)

Dispatch: `2026-07-06-dsv2-discovery-repo-fidelity-review` (`dispatch_type: review`, inline + banked)
Question: **is the discovery faithful to the rest of the domainspec-v2 repo** — every claim matches source/state/law, no load-bearing repo concept silently omitted.
Method: 5 red-team attackers (attack-vector axis) → robot-talks → synthesis → 2 independent verifiers (zig-zag, 2 turns) → coverage auditor (final_approver: ACCEPT).
Verdict: **FIX** — 3 MAJOR + 4 MINOR survive verification; 3 findings dropped on refutation.

## Surviving change-requests

| # | Sev | Doc → repo | Evidence (doc vs repo) | Fix |
|---|-----|-----------|------------------------|-----|
| 1 | **MAJOR** | §2/§3 "31 legal signatures", step-3 (doc:146), OQ-3 → `DEC-DSV2-EDGE-ADMISSIBILITY` (CRAFT.md:36), DS-D8/DS-D2; D16 (DEFINITIONS.md:621-623) | Doc validates edges & raises OQ-3 but never names **the criterion that admits a signature** (why 31, what admits a 32nd) nor its authorities. doc:146 "checked against the legal signatures" **clashes** with D16: a forbidden edge is *unconstructible, not flagged*. | Name the admissibility criterion + DS-D8/DS-D2 as signature/verb authority; correct step-3 wording to D16 modality. |
| 2 | **MAJOR** ⚠️ | Lines 84 / 89-91 → `relationships.yml` (active) | "11 UI types … prose in TAXONOMY.md only, **no registry row**" is **literally false**: relationships.yml registers all 11 UI types as active typed edge endpoints. Central 14/25 *criterion* thesis stays intact. | Narrow to "no *meta-type registry row* / no *criterion schema* — UI types are machine-registered as active endpoints in relationships.yml." |
| 3 | **MAJOR** ⚠️ | §4 (loop), §6 (open-questions register) → `DEC-DSV2-LANE-ZA` | §6 IS the open-questions register yet **never names the single open architectural bet**. §4 carries both "one typed graph"(171, fuse/Lane Z) and "fills a mold"(176, generate/Lane A). | Add OQ-5 naming DEC-DSV2-LANE-ZA (fuse vs generate+separate; default-defer; decider = agent-cost experiment); disambiguate §4's two claims (demoted to MINOR rider). |
| 5 | MINOR | OQ-1 → D15 (DEFINITIONS.md:561-598) | OQ-1 raises the discriminator risk that D15 ("do not infer the discriminator by parsing the Formal cell") already resolves by convention; OQ-1 voices the caveat but never cites the mechanism. | Cross-ref D15 in OQ-1. |
| 6 | MINOR | "no clock" citation → `rules/index.ts:37` | Citation points at `index.ts` (which asserts no-LLM/no-network only); the "no clock" property lives in `rules/index.ts:37`. | Repoint the citation. |
| 7 | MINOR | OQ-3 → `derive()` | "7 EdgeTypes for derivation" overstates: `derive()` reads `byType(graph,NodeType)` only, never `graph.edges`. | Qualify OQ-3: derive reads nodes-by-type only. |
| 9 | MINOR | "what's broken" (Obs-B) → AUTHORITY-MODEL:38 | Obs-B listed as an open problem, but it is an already-holding emit-time invariant ("needs no later decision to become true"). | Move Obs-B out of "broken"; relist as the holding guard against mint-time leakage. |

## Dropped on verification

- **#1-math** — the D18 non-collapse test + D20-D25 properties *as formalism* are the recursive-governance math §1 (lines 62-73) explicitly scopes out. Only the criterion/authority **naming** is owed (→ #1). This is why no CRITICAL survives.
- **#4 (§5 "witness" over-labels)** — both verifiers refuted: §5 scopes the witness to "(non-vacuous validators)" and the doc never claims `derive` ran on financial-settlement; §5 also concedes the loop "has not been run end to end." No literal clash.
- **#8 (§3 "what runs today")** — internally hedged (step 6 "wired, not exercised"); no clash.

## Owner judgment calls (flagged, not auto-resolved)

1. **#2 severity — MAJOR vs MINOR.** A literally-false clause ("no registry row") sits inside the doc's central machine-backing thesis (synthesizer holds MAJOR); defensible as MINOR since the load-bearing 14/25 *criterion* claim is correct and the fix is a narrowing, not a retraction (Kahneman).
2. **#3 §4 rider sufficiency.** §6-register omission held MAJOR; the §4 Z/A conflation demoted to a MINOR rider because §4 already flags "hypothesis under test." Confirm that hedge is enough.
3. **#1 scope of the fix.** Confirm only the criterion + authority *naming* is owed, not the D18/D20-D25 *math* (which §1 legitimately scopes out).

## What held (attacked, survived)

All numeric/mechanical claims are accurate: 14 backend meta-types (meta-types.yml), 31 signatures, 7 EdgeTypes, derive counts RANGE→4 / COUNT_CAP→2. Governance triad (LAW/CHECK/TREND), promotion gates, ratification dates, νF/`Stream<CheckResult>` honesty, and Saturn non-collapse all match the authority docs. The doc's self-flagged inconsistencies (25-vs-14 header, two edge vocabularies) are surfaced, not hidden. The fidelity gap is concentrated in **omitted authority naming and one over-strong body clause**, not in miscounts.

---
*Infra note: init-time anti-bias (check-tension) gate ran 3× (once per sheet revision), PASS/PASS each. Attacker robot-talks resumed the 5 attackers with cross-findings before synthesis. Verifier zig-zag ran 2 turns to reconcile a genuine scope dissent between the two verifiers.*
