# Balancer R2 — goal dependence survives; boundary cases remain

Round 2/3, independent A/B design critique. No implementation or efficacy result. The complete three-stage run is the user's minimum candidate context, not a theorem about adaptation. Component novelty is disclaimed; global novelty remains unknown.

## Repairs accepted as design contracts

R2 closes several R1 omissions: one deployed hero; public observation fields; declared action commitment/cancel windows; six-rule authoring ceiling; temporal escape obligations; attribution of voluntary entrapment; one bindable commitment; finite catalyst capacity/refills; attack-instance resolution ordering; and visibly announced counter variants. These are completed specification decisions, not evidence that their implementation works or players understand them. Do not repeatedly reopen them merely because testing remains future work.

## Track A — controller and preparation boundaries

### A-R2.1 — Hidden coupling: waiting versus rejection changes the controller

**Claim:** “A conflicting command waits or is rejected visibly.” **Evidence/assumption:** admission boundaries and recovery are defined; the disposition remains an alternative. **Counterexample:** a guard request made during cast recovery waits until the warning has ended, while auto's newly evaluated retreat replaces its stale request. Alternatively, queueing every manual input executes several obsolete attacks. **Minimal repair:** choose one provisional rule per command channel, including queue capacity, replacement, expiry and what happens when predicates cease to hold. A diagram or small state table is sufficient. Visibility alone does not settle execution semantics.

### A-R2.2 — Unsupported knowledge: equal cadence does not establish Soulslike feel

**Claim:** 50 ms simulation and 100 ms admission/snapshots support both modes. **Evidence/assumption:** these are openly provisional values; responsiveness is unknown. **Counterexample:** a manual dodge misses the next admission boundary and waits almost 100 ms before recovery checks, making a narrow dodge window feel unreliable. Equal latency cannot repair that experience. **Minimal repair:** mark cadence/window values as tunable and separate shared state/resource/action contracts from input responsiveness. Either retain a measured prototype assumption or declare responsive manual input with bounded auto observations. Require timing/game-feel measurement later; no specific cadence earns readiness by itself.

### A-R2.3 — Agency: hazard exclusions conceal route authority

**Claim:** execution policy “never … changes a route,” but the authored template follows a route “while excluding warned polygons.” **Evidence/assumption:** player authors the exception; the executor's permitted response is undefined. **Counterexample:** the next waypoint lies inside poison rain. The executor silently finds a new path, or freezes until the hero dies; both could claim to honor exclusion. **Minimal repair:** specify whether exclusion means stop, select an explicitly authored alternate segment, or execute a declared local avoidance action. Show that choice before admission. Give manual access to the same route command if route execution is part of the command vocabulary.

### A-R2.4 — Unsupported knowledge: weak controls can manufacture preparation value

**Claim:** authored retreat beats fixed hold-ground or always-retreat in the discriminating case. **Evidence/assumption:** plausible example; comparison validity is untested. **Counterexample:** a generic fixed hazard-avoidance policy makes exactly the authored retreat, exposing only that reckless baselines lose. **Minimal repair:** include a competent fixed policy with identical observations, action vocabulary and costs. Predeclare what the player may know when authoring and revising. Compare a meaningful sacrifice tradeoff across encounter variants, not only the seed designed to favor its exception. Keep these as planned comparisons.

## Track B — one bound contradiction

### B-R2.1 — Novelty equivalence: changed payouts need not change choices

**Claim:** fully guarded contact satisfies touch but defeats wound; public goals should change rational response. **Evidence/assumption:** reward dependence is now explicit; policy dependence is still a hypothesis. **Counterexample:** dodging avoids both touch and wound, earns either payoff, and has lower cost than guarding. Players always dodge; the token changes the explanation but never the decision. **Minimal repair:** retain this unusually legible contradiction, but specify a candidate situation where guard and dodge have real opposing costs. Compare the same physical attack under changed goals and a goal-independent avoidance reward with matched resources/payoffs. A changed reward table alone does not establish changed strategy or originality.

### B-R2.2 — Closure and resource ordering: cancellation lacks a complete lifecycle

**Claim:** bind spends immediately; no refund on cancel; freeze at attack lock; failure pays once if it qualifies. **Evidence/assumption:** spend and resolution order are explicit; cancellation qualification is not. **Counterexample:** the hero binds reach-seal, then interrupts the charge before lock. Was the promise defeated for a payoff, or did its token disappear? A second binding with an existing stored payoff also has undefined overwrite/waste behavior. **Minimal repair:** close unbound → bound → locked → resolved/cancelled/dead states; distinguish player-caused cancellation from issuance invalidation. State payoff replacement and whether binding while storage is occupied is permitted. Use one state table, not additional operators.

### B-R2.3 — Hidden coupling: touch/wound observation needs an endpoint

**Claim:** wound means any attack-caused HP loss; evaluate after ordered hits and same-boundary poison. **Evidence/assumption:** direct-hit attribution is clear; status and collision semantics remain assumed. **Counterexample:** a blocked poisoned strike closes with zero HP loss, then its poison damages the hero one boundary later. An invulnerable dodge overlaps a weapon without an admitted hit. Which promise succeeded? **Minimal repair:** define touch as a named accepted collision/hit event and wound over an explicit observation window. State whether delayed status damage belongs to that window; after closure it cannot reverse the result. Preserve poison as a separate danger.

### B-R2.4 — Fairness: announced counters still need one feasible response

**Claim:** delay and wall breaking leave affordable bait/reroute responses. **Evidence/assumption:** observability is contracted; feasibility remains an asserted constraint. **Counterexample:** Mason has one surviving wall and placement recovery exceeds the announced charge interval; Bastion's stamina cannot cover delay plus guard. The counter is clear but no available response exists. **Minimal repair:** annotate each starting counter with at least one response available under its stated resource/recovery conditions. If none remains, decline binding before spending or expose the deliberate risk. Do not guarantee payoff or prevent ordinary failed play.

## Round verdict

**A: flag. B: flag.** The goal-dependent contradiction is worth retaining. R3 should close command disposition, route authority, token lifecycle and predicate endpoints; keep numeric tuning and efficacy as future verification. Sarcasm collisions, anchor betrayal and wild singing remain separable tests. No extra heroes, operators or recursive rounds are needed.
