# Frozen synthetic case bank

Frozen 11 October 2026, 18:40:28 UTC. [CASES.json](CASES.json) is the authoritative rule contract. These cases were newly authored by the native `pending_game_case` agent for the pending-strategy investigation. No prior study results, worked examples, gameplay or efficacy assessments were imported.

The bank contains five cases. G-survival, G-expression and G-absurd share one bounded game. H-joint and W-workflow provide non-game applications. Facts described as observed are **synthetic observations within the case**, not observations of this workspace, real players, materials or services.

## Shared game

Choose Ranger, Vanguard or Builder before starting; survive three bosses sequentially, acquiring one item during each stage. Manual control and an authored six-rule autoplay controller use the same world. The 7x5 arena is fully visible:

```text
    1234567
1   .......
2   ..#....
3   S..B...
4   ..#....
5   .......
```

S is the hero start and acquisition tile; B is the boss anchor. The two fixed walls block paths/projectiles. Vents at (4,2) and (4,4) warn before pulsing. Ranger trades low HP for range; Vanguard trades short range for HP/damage; Builder trades low damage for energy and cheaper barriers. JSON supplies every statistic, timing window, target rule, resource cost, tie and status duration.

One action resolves per 250ms tick. Movement, roll, strike, guard, poison, slow, push, temporary barrier, acquisition and wait are ordinary primitives. Bosses warn exact impact tiles before attacks. The three attacks target a tile, a cross and a row respectively; later bosses add poison, slow and knockback. No hidden damage, resistance or instant-kill rule exists. Death fails even when simultaneous with boss death. Clear also requires the mid-stage acquisition.

The baseline selects Ranger, two lenses and a flask. Its six ordered rules escape a warning when possible, otherwise guard, acquire when at S, travel to the available acquisition, strike in recovery, then return to S or wait. Selectors and offsets are frozen in JSON. A simple ordinary route uses the left column to leave warnings and return for recovery shots. Its arithmetic fits the deadline; this supplies a viability witness for investigation, **not an executed or validated game**. Candidate controllers must also specify all six rules, item choices, targets, ties and offsets.

## Investigation cases

| ID | Frozen target | Open construction surface |
|---|---|---|
| G-survival | Three clears with one hero and ordinary costs | Strategy/build changes or declared mechanics involving the shared effects |
| G-expression | Same survival objective and world | Optional calibrated onset timing; equivalent button and authored autoplay offset |
| G-absurd | Same objective, controls and states | Straight courier premise versus furniture seeking promotion from staplers |
| H-joint | Reusable, removable 200N shear connection; intact surfaces/sensor | Arrangement or specified connection mechanism under 240s/100g/25-credit limits |
| W-workflow | Five working logins and exact 100-row export by minute 120 | Scheduling, evidence, linkage and completion rules within role budgets |

Voice uses only a calibrated onset time. It does not infer beauty, identity or musical quality; a failed calibration permits the equivalent button. Input detection and fatigue remain unknown. The absurd frame changes names and expectations only; an added world effect requires a declared extension.

H-joint includes a constrained geometry and finite hammer, nail, clamp, strap and tape inventory. Ratings and install times are explicit synthetic assumptions. Unknown friction, creep and removability cannot be silently supplied. W-workflow includes timed reports, temporary restart relief, different asserted meanings of “done,” person-minute budgets and independent task probes. Shared symptoms do not establish duplicates or a common cause.

## Boundary and diagnostic packet

Both strategy and ordinary control authors receive the same extension allowance. An extension needs a complete condition/action/state/cost/feedback/timing/counter contract and interactions with existing effects. It cannot silently replace the protected outcome, add resources or omit actor inputs. A different run structure is labeled as another concept.

For every proposed operation, preserve one concrete same-action comparison: fixed state and input under ordinary rules, then under the declared change, with the predicted next state and changed dependency. Compare the nearest conventional equivalent at matched cost, power and information. Identical state transitions support a presentation or combination claim rather than a new primitive. A useful probe must be able to expose an invalid construction or equivalence; no desired novel conclusion is built into this bank.

This packet supports written construction and mechanism comparisons. Outcomes requiring gameplay, audience testing, material testing or service verification remain unknown. It contains no efficacy grades.

## Source reads and provenance

Only these three task-authorized sources were read; their exact paths and SHA-256 identities are recorded in JSON:

- MECHANIC-GENERATION-STRATEGIES.md: rule-contract and preserved game obligations.
- RHETORICAL-STRATEGIES.md: distinction between construction, rhetoric, equivalence and evidence.
- PRINCIPLE-STRATEGIES.md: broader protected outcomes, attributed expectations and experience comparisons.

The sources' prepared/untested status remains unchanged. Case numbers, names, ratings, maps and observation histories were invented in this author turn and are not empirical findings.
